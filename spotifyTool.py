import pandas as pd
import numpy as np

from sklearn import tree
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split

from matplotlib import pyplot as plt
import seaborn as sns

import graphviz
import pydotplus
import io

from scipy import misc

from sklearn.metrics import accuracy_score

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util

cid ="69457297a5cc42a4a9b19ba477558210"
secret = "b8df8b59a120497eb7667bdb881058b7"
username = "dylrobinson22"

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


results = sp.current_user_saved_tracks()
for item in results['items']:
    track = item['track']
    print(track['name'] + ' - ' + track['artists'][0]['name'])

good_playlist = sp.user_playlist("dylrobinson22", "3C6CreIyZLBqjlvls0KKKR")

# Return a list of ids for all the songs in the given playlist
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

#good_ids = getIDs(good_playlist)

features = []

# Takes in feature list f and list of song ids. Get the audio features of
# the songs for each id and add them to the feature list. Take in target int
# to set the target for the songs.
def addFeatures(f, playlist, target, weight):
    tracks = playlist["tracks"]
    songs = tracks["items"]
    ids = getIDs(tracks, songs)
    k = 0
    for i in range(0, len(ids), 50):
        audio_features = sp.audio_features(ids[i:i+50])
        for track in audio_features:
            track['id'] = ids[k]
            track['song_title'] = songs[k]['track']['name']
            track['artist'] = songs[k]['track']['artists'][0]['name']
            popularity = songs[k]['track']['popularity']
            #artistPopularity = sp.artist(songs[k]['track']['artists'][0]['id'])['popularity']
            k = k + 1
            for j in range(0, weight):
                f.append(track)
                f[-1]['trackPopularity'] =  popularity
                #f[-1]['artistPopularity'] = artistPopularity
                f[-1]['target'] = target

# Takes in feature list f, a list of playlists and target number. Adds the
# audio features of all the songs in all playlist to the feature list with
# the given target.
def addPlaylistFeatures(f, playlists, target):
    for playlist in playlists:
        addFeatures(f, playlist, target, playlist['weight'])

#addFeatures(features, good_playlist, 1, 1)
playlist2 = sp.user_playlist("dylrobinson22", "0qKTx8hazCzOCYYMjyZHzk")
playlists = []
playlists.append(good_playlist)
playlists[-1]['weight'] = 1
playlists.append(playlist2)
playlists[-1]['weight'] = 1

addPlaylistFeatures(features, playlists, 1)

#print(len(good_ids))
print(len(features))

bad_playlist = sp.user_playlist("dylrobinson22", "44lhNWvKtZDX1a83LW14dW")

#bad_ids = getIDs(bad_playlist)
addFeatures(features, bad_playlist, 0, 1)

print(len(features))

trainingData = pd.DataFrame(features)
trainingData.head()

train, test = train_test_split(trainingData, test_size = 0.15)
print("Training size: {}, Test size: {}".format(len(train),len(test)))

# Custom Color Palette for graphs
red_blue = ['#19B5FE', '#EF4836']
palette = sns.color_palette(red_blue)
sns.set_palette(palette)
sns.set_style('white')

# breaking data into pos/neg categories
pos_tempo = trainingData[trainingData['target'] == 1]['tempo']
neg_tempo = trainingData[trainingData['target'] == 0]['tempo']
pos_dance = trainingData[trainingData['target'] == 1]['danceability']
neg_dance = trainingData[trainingData['target'] == 0]['danceability']
pos_duration = trainingData[trainingData['target'] == 1]['duration_ms']
neg_duration = trainingData[trainingData['target'] == 0]['duration_ms']
pos_loudness = trainingData[trainingData['target'] == 1]['loudness']
neg_loudness = trainingData[trainingData['target'] == 0]['loudness']
pos_speechiness = trainingData[trainingData['target'] == 1]['speechiness']
neg_speechiness = trainingData[trainingData['target'] == 0]['speechiness']
pos_valence = trainingData[trainingData['target'] == 1]['valence']
neg_valence = trainingData[trainingData['target'] == 0]['valence']
pos_energy = trainingData[trainingData['target'] == 1]['energy']
neg_energy = trainingData[trainingData['target'] == 0]['energy']
pos_acousticness = trainingData[trainingData['target'] == 1]['acousticness']
neg_acousticness = trainingData[trainingData['target'] == 0]['acousticness']
pos_key = trainingData[trainingData['target'] == 1]['key']
neg_key = trainingData[trainingData['target'] == 0]['key']
pos_instrumentalness = trainingData[trainingData['target'] == 1]['instrumentalness']
neg_instrumentalness = trainingData[trainingData['target'] == 0]['instrumentalness']
# popularity not part of audio features, data in track itself
pos_popularity = trainingData[trainingData['target'] == 1]['trackPopularity']
neg_popularity = trainingData[trainingData['target'] == 0]['trackPopularity']

# Tempo Graph
fig = plt.figure(figsize=(12,8))
plt.title("Song Tempo Like / Dislike Distribution")
pos_tempo.hist(alpha=0.7, bins=30, label='positive')
neg_tempo.hist(alpha=0.7, bins=30, label='negative')
plt.legend(loc='upper right')
plt.show()

fig2 = plt.figure(figsize=(15,15))

#Danceability
ax3 = fig2.add_subplot(331)
ax3.set_xlabel('Danceability')
ax3.set_ylabel('Count')
ax3.set_title('Song Danceability Like Distribution')
pos_dance.hist(alpha= 0.5, bins=30)
ax4 = fig2.add_subplot(331)
neg_dance.hist(alpha= 0.5, bins=30)

#Duration_ms
ax5 = fig2.add_subplot(332)
ax5.set_xlabel('Duration')
ax5.set_ylabel('Count')
ax5.set_title('Song Duration Like Distribution')
pos_duration.hist(alpha= 0.5, bins=30)
ax6 = fig2.add_subplot(332)
neg_duration.hist(alpha= 0.5, bins=30)

#Loudness
ax7 = fig2.add_subplot(333)
ax7.set_xlabel('Loudness')
ax7.set_ylabel('Count')
ax7.set_title('Song Loudness Like Distribution')
pos_loudness.hist(alpha= 0.5, bins=30)
ax8 = fig2.add_subplot(333)
neg_loudness.hist(alpha= 0.5, bins=30)

#Speechiness
ax9 = fig2.add_subplot(334)
ax9.set_xlabel('Speechiness')
ax9.set_ylabel('Count')
ax9.set_title('Song Speechiness Like Distribution')
pos_speechiness.hist(alpha= 0.5, bins=30)
ax10 = fig2.add_subplot(334)
neg_speechiness.hist(alpha= 0.5, bins=30)

#Valence
ax11 = fig2.add_subplot(335)
ax11.set_xlabel('Valence')
ax11.set_ylabel('Count')
ax11.set_title('Song Valence Like Distribution')
pos_valence.hist(alpha= 0.5, bins=30)
ax12 = fig2.add_subplot(335)
neg_valence.hist(alpha= 0.5, bins=30)

#Energy
ax13 = fig2.add_subplot(336)
ax13.set_xlabel('Energy')
ax13.set_ylabel('Count')
ax13.set_title('Song Energy Like Distribution')
pos_energy.hist(alpha= 0.5, bins=30)
ax14 = fig2.add_subplot(336)
neg_energy.hist(alpha= 0.5, bins=30)

#Key
ax15 = fig2.add_subplot(337)
ax15.set_xlabel('Key')
ax15.set_ylabel('Count')
ax15.set_title('Song Key Like Distribution')
pos_key.hist(alpha= 0.5, bins=30)
ax16 = fig2.add_subplot(337)
neg_key.hist(alpha= 0.5, bins=30)

#Popularity
ax15 = fig2.add_subplot(338)
ax15.set_xlabel('Popularity')
ax15.set_ylabel('Count')
ax15.set_title('Popularity Distribution')
pos_popularity.hist(alpha= 0.5, bins=30)
ax16 = fig2.add_subplot(338)
neg_popularity.hist(alpha= 0.5, bins=30)

plt.show()



#Define the set of features that we want to look at
features = ["danceability", "loudness", "valence",
            "energy", "instrumentalness", "acousticness",
            "key", "speechiness", "mode", "time_signature"]

#Split the data into x and y test and train sets to feed them into a bunch of classifiers!
x_train = train[features]
y_train = train["target"]

x_test = test[features]
y_test = test["target"]

c = DecisionTreeClassifier(min_samples_split=100)
dt = c.fit(x_train, y_train)
y_pred = c.predict(x_test)
score = accuracy_score(y_test, y_pred) * 100
print("Accuracy using Decision Tree: ", round(score, 1), "%")

from sklearn.neighbors import KNeighborsClassifier
knn = KNeighborsClassifier(3)
knn.fit(x_train, y_train)
knn_pred = knn.predict(x_test)
score = accuracy_score(y_test, knn_pred) * 100
print("Accuracy using Knn Tree: ", round(score, 1), "%")

from sklearn.neural_network import MLPClassifier
mlp = MLPClassifier()
mlp.fit(x_train, y_train)
mlp_pred = mlp.predict(x_test)
score = accuracy_score(y_test, mlp_pred) * 100
print("Accuracy using mlp Tree: ", round(score, 1), "%")

from sklearn.ensemble import RandomForestClassifier
forest = RandomForestClassifier(max_depth=None, n_estimators=10, max_features=1)
forest.fit(x_train, y_train)
forest_pred = forest.predict(x_test)
from sklearn.metrics import accuracy_score
score = accuracy_score(y_test, forest_pred) * 100
print("Accuracy using random forest: ", round(score, 1), "%")

from sklearn.ensemble import AdaBoostClassifier
ada = AdaBoostClassifier(n_estimators=100)
ada.fit(x_train, y_train)
ada_pred = ada.predict(x_test)
from sklearn.metrics import accuracy_score
score = accuracy_score(y_test, ada_pred) * 100
print("Accuracy using ada: ", round(score, 1), "%")

from sklearn.naive_bayes import GaussianNB
gauss = GaussianNB()
gauss.fit(x_train, y_train)
gauss_pred = gauss.predict(x_test)
score = accuracy_score(y_test, gauss_pred)*100
print("Accuracy using gauss: ", round(score, 1), "%")

from sklearn.cluster import KMeans
k_means = KMeans(n_clusters=3, random_state=0)
k_means.fit(x_train, y_train)
predicted= k_means.predict(x_test)
score = accuracy_score(y_test, predicted)*100
print("Accuracy using Kmeans: ", round(score, 1), "%")

from sklearn.ensemble import GradientBoostingClassifier
gbc = GradientBoostingClassifier(n_estimators=100, learning_rate=.05, max_depth=5, random_state=0)
gbc.fit(x_train, y_train)
predicted = gbc.predict(x_test)
score = accuracy_score(y_test, predicted)*100
print("Accuracy using Gbc: ", round(score, 1), "%")


# Load in audio features from a selected playlist
playlistToFindSongsYouLikeIn = sp.user_playlist("1g6508li3gcwq7ok6bfzc7gl6",
                                                "7aQw0lddqWohUSNNpRQlIS")


newPlaylist_features = []
addFeatures(newPlaylist_features, playlistToFindSongsYouLikeIn, -1, 1)


print(len(newPlaylist_features))

playlistToLookAtFeatures = pd.DataFrame(newPlaylist_features)


# Predict what songs will be liked and add to a playlist
pred = gbc.predict(playlistToLookAtFeatures[features])

# clears playlist before adding predicted songs to it
sp.user_playlist_replace_tracks(username, "6GsQTpEaNs0JAj1khFABaM", [])

def addPredictedSongs(playlist, predictions, features):
    i = 0
    for prediction in predictions:
        if(prediction == 1):
            print ("Song: " + features["song_title"][i]
                    + ", By: " + features["artist"][i])
            sp.user_playlist_add_tracks(playlist['owner']['id'], playlist['id'], [features["id"][i]])
        i = i + 1

addPredictedSongs(sp.user_playlist("dylrobinson22", "6GsQTpEaNs0JAj1khFABaM"), pred, playlistToLookAtFeatures)
