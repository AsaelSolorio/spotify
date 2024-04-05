import os
os.environ['PYSPARK_SUBMIT_ARGS'] = "--packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.1.2 pyspark-shell"

import pyspark
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, to_timestamp, window, avg, col
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType, TimestampType

# Initialize a Spark session with necessary Kafka and JDBC dependencies
KAFKA_BOOTSTRAP_SERVERS = "kafka:9093"
subscribeType = "subscribe"
KAFKA_TOPIC = "spotify"

spark = SparkSession.builder\
    .appName("StreamSpotifyProcessing")\
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.1.2,org.mongodb.spark:mongo-spark-connector_3.0:3.0.1")\
    .getOrCreate()

    
# # Step 2: Define the schema of the data
schema = StructType([
    StructField("Temperature_max", DoubleType(), True),
    StructField("Temperature_min", DoubleType(), True),
    StructField("humidity", StringType(), True),
    StructField("timestamp", StringType(), True)
])

# # Step 3:read from kafka
df = spark.readStream.format("kafka")\
    .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS)\
    .option(subscribeType, KAFKA_TOPIC)\
    .option("failOnDataLoss", "false")\
    .option("startingOffsets", "latest").load()

# # Step 4: Deserialize JSON and convert timestamp
weather_data = df.selectExpr("CAST(value AS STRING)")\
    .select(from_json("value", schema).alias("data"))\
    .select("data.*")\
    .withColumn("timestamp", to_timestamp("timestamp", "yyyy-MM-dd'T'HH:mm:ss.SSSSSS"))
 
# Step 5: Apply a 20-second windowed operation
windowed_data = weather_data\
    .groupBy(
        window(col("timestamp"), "20 seconds"),  # Defining the window duration
    )\
    .agg(avg((col("Temperature_min") + col("Temperature_max")) / 2).alias("avg_temp"),
        avg(col("humidity").cast("double")).alias("avg_humidity"))  # Calculate average humidity

# Step 6: Prepare the final DataFrame for writing
output_data = windowed_data.select(
    col("window.start").alias("window_start"),
    col("window.end").alias("window_end"),
    col("avg_humidity"),  # Select average humidity column
    col("avg_temp")
)


def writeToMongo(df, batchId):
        df.write \
        .format("mongo") \
        .option('uri', 'mongodb://127.0.0.1')\
        .option('database', 'spotifydb') \
        .option('collection', 'spotifycoll') \
        .mode("append") \
        .save()
        pass
