from tkinter import *
from tkinter import messagebox

from collections import Counter

import pandas as pd
import numpy as np

from sklearn import tree
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split

from scipy import misc

from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score

import random

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util

BUTTON_COLOR = "#1db853"
BUTTON_TEXT_COLOR = "white"
BUTTON_CLICKED = "#15823b"
LIST_BG = "#121212"
LIST_FG = "#6e6e6e"
LIST_SELECT = BUTTON_CLICKED#"#1ed65e"
FRAME_BG = "#262626"
LABEL_TEXT = "white"
QUIT_BG = "#cc1b29"
QUIT_FG = "white"
QUIT_CLICKED = "#9e0000"
SETTINGS_BG = FRAME_BG#"#4f4f4f"

LISTBOX_HEIGHT = 25
LISTBOX_WIDTH = 30



cid ="69457297a5cc42a4a9b19ba477558210"
secret = ""
username = ""
scope = 'playlist-modify-private playlist-modify-public playlist-read-private user-library-read user-top-read'



class LoginWindow():

    def __init__(self, master):

        self.master = master
        master.title("Log in")

        self.sp = None
        self.token_info = None

        self.user = Entry(master)
        self.userLabel = Label(master, text="username: ")

        self.url = Entry(master)
        self.urlLabel = Label(master, text="url: ")

        self.quitButton = Button(master, text="Quit", command=master.destroy)
        self.geturl = Button(master, text="Get URL", command=self.geturlAuth)
        self.login = Button(master, text="Login", command=self.loginAuth)

        # LAYOUT

        self.userLabel.grid(row=0, column=0)
        self.user.grid(row=0, column=1)

        self.urlLabel.grid(row=1, column=0)
        self.url.grid(row=1, column=1)

        self.quitButton.grid(row=2, column=0)
        self.geturl.grid(row=2, column=1)
        self.login.grid(row=2, column=2)


    def getTokenInfo(self, token_info):
        if not token_info:

            try:
                response = self.url.get()
                #response = raw_input("Enter the URL you were redirected to: ")
            except NameError:
                response = self.url.get()
                #response = input("Enter the URL you were redirected to: ")

            print()
            print()

            code = self.sp_oauth.parse_response_code(response)
            token_info = self.sp_oauth.get_access_token(code)
        # Auth'ed API request
        if token_info:
            return token_info['access_token']
        else:
            return None



    def loginAuth(self):
        token = self.getTokenInfo(self.token_info)

        if token:
            self.sp = spotipy.Spotify(auth=token)
            print("Success?")
            self.master.quit()


        else:
            print("Can't get token for", username)

    def geturlAuth(self):

        username = self.user.get()

        client_credentials_manager = SpotifyClientCredentials(client_id=cid,
                                                            client_secret=secret)

        self.sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        #scope = 'playlist-modify-private playlist-modify-public playlist-read-private user-library-read'
        self.token_info = self.prompt_for_user_token(username, scope, client_id=cid, client_secret=secret, redirect_uri='http://localhost/')


    def prompt_for_user_token(self, username, scope=None, client_id = None,
            client_secret = None, redirect_uri = None, cache_path = None):
        ''' prompts the user to login if necessary and returns
            the user token suitable for use with the spotipy.Spotify
            constructor
            Parameters:
             - username - the Spotify username
             - scope - the desired scope of the request
             - client_id - the client id of your app
             - client_secret - the client secret of your app
             - redirect_uri - the redirect URI of your app
             - cache_path - path to location to save tokens
        '''

        if not client_id:
            client_id = os.getenv('SPOTIPY_CLIENT_ID')

        if not client_secret:
            client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')

        if not redirect_uri:
            redirect_uri = os.getenv('SPOTIPY_REDIRECT_URI')

        if not client_id:
            print('''
                You need to set your Spotify API credentials. You can do this by
                setting environment variables like so:
                export SPOTIPY_CLIENT_ID='your-spotify-client-id'
                export SPOTIPY_CLIENT_SECRET='your-spotify-client-secret'
                export SPOTIPY_REDIRECT_URI='your-app-redirect-url'
                Get your credentials at
                    https://developer.spotify.com/my-applications
            ''')
            raise spotipy.SpotifyException(550, -1, 'no credentials set')

        cache_path = cache_path or ".cache-" + username
        self.sp_oauth = oauth2.SpotifyOAuth(client_id, client_secret, redirect_uri,
            scope=scope, cache_path=cache_path)

        # try to get a valid token for this user, from the cache,
        # if not in the cache, the create a new (this will send
        # the user to a web page where they can authorize this app)

        token_info = self.sp_oauth.get_cached_token()

        if not token_info:
            print('''
                User authentication requires interaction with your
                web browser. Once you enter your credentials and
                give authorization, you will be redirected to
                a url.  Paste that url you were directed to to
                complete the authorization.
            ''')
            auth_url = self.sp_oauth.get_authorize_url()
            try:
                import webbrowser
                webbrowser.open(auth_url)
                print("Opened %s in your browser" % auth_url)
            except:
                print("Please navigate here: %s" % auth_url)

            print()
            print()

            return token_info

        return token_info






def getSP():
    """Using the current credentials, get authorization from Spotify"""

    client_credentials_manager = SpotifyClientCredentials(client_id=cid,
                                                        client_secret=secret)

    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    scope = 'playlist-modify-private playlist-modify-public playlist-read-private user-library-read user-top-read'
    token = util.prompt_for_user_token(username, scope, client_id=cid, client_secret=secret, redirect_uri='http://localhost/')
    if token:
        sp = spotipy.Spotify(auth=token)
        print("Success?")

    else:
        print("Can't get token for", username)
    return sp

def getItems(page):
    """Given a Spotify page object, return a list of the contained items"""
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

# TODO update code to use getItems and getIDs where it should

def getSongs(tracks):
    """Given the Spotify tracks page object, return a list of songs"""
    sp = getSP()
    songs = tracks["items"]
    while tracks['next']:
        tracks = sp.next(tracks)
        for item in tracks["items"]:
            songs.append(item)
    return songs

def getSongIDs(songs):
    """Given a list of songs, return the song IDs"""
    ids = []
    for i in range(len(songs)):
        ids.append(songs[i]['track']['id'])
    return ids

def getSongIDsFromPlaylist(playlist):
    """Given a playlist, return the song IDs"""
    songs = getSongs(playlist["tracks"])
    return getSongIDs(songs)


def getPlaylists(playlistPage):
    """Given the Spotify playlist page object, return a list of playlists"""
    sp = getSP()
    playlists = playlistPage["items"]
    while playlistPage["next"]:
        playlistPage = sp.next(playlistPage)
        for playlist in playlistPage["items"]:
            playlists.append(playlist)
    return playlists

################### Start SongPredictor Class ########################

class SongPredictor():
    """Uses a list of liked playlists and a list of disliked playlists
        to predict the songs on a target playlist that will be liked."""

    def __init__(self):

        self.features = []
        self.goodPlaylists = []
        self.badPlaylists = []
        self.targetPlaylist = None
        self.classifier = None
        self.oldGood = []
        self.oldBad = []
        self.oldFeatures = []

        self.featuresToCheck = ["danceability", "loudness", "valence",
                    "energy", "instrumentalness", "acousticness",
                    "key", "speechiness", "time_signature"]

    def addGoodPlaylist(self, playlist, weight):
        """Add the given playlist with the given weight to goodPlaylists"""
        pl = playlist
        pl["weight"] = weight
        self.goodPlaylists.append(pl)

    def addBadPlaylist(self, playlist, weight):
        """Add the given playlist with the given weight to badPlaylists"""
        pl = playlist
        pl["weight"] = weight
        self.badPlaylists.append(pl)

    def addFeaturesSongs(self, f, songs, target, weight):
        """Gets the audio features from the given song list and adds them
            to the given features list with the given target and given weight"""
        sp = getSP()
        ids = getSongIDs(songs)
        k = 0
        for i in range(0, len(ids), 50):
            audio_features = sp.audio_features(ids[i:i+50])
            for track in audio_features:
                if track != None:
                    track['id'] = ids[k]
                    track['song_title'] = songs[k]['track']['name']
                    track['artist'] = songs[k]['track']['artists'][0]['name']
                    popularity = songs[k]['track']['popularity']
                    k = k + 1
                    for j in range(0, weight):
                        f.append(track)
                        f[-1]['trackPopularity'] = popularity
                        f[-1]['target'] = target
                else:
                    break

    def addFeatures(self, f, playlist, target, weight):
        """Gets the audio features from the given playlist and adds them
            to the given features list with the given target and given weight"""
        #sp = getSP() # update Spotify authorization
        tracks = playlist["tracks"]
        songs = getSongs(tracks)
        # ids = getSongIDs(tracks, songs)
        self.addFeaturesSongs(f, songs, target, weight)

    def addPlaylistFeatures(self, f, playlists, target):
        """Adds features from the given playlists to the given features list
            with the given target"""
        for playlist in playlists:
            self.addFeatures(f, playlist, target, playlist["weight"])

    def setUpFeatures(self):
        """Sets up the features list with the good and bad playlists"""
        if (self.goodPlaylists == self.oldGood and
            self.badPlaylists == self.oldBad):
            self.features = self.oldFeatures
        else:
            self.addPlaylistFeatures(self.features, self.goodPlaylists, 1)
            self.addPlaylistFeatures(self.features, self.badPlaylists, 0)

    def setUpClassifier(self):
        """Set up and fit the classifier to be used to predict liked songs"""
        trainingData = pd.DataFrame(self.features)
        trainingData.head()

        train, test = train_test_split(trainingData, test_size = 0.15)

        x_train = train[self.featuresToCheck]
        y_train = train["target"]

        x_test = test[self.featuresToCheck]
        y_test = test["target"]

        self.classifier = GradientBoostingClassifier(n_estimators=100,
                                                    learning_rate=0.1,
                                                    max_depth=5,
                                                    random_state=0)
        self.classifier.fit(x_train, y_train)
        predicted = self.classifier.predict(x_test)
        score = accuracy_score(y_test, predicted)*100
        print("Predication accuracy: ", round(score, 1), "%")

    def predictSongsHelp(self, songs):
        """Predict liked songs from the given list of songs"""

        features = []
        self.addFeaturesSongs(features, songs, -1, 1)

        songFeaturesToLookAt = pd.DataFrame(features)

        pred = self.classifier.predict(songFeaturesToLookAt[self.featuresToCheck])
        return pred

    def addPredictedSongs(self, pred, songs, playlist):
        sp = getSP()
        i = 0
        for prediction in pred:
            if(prediction == 1):
                sp.user_playlist_add_tracks(username, playlist["id"], [songs[i]["track"]["id"]])
            i = i + 1

    def predictSongs(self, songs, targetPlaylist, replace):

        sp = getSP()

        if replace == 1:
            sp.user_playlist_replace_tracks(username, targetPlaylist["id"], [])

        self.setUpFeatures()
        self.setUpClassifier()
        pred = self.predictSongsHelp(songs)
        self.addPredictedSongs(pred, songs, targetPlaylist)
        self.reset()

    def reset(self):
        self.oldGood = self.goodPlaylists
        self.oldBad = self.badPlaylists
        self.oldFeatures = self.features
        self.goodPlaylists = []
        self.badPlaylists = []
        self.features = []





################### End SongPredictor Class ########################



################### Start SongPredictorWindow Class ########################

class SongPredictorWindow():

    def __init__(self, master):

        self.master = master
        master.title("Spotify Song Predictor")

        self.frame = Frame(master,
                            bg = FRAME_BG)

        self.songPredictor = SongPredictor()

        sp = getSP()

        playlistPage = sp.current_user_playlists(limit=50, offset=0)
        self.playlists = getPlaylists(playlistPage)
        self.playlistIDs = []

        self.goodList = Listbox(self.frame,
                                selectmode=MULTIPLE,
                                exportselection=False,
                                highlightthickness = 0,
                                bg = LIST_BG,
                                fg = LIST_FG,
                                selectbackground = LIST_SELECT,
                                relief = FLAT,
                                height = LISTBOX_HEIGHT,
                                width = LISTBOX_WIDTH)
        self.badList = Listbox(self.frame,
                                selectmode=MULTIPLE,
                                exportselection=False,
                                highlightthickness = 0,
                                bg = LIST_BG,
                                fg = LIST_FG,
                                selectbackground = LIST_SELECT,
                                relief = FLAT,
                                height = LISTBOX_HEIGHT,
                                width = LISTBOX_WIDTH)
        self.targetList = Listbox(self.frame,
                                exportselection=False,
                                highlightthickness = 0,
                                bg = LIST_BG,
                                fg = LIST_FG,
                                selectbackground = LIST_SELECT,
                                relief = FLAT,
                                height = LISTBOX_HEIGHT,
                                width = LISTBOX_WIDTH)

        for playlist in self.playlists:
            self.playlistIDs.append(playlist["id"])
            self.goodList.insert(END, playlist["name"])
            self.badList.insert(END, playlist["name"])
            self.targetList.insert(END, playlist["name"])

        self.userID = Entry(self.frame)
        self.playlistID = Entry(self.frame)

        self.userIDLabel = Label(self.frame, text="User ID:",
                                bg = FRAME_BG,
                                fg = LABEL_TEXT,
                                justify=RIGHT)
        self.playlistIDLabel = Label(self.frame, text="Playlist ID:",
                                bg = FRAME_BG,
                                fg = LABEL_TEXT,
                                justify=RIGHT)

        #TODO add commands for buttons
        self.predictPlaylist = Button(self.frame, text="Predict Playlist Songs",
                                    command=self.predictSongsPlaylist,
                                    bg = BUTTON_COLOR,
                                    fg = BUTTON_TEXT_COLOR,
                                    activebackground = BUTTON_CLICKED,
                                    activeforeground = BUTTON_TEXT_COLOR)

        usageText = ("Here you can predict songs that you might like. To use, "
            + "select playlists that you like, playlists you dislike, and a target "
            + "playlist to place the predicted songs in. To choose what songs to "
            + "predict from, enter a user ID and playlist ID then press the "
            + "'Predict Playlist Songs' button.")

        self.info = Message(self.frame, text=usageText,
                                bg = FRAME_BG,
                                fg = LABEL_TEXT)

        self.goodLabel = Label(self.frame, text="Liked Playlists",
                                bg = FRAME_BG,
                                fg = LABEL_TEXT)
        self.badLabel = Label(self.frame, text="Disliked Playlists",
                                bg = FRAME_BG,
                                fg = LABEL_TEXT)
        self.targetLabel = Label(self.frame, text="Target Playlist",
                                bg = FRAME_BG,
                                fg = LABEL_TEXT)

        self.checkEmpty = IntVar()
        self.emptyTargetButton = Checkbutton(self.frame,
                                text="Replace Target Playlist",
                                variable=self.checkEmpty,
                                bg = FRAME_BG,
                                fg = LABEL_TEXT,
                                activebackground=FRAME_BG,
                                activeforeground=LABEL_TEXT,
                                selectcolor=BUTTON_CLICKED)

        self.quitButton = Button(self.frame, text="Quit",
                                command=master.destroy,
                                bg = QUIT_BG,
                                fg = QUIT_FG,
                                activebackground = QUIT_CLICKED,
                                activeforeground = QUIT_FG,
                                relief = FLAT)

        # LAYOUT
        self.frame.pack(fill = BOTH,
                        expand = 1)

        self.goodLabel.grid(row=0, column=0)
        self.badLabel.grid(row=0, column=1)
        self.targetLabel.grid(row=0, column=2)

        self.goodList.grid(row=1, column=0, padx=10, pady=10)
        self.badList.grid(row=1, column=1, padx=10, pady=10)
        self.targetList.grid(row=1, column=2, padx=10, pady=10)

        self.userIDLabel.grid(row=2, column=0, sticky=E)
        self.userID.grid(row=2, column=1, sticky=W+E)
        self.emptyTargetButton.grid(row=2, column=2)

        self.playlistIDLabel.grid(row=3, column=0, sticky=E)
        self.playlistID.grid(row=3, column=1, sticky=W+E)

        self.info.grid(row=4, column=1, rowspan=2, pady=10)
        self.predictPlaylist.grid(row=4, column=2)

        self.quitButton.grid(row=6, column=2, pady=10)


    def predictSongs(self, songs):
        """Using the given songs, predict liked songs"""
        goodIndexes = self.goodList.curselection()
        badIndexes = self.badList.curselection()
        targetIndex = self.targetList.curselection()[0]

        sp = getSP()

        goodPlaylists = []
        badPlaylists = []
        targetPlaylist = sp.user_playlist(self.playlists[targetIndex]["owner"]["id"],
                                        self.playlists[targetIndex]["id"])

        for index in goodIndexes:
            goodPlaylists.append(
                sp.user_playlist(self.playlists[index]["owner"]["id"],
                                self.playlists[index]["id"]))
        for index in badIndexes:
            badPlaylists.append(
                sp.user_playlist(self.playlists[index]["owner"]["id"],
                                self.playlists[index]["id"]))

        for playlist in goodPlaylists:
            self.songPredictor.addGoodPlaylist(playlist, 1)
        for playlist in badPlaylists:
            self.songPredictor.addBadPlaylist(playlist, 1)

        self.songPredictor.predictSongs(songs, targetPlaylist, self.checkEmpty.get())

    def predictSongsPlaylist(self):
        """Predict liked songs from the chosen playlist"""

        if (len(self.goodList.curselection()) == 0
            or len(self.badList.curselection()) == 0
            or len(self.targetList.curselection()) == 0):
            messagebox.showerror("Error", "Must select playlists!")
            return

        uID = self.userID.get()
        pID = self.playlistID.get()

        sp = getSP()

        try:
            playlist = sp.user_playlist(uID, pID)
        except spotipy.client.SpotifyException:
            messagebox.showerror("Error", "Invalid UserID or PlaylistID")
            return
        songs = getSongs(playlist["tracks"])
        self.predictSongs(songs)

        messagebox.showinfo("Finished", "Predicted liked songs in " + playlist["name"])


################### End SongPredictorWindow Class ########################



#################### Start ShuffleWindow Class ##########################

class ShuffleWindow():

    def __init__(self, master):

        self.master = master
        master.title("Spotify Playlist Shuffler")

        self.frame = Frame(master,
                            bg = FRAME_BG)

        sp = getSP()

        playlistPage = sp.current_user_playlists(50, 0)
        self.playlists = getPlaylists(playlistPage)

        self.scrollbar = Scrollbar(self.frame,
                                    orient=VERTICAL)

        self.listLabel = Label(self.frame, text="Your Playlists",
                                bg = FRAME_BG,
                                fg = "white")
        self.plList = Listbox(self.frame,
                            yscrollcommand=self.scrollbar.set,
                            highlightthickness = 0,
                            bg = LIST_BG,
                            fg = LIST_FG,
                            selectbackground = LIST_SELECT,
                            relief = FLAT,
                            height = LISTBOX_HEIGHT,
                            width = LISTBOX_WIDTH)
        for playlist in self.playlists:
            self.plList.insert(END, playlist["name"])

        self.scrollbar.config(command=self.plList.yview)

        self.button = Button(self.frame,
                            text="Shuffle Playlist",
                            command=self.shuffle,
                            bg = BUTTON_COLOR,
                            fg = BUTTON_TEXT_COLOR,
                            activebackground = BUTTON_CLICKED,
                            activeforeground = BUTTON_TEXT_COLOR)
        self.label = Label(self.frame,
                            text="Select a playlist and hit 'Shuffle Playlist'",
                            bg = FRAME_BG,
                            fg = "white")

        self.quitButton = Button(self.frame, text="Quit",
                                command=master.destroy,
                                bg = QUIT_BG,
                                fg = QUIT_FG,
                                activebackground = QUIT_CLICKED,
                                activeforeground = QUIT_FG,
                                relief = FLAT)

        # LAYOUT
        self.frame.pack(fill = BOTH,
                        expand = 1)

        self.listLabel.grid(row=0, column=0)
        self.plList.grid(row=1, column=0, rowspan=4)

        self.scrollbar.grid(row=1, column=1, rowspan=4, sticky=N+S)

        self.label.grid(row=2, column=3)
        self.button.grid(row=3, column=3)

        self.quitButton.grid(row=4, column=3)


    def shufflePlaylist(self, playlistToShuffle):
        """Shuffle the given Spotify playlist"""

        sp = getSP()

        songs = getSongs(playlistToShuffle["tracks"])
        ids = getSongIDs(songs)
        random.shuffle(ids)

        if len(ids) <= 100:
            sp.user_playlist_replace_tracks(username, playlistToShuffle["id"], ids)
        else:
            sp.user_playlist_replace_tracks(username, playlistToShuffle["id"], ids[0:100])
            for i in range(100, len(ids), 100):
                sp = getSP()
                sp.user_playlist_add_tracks(username, playlistToShuffle["id"], ids[i:i+100])

    def shuffle(self):
        """Shuffle the currently selected playlist"""

        if len(self.plList.curselection()) == 0:
            messagebox.showerror("Error", "You need to select a playlist to shuffle!")
            return

        playlist = self.playlists[self.plList.curselection()[0]]

        if playlist["owner"]["id"] != username:
            messagebox.showerror("Error", "Can't shuffle a playlist that's not yours!")
            return

        sp = getSP()
        playlist = sp.user_playlist(username, playlist["id"])
        self.shufflePlaylist(playlist)
        messagebox.showinfo("Finished", "Shuffled " + playlist["name"])

#################### End ShuffleWindow Class ##########################


#################### Start SongSuggester Class ##########################

class SongSuggester():
    """Gets the current user's top artists and tracks, then uses them to
        suggest new songs"""

    def __init__(self):

        self.taShort, self.taMed, self.taLong = self.getTopArtists()
        self.taShortIDs = getIDs(self.taShort)
        self.taMedIDs = getIDs(self.taMed)
        self.taLongIDs = getIDs(self.taLong)

        self.taSeeds = self.taShortIDs + self.getCommonIDs(self.taShortIDs + self.taMedIDs + self.taLongIDs, 3)

        self.tsShort, self.tsMed, self.tsLong = self.getTopSongs()
        self.tsShortIDs = getIDs(self.tsShort)
        self.tsMedIDs = getIDs(self.tsMed)
        self.tsLongIDs = getIDs(self.tsLong)

        self.tsSeeds = self.tsShortIDs + self.getCommonIDs(self.tsShortIDs + self.tsMedIDs + self.tsLongIDs, 2)

        self.songFeatures = self.getSongFeatures(self.tsShortIDs, 2)
        self.songFeatures.extend(self.getSongFeatures(self.tsMedIDs, 3))
        self.songFeatures.extend(self.getSongFeatures(self.tsLongIDs, 1))

        songData = pd.DataFrame(self.songFeatures)
        self.songData = songData

        self.targets = {}


    def getTopArtists(self):
        """Get the current users top artists"""

        sp = getSP()

        artistsPageShort = sp.current_user_top_artists(limit=50, offset=0, time_range="short_term")
        artistsPageMed = sp.current_user_top_artists(limit=50, offset=0, time_range="medium_term")
        artistsPageLong = sp.current_user_top_artists(limit=50, offset=0, time_range="long_term")


        topArtistsShort = getItems(artistsPageShort)
        topArtistsMed = getItems(artistsPageMed)
        topArtistsLong = getItems(artistsPageLong)

        return topArtistsShort, topArtistsMed, topArtistsLong

    def getTopGenres(self):
        """Get the top genres using the top arists"""

        genres = []
        for artist in (self.taShort + self.taMed + self.taLong):
            genres.extend(artist["genres"])

        topGenreCount = Counter(genres).most_common()

        topGenres = []

        for genre in topGenreCount:
            topGenres.append(genre)

        return topGenres

    def getTopSongs(self):
        """Get the current users top songs"""

        sp = getSP()

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

        return topSongsShort, topSongsMed, topSongsLong

    def getCommonIDs(self, ids, num):
        """Return the ids that appear at least the given number of times"""
        idCount = Counter(ids)

        commonTopIDs = []

        for id in idCount:
            if idCount[id] >= num:
                commonTopIDs.append(id)

        return commonTopIDs

    def getSongFeatures(self, ids, weight):
        """Given a list of song ids, return a list of their audio features"""
        sp = getSP()
        features = []
        for i in range(0, len(ids), 50):
            audio_features = sp.audio_features(ids[i:i+50])
            for j in range(0, weight):
                features.extend(audio_features)
        return features

    def autoGenTarget(self, feature):
        """Generate a target value for the given feature based on the how the
            values relate to the mean"""

        mean = self.songData[feature].mean()
        std = self.songData[feature].std()

        total = self.songData[feature].count()
        less = self.songData[self.songData[feature] < mean][feature].count()
        more = self.songData[self.songData[feature] > mean][feature].count()

        if abs(less/total - more/total) < .1:
            return mean
        if less < more:
            return mean + std
        else:
            return mean - std

    def randGenTarget(self, feature):
        """Generate a target value for the given feature randomly
            using the mean and standard deviation"""

        mean = self.songData[feature].mean()
        std = self.songData[feature].std()

        num = random.randint(-1, 1)

        return mean + num*std

    def genTarget(self, feature, num):
        """Generate a target value for the given feature by adding the
            standard deviation to the mean the given number of times"""

        mean = self.songData[feature].mean()
        std = self.songData[feature].std()

        print(num)

        return mean + (num*std)

    def setTarget(self, feature, choice, num):

        if choice == 0:
            self.targets[feature] = self.autoGenTarget(feature)
        elif choice == 1:
            self.targets[feature] = self.randGenTarget(feature)
        else:
            self.targets[feature] = self.genTarget(feature, num)


    def getRandomSeeds(self, seeds, num):
        """Given a list of seeds, return a given number of them randomly"""
        seedsResult = []

        for i in range(0, num):
            while True:
                seed = seeds[random.randint(0, len(seeds) - 1)]
                if not(seed in seedsResult):
                    seedsResult.append(seed)
                    break
        return seedsResult

    def getRecommendations(self, seedArtists, seedSongs, seedGenres, limit):

        sp = getSP()
        rec = sp.recommendations(seed_artists=seedArtists,
                seed_tracks=seedSongs,
                seed_genres=seedGenres,
                limit=limit,
                country="US",
                target_tempo=self.targets["tempo"],
                target_danceability=self.targets["danceability"],
                target_loudness=self.targets["loudness"],
                target_speechiness=self.targets["speechiness"],
                target_valence=self.targets["valence"],
                target_energy=self.targets["energy"],
                target_acousticness=self.targets["acousticness"],
                target_instrumentalness=self.targets["instrumentalness"])

        return getIDs(rec["tracks"])

    def suggestSongs(self, seedGenres, playlistID, replace):

        sp = getSP()

        seedSongs = self.getRandomSeeds(self.tsSeeds, 5 - len(seedGenres))
        seedArtists = self.getRandomSeeds(self.taSeeds, 5 - len(seedGenres) - len(seedSongs))

        recTracks = self.getRecommendations(seedArtists, seedSongs, seedGenres, 30)

        recTracksFinal = []

        while True:
            for trackID in recTracks:
                if not sp.current_user_saved_tracks_contains([trackID])[0]:
                    recTracksFinal.append(trackID)
            recTracksFinal = list(set(recTracksFinal))
            if len(recTracksFinal) >= 30:
                break
            seedSongs = self.getRandomSeeds(self.tsSeeds, 5 - len(seedGenres))
            seedArtists = self.getRandomSeeds(self.taSeeds, 5 - len(seedGenres) - len(seedSongs))
            recTracks = self.getRecommendations(seedArtists, seedSongs, seedGenres, 30 - len(recTracksFinal))

        if replace:
            sp.user_playlist_replace_tracks(username, playlistID, [])

        sp.user_playlist_add_tracks(username, playlistID, recTracksFinal)


#################### End SongSuggester Class ##########################



class SongSuggesterWindow():


    def __init__(self, master):


        self.master = master
        master.title("Spotify Song Suggester")

        self.frame = Frame(master,
                            bg = FRAME_BG)

        sp = getSP()

        self.suggester = SongSuggester()

        playlistPage = sp.current_user_playlists(50, 0)
        self.playlists = getPlaylists(playlistPage)

        self.scrollbar = Scrollbar(self.frame,
                                    orient=VERTICAL)

        self.listLabel = Label(self.frame, text="Your Playlists",
                                bg = FRAME_BG,
                                fg = "white")
        self.plList = Listbox(self.frame,
                            yscrollcommand=self.scrollbar.set,
                            highlightthickness = 0,
                            bg = LIST_BG,
                            fg = LIST_FG,
                            selectbackground = LIST_SELECT,
                            relief = FLAT,
                            height = LISTBOX_HEIGHT,
                            width = LISTBOX_WIDTH)
        for playlist in self.playlists:
            self.plList.insert(END, playlist["name"])

        self.scrollbar.config(command=self.plList.yview)

        self.genreLabel = Label(self.frame, text="Genre Seeds",
                                bg=FRAME_BG,
                                fg=LABEL_TEXT)

        self.topGenreLabel = Label(self.frame, text="Your Top Genres",
                                bg=FRAME_BG,
                                fg=LABEL_TEXT)

        self.checkEmpty = IntVar()
        self.emptyTargetButton = Checkbutton(self.frame,
                                text="Replace Target Playlist",
                                variable=self.checkEmpty,
                                bg = FRAME_BG,
                                fg = LABEL_TEXT,
                                activebackground=FRAME_BG,
                                activeforeground=LABEL_TEXT,
                                selectcolor=BUTTON_CLICKED)

        self.genres = sp.recommendation_genre_seeds()["genres"]
        topGenres = self.suggester.getTopGenres()


        self.scrollbarGS = Scrollbar(self.frame,
                                    orient=VERTICAL)
        self.genreSelect = Listbox(self.frame,
                                selectmode = MULTIPLE,
                                yscrollcommand=self.scrollbarGS.set,
                                highlightthickness = 0,
                                bg = LIST_BG,
                                fg = LIST_FG,
                                selectbackground = LIST_SELECT,
                                relief = FLAT,
                                height = round(LISTBOX_HEIGHT/2),
                                width = LISTBOX_WIDTH)
        self.scrollbarGS.config(command=self.genreSelect.yview)

        self.scrollbarTGL = Scrollbar(self.frame,
                                    orient=VERTICAL)
        self.topGenreList = Listbox(self.frame,
                                yscrollcommand=self.scrollbarTGL.set,
                                highlightthickness = 0,
                                bg = LIST_BG,
                                fg = LIST_FG,
                                selectbackground = LIST_SELECT,
                                relief = FLAT,
                                height = round(LISTBOX_HEIGHT/2),
                                width = LISTBOX_WIDTH)
        self.scrollbarTGL.config(command=self.topGenreList.yview)

        for genre in self.genres:
            self.genreSelect.insert(END, genre)
        for genre in topGenres:
            self.topGenreList.insert(END, genre)

        self.button = Button(self.frame,
                            text="Generate Recommendations",
                            command=self.suggestSongs,
                            bg=BUTTON_COLOR,
                            fg=BUTTON_TEXT_COLOR,
                            activebackground=BUTTON_CLICKED,
                            activeforeground=BUTTON_TEXT_COLOR)


        self.settingsLabel = Label(self.frame, text="Settings",
                                    bg=FRAME_BG, fg=LABEL_TEXT)

        settings = Frame(self.frame, bg=SETTINGS_BG)

        frameTempo = Frame(settings, bg=SETTINGS_BG)
        self.tempoSettings = FeatureSettings(frameTempo, "Tempo")

        frameDance = Frame(settings, bg=SETTINGS_BG)
        self.danceSettings = FeatureSettings(frameDance, "Danceability")

        frameLoudness = Frame(settings, bg=SETTINGS_BG)
        self.loudnessSettings = FeatureSettings(frameLoudness, "Loudness")

        frameSpeech = Frame(settings, bg=SETTINGS_BG)
        self.speechSettings = FeatureSettings(frameSpeech, "Speechiness")

        frameValence = Frame(settings, bg=SETTINGS_BG)
        self.valenceSettings = FeatureSettings(frameValence, "Valence")

        frameEnergy = Frame(settings, bg=SETTINGS_BG)
        self.energySettings = FeatureSettings(frameEnergy, "Energy")

        frameAcoustic = Frame(settings, bg=SETTINGS_BG)
        self.acousticnessSettings = FeatureSettings(frameAcoustic, "Acousticness")

        frameInstrumental = Frame(settings, bg=SETTINGS_BG)
        self.instrumentalnessSettings = FeatureSettings(frameInstrumental, "Instrumentalness")

        self.values = [self.tempoSettings, self.danceSettings,
                        self.loudnessSettings, self.speechSettings,
                        self.valenceSettings, self.energySettings,
                        self.acousticnessSettings, self.instrumentalnessSettings]

        # Settings Layout

        frameTempo.grid(row=0,column=0)
        frameDance.grid(row=0,column=1)
        frameLoudness.grid(row=1,column=0)
        frameSpeech.grid(row=1,column=1)
        frameValence.grid(row=2,column=0)
        frameEnergy.grid(row=2,column=1)
        frameAcoustic.grid(row=3,column=0)
        frameInstrumental.grid(row=3,column=1)

        # LAYOUT

        self.frame.pack(fill=BOTH, expand=1)

        self.plList.grid(row=0, column=0, rowspan=8, sticky=N+S+W)
        self.scrollbar.grid(row=0, column=1, rowspan=8, sticky=N+S, padx=(0, 10))

        self.button.grid(row=0, rowspan=2, column=2, columnspan=8)
        self.emptyTargetButton.grid(row=2, rowspan=2, column=2,columnspan=8)

        self.settingsLabel.grid(row=4, column=2, columnspan=8)

        settings.grid(row=5, rowspan=5, column=2, columnspan=4)

        self.genreLabel.grid(row=5, column=6, columnspan=2)
        self.topGenreLabel.grid(row=5, column=9, columnspan=2)

        self.genreSelect.grid(row=6, rowspan=3, column=6, columnspan=2, padx=(10,0))
        self.scrollbarGS.grid(row=6, rowspan=3, column=8, sticky=N+S, padx=(0, 10))
        self.topGenreList.grid(row=6, rowspan=3, column=9, columnspan=2)
        self.scrollbarTGL.grid(row=6, rowspan=3, column=11, stick=N+S, padx=(0, 10))


    def updateSettings(self):

        for feature in self.values:
            self.suggester.setTarget(feature.feature.lower(),
                                        feature.getButton(),
                                        feature.getSpinVal())

    def suggestSongs(self):

        self.updateSettings()

        if len(self.plList.curselection()) == 0:
            messagebox.showerror("Error", "You need to select a playlist to add recommendations to!")
            return

        playlist = self.playlists[self.plList.curselection()[0]]

        if playlist["owner"]["id"] != username:
            messagebox.showerror("Error", "Can't add songs to a playlist that's not yours!")
            return

        seedGenreIDX = self.genreSelect.curselection()

        if len(seedGenres) > 5:
            messagebox.showerror("Error", "Max 5 Genre Seeds!")
            return

        seedGenres = []

        for index in seedGenreIDX:
            seedGenres.append(self.genres[index])

        if self.checkEmpty.get() == 1:
            replace = True
        else:
            replace = False

        self.suggester.suggestSongs(seedGenres, playlist["id"], replace)

        if self.checkEmpty.get() == 1:
            replace = True

        messagebox.showinfo("Finished", "Finished recommending songs!")




class FeatureSettings():

    def __init__(self, master, feature):

        self.master = master

        self.feature = feature

        self.val = IntVar()
        auto = Radiobutton(master,
                                text="Auto",
                                variable=self.val,
                                value=0,
                                bg=SETTINGS_BG,
                                fg=LABEL_TEXT,
                                activebackground=SETTINGS_BG,
                                activeforeground=LABEL_TEXT,
                                selectcolor=BUTTON_CLICKED)
        rand = Radiobutton(master,
                                text="Rand",
                                variable=self.val,
                                value=1,
                                bg=SETTINGS_BG,
                                fg=LABEL_TEXT,
                                activebackground=SETTINGS_BG,
                                activeforeground=LABEL_TEXT,
                                selectcolor=BUTTON_CLICKED)
        select = Radiobutton(master,
                                text="Select",
                                variable=self.val,
                                value=2,
                                bg=SETTINGS_BG,
                                fg=LABEL_TEXT,
                                activebackground=SETTINGS_BG,
                                activeforeground=LABEL_TEXT,
                                selectcolor=BUTTON_CLICKED)
        self.spin = Spinbox(master,
                                from_=-1,
                                to=1,
                                width = 5,
                                state="readonly")
        label = Label(master, text=feature,
                            bg=SETTINGS_BG, fg=LABEL_TEXT)
        label.grid(row=0, column=0, columnspan=4)
        auto.grid(row=1, column=0)
        rand.grid(row=1, column=1)
        select.grid(row=1, column=2)
        self.spin.grid(row=1, column=3)

    def getButton(self):
        return self.val.get()

    def getSpinVal(self):
        return self.spin.get()



################### Start MainWindow Class ########################

class MainWindow():

    def __init__(self, master):

        self.master = master
        master.title("SpotifyTool")

        self.loginWindow = Toplevel(self.master)
        self.login = LoginWindow(self.loginWindow)

        self.frame = Frame(master,
                            bg = FRAME_BG)

        self.shuffle = Button(self.frame,
                            text="Shuffle a Playlist",
                            command=self.openShuffle,
                            bd = 2,
                            bg = BUTTON_COLOR,
                            fg = BUTTON_TEXT_COLOR,
                            activebackground = BUTTON_CLICKED,
                            activeforeground = BUTTON_TEXT_COLOR,
                            relief = FLAT)
        self.predict = Button(self.frame, text="Predict Liked Songs",
                            command=self.openPredict,
                            bd = 2,
                            bg = BUTTON_COLOR,
                            fg = BUTTON_TEXT_COLOR,
                            activebackground = BUTTON_CLICKED,
                            activeforeground = BUTTON_TEXT_COLOR,
                            relief = FLAT)
        self.suggest = Button(self.frame, text="Get Song Recommendations",
                            command=self.openSuggest,
                            bd = 2,
                            bg = BUTTON_COLOR,
                            fg = BUTTON_TEXT_COLOR,
                            activebackground = BUTTON_CLICKED,
                            activeforeground = BUTTON_TEXT_COLOR,
                            relief = FLAT)
        self.quitButton = Button(self.frame, text="Quit",
                            command=master.quit,
                            bg = QUIT_BG,
                            fg = QUIT_FG,
                            activebackground = QUIT_CLICKED,
                            activeforeground = QUIT_FG,
                            relief = FLAT)

        # LAYOUT
        self.frame.pack(fill = BOTH,
                        expand = 1)

        self.shuffle.grid(row=0, column=0, pady=10, padx=10)
        self.predict.grid(row=1, column=0, pady=5, padx=10)
        self.suggest.grid(row=2, column=0, pady=10, padx=10)
        self.quitButton.grid(row=3, column=0, pady=5, padx=10)

    def openShuffle(self):
        """Open a new Shuffle Window"""
        self.shuffleWindow = Toplevel(self.master)
        self.shuffler = ShuffleWindow(self.shuffleWindow)

    def openPredict(self):
        """Open a new Song Predictor Window"""
        self.predictWindow = Toplevel(self.master)
        self.predicter = SongPredictorWindow(self.predictWindow)

    def openSuggest(self):
        """Open a new Song Suggester Window"""
        self.suggestWindow = Toplevel(self.master)
        self.suggester = SongSuggesterWindow(self.suggestWindow)



################### End MainWindow Class ########################


root = Tk()
#predictor = SongPredictorWindow(root)
#shuffle = ShuffleWindow(root)
mainWindow = MainWindow(root)

root.mainloop()
