from __future__ import print_function

from tkinter import *

import random


import os
from spotipy import oauth2

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util

cid ="69457297a5cc42a4a9b19ba477558210"
secret = "b8df8b59a120497eb7667bdb881058b7"
username = "dylrobinson22"
scope = 'playlist-modify-private playlist-modify-public playlist-read-private user-library-read user-top-read'



class App:

    def __init__(self, master):

        self.master = master
        self.frame = Frame(self.master)
        self.frame.pack()

        self.sp = None
        self.token_info = None

        self.entry = Entry(self.frame)
        self.entry.pack()

        self.button = Button(
            self.frame, text="QUIT", fg="red", command=self.master.quit
            )
        self.button.pack(side=LEFT)

        self.hi_there = Button(self.frame, text="Hello",
                                command=self.setSP)
        self.hi_there.pack(side=LEFT)

        self.ok = Button(self.frame, text="OK", command=self.setSPhelp)
        self.ok.pack(side=LEFT)

        self.text = Text(self.frame)
        self.text.pack(side=RIGHT)

        self.pressed = False

    def setSPhelp(self):

        token = self.getTokenInfo(self.token_info)

        if token:
            self.sp = spotipy.Spotify(auth=token)
            print("Success?")
            self.master.quit()


        else:
            print("Can't get token for", username)


    def say_hi(self):
        print(self.entry.get())

    def setSP(self):

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



    def getTokenInfo(self, token_info):
            if not token_info:

                try:
                    response = self.entry.get()
                    #response = raw_input("Enter the URL you were redirected to: ")
                except NameError:
                    response = self.entry.get()
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



root = Tk()
app = App(root)

root.mainloop()












#####################################################
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

class ShuffleGUI():

    def __init__(self, master):

        self.master = master
        master.title("PlaylistShuffler")

        frame = Frame(master)
        frame.pack()

        sp = getSP()

        playlistPage = sp.user_playlists(username, 50, 0)
        self.playlists = playlistPage["items"]
        while playlistPage["next"]:
            playlistPage = sp.next(playlistPage)
            for playlist in playlistPage["items"]:
                self.playlists.append(playlist)

        self.playlistIDs = []

        scrollbar = Scrollbar(frame, orient=VERTICAL)
        scrollbar.pack(side=RIGHT, fill=Y)

        self.plList = Listbox(frame, yscrollcommand=scrollbar.set)
        for playlist in self.playlists:
            self.playlistIDs.append(playlist["id"])
            self.plList.insert(END, playlist["name"])

        self.plList.pack(side=LEFT)

        scrollbar.config(command=self.plList.yview)

        self.button = Button(frame, text="Shuffle", command=self.shufflePlaylist)
        self.button.pack(side=BOTTOM)

        self.labelText = StringVar()
        self.label = Label(frame, bg="white", textvariable=self.labelText)
        self.labelText.set("Select a playlist and hit 'Shuffle'")
        self.label.pack(side=BOTTOM)

    def shufflePlaylist(self):

        selected = 0
        try:
            selected = self.plList.curselection()[0]
        except IndexError:
            self.labelText.set("You need to select a playlist to shuffle!")
            return

        print(selected)

        playlist = self.playlists[selected]
        if playlist["owner"]["id"] != username:
            self.labelText.set("Can't shuffle a playlist that's not yours!")
            return


        print(playlist)
        sp = getSP()
        playlist = sp.user_playlist(username, playlist["id"])
        tracks = playlist['tracks']
        songs = tracks['items']
        ids = self.getIDs(tracks, songs)
        random.shuffle(ids)
        if len(ids) <= 100:
            sp.user_playlist_replace_tracks(username, playlist['id'], ids)
        else:
            sp.user_playlist_replace_tracks(username, playlist['id'], ids[0:100])
            for i in range(100, len(ids), 100):
                sp.user_playlist_add_tracks(username, playlist['id'], ids[i:i+100])
        self.labelText.set("Shuffled " + playlist["name"])


    def getIDs(self, tracks, songs):
        sp = getSP()
        while tracks['next']:
            tracks = sp.next(tracks)
            for item in tracks["items"]:
                songs.append(item)
        ids = []
        for i in range(len(songs)):
            ids.append(songs[i]['track']['id'])
        return ids




root = Tk()
shuffleGUI = ShuffleGUI(root)

root.mainloop()
