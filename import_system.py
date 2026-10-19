from pathlib import Path
import importlib
import keyword
import re
import songs_path

def reload_songs_path():
    for variable_name in dir(songs_path):
        if not variable_name.startswith("__"):
            delattr(songs_path, variable_name)
    importlib.reload(songs_path)

def get_playlists():
    playlists_list = []

    for variable_name, attribute in vars(songs_path).items():
        if isinstance(attribute,list):
            playlists_list.append(variable_name)
    return playlists_list

def is_valid_playlist_name(playlist_name):
    return playlist_name.isidentifier() and not keyword.iskeyword(playlist_name) and not playlist_name.startswith("__")

def is_folder_playlist(playlist_name):
    with open("songs_path.py", "r", encoding="utf-8") as f:
        content = f.read()

    pattern = rf"^# Auto-imported playlist from: [^\n]*\n{re.escape(playlist_name)} = \["
    return re.search(pattern, content, re.M) is not None

def append_folder_to_songs_path(folder_path, playlist_name, shutup= False):

    playlists_list = []

    for variable_name in dir(songs_path):
        if not variable_name.startswith("__"):
            playlists_list.append(variable_name)
    if " " in playlist_name:
        playlist_name = playlist_name.replace(" ", "_")
    if not is_valid_playlist_name(playlist_name):
        print("Playlist name can only use letters, numbers and underscores, and can't start with a number.")

        return False

    if playlist_name in playlists_list:
        if not shutup:
            print("This name is already taken please and try something else!")
        return False

    else:
        path = Path(folder_path).expanduser().resolve()
        if not path.is_dir():
            print(f"Error: Directory '{folder_path}' not found.")
            return False

        valid_exts = {'.mp3', '.wav', '.flac', '.m4a', '.ogg'}
        audio_files = [str(f) for f in path.rglob('*') if f.suffix.lower() in valid_exts]
        if not audio_files:
            print(f"No audio files found in '{folder_path}'.")
            return False

        python_code = f"\n# Auto-imported playlist from: {path}\n{playlist_name} = [\n"
        python_code += "".join(f"    {repr(audio)},\n" for audio in audio_files)
        python_code += "]\n"
        with open("songs_path.py", "a", encoding="utf-8") as f:
            f.write(python_code)
        reload_songs_path()
        print(f"Added {len(audio_files)} songs to songs_path.py as list '{playlist_name}'.")
        return True

def save_playlist_to_songs_path(playlist_name, songs):
    with open("songs_path.py", "r", encoding="utf-8") as f:
        content = f.read()

    pattern = re.compile(rf"(^#[^\n]*\n)?^{re.escape(playlist_name)} = \[\n.*?^\]", re.S | re.M)
    match = pattern.search(content)

    comment_line = match.group(1) or ""

    block = comment_line + f"{playlist_name} = [\n" + "".join(f"    {repr(s)},\n" for s in songs) + "]"
    content = pattern.sub(lambda m: block, content, count=1)

    with open("songs_path.py", "w", encoding="utf-8") as f:
        f.write(content)
    reload_songs_path()

def delete_playlist_from_songs_path(playlist_name):

    with open("songs_path.py", "r", encoding="utf-8") as f:
        content = f.read()

    pattern = re.compile(rf"(^#[^\n]*\n)?^{re.escape(playlist_name)} = \[\n.*?^\]\n?", re.S | re.M)

    if not pattern.search(content):
        print(f"Error: Playlist '{playlist_name}' not found.")
        return False

    content = pattern.sub("", content, count=1).strip()
    if content:
        content += "\n"

    with open("songs_path.py", "w", encoding="utf-8") as f:
        f.write(content)
    reload_songs_path()
    print(f"Deleted playlist '{playlist_name}'.")
    return True

def delete_song_from_playlist(playlist_name, song_index):

    if is_folder_playlist(playlist_name):
        print("Folder playlists stay in sync with their folder. Only virtual playlists can be edited.")
        return False

    songs = list(getattr(songs_path, playlist_name, []))

    if song_index < 0 or song_index >= len(songs):
        print("Error: Song not found.")
        return False

    if len(songs) <= 1:
        print("A playlist can't be empty. Delete the playlist instead.")
        return False

    removed_song = songs.pop(song_index)
    save_playlist_to_songs_path(playlist_name, songs)
    print(f"Removed '{Path(removed_song).name}' from '{playlist_name}'.")
    return True

def add_song_to_playlist(playlist_name, song_path):

    if is_folder_playlist(playlist_name):
        print("Folder playlists stay in sync with their folder. Only virtual playlists can be edited.")
        return False

    songs = list(getattr(songs_path, playlist_name, []))
    path = Path(song_path.strip().strip("'\"").replace("\\ ", " ")).expanduser().resolve()

    if not path.is_file():
        print(f"Error: File '{song_path}' not found.")
        return False

    valid_exts = {'.mp3', '.wav', '.flac', '.m4a', '.ogg'}
    if path.suffix.lower() not in valid_exts:
        print("Error: That is not a supported audio file (mp3, wav, flac, m4a, ogg).")
        return False

    if str(path) in songs:
        print("That song is already in this playlist.")
        return False

    songs.append(str(path))
    save_playlist_to_songs_path(playlist_name, songs)
    print(f"Added '{path.name}' to '{playlist_name}'.")
    return True

def create_virtual_playlist_in_songs_path(playlist_name, songs):

    if not is_valid_playlist_name(playlist_name):
        print("Playlist name can only use letters, numbers and underscores, and can't start with a number.")
        return False

    if playlist_name in get_playlists():
        print("this name is already taken please and try something other")
        return False

    if not songs:
        print("No songs were selected.")
        return False

    python_code = f"\n# Virtual playlist\n{playlist_name} = [\n"
    python_code += "".join(f"    {repr(song)},\n" for song in songs)
    python_code += "]\n"
    with open("songs_path.py", "a", encoding="utf-8") as f:
        f.write(python_code)
    reload_songs_path()
    print(f"Created virtual playlist '{playlist_name}' with {len(songs)} songs.")
    return True