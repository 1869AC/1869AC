import sys
from pathlib import Path 
sys.path.insert(0,str(Path(__file__).resolve().parent.parent.parent)) #TO SEE THE PYTHON BACK END MAIN STUFF TOO :D
import songs_path
#comes in a fat chunk
#import last_played.json 
from fastapi import FastAPI, HTTPException #creates server + allows to return errers 404 
from fastapi.responses import FileResponse #sends files to browsert
from fastapi.middleware.cors import CORSMiddleware


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
playlists = {
    name:songs
    #gets playlist name
    for name, songs in vars(songs_path).items()
    if isinstance(songs,list) #exclude comments
}


@app.get("/GIMMETHOSESONGS/{index}")
def give_playlists(index:int): 
    playlist_names = list(playlists.keys())
    if int(index) <0 or int(index) >= len(playlist_names):
        raise HTTPException(status_code= 6767, detail = "ERROR GETTING SONG!")
    return{
        "name": playlist_names[int(index)],
        "songs": playlists[playlist_names[int(index)]]
    }

@app.get("/PLAYSONG/{playlist_index}/{song_index}")
def play(playlist_index,song_index):
    playlist_names = list(playlists.keys())
    if playlist_index <0 or playlist_index >= len(playlist_names):
        raise HTTPException(status_code= 6767, detail = "ERROR PLAYLIST!")
    playlist_name = playlist_names[playlist_index]
    playlist_songs = playlists[playlist_name]
    if song_index <0 or song_index >= len(playlist_songs):
        raise HTTPException(status_code= 6767, detail = "ERROR SONG!")
    songs = playlist_songs[song_index]

    ##FILE EXTENSION
    my_type = allowed_song_types.get(songs.suffix.lower(), "application/octet-stream")    
    if not songs.is_file() or my_type is None:
        raise HTTPException(status_code= 6767, detail = "Invalid Song. Can only be MP3, OGG, WAV or FLAC!")
    return FileResponse(songs, type = my_type)

