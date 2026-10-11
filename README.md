# Base-Mac-1869AC
it is just natural code for the music player

```
brew install --cask vlc
brew trust mrpeng4/tap
brew tap mrpeng4/tap
brew install ac1869
1869ac
```

## Windows

1. Install Python 3.12 or newer (tick "Add Python to PATH" in the installer)
2. Install the 64-bit VLC media player from https://www.videolan.org/vlc/ (it has to match your Python, so 64-bit with 64-bit)
3. Open a terminal in this folder and run:

```
pip install -r requirements.txt
python main.py
```

Windows Terminal (the default terminal on Windows 11) shows the player symbols best.
Your `songs_path.py` stores full file paths, so don't copy it between Mac and Windows. Start with an empty one and import your music folder again.
