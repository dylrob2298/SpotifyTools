import pandas as pd
import numpy as np

from collections import Counter

import random

from matplotlib import pyplot as plt
import seaborn as sns

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util

SHORT_SONG_WEIGHT = 2
MED_SONG_WEIGHT = 3
LONG_SONG_WEIGHT = 1


cid ="69457297a5cc42a4a9b19ba477558210"
secret = ""
username = ""

def getSP():


    client_credentials_manager = SpotifyClientCredentials(client_id=cid,
                                                        client_secret=secret)

    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    scope = 'playlist-modify-private playlist-modify-public playlist-read-private user-library-read user-top-read'
    token = util.prompt_for_user_token(username, scope, client_id=cid, client_secret=secret, redirect_uri='http://localhost/')
    if token:
        sp = spotipy.Spotify(auth=token)
        #print("Success?")

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


def getSongFeatures(ids, weight):
    """Given a list of song ids, return a list of their audio features"""
    sp = getSP()
    features = []
    for i in range(0, len(ids), 50):
        audio_features = sp.audio_features(ids[i:i+50])
        for j in range(0, weight):
            features.extend(audio_features)
    return features


# Get top artists

sp = getSP()

artistsPageShort = sp.current_user_top_artists(limit=50, offset=0, time_range="short_term")
artistsPageMed = sp.current_user_top_artists(limit=50, offset=0, time_range="medium_term")
artistsPageLong = sp.current_user_top_artists(limit=50, offset=0, time_range="long_term")


topArtistsShort = getItems(artistsPageShort)
topArtistsMed = getItems(artistsPageMed)
topArtistsLong = getItems(artistsPageLong)

topArtistIDsShort = getIDs(topArtistsShort)
topArtistIDsMed = getIDs(topArtistsMed)
topArtistIDsLong = getIDs(topArtistsLong)


# Get common top artist IDs

topArtistIDCount = Counter(topArtistIDsShort + topArtistIDsMed + topArtistIDsLong)


commonTopArtistIDs = []

for id in topArtistIDCount:
    if topArtistIDCount[id] == 3:
        commonTopArtistIDs.append(id)

# The possible artist seeds to be used when generating recommendations
topArtistIDSeeds = commonTopArtistIDs + topArtistIDsShort

# Get top songs

songsPageShort = sp.current_user_top_tracks(limit=50, offset=0, time_range="short_term")
songsPageShort2 = sp.current_user_top_tracks(limit=50, offset=49, time_range="short_term")
songsPageMed = sp.current_user_top_tracks(limit=50, offset=0, time_range="medium_term")
songsPageMed2 = sp.current_user_top_tracks(limit=50, offset=49, time_range="medium_term")
songsPageLong = sp.current_user_top_tracks(limit=50, offset=0, time_range="long_term")
songsPageLong2 = sp.current_user_top_tracks(limit=50, offset=49, time_range="long_term")

topSongsShort = getItems(songsPageShort)
topSongsShort.extend(getItems(songsPageShort2)[1:])
topSongsMed = getItems(songsPageMed)
topSongsMed.extend(getItems(songsPageMed2)[1:])
topSongsLong = getItems(songsPageLong)
topSongsLong.extend(getItems(songsPageLong2)[1:])

topSongIDsShort = getIDs(topSongsShort)
topSongIDsMed = getIDs(topSongsMed)
topSongIDsLong = getIDs(topSongsLong)

# Get common top artist IDs

topSongIDCount = Counter(topSongIDsShort + topSongIDsMed + topSongIDsLong)

commonTopSongIDs = []

for id in topSongIDCount:
    if topSongIDCount[id] >= 2:
        commonTopSongIDs.append(id)

# The possible song seeds to be used when generating recommendations
topSongIDSeeds = commonTopSongIDs + topSongIDsShort

# Get the audio features of all songs

songFeatures = []
songFeatures = getSongFeatures(topSongIDsShort, SHORT_SONG_WEIGHT)
songFeatures.extend(getSongFeatures(topSongIDsMed, MED_SONG_WEIGHT))
songFeatures.extend(getSongFeatures(topSongIDsLong, LONG_SONG_WEIGHT))

# Put the song audio features into a DataFrame

songData = pd.DataFrame(songFeatures)

ROUND_TO = 3

# Get the means for important features

meanAcousticness = round(songData["acousticness"].mean(), ROUND_TO)
meanDance = round(songData["danceability"].mean(), ROUND_TO)
meanEnergy = round(songData["energy"].mean(), ROUND_TO)
meanInstrumental = round(songData["instrumentalness"].mean(), ROUND_TO)
meanLoudness = round(songData["loudness"].mean(), ROUND_TO)
meanSpeechiness = round(songData["speechiness"].mean(), ROUND_TO)
meanTempo = round(songData["tempo"].mean(), ROUND_TO)
meanValence = round(songData["valence"].mean(), ROUND_TO)

# Get the standard deviation for important features

stdAcousticness = round(songData["acousticness"].std(), ROUND_TO)
stdDance = round(songData["danceability"].std(), ROUND_TO)
stdEnergy = round(songData["energy"].std(), ROUND_TO)
stdInstrumental = round(songData["instrumentalness"].std(), ROUND_TO)
stdLoudness = round(songData["loudness"].std(), ROUND_TO)
stdSpeechiness = round(songData["speechiness"].std(), ROUND_TO)
stdTempo = round(songData["tempo"].std(), ROUND_TO)
stdValence = round(songData["valence"].std(), ROUND_TO)




def genTarget(mean, std):
    """Given a mean and standard deviation, randomly decide whether to add or
        subtract the std from the mean or not and return the result"""
    num = random.randint(-1, 1)
    return mean + num*std


def getRandomSeeds(seeds, num):
    """Given a list of seeds, return a given number of them randomly"""
    seedsResult = []

    for i in range(0, num):
        while True:
            seed = seeds[random.randint(0, len(seeds) - 1)]
            if not(seed in seedsResult):
                seedsResult.append(seed)
                break
    return seedsResult

# Generate seeds

seedGenres = []
seedArtists = getRandomSeeds(topArtistIDSeeds, 5 - len(seedGenres))
seedSongs = getRandomSeeds(topSongIDSeeds, 5 - len(seedGenres) - len(seedArtists))

# Generate target values

targetTempo = genTarget(meanTempo, stdTempo)
targetDance = genTarget(meanDance, stdDance)
targetLoudness = genTarget(meanLoudness, stdLoudness)
targetSpeechiness = genTarget(meanSpeechiness, stdSpeechiness)
targetValence = genTarget(meanValence, stdValence)
targetEnergy = genTarget(meanEnergy, stdEnergy)
targetAcousticness = genTarget(meanAcousticness, stdAcousticness)
targetInstrumentalness = genTarget(meanInstrumental, stdInstrumental)



def getRecommendations(seedArtists, seedSongs, seedGenres, limit):
    """Using the given seeds, get the given number of recommended songs
        and return a list of their IDs"""

    targetTempo = genTarget(meanTempo, stdTempo)
    targetDance = genTarget(meanDance, stdDance)
    targetLoudness = genTarget(meanLoudness, stdLoudness)
    targetSpeechiness = genTarget(meanSpeechiness, stdSpeechiness)
    targetValence = genTarget(meanValence, stdValence)
    targetEnergy = genTarget(meanEnergy, stdEnergy)
    targetAcousticness = genTarget(meanAcousticness, stdAcousticness)
    targetInstrumentalness = genTarget(meanInstrumental, stdInstrumental)

    rec = sp.recommendations(seed_artists=seedArtists,
                seed_tracks=seedSongs,
                seed_genres=seedGenres,
                limit=limit,
                country="US",
                target_tempo=targetTempo,
                target_danceability=targetDance,
                target_loudness=targetLoudness,
                target_speechiness=targetSpeechiness,
                target_valence=targetValence,
                target_energy=targetEnergy,
                target_acousticness=targetAcousticness,
                target_instrumentalness=targetInstrumentalness)

    return getIDs(rec["tracks"])


recTracks = getRecommendations(seedArtists, seedSongs, seedGenres, 30)

recTracksFinal = []

while True:
    for trackID in recTracks:
        if not sp.current_user_saved_tracks_contains([trackID])[0]:
            recTracksFinal.append(trackID)
    recTracksFinal = list(set(recTracksFinal))
    if len(recTracksFinal) >= 30:
        break
    else:
        seedArtists = getRandomSeeds(topArtistIDSeeds, 5 - len(seedGenres))
        seedSongs = getRandomSeeds(topSongIDSeeds, 5 - len(seedGenres) - len(seedArtists))
        recTracks = getRecommendations(seedArtists, seedSongs,
                                    seedGenres, 30 - len(recTracksFinal))


sp.user_playlist_add_tracks("dylrobinson22", "76F0qSYJVNl4UGXdW0gd3L", recTracksFinal)
