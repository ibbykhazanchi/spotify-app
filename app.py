from flask import Flask, render_template, request, url_for, redirect, session
from spotipy.oauth2 import SpotifyOAuth
import spotipy, time, os, operator
from User import User

 
app = Flask(__name__)
app.secret_key = "jnsdlkfn4389nfe3ubs"
app.config['SESSION_COOKIE_NAME'] = 'bois cookie'

scope = "user-library-read"
SPOTIPY_CLIENT_ID = "6aebb34eb7f44d218a6925fb96ffd972"
SPOTIPY_CLIENT_SECRET = "bb70797d72ea4852adbaf458c7397c9e"

TOKEN_INFO = "token_info"
TOKEN_INFO2 = "token_info2"

userOneGo = 1
user1 = User()
user2 = User()

def create_spotify_oauth():
   return SpotifyOAuth(
       client_id =SPOTIPY_CLIENT_ID,
       client_secret = SPOTIPY_CLIENT_SECRET,
       redirect_uri = url_for('redirectPage', _external=True),
       scope = "user-top-read user-library-read", show_dialog=True)

def get_token():
    if userOneGo ==1:
        token_info = session.get(TOKEN_INFO, None)
    else:
        token_info = session.get(TOKEN_INFO2, None)
    if not token_info:
        raise "exception"
    now = int(time.time())

    is_expired = token_info['expires_at'] - now < 60
    if(is_expired):
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])

    return token_info

def logOut():
    try:
        # Remove the CACHE file (.cache-test) so that a new user can authorize.
        os.remove("/Users/ibrahimkhajanchi/Desktop/spotify-app/.cache")
        session.clear()
    except OSError as e:
        print ("Error: %s - %s." % (e.filename, e.strerror))

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login")
def login():
    global userOneGo
    if(os.path.exists("/Users/ibrahimkhajanchi/Desktop/spotify-app/.cache")):
        userOneGo = 0
        logOut()
    print(userOneGo)
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/redirect')
def redirectPage():
    global userOneGo
    sp_oauth = create_spotify_oauth()
    session.clear()
    code = request.args.get('code')
    if(userOneGo == 1):
        token_info = sp_oauth.get_access_token(code)
        session[TOKEN_INFO] = token_info
    else:
        token_info = sp_oauth.get_access_token(code)
        session[TOKEN_INFO2] = token_info

    return redirect(url_for('getTracks', _external=True))

@app.route("/secondUser")
def secondUser():
    return render_template("secondUser.html")


@app.route("/analyzeData")
def analyzeData():
    global user1, user2

    top_artists1 = []
    top_genres1 = {}
    top_artists2 = []
    top_genres2 = {}

    for artist in user1.artist_dump:
        top_artists1.append(artist[0])

        for genre in artist[1]:
            if top_genres1.get(genre) != None:
                top_genres1[genre] = top_genres1[genre]+1
            else:
                top_genres1[genre] = 1

    user1.top_genres = top_genres1
    user1.top_artists = top_artists1

    for artist in user2.artist_dump:
        top_artists2.append(artist[0])

        for genre in artist[1]:
            if top_genres2.get(genre) != None:
                top_genres2[genre] = top_genres2[genre]+1
            else:
                top_genres2[genre] = 1

    user2.top_genres = top_genres2            
    user2.top_artists = top_artists2

    top_artists1_asSet = set(top_artists1)
    artist_intersection = top_artists1_asSet.intersection(top_artists2)

    top_genres1_asSet = set(user1.top_genres.keys())
    #genre_intersection = top_genres1_asSet.intersection(top_genres2)
    
    return render_template('results.html', url1 = user1.profile_pic, url2 = user2.profile_pic, user1 = user1, user2 = user2, intersection = artist_intersection)
    

@app.route("/getTracks")
def getTracks():
    global user1, user2, userOneGo
    try:
        token_info = get_token()
    except:
        print("user not logged in")
        return redirect(url_for("login", _external=False))
 
    
    sp = spotipy.Spotify(auth=token_info['access_token'])
    print(sp.me())
    all_artists = []
    all_songs = []
    iter = 0
    while True:
        artists = sp.current_user_top_artists(limit=20, offset=iter*20, time_range="medium_term")['items']
        songs = sp.current_user_top_tracks(limit=20, offset=iter*20, time_range="medium_term")['items']
        all_artists += artists
        all_songs += songs
        iter+=1
        if(len(artists) < 20 and len(songs) < 20):
            break
    
    artist_list = []
    for item in all_artists:
        artist_list.append((item["name"], item["genres"], item["popularity"]))

    song_list = []
    for item in all_songs:
        song_list.append((item["name"], item["popularity"]))

    if userOneGo:
        user1.name = sp.me()['display_name']
        if len(sp.me()['images']) == 0:
            user1.profile_pic = "/static/blank-user.jpg"
        else:
            user1.profile_pic = sp.me()['images'][0]['url']
        user1.artist_dump = artist_list
        user1.song_dump = song_list
        return redirect(url_for("secondUser", _external=False))
    else:
        logOut()
        user2.name = sp.me()['display_name']
        if len(sp.me()['images']) == 0:
            user2.profile_pic = "/static/blank-user.jpg"
        else:
            user2.profile_pic = sp.me()['images'][0]['url']
            print(user2.profile_pic)
        user2.artist_dump = artist_list
        user2.song_dump = song_list
        return redirect(url_for("analyzeData", __exernal=False))


    


if __name__ == "__main__":
   app.run(debug=True)