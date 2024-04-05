# Use the official Spark base image
FROM bitnami/spark:latest

# Copy the PostgreSQL JDBC driver JAR file into the Spark jars directory
COPY ./requirements.txt /requirements.txt

RUN pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r /requirements.txt

# Set the Spark master command
CMD ["bin/spark-class", "org.apache.spark.deploy.master.Master"]
