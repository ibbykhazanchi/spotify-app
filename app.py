from os import name
import os
from flask import Flask, render_template, request, url_for, redirect, session
import spotipy, time
from spotipy.oauth2 import SpotifyOAuth
 
app = Flask(__name__)
app.secret_key = "jnsdlkfn4389nfe3ubs"
app.config['SESSION_COOKIE_NAME'] = 'bois cookie'
 
client_id = "6aebb34eb7f44d218a6925fb96ffd972"
client_Secret = "bb70797d72ea4852adbaf458c7397c9e"
TOKEN_INFO = "token_info"
TOKEN_INFO2 = "token_info2"

x = ["user-library-read", "user-top-read"]
 
list1 = []
y=1
list2 = []

@app.route("/")
def home():
    return render_template("home.html")
      

@app.route("/login")
def login():
   sp_oauth = create_spotify_oauth()
   auth_url = sp_oauth.get_authorize_url()
   return redirect(auth_url)
 
 
@app.route('/redirect')
def redirectPage():
   sp_oauth = create_spotify_oauth()
   session.clear()
   code = request.args.get('code')
   token_info = sp_oauth.get_access_token(code)
   session[TOKEN_INFO] = token_info
   return redirect(url_for('getTracks', _external=True))

@app.route("/login2")
def login2():
    try:
        # Remove the CACHE file (.cache-test) so that a new user can authorize.
        os.remove("/Users/ibrahimkhajanchi/Desktop/test/.cache")
        session.clear()
    except OSError as e:
        print ("Error: %s - %s." % (e.filename, e.strerror))
    sp_oauth = create_spotify_oauth2()
    auth_url2 = sp_oauth.get_authorize_url()
    print("authenticated")
    return redirect(auth_url2)
 
 
@app.route('/redirect2')
def redirectPage2():
    print("in redirect2")
    sp_oauth = create_spotify_oauth2()
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session[TOKEN_INFO2] = token_info
    print("4")
    return redirect(url_for('getTracks2', _external=True))
 
 
@app.route("/getTracks")
def getTracks():
    try:
        token_info = get_token()
    except:
        print("user not logged in")
        return redirect(url_for("login", _external=False))
 
    sp = spotipy.Spotify(auth=token_info['access_token'])
    all_songs = []
    iter = 0
    while True:
    #items= sp.current_user_saved_tracks(limit=50, offset=iter*50)['items']
        items = sp.current_user_top_artists()['items']
        all_songs += items
        iter+=1
        if(len(items) < 50):
            break

    one = all_songs[0]
    print(one["name"])

    artist_list = []
    for item in all_songs:
        artist_list.append(item["name"])

    list1 = artist_list
    return redirect(url_for("hi", _external=False))
   
@app.route("/hi")
def hi():
    return render_template("hi.html")


@app.route("/getTracks2")
def getTracks2():
    try:
        print("getting second guy token")
        token_info = get_token2()
    except:
        print("user not logged in 2")
        return redirect(url_for("login2", _external=False))

 
    sp = spotipy.Spotify(auth=token_info['access_token'])
    all_songs = []
    iter = 0
    while True:
    #items= sp.current_user_saved_tracks(limit=50, offset=iter*50)['items']
        items = sp.current_user_top_artists()['items']
        all_songs += items
        iter+=1
        if(len(items) < 50):
            break

    one = all_songs[0]
    print(one["name"])

    artist_list = []
    for item in all_songs:
        artist_list.append(item["name"])

    list2 = artist_list
    print("YOOOOOOOOOOOO")
    return str(artist_list)
 
 
def get_token():
   token_info = session.get(TOKEN_INFO, None)
   if not token_info:
       raise "exception"
   now = int(time.time())
 
   is_expired = token_info['expires_at'] - now < 60
   if(is_expired):
       sp_oauth = create_spotify_oauth()
       token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
 
   return token_info

def get_token2():
   token_info = session.get(TOKEN_INFO2, None)
   if not token_info:
       raise "exception"
   now = int(time.time())
   print("no exception")
   is_expired = token_info['expires_at'] - now < 60
   if(is_expired):
       sp_oauth = create_spotify_oauth2()
       token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
 
   return token_info

def create_spotify_oauth():
   return SpotifyOAuth(
       client_id =client_id,
       client_secret = client_Secret,
       redirect_uri = url_for('redirectPage', _external=True),
       scope = "user-top-read user-library-read")


 
def create_spotify_oauth2():
   return SpotifyOAuth(
       client_id =client_id,
       client_secret = client_Secret,
       redirect_uri = url_for('redirectPage2', _external=True),
       scope = "user-top-read user-library-read")



 
if __name__ == "__main__":
   app.run(debug=True)