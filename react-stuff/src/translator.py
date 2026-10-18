import songs_path
#comes in a fat chunk
#import last_played.json 
from fastapi import FastAPI, HTTPException #creates server + allows to return errers 404 
from fastapi.responses import FileResponse #sends files to browsert


app = FastAPI() #uses the import to make a python server w Uvicorn

#MAKE DICTIONARY T-T why did we not do this from the startt 

playlists = {
    name:songs
    #gets playlist name
    for name, songs in vars(songs_path).items()
    if isinstance(songs,list) #exclude comments
}


@app.get("/GIMMETHOSESONGS/{index}")
def give_playlists(index): 
    return{
        playlists[index]
    }

@app.get("/PLAYSONG/{playlist_index}/{song_index}")
def play(playlist_index,song_index):
    playlist = playlists[playlist_index]
    if playlist is None:
        raise HTTPException(status_code= 6767, detail = "ERROR PLAYLIST!")
    if song_index <0 or song_index >= len(playlist):
        raise HTTPException(status_code= 6767, detail = "ERROR SONG!")
    songs = playlist[song_index]
    return songs

