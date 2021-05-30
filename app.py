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
        os.remove("/Users/Sheel/Desktop/spotify-app/.cache")
        session.clear()
    except OSError as e:
        print ("Error: %s - %s." % (e.filename, e.strerror))

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login")
def login():
    global userOneGo
    if(os.path.exists("/Users/Sheel/Desktop/spotify-app/.cache")):
        userOneGo = 0
        logOut()
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

    for artist in user1.artist_dump.keys():
        top_artists1.append(artist)

        for genre in artist[1]:
            if top_genres1.get(genre) != None:
                top_genres1[genre] = top_genres1[genre]+1
            else:
                top_genres1[genre] = 1

    user1.top_genres = top_genres1
    user1.top_artists = top_artists1

    for artist in user2.artist_dump.keys():
        top_artists2.append(artist)

        for genre in artist[1]:
            if top_genres2.get(genre) != None:
                top_genres2[genre] = top_genres2[genre]+1
            else:
                top_genres2[genre] = 1

    user2.top_genres = top_genres2            
    user2.top_artists = top_artists2

    commonArtist_dict = findCommonDict(top_artists1, top_artists2)
    commonSongs_dict = findCommonDict(user1.top_tracks, user2.top_tracks)
    commonArtist_dict = dict(sorted(commonArtist_dict.items(), key=lambda item: item[1]))
    commonSongs_dict = dict(sorted(commonSongs_dict.items(), key=lambda item: item[1]))
    commonArtist_list = (list) (commonArtist_dict.keys())
    commonSongs_list = (list) (commonSongs_dict.keys())

    #print(commonSongs_list)

    #print(commonArtist_dict)
    
    artist_intersection_tuples = []
    for artist in commonArtist_list:
        artist_intersection_tuples.append((artist, user1.artist_dump.get(artist)[2], (user1.top_artists.index(artist) + 1), (user2.top_artists.index(artist)) + 1))

    #truncate list to max 5 items
    artist_intersection_tuples = artist_intersection_tuples[0:min(len(artist_intersection_tuples), 5)]


    song_intersection_tuples = []
    for song in commonSongs_list:
        song_intersection_tuples.append((song, user1.song_dump[song][1]))

    artist_avgLen = (len(top_artists1) + len(top_artists2))/2
    commonArtist_percentage = (len(commonArtist_list))/(artist_avgLen)
    commonArtist_value = commonArtist_percentage * 70 #artists get 70% weight
    commonArtist_value = round(commonArtist_value, 2)

    songs_avgLen = (len(user1.top_tracks) + len(user2.top_tracks))/2
    commonSongs_percentage = (len(commonSongs_list))/(songs_avgLen)
    commonSongs_value = commonSongs_percentage * 30 #songs get 30% weight
    commonSongs_value = round(commonSongs_value, 2)
    
    totalPercentage_value = commonArtist_value + commonSongs_value
    #truncate list to max 5 items
    song_intersection_tuples = song_intersection_tuples[0: min(len(song_intersection_tuples), 5)]
    
    #print(user1.song_dump)

    return render_template('results.html', url1 = user1.profile_pic, url2 = user2.profile_pic, user1 = user1, user2 = user2, intersection = artist_intersection_tuples, song_intersection = song_intersection_tuples, totalPercentage_value = totalPercentage_value)
    
    
def findCommonDict(list1, list2):
    commonDict = {}
    for i in range (0, len(list1)):
        for j in range(0, len(list2)):
            if(list1[i] == list2[j]):
                commonDict[list1[i]] = i+j
    return commonDict


@app.route("/getTracks")
def getTracks():
    global user1, user2, userOneGo
    try:
        token_info = get_token()
    except:
        print("user not logged in")
        return redirect(url_for("login", _external=False))
 
    
    sp = spotipy.Spotify(auth=token_info['access_token'])
    all_artists = []
    all_songs = []
    songs1 = []
    songs2 = []
    iter = 0
    while True:
        artists = sp.current_user_top_artists(limit=20, offset=iter*20, time_range="medium_term")['items']
        songs = sp.current_user_top_tracks(limit=20, offset=iter*20, time_range="medium_term")['items']
        all_artists += artists
        all_songs += songs
        iter+=1
        if(len(artists) < 20 and len(songs) < 20):
            break

    artist_list = {}
    for item in all_artists:
        artist_list[item["name"]] = (item["genres"], item["popularity"], item['images'][0]['url'])

    song_list = {}
    for item in all_songs:
        song_list[item["name"]] = (item["popularity"], item["preview_url"])
    

    if userOneGo:
        user1.name = sp.me()['display_name']
        if len(sp.me()['images']) == 0:
            user1.profile_pic = "/static/blank-user.jpg"
        else:
            user1.profile_pic = sp.me()['images'][0]['url']
        user1.artist_dump = artist_list
        user1.song_dump = song_list

        for song in user1.song_dump.keys():
            songs1.append(song)
        user1.top_tracks = songs1
        return redirect(url_for("secondUser", _external=False))
    else:
        logOut()
        user2.name = sp.me()['display_name']
        if len(sp.me()['images']) == 0:
            user2.profile_pic = "/static/blank-user.jpg"
        else:
            user2.profile_pic = sp.me()['images'][0]['url']
        user2.artist_dump = artist_list
        user2.song_dump = song_list
        for song in user2.song_dump.keys():
            songs2.append(song)
        user2.top_tracks = songs2
        return redirect(url_for("analyzeData", __exernal=False))


if __name__ == "__main__":
   app.run(debug=True)