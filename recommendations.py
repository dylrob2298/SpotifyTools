import pandas as pd
import numpy as np

from collections import Counter

import random

from matplotlib import pyplot as plt
import seaborn as sns

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util

cid = "69457297a5cc42a4a9b19ba477558210"
secret = "b8df8b59a120497eb7667bdb881058b7"
username = "dylrobinson22"


def getSP():

    client_credentials_manager = SpotifyClientCredentials(client_id=cid,
                                                          client_secret=secret)

    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    scope = 'playlist-modify-private playlist-modify-public playlist-read-private user-library-read user-top-read'
    token = util.prompt_for_user_token(
        username, scope, client_id=cid, client_secret=secret, redirect_uri='http://localhost/')
    if token:
        sp = spotipy.Spotify(auth=token)
        # print("Success?")

    else:
        print("Can't get token for", username)
    return sp


def getItems(page):
    sp = getSP()
    items = page["items"]
    while page["next"]:
        page = sp.next(page)
        items.extend(page["items"])
    return items


def getIDs(items):
    """Given a list of Spotify objects with IDs, return the IDs"""
    ids = []
    for i in range(len(items)):
        ids.append(items[i]['id'])
    return ids


sp = getSP()

# Get top artists

artistsPageShort = sp.current_user_top_artists(
    limit=50, offset=0, time_range="short_term")
artistsPageMed = sp.current_user_top_artists(
    limit=50, offset=0, time_range="medium_term")
artistsPageLong = sp.current_user_top_artists(
    limit=50, offset=0, time_range="long_term")

print(artistsPageShort["total"])
print(artistsPageShort["next"])
print(artistsPageMed["total"])
print(artistsPageMed["next"])
print(artistsPageLong["total"])
print(artistsPageLong["next"])

topArtistsShort = getItems(artistsPageShort)
topArtistsMed = getItems(artistsPageMed)

topArtistsLong = getItems(artistsPageLong)

taShortNames = []
for artist in topArtistsShort:
    taShortNames.append(artist["name"])

taMedNames = []
for artist in topArtistsMed:
    taMedNames.append(artist["name"])

taLongNames = []
for artist in topArtistsLong:
    taLongNames.append(artist["name"])

taShortNames
taMedNames
taLongNames

artistNames = taShortNames + taMedNames + taLongNames

artistNameCount = Counter(artistNames)

artist3 = []

for artist in artistNameCount:
    if artistNameCount[artist] == 3:
        artist3.append(artist)

artist3

# Get Top Songs

songsPageShort = sp.current_user_top_tracks(
    limit=50, offset=0, time_range="short_term")
songsPageShort2 = sp.current_user_top_tracks(
    limit=50, offset=49, time_range="short_term")
songsPageMed = sp.current_user_top_tracks(
    limit=50, offset=0, time_range="medium_term")
songsPageMed2 = sp.current_user_top_tracks(
    limit=50, offset=49, time_range="medium_term")
songsPageLong = sp.current_user_top_tracks(
    limit=50, offset=0, time_range="long_term")
songsPageLong2 = sp.current_user_top_tracks(
    limit=50, offset=49, time_range="long_term")

print(songsPageLong["total"])

topSongsShort = getItems(songsPageShort)
topSongsShort2 = getItems(songsPageShort2)
topSongsMed = getItems(songsPageMed)
topSongsMed2 = getItems(songsPageMed2)
topSongsLong = getItems(songsPageLong)
topSongsLong2 = getItems(songsPageLong2)

topSongsShort.extend(topSongsShort2[1:])
topSongsMed.extend(topSongsMed2[1:])
topSongsLong.extend(topSongsLong2[1:])


songShortNames = []
for song in topSongsShort:
    songShortNames.append(song["name"])

songShortNames

songMedNames = []
for song in topSongsMed:
    songMedNames.append(song["name"])

songMedNames

songLongNames = []
for song in topSongsLong:
    songLongNames.append(song["name"])

songLongNames2 = []
for song in topSongsLong2:
    songLongNames2.append(song["name"])

songLongNames
songLongNames2


songNames = songShortNames + songMedNames + songLongNames

songOccurences = Counter(songNames)

songs3 = []
songs2 = []

for song in songOccurences:
    if songOccurences[song] == 3:
        songs3.append(song)

for song in songOccurences:
    if songOccurences[song] == 2:
        songs2.append(song)

songs3
songs2

songShortIDs = getIDs(topSongsShort)
songMedIDs = getIDs(topSongsMed)
songLongIDs = getIDs(topSongsLong)

songFeatures = []


def addSongFeatures(features, songs, ids, target, weight):
    sp = getSP()
    k = 0
    for i in range(0, len(ids), 50):
        audio_features = sp.audio_features(ids[i:i + 50])
        for track in audio_features:
            # track['id'] = ids[k]
            # track['song_title'] = songs[k]['track']['name']
            # track['artist'] = songs[k]['track']['artists'][0]['name']
            popularity = songs[k]['popularity']
            for j in range(0, weight):
                features.append(track)
                features[-1]['trackPopularity'] = popularity
                features[-1]["target"] = target


addSongFeatures(songFeatures, topSongsShort, songShortIDs, 0, 2)
addSongFeatures(songFeatures, topSongsMed, songMedIDs, 1, 3)
addSongFeatures(songFeatures, topSongsLong, songLongIDs, 2, 1)


print(len(topSongsShort))
print(len(topSongsMed))
print(len(topSongsLong))

print(len(songFeatures))

songData = pd.DataFrame(songFeatures)
songData.head()

# Custom Color Palette for graphs
red_blue_yellow = ['#19B5FE', '#EF4836', '#ffff64']
palette = sns.color_palette(red_blue_yellow)
sns.set_palette(palette)
sns.set_style('white')

short_tempo = songData[songData["target"] == 0]["tempo"]
med_tempo = songData[songData["target"] == 1]["tempo"]
long_tempo = songData[songData["target"] == 2]["tempo"]
short_danceability = songData[songData["target"] == 0]["danceability"]
med_danceability = songData[songData["target"] == 1]["danceability"]
long_danceability = songData[songData["target"] == 2]["danceability"]
short_loudness = songData[songData["target"] == 0]["loudness"]
med_loudness = songData[songData["target"] == 1]["loudness"]
long_loudness = songData[songData["target"] == 2]["loudness"]
short_speechiness = songData[songData["target"] == 0]["speechiness"]
med_speechiness = songData[songData["target"] == 1]["speechiness"]
long_speechiness = songData[songData["target"] == 2]["speechiness"]
short_valence = songData[songData["target"] == 0]["valence"]
med_valence = songData[songData["target"] == 1]["valence"]
long_valence = songData[songData["target"] == 2]["valence"]
short_energy = songData[songData["target"] == 0]["energy"]
med_energy = songData[songData["target"] == 1]["energy"]
long_energy = songData[songData["target"] == 2]["energy"]
short_acousticness = songData[songData["target"] == 0]["acousticness"]
med_acousticness = songData[songData["target"] == 1]["acousticness"]
long_acousticness = songData[songData["target"] == 2]["acousticness"]
short_key = songData[songData["target"] == 0]["key"]
med_key = songData[songData["target"] == 1]["key"]
long_key = songData[songData["target"] == 2]["key"]
short_instrumentalness = songData[songData["target"] == 0]["instrumentalness"]
med_instrumentalness = songData[songData["target"] == 1]["instrumentalness"]
long_instrumentalness = songData[songData["target"] == 2]["instrumentalness"]
short_time_signature = songData[songData["target"] == 0]["time_signature"]
med_time_signature = songData[songData["target"] == 1]["time_signature"]
long_time_signature = songData[songData["target"] == 2]["time_signature"]
short_liveness = songData[songData["target"] == 0]["liveness"]
med_liveness = songData[songData["target"] == 1]["liveness"]
long_liveness = songData[songData["target"] == 2]["liveness"]
short_popularity = songData[songData["target"] == 0]["trackPopularity"]
med_popularity = songData[songData["target"] == 1]["trackPopularity"]
long_popularity = songData[songData["target"] == 2]["trackPopularity"]
short_mode = songData[songData["target"] == 0]["mode"]
med_mode = songData[songData["target"] == 1]["mode"]
long_mode = songData[songData["target"] == 2]["mode"]


# Tempo Graph
fig = plt.figure(figsize=(12, 8))
plt.title("Song Tempo Distribution")
short_tempo.hist(alpha=0.5, bins=30, label="short term")
med_tempo.hist(alpha=0.5, bins=30, label="medium term")
long_tempo.hist(alpha=0.5, bins=30, label="long term")
plt.legend(loc="upper right")
plt.show()


# Danceability Graph
fig2 = plt.figure(figsize=(12, 8))
plt.title("Song Danceability Distribution")
short_danceability.hist(alpha=0.5, bins=30, label="short term")
med_danceability.hist(alpha=0.5, bins=30, label="medium term")
long_danceability.hist(alpha=0.5, bins=30, label="long term")
plt.legend(loc="upper right")
plt.show()


# Loudness Graph
fig = plt.figure(figsize=(12, 8))
plt.title("Song Loudness Distribution")
short_loudness.hist(alpha=0.5, bins=30, label="short term")
med_loudness.hist(alpha=0.5, bins=30, label="medium term")
long_loudness.hist(alpha=0.5, bins=30, label="long term")
plt.legend(loc="upper right")
plt.show()


# Speechiness Graph
fig = plt.figure(figsize=(12, 8))
plt.title("Song Speechiness Distribution")
short_speechiness.hist(alpha=0.5, bins=30, label="short term")
med_speechiness.hist(alpha=0.5, bins=30, label="medium term")
long_speechiness.hist(alpha=0.5, bins=30, label="long term")
plt.legend(loc="upper right")
plt.show()


# Valence Graph
fig = plt.figure(figsize=(12, 8))
plt.title("Song Valence Distribution")
short_valence.hist(alpha=0.5, bins=30, label="short term")
med_valence.hist(alpha=0.5, bins=30, label="medium term")
long_valence.hist(alpha=0.5, bins=30, label="long term")
plt.legend(loc="upper right")
plt.show()


# Energy Graph
fig = plt.figure(figsize=(12, 8))
plt.title("Song Energy Distribution")
short_energy.hist(alpha=0.5, bins=30, label="short term")
med_energy.hist(alpha=0.5, bins=30, label="medium term")
long_energy.hist(alpha=0.5, bins=30, label="long term")
plt.legend(loc="upper right")
plt.show()


# Acousticness Graph
fig = plt.figure(figsize=(12, 8))
plt.title("Song Acousticness Distribution")
short_acousticness.hist(alpha=0.5, bins=30, label="short term")
med_acousticness.hist(alpha=0.5, bins=30, label="medium term")
long_acousticness.hist(alpha=0.5, bins=30, label="long term")
plt.legend(loc="upper right")
plt.show()


# Key Graph
fig = plt.figure(figsize=(12, 8))
plt.title("Song Key Distribution")
short_key.hist(alpha=0.5, bins=30, label="short term")
med_key.hist(alpha=0.5, bins=30, label="medium term")
long_key.hist(alpha=0.5, bins=30, label="long term")
plt.legend(loc="upper right")
plt.show()


# Instrumentalness Graph
fig = plt.figure(figsize=(12, 8))
plt.title("Song Instrumentalness Distribution")
short_instrumentalness.hist(alpha=0.5, bins=30, label="short term")
med_instrumentalness.hist(alpha=0.5, bins=30, label="medium term")
long_instrumentalness.hist(alpha=0.5, bins=30, label="long term")
plt.legend(loc="upper right")
plt.show()


# Time Signature Graph
fig = plt.figure(figsize=(12, 8))
plt.title("Song Time Signature Distribution")
short_time_signature.hist(alpha=0.5, bins=30, label="short term")
med_time_signature.hist(alpha=0.5, bins=30, label="medium term")
long_time_signature.hist(alpha=0.5, bins=30, label="long term")
plt.legend(loc="upper right")
plt.show()


# Liveness Graph
fig = plt.figure(figsize=(12, 8))
plt.title("Song Liveness Distribution")
short_liveness.hist(alpha=0.5, bins=30, label="short term")
med_liveness.hist(alpha=0.5, bins=30, label="medium term")
long_liveness.hist(alpha=0.5, bins=30, label="long term")
plt.legend(loc="upper right")
plt.show()


# Mode Graph
fig = plt.figure(figsize=(12, 8))
plt.title("Song Mode Distribution")
short_mode.hist(alpha=0.5, bins=30, label="short term")
med_mode.hist(alpha=0.5, bins=30, label="medium term")
long_mode.hist(alpha=0.5, bins=30, label="long term")
plt.legend(loc="upper right")
plt.show()


# Short term means
short_acousticness.mean()
short_danceability.mean()
short_energy.mean()
short_instrumentalness.mean()
short_loudness.mean()
short_speechiness.mean()
short_tempo.mean()
short_valence.mean()


# Medium term means
med_acousticness.mean()
med_danceability.mean()
med_energy.mean()
med_instrumentalness.mean()
med_loudness.mean()
med_speechiness.mean()
med_tempo.mean()
med_valence.mean()


# Long term means
long_acousticness.mean()
long_danceability.mean()
long_energy.mean()
long_instrumentalness.mean()
long_loudness.mean()
long_speechiness.mean()
long_tempo.mean()
long_valence.mean()

meanAcousticness = round(songData["acousticness"].mean(), 3)
meanDance = round(songData["danceability"].mean(), 3)
meanEnergy = round(songData["energy"].mean(), 3)
meanInstrumental = round(songData["instrumentalness"].mean(), 3)
meanLoudness = round(songData["loudness"].mean(), 3)
meanSpeechiness = round(songData["speechiness"].mean(), 3)
meanTempo = round(songData["tempo"].mean(), 3)
meanValence = round(songData["valence"].mean(), 3)

# Standard Deviation

stdAcousticness = songData["acousticness"].std()
stdDance = songData["danceability"].std()
stdEnergy = songData["energy"].std()
stdInstrumental = songData["instrumentalness"].std()
stdLoudness = songData["loudness"].std()
stdSpeechiness = songData["speechiness"].std()
stdTempo = songData["tempo"].std()
stdValence = songData["valence"].std()


def getAlbumIDs(songs):
    ids = []
    for song in songs:
        ids.append(song["album"]["id"])
    return ids


def getAlbums(songs):
    sp = getSP()
    ids = getAlbumIDs(songs)
    albums = []
    k = 0
    for i in range(0, len(ids), 20):
        # albums.append([])
        albums.extend(sp.albums(ids[i:i + 20])["albums"])
        #k = k + 1
    return albums

# Albums currently don't seem to store genres

# albumIDs = getAlbumIDs(topSongsShort)
# sp = getSP()
# albums = sp.albums(albumIDs[0:20])
# albums["albums"][6]["artists"]
#
# topShortAlbums = getAlbums(topSongsShort)
#
# topShortAlbums[0]
#
# print(topShortAlbums)
# len(topShortAlbums)
#
# albGenres = []
# for album in topShortAlbums:
#     albGenres.append(album["genres"])


topArtistsShort
topArtistsMed
topArtistsLong


genres = sp.recommendation_genre_seeds()["genres"]
genres
# genreDict = {}
#
# for i in range(0, len(genres)):
#     genreDict[genres[i]] = 0

genres = []

for artist in topArtistsShort:
    genres = genres + artist["genres"]

for artist in topArtistsMed:
    genres = genres + artist["genres"]

for artist in topArtistsLong:
    genres = genres + artist["genres"]

genreCount = Counter(genres)

genreCount

genreCount.most_common()


taShortIDs = getIDs(topArtistsShort)
taMedIDs = getIDs(topArtistsMed)
taLongIDs = getIDs(topArtistsLong)

topArtistIDs = taShortIDs + taMedIDs + taLongIDs

topACommonIDs = Counter(topArtistIDs)

topArtists3IDs = []

for id in topACommonIDs:
    if topACommonIDs[id] == 3:
        topArtists3IDs.append(id)

topArtists3IDs

topArtists = topArtistsShort + topArtistsMed + topArtistsLong

topArtists3 = []

for i in range(0, len(topArtists3IDs)):
    for artist in topArtists:
        if artist["id"] == topArtists3IDs[i]:
            topArtists3.append(artist)
            break

topArtistSeeds = topArtistIDs + topArtists3IDs  # + topArtists3IDs


songShortIDs
songMedIDs
songLongIDs

topSongIDs = songShortIDs + songMedIDs + songLongIDs

topSCommonIDs = Counter(topSongIDs)

topSongIDs2 = []

for id in topSCommonIDs:
    if topSCommonIDs[id] >= 2:
        topSongIDs2.append(id)

topSongs = topSongsShort + topSongsMed + topSongsLong

topSongs2 = []

for i in range(0, len(topSongIDs2)):
    for song in topSongs:
        if song["id"] == topSongIDs2[i]:
            topSongs2.append(song)
            break

topSongSeeds = getIDs(topSongs + topSongs2)  # + topSongs2)


def getRandomSeeds(seeds, num):
    seedsResult = []

    for i in range(0, num):
        x = True
        while x:
            seed = seeds[random.randint(0, len(seeds) - 1)]
            if not(seed in seedsResult):
                seedsResult.append(seed)
                x = False

    return seedsResult


artistSeeds = getRandomSeeds(topArtistSeeds, 5)

print(artistSeeds)

sp = getSP()


def getRecommendations(seed_artists, seed_tracks, seed_genres, limit):

    rec = sp.recommendations(seed_artists=seed_artists,
                             seed_tracks=seed_tracks,
                             seed_genres=seed_genres,
                             limit=limit,
                             country="US",
                             target_tempo=meanTempo + stdTempo,
                             target_danceability=meanDance - stdDance,
                             target_loudness=meanLoudness,
                             target_speechiness=meanSpeechiness,
                             target_valence=meanValence + stdValence,
                             target_energy=meanEnergy + stdEnergy,
                             target_acousticness=meanAcousticness,
                             target_instrumentalness=meanInstrumental,
                             max_speechiness=meanSpeechiness + stdSpeechiness,
                             max_instrumentalness=meanInstrumental + stdInstrumental,
                             max_acousticness=meanAcousticness + 2 * stdAcousticness)

    return getIDs(rec["tracks"])


artistSeeds = getRandomSeeds(topArtistSeeds, 1)
songSeeds = getRandomSeeds(topSongSeeds, 2)
genreSeeds = ["punk", "rock"]


recTracks = getRecommendations(artistSeeds, songSeeds, genreSeeds, 30)

print(recTracks)

recTracksFinal = []
x = 0
while True:
    for track in recTracks:
        if not sp.current_user_saved_tracks_contains([track])[0]:
            recTracksFinal.append(track)
    recTracksFinal = list(set(recTracksFinal))
    if len(recTracksFinal) >= 30:
        break
    else:
        print(x)
        x = x + 1
        artistSeeds = getRandomSeeds(topArtistSeeds, 1)
        songSeeds = getRandomSeeds(topSongSeeds, 4)
        genreSeeds = []
        recTracks = getRecommendations(artistSeeds, songSeeds,
                                       genreSeeds, 30 - len(recTracksFinal))


sp.user_playlist_add_tracks(
    "dylrobinson22", "76F0qSYJVNl4UGXdW0gd3L", recTracksFinal)


#
#
#
# recFromArtistSeeds = (sp.recommendations(seed_artists = artistSeeds,
#                                         limit = 40,
#                                         target_tempo = meanTempo,
#                                         target_danceability = meanDance,
#                                         target_loudness = meanLoudness,
#                                         target_valence = meanValence,
#                                         target_energy = meanEnergy,
#                                         target_acousticness = meanAcousticness,
#                                         target_instrumentalness = meanInstrumental,
#                                         max_danceability = meanDance + stdDance,
#                                         min_energy = meanEnergy - stdEnergy)["tracks"])
#
# for track in recFromArtistSeeds:
#     print(sp.current_user_saved_tracks_contains([track["id"]]))
#
#
#
#
# recFromArtistFinal = []
# while True:
#     for track in recFromArtistSeeds:
#         if not sp.current_user_saved_tracks_contains([track["id"]])[0]:
#             recFromArtistFinal.append(track)
#     if len(recFromArtistFinal) >= 40:
#         break
#     else:
#         artistSeeds = getRandomSeeds(topArtistSeeds, 5)
#         recFromArtistSeeds = (sp.recommendations(seed_artists = artistSeeds,
#                                                 limit = 40 - len(recFromArtistFinal),
#                                                 target_tempo = meanTempo,
#                                                 target_danceability = meanDance,
#                                                 target_loudness = meanLoudness,
#                                                 target_valence = meanValence,
#                                                 target_energy = meanEnergy,
#                                                 target_acousticness = meanAcousticness,
#                                                 target_instrumentalness = meanInstrumental,
#                                                 max_danceability = meanDance + stdDance,
#                                                 min_energy = meanEnergy - stdEnergy)["tracks"])
#         #recFromArtistSeeds = list(set(recFromArtistSeeds))
#
# #print(recFromArtistFinal)
# print(len(recFromArtistFinal))
#
#
# for track in recFromArtistFinal:
#     sp.user_playlist_add_tracks("dylrobinson22", "6exoLbn2dTavcDnmr3bCvv", [track["id"]])
#
#
# # Generate recommendations from song seeds
#
# songSeeds = getIDs(getRandomSeeds(topSongSeeds, 5))
#
# artistSeed = getIDs(getRandomSeeds(topArtistSeeds, 0))
# print(songSeeds)
#
# recFromSongSeeds = (sp.recommendations(seed_artists = artistSeed,
#                                         seed_tracks = songSeeds,
#                                         target_tempo = meanTempo,
#                                         target_danceability = meanDance,
#                                         target_loudness = meanLoudness,
#                                         target_valence = meanValence,
#                                         target_energy = meanEnergy,
#                                         target_acousticness = meanAcousticness,
#                                         target_instrumentalness = meanInstrumental,
#                                         max_danceability = meanDance + stdDance,
#                                         min_energy = meanEnergy - stdEnergy)["tracks"])
#
#
#
# for track in recFromSongSeeds:
#     print(sp.current_user_saved_tracks_contains([track["id"]]))
#
# recFromSongFinal = []
# while True:
#     for track in recFromSongSeeds:
#         if not sp.current_user_saved_tracks_contains([track["id"]])[0]:
#             recFromSongFinal.append(track)
#     if len(recFromSongFinal) >= 40:
#         break
#     else:
#         songSeeds = getIDs(getRandomSeeds(topSongSeeds, 5))
#         recFromSongSeeds = (sp.recommendations(seed_tracks = songSeeds,
#                                                 seed_artists = artistSeed,
#                                                 limit = 40 - len(recFromSongFinal),
#                                                 target_tempo = meanTempo,
#                                                 target_danceability = meanDance,
#                                                 target_loudness = meanLoudness,
#                                                 target_valence = meanValence,
#                                                 target_energy = meanEnergy,
#                                                 target_acousticness = meanAcousticness,
#                                                 target_instrumentalness = meanInstrumental,
#                                                 max_danceability = meanDance + stdDance,
#                                                 min_energy = meanEnergy - stdEnergy)["tracks"])
#

#
# for track in recFromSongFinal:
#     sp.user_playlist_add_tracks("dylrobinson22", "76F0qSYJVNl4UGXdW0gd3L", [track["id"]])
