import json
import os
import sys
import json
import time
import pprint
try:
    import vlc
except (ImportError, OSError):
    print("VLC could not be loaded. Please install VLC media player and python-vlc, then run again.")
    sys.exit(1)
import widgets
import songs_path
from import_system import append_folder_to_songs_path, get_playlists
import re
import importlib
from pathlib import Path

if os.name == "nt":
    os.system("")
if os.name != "nt" or os.name != "win32":
    stderr_fd = sys.stderr.fileno()
    devnull = os.open(os.devnull, os.O_WRONLY)
    os.dup2(devnull, stderr_fd)
    os.close(devnull)
##SUPABASE STUFF
name2 = "guest"
username = "guest"
jsdoit = False
allowed_song_types = {
    ".mp3": "audio/mpeg",
    ".ogg": "audio/ogg",
    ".wav": "audio/wav",
    ".flac": "audio/flac",
}

##AUTH IMPORTS
from supabaseclient import supabase
from auth import account

def sync_playlists_with_folders():
    valid_exts = {'.mp3', '.wav', '.flac', '.m4a', '.ogg'}

    with open("songs_path.py", "r", encoding="utf-8") as f:
        content: str = f.read()

    sources = re.findall(r"# Auto-imported playlist from: (.+)\n(\w+) = \[", content)
    if not sources:
        print("Sync: no imported playlists to check.")
        return

    changed = False
    for folder, name in sources:
        folder = str(folder).strip()
        name = str(name)
        old = getattr(songs_path, name, [])
        path = Path(folder)

        if not path.is_dir():
            print(f"[{name}] source folder not found, skipped: {folder}")
            continue

        new = [str(p) for p in path.rglob('*') if p.suffix.lower() in valid_exts]

        if not new:
            print(f"[{name}] source folder has no audio files, skipped: {folder}")
            continue
        old_set, new_set = set(old), set(new)
        added = sorted(new_set - old_set)
        removed = [s for s in old if s not in new_set]

        if not added and not removed:
            print(f"[{name}] up to date ({len(old)} songs)")
            continue

        updated = [s for s in old if s in new_set] + added
        block = f"{name} = [\n" + "".join(f"    {repr(s)},\n" for s in updated) + "]"

        pattern = re.compile(rf"^{re.escape(name)} = \[\n.*?^\]", re.S | re.M)
        content = pattern.sub(lambda m: block, content, count=1)
        changed = True

        print(f"[{name}] updated: +{len(added)} added, -{len(removed)} removed")
        for s in added:
            print(f"   + {Path(s).name}")
        for s in removed:
            print(f"   - {Path(s).name}")

    if changed:
        with open("songs_path.py", "w", encoding="utf-8") as f:
            f.write(content)
        importlib.reload(songs_path)

        time.sleep(2)
#FIRST ASK LOGIN OR LOCAL!
print("+====================================================+")
print("Hello! Welcome to 1869AC - the terminal music player!")
print("Continue as a guest or authenticate to save your playlists to the cloud!")
print("( a/ g ): ")
choice = input("").strip()
if choice.lower() == 'a':
    name2 = account()
    if name2 != "guest":
        #user exists need to sync to cloud
        try:
            response = supabase.table("users").select("songs").eq("id", name2).maybe_single().execute()
            if response and response.data and "songs" in response.data:
                playlists_list = response.data["songs"] or []
                current_playlists = get_playlists()
                for playlist in playlists_list: 
                    song = playlist["name"]
                    directory = playlist["dir"]
                    if song in current_playlists:
                        continue
                    append_folder_to_songs_path(directory, song, shutup = True)
                importlib.reload(songs_path)
        except Exception as e:
            print(e)
    elif choice.lower() == 'g':  
        print("continuing as a guest...") 
    else:
        print("invalid. defaulting to guest mode.") 

if not get_playlists():
    playlists_list = get_playlists()
    while True:
            print("\033[H\033[2J", end="", flush=True)
            print("+=======================================================================+")
            print(
                "It seems like there are no songs added. Please paste a folder path down below where all your music is located:")
            user_directory = input("Folder path: ").strip()
            if user_directory == "`":
                continue
            print("Please provide a name for the playlist:")
            user_directory_name = input("Playlist name: ").strip()
            if user_directory_name == "`":
                continue

            if "" != user_directory and "" != user_directory_name:
                answer = append_folder_to_songs_path(user_directory, user_directory_name)
                if answer:
                    print("Playlist saved! Loading...")
                    print("\033[H\033[2J", end="", flush=True)
                    if name2 != "guest":
                        oldSongs = []
                        try: 
                            response = supabase.table("users").select("songs").eq("id", name2).maybe_single().execute()
                            if response is None or response.data is None:
                                oldSongs = []
                            else:
                                oldSongs = response.data["songs"]
                            response = supabase.table("users").upsert({
                                "id": name2, 
                                "songs": oldSongs + [{"dir": user_directory, "name":user_directory_name}]
                            }).execute()
                        except Exception as e: 
                            print(e)
                            
                    break
                else:
                    print("Playlist not saved! Please try again")
                    time.sleep(1.5)

sync_playlists_with_folders()

while True:
    print("+==================================+")
    print("         SELECT A PLAYLIST          ")
    print("+==================================+")

    for index, name in enumerate(playlists_list):
        tobeornottobe = name["name"] if isinstance(name,dict) else name
        print(f"{index}. {tobeornottobe}")
    print("\nPress the \"z\" to play the last song you played")
    print("Please enter the number next to the playlist you want to play: ")
    playlist_index = input().strip().lower()

    if playlist_index == "z":

        try:
            with open("last_played.json", "r") as user_saves_raw:
                user_saves = json.load(user_saves_raw)
        except (FileNotFoundError, json.JSONDecodeError):
            user_saves = {}

        saved_playlist = getattr(songs_path, str(user_saves.get("playlist", "")), [])
        saved_index = user_saves.get("index_of_song", -1)
        if user_saves and saved_playlist and 0 <= saved_index < len(saved_playlist):

            name_for_Playlist = user_saves["playlist"]
            playlist = getattr(songs_path, name_for_Playlist)
            current_song_index = user_saves["index_of_song"]
            current_song = playlist[current_song_index]
            current_song_name = Path(current_song).name
            #### added
            current_song_path = str(current_song).replace("\\", "/")
            player = vlc.MediaPlayer(current_song_path)
            player.play()
            volume = user_saves.get("self.volume_level", 10)
            player.audio_set_volume(volume * 10)

            data_to_save = {
                "self.volume_level": volume,
                "playlist": name_for_Playlist,
                "index_of_song": current_song_index,
                "shuffle": False,
                "auto": "auto"
            }
            with open("last_played.json", "w") as user_save:
                json.dump(data_to_save, user_save, indent=4)

            break
        else:
            print("No valid last played song found.")
            time.sleep(1)
    else:
        if not playlist_index.isdigit() or int(playlist_index) >= len(playlists_list):
            print("Invalid selection.")
        else:
            #name_for_Playlist = playlists_list[int(playlist_index)]
            #playlist = getattr(songs_path, name_for_Playlist)
            rot = playlists_list[int(playlist_index)]
            if isinstance(rot,dict):
                name_for_Playlist = rot["name"]
            else:
                name_for_Playlist = rot
            
            playlist = getattr(songs_path, name_for_Playlist)
            if not playlist:
                print("That playlist is empty.")
                continue

            current_song_index = 0
            current_song = playlist[current_song_index]
            current_song_name = Path(current_song).name

            current_song_path = str(current_song).replace("\\", "/")
            player = vlc.MediaPlayer(current_song_path)
            player.play()

            try:
                with open("last_played.json", "r") as user_saves_raw:
                    user_saves = json.load(user_saves_raw)
            except (FileNotFoundError, json.JSONDecodeError):
                user_saves = {}

            if user_saves:
                volume = user_saves.get("self.volume_level", 10)
                player.audio_set_volume(volume * 10)
            else:
                volume = 10
                player.audio_set_volume(volume * 10)

            data_to_save = {
                "self.volume_level": volume,
                "playlist": name_for_Playlist,
                "index_of_song": current_song_index,
                "shuffle": False,
                "auto": "auto"
            }
            with open("last_played.json", "w") as user_save:
                json.dump(data_to_save, user_save, indent=4)
            break


waited = 0
while player.get_length() <= 0 and waited < 5:
    time.sleep(0.1)
    waited += 0.1

if player.get_length() <= 0:
    current_song_name = current_song_name + " (could not load)"

length_of_song = max(0, player.get_length()) / 1000.0
widget = widgets.UiWidgets(current_song_name, player, name_for_Playlist, current_song_index, volume)

print("\033[3J\033[H\033[2J", end="", flush=True)

try:
    widget.loop_for_song(player, length_of_song, playlist)
except KeyboardInterrupt:
    print("\nStopped.")