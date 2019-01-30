from __future__ import print_function

from tkinter import *

import random


import os
from spotipy import oauth2

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util

cid = "69457297a5cc42a4a9b19ba477558210"
secret = "b8df8b59a120497eb7667bdb881058b7"
username = "dylrobinson22"
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

        self.sp = spotipy.Spotify(
            client_credentials_manager=client_credentials_manager)
        #scope = 'playlist-modify-private playlist-modify-public playlist-read-private user-library-read'
        self.token_info = self.prompt_for_user_token(
            username, scope, client_id=cid, client_secret=secret, redirect_uri='http://localhost/')

    def prompt_for_user_token(self, username, scope=None, client_id=None,
                              client_secret=None, redirect_uri=None, cache_path=None):
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


##############################################
root = Tk()
login = LoginWindow(root)
root.mainloop()
