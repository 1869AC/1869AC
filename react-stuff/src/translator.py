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
    allow_origins = ["http://localhost:8000","http://localhost:5174", "https://1869ac.github.io","https://thepillu.site/", ], 
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
playlists = {}
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

    print("Playlists", repr(playlists))
    print("Names", repr(playlist_names))
    print("PLaylist index", playlist_index)
    print("Song index", song_index)


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

##GET ALL SONGS 
@app.get("/SENDSESSION/{session}")
def sendsession(session): 
    global playlists
    try:
        response = supabase.auth.get_user(session)
        user = response.user
        if not user: 
            raise HTTPException(status_code= 401, detail = "NOT LOGGED IN??")
        supabase.postgrest.auth(session)
        result = supabase.table("users").select("songs").eq("id", user.id).execute()
        if not result.data:
            raise HTTPException(status_code= 401, detail = "user does not exist")
        songs = result.data[0].get("songs") or []
        playlist_dos = {}
        #SONG FOLDER TO SONGS INDIVIDUAL
        for playlist in songs: 
            print("MADE IT")
            if isinstance(playlist, dict) and "name" in playlist and "dir" in playlist:
                print("VALID")
                folder = Path(playlist["dir"])
                print("WHAT?")
                if not folder.is_dir(): 
                    print("BAD PATH")
                    return
                print("meep")
                playlist_dos[playlist["name"]] = [
                    str(file)
                    for file in folder.iterdir()
                    if file.is_file()
                    and file.suffix.lower() in allowed_song_types
                ]
                print("POPULATED")
        playlists = playlist_dos
        print(repr(playlists))
        return {"message": "TEST"}
    except Exception:
        if not response.user or not response: 
            raise HTTPException(status_code= 404, detail = "ERROR SYNCING LOGIN!")
    except HTTPException: 
        raise
    except Exception as e: 
        print(repr(e))
        raise HTTPException(status_code= 401, detail = "SPECIFIC ERROR")

@app.post("/LOGOUT/{session}")
def logout(session):
    global playlists
    playlists.clear()
    response = supabase.auth.get_user(session)
    supabase.postgrest.auth(session)
    error = supabase.auth.sign_out()
    if not error:
       return "works!"
    else:
        return None