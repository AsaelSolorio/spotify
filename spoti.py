import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

ID_PLAYLIST = '38MPRPbymlDZF4rTvgV575'
market = 'MX'

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id="8811d03106ae4aafb614b1432c9ce321",
                                                           client_secret="19ea883ff0d44a51a0eabae2621173ae"))
playlist_url = f'https://api.spotify.com/v1/playlists/{ID_PLAYLIST}?market={market}'



def getTrackID(user, playlist_id):
        id = []
        playlist = sp.user_playlist(user, playlist_id)
        for item in playlist['tracks']['items']:
                track = item['track']
                id.append(track['id'])
        return id
    
def getTrackFeatures(id):
        meta = sp.track(id)
        features = sp.audio_features(id)
        
        # meta data
        name = meta['name']
        album = meta['album']['name']
        artist = meta['album']['artists'][0]['name']
        # features from data
        danceability = features[0]['danceability']
        track = [name, album, artist, danceability]
        return track
    