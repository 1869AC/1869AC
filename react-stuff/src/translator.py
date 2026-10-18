import sys
from pathlib import Path 
sys.path.insert(0,str(Path(__file__).resolve().parent.parent.parent)) #TO SEE THE PYTHON BACK END MAIN STUFF TOO :D
import songs_path
from  supabaseclient import supabase
#comes in a fat chunk
#import last_played.json 
from fastapi import FastAPI, HTTPException #creates server + allows to return errers 404 
from fastapi.responses import FileResponse #sends files to browsert
from fastapi.middleware.cors import CORSMiddleware
from widgets import get_cur_song


app = FastAPI() #uses the import to make a python server w Uvicorn
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["http://localhost:8000","http://localhost:5173"], 
    allow_methods = ["*"], 
    allow_headers = ["*"], 
)
#MAKE DICTIONARY T-T why did we not do this from the startt 
allowed_song_types = {
    ".mp3": "audio/mpeg",
    ".ogg": "audio/ogg",
    ".wav": "audio/wav",
    ".flac": "audio/flac",
}
response = supabase.auth.get_user()
user = response.user
if not user: 
    raise HTTPException(status_code= 401, detail = "NOT LOGGED IN??")
result = supabase.table("users").select("songs").eq("id", user.id).maybeSingle().execute()
playlists = result.data["songs"] if result.data else []


##NAMES
@app.get("/GIMMETHOSESONGS/{index}")
def give_playlists(index:int): 
    playlist_names = list(playlists.keys())
    if int(index) <0 or int(index) >= len(playlist_names):
        raise HTTPException(status_code= 401, detail = "ERROR GETTING SONG!")
    #return{
    #    "name": playlist_names[int(index)],
    #    "songs": playlists[playlist_names[int(index)]]
    #}
    return playlist_names

##PLAY SONG
@app.get("/PLAYSONG/{playlist_index}/{song_index}")
def play(playlist_index:int,song_index:int):
    playlist_names = list(playlists.keys())
    if playlist_index <0 or playlist_index >= len(playlist_names):
        raise HTTPException(status_code= 101, detail = "ERROR PLAYLIST!")
    playlist_name = playlist_names[playlist_index]
    playlist_songs = playlists[playlist_name]
    if song_index <0 or song_index >= len(playlist_songs):
        raise HTTPException(status_code= 101, detail = "ERROR SONG!")
    songs = Path(playlist_songs[song_index]) #str to path

    ##FILE EXTENSION
    my_type = allowed_song_types.get(songs.suffix.lower())    
    if my_type is None or not songs.is_file() :
        raise HTTPException(status_code= 401, detail = "Invalid Song. Can only be MP3, OGG, WAV or FLAC!")
    return FileResponse(path = str(songs), media_type = my_type)
##LAST PLAID
@app.get("/NAMEOFSTUPIDSONG/")
def song_getter():
   return get_cur_song()

##GET ALL SONGS 
@app.get("/ALLSONGS/{playlist_index}")
def get_all_songs(playlist_index:int): 
    playlist_names = list(playlists.keys()) #all the playlists
    print(playlist_index)
    print(len(playlist_names))
    if int(playlist_index) <0 or int(playlist_index) >= len(playlist_names):
        raise HTTPException(status_code= 404, detail = "ERROR GETTING SONG!")
    #NAMES
    print("HTTPS")
    playlist_name = playlist_names[playlist_index]
    #SONGS
    playlist_songs = playlists[playlist_name]
    print("RETURNULOUS")
    return{
        "name": playlist_name,
        "songs": [
            {
                "index": i,
                "name": str(song_name)
            }
            for i, song_name in enumerate(playlist_songs)
        ],
        "playlist_index": playlist_index, 
        "length": len(playlist_songs),
    }

