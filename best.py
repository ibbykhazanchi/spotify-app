from os import name
import os
from flask import Flask, render_template, request, url_for, redirect, session
import spotipy, time
from spotipy.oauth2 import SpotifyOAuth
 
app = Flask(__name__)
app.secret_key = "jnsdlkfn4389nfe3ubs"
app.config['SESSION_COOKIE_NAME'] = 'bois cookie'

scope = "user-library-read"
SPOTIPY_CLIENT_ID = "6aebb34eb7f44d218a6925fb96ffd972"
SPOTIPY_CLIENT_SECRET = "bb70797d72ea4852adbaf458c7397c9e"
SPOTIPY_REDIRECT_URI = "http://localhost:8910"

user1_data = []
user2_data = []

@app.route("/")
def home():
    return render_template("home.html")

"""
def populateData(sp, user_data):
    results = sp.current_user_saved_tracks()
    for idx, item in enumerate(results['items']):
        track = item['track']
        user_data+=idx, track['artists'][0]['name'], " – ", track['name']
"""

@app.route("/login")
def login():
    global user1_data
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, redirect_uri="http://127.0.0.1:5000/secondLogin",scope=scope, show_dialog=True))    
    results = sp.current_user_saved_tracks()
    for idx, item in enumerate(results['items']):
        track = item['track']
        user1_data+= idx, track['artists'][0]['name'], " – ", track['name']
    return redirect(url_for('secondLogin', _external=True))


def logOut():
    try:
        # Remove the CACHE file (.cache-test) so that a new user can authorize.
        os.remove("/Users/ibrahimkhajanchi/Desktop/test/.cache")
        session.clear()
    except OSError as e:
        print ("Error: %s - %s." % (e.filename, e.strerror))

@app.route("/secondLogin")
def secondLogin():
    global user2_data
    global user1_data
    logOut()
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, redirect_uri=SPOTIPY_REDIRECT_URI,scope=scope, show_dialog=True))
    results = sp.current_user_saved_tracks()
    for idx, item in enumerate(results['items']):
        track = item['track']
        user2_data+= idx, track['artists'][0]['name'], " – ", track['name']
    print(user2_data)
    print(user1_data)
    logOut()
    return (("user 1 data: {}. User 2 data: {}".format(user1_data,user2_data)))

if __name__=="__main__":
    app.run(debug=True)