import random

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util

cid ="69457297a5cc42a4a9b19ba477558210"
secret = "b8df8b59a120497eb7667bdb881058b7"
username = "dylrobinson22"

def getSP():


    client_credentials_manager = SpotifyClientCredentials(client_id=cid,
                                                        client_secret=secret)

    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    scope = 'playlist-modify-private playlist-modify-public playlist-read-private user-library-read'
    token = util.prompt_for_user_token(username, scope, client_id=cid, client_secret=secret, redirect_uri='http://localhost/')
    if token:
        sp = spotipy.Spotify(auth=token)
        print("Success?")

    else:
        print("Can't get token for", username)
    return sp

sp = getSP()

playlistToShuffle = sp.user_playlist(username, "2r9yCEJvyTzopApX2t4Mvw")

def getIDs(tracks, songs):
    #tracks = playlist["tracks"]
    #songs = tracks["items"]
    while tracks['next']:
        tracks = sp.next(tracks)
        for item in tracks["items"]:
            songs.append(item)
    ids = []
    for i in range(len(songs)):
        ids.append(songs[i]['track']['id'])
    return ids


def shufflePlaylist(playlist):
    tracks = playlist['tracks']
    songs = tracks['items']
    ids = getIDs(tracks, songs)
    random.shuffle(ids)
    if len(ids) <= 100:
        sp.user_playlist_replace_tracks(username, playlistToShuffle['id'], ids)
    else:
        sp.user_playlist_replace_tracks(username, playlistToShuffle['id'], ids[0:100])
        for i in range(100, len(ids), 100):
            sp.user_playlist_add_tracks(username, playlistToShuffle['id'], ids[i:i+100])

#shufflePlaylist(playlistToShuffle)
sp.user_playlists(username, 50, 0)
print("Reordered playlist")
