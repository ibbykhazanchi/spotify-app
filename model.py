import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from flask_session import Session
from flask import Flask, session, request, redirect


scope = "user-library-read"

SPOTIPY_CLIENT_ID = "6aebb34eb7f44d218a6925fb96ffd972"
SPOTIPY_CLIENT_SECRET = "bb70797d72ea4852adbaf458c7397c9e"
SPOTIPY_REDIRECT_URI = "http://localhost:5000/redirect/"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, redirect_uri=SPOTIPY_REDIRECT_URI,scope=scope, show_dialog=True))

def logOut():
    try:
        # Remove the CACHE file (.cache-test) so that a new user can authorize.
        os.remove("/Users/ibrahimkhajanchi/Desktop/test/.cache")
    except OSError as e:
        print ("Error: %s - %s." % (e.filename, e.strerror))

def signIn():
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, redirect_uri=SPOTIPY_REDIRECT_URI,scope=scope, show_dialog=True))
    results = sp.current_user_saved_tracks()
    for idx, item in enumerate(results['items']):
        track = item['track']
        print(idx, track['artists'][0]['name'], " – ", track['name'])

results = sp.current_user_saved_tracks()
for idx, item in enumerate(results['items']):
    track = item['track']
    print(idx, track['artists'][0]['name'], " – ", track['name'])

logOut()
signIn()