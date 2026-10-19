import time
import sys
import os
import vlc
import datetime
from supabaseclient import supabase
from auth import get_uid
from pygame import mixer
import random
try:
    import select
    HAS_SELECT = True
except ImportError:
    select = None
    HAS_SELECT = False

try:
    import termios
    import tty # line 18
    HAS_TERMIOS = True
except ImportError:
    termios = None
    tty = None
    HAS_TERMIOS = False
try:
    import msvcrt
    HAS_MSVCRT = True
except ImportError:
    msvcrt = None
    HAS_MSVCRT = False
if os.name == "nt":
    os.system("")
IS_WINDOWS = (os.name == "nt" or sys.platform == "win32") and HAS_MSVCRT

LIST_BOX_WIDTH = 80
DIM = "\033[2m"
REV = "\033[7m"
RESET = "\033[0m"
##GLOBALS
cur_song_index = 0 
cur_playlist = 0 
def delete_from_supabase(playlist_name):
        name = get_uid()
        if name != "guest": 
            try:
                response = supabase.table("users").select("songs").eq("id", name).maybe_single().execute()
                if not response.data: 
                    return 
                playlists = response.data.get("songs") or []
                ##NOW DELTE
                new_playlist = [
                    p for p in playlists
                    if p.get("name") != playlist_name
                ]
                response1 = supabase.table("users").update({
                    "songs":new_playlist
                }).eq("id", name).execute()
            except Exception as e: 
                print(f"something went wrong ! {e}")
def truncate(text, max_width):
    return text if len(text) <= max_width else text[:max_width - 3] + "..."

def _song_name(path):
    base = os.path.basename(str(path))
    stem, dot, _ext = base.rpartition(".")
    return stem if dot and stem else base

from import_system import append_folder_to_songs_path, get_playlists, is_valid_playlist_name, \
    delete_playlist_from_songs_path, delete_song_from_playlist, add_song_to_playlist, \
    create_virtual_playlist_in_songs_path, is_folder_playlist

import songs_path
import json

class UiWidgets:

    def __init__(self, name_of_song, player, name_of_playlist, current_index, volume):
        mixer.init()

        try:
            with open("last_played.json", "r") as user_saves_raw:
                user_saves = json.load(user_saves_raw)
        except (FileNotFoundError, json.JSONDecodeError):
            user_saves = {}

        self.click_sound = mixer.Sound("./turning_pages-ui-toggle-off-confirmation-608627.mp3")
        self.song = name_of_song
        self.current_sec = 0
        self.current_min = 0
        self.current_timeline_part = 0
        self.seconds_for_vinyl = 0
        self.new_timeline = "-------------------------"
        self.vinyl = ["◐", "◓", "◑", "◒"]
        self.volume_level = volume
        self.volume_list = ["⏹"] * self.volume_level + [" "] * (10 - self.volume_level)
        self.play_pause = "⏸"
        self.current_vinyl = "◐"
        self.current_vinyl_frame = 0
        self.line_list = ["-"] * 25
        self.total_sec = None

        if user_saves != {}:
            if user_saves["shuffle"]:
                self.shuffle = True
                self.shuffle_symbol = "⤭"
            else:
                self.shuffle = False
                self.shuffle_symbol = "⇉"
        else:
            self.shuffle = False
            self.shuffle_symbol = "⇉"

        self.shuffled_song_list = []

        if user_saves != {}:
            if user_saves["auto"] == "auto":
                self.loop_type = "auto"
                self.loop_type_symbol = "↬"
            else:
                self.loop_type = "one"
                self.loop_type_symbol = "⥁"
        else:
            self.loop_type = "auto"
            self.loop_type_symbol = "↬"

        self.previous_vol_lvl = 0
        self.mute_on_off = False
        self.playlist_added = False
        self.old_settings = None
        self.help_menu_toggle = False
        self.current_ms = None
        self.name_of_playlist = name_of_playlist
        self.current_index = current_index
        self._pending_keys = []

    @staticmethod
    def _parse_escape_sequence(seq):
        if not seq or seq[0] != '\x1b':
            return None
        if len(seq) == 1:
            return None
        rest = seq[1:] 
        if rest.startswith('[') or rest.startswith('O'):
            last = rest[-1]
            if last == 'A':
                return 'UP'
            if last == 'B':
                return 'DOWN'
            if last == 'C':
                return 'RIGHT'
            if last == 'D':
                return 'LEFT'
        return None

    def check_key_presses(self):
        if self._pending_keys:
            return self._pending_keys.pop(0)
        
        if IS_WINDOWS:
            return self._check_key_windows()
        
        return self._check_key_unix()

    def _check_key_windows(self):
        try:
            if not msvcrt.kbhit():
                return None
            ch = msvcrt.getwch()
        except (AttributeError, ValueError, OSError, IOError):
            return None
        if ch == "\x1b":
            for _ in range(15):
                if msvcrt.kbhit():
                    break
                    
                time.sleep(0.002)

            if not msvcrt.kbhit():
                return "ESC"
                
            ch2 = msvcrt.getwch()
            if ch2 == "[":
                for _ in range(15):
                    if msvcrt.kbhit():
                        break
                    time.sleep(0.002)
                        
                if msvcrt.kbhit():
                    ch3 = msvcrt.getwch()
                    arrow = {"A": "UP", "B": "DOWN", "C": "RIGHT", "D": "LEFT",
                            "a": "UP", "b": "DOWN", "c": "RIGHT", "d": "LEFT"}.get(ch3)
                        
                    if arrow:
                        return arrow
                        
                return None
                
            if ch2 in ("O", "o"):
                for _ in range(15):
                    if msvcrt.kbhit():
                        break
                    time.sleep(0.002)
                if msvcrt.kbhit():
                    ch3 = msvcrt.getwch()
                    arrow = {"A": "UP", "B": "DOWN", "C": "RIGHT", "D": "LEFT",
                                "a": "UP", "b": "DOWN", "c": "RIGHT", "d": "LEFT"}.get(ch3)

                    if arrow:
                        return arrow

                return {"A": "UP", "B": "DOWN", "C": "RIGHT", "D": "LEFT"}.get(ch2)

        if ch in ("\x00", "\xe0"):
            try:
                ch2 = msvcrt.getwch()

            except (AttributeError, ValueError, OSError, IOError):
                return None

            return {"H": "UP", "P": "DOWN", "K": "LEFT", "M": "RIGHT",
                    "h": "UP", "p": "DOWN", "k": "LEFT", "m": "RIGHT"}.get(ch2, None)

        if ch == "\r":
            return "\n"
        return ch

    def _check_key_unix(self):
        if not HAS_TERMIOS or not HAS_SELECT:
            return None
        try:
            fd = sys.stdin.fileno()
        except (AttributeError, ValueError, OSError, IOError):
            return None
        try:
            ready, _, _ = select.select([sys.stdin], [], [], 0)
        except (ValueError, OSError):
            return None
        if not ready:
            return None
        try:
            data = os.read(fd, 16)
        except OSError:
            return None
        if not data:
            return None
        try:
            text = data.decode('utf-8', errors='ignore')
        except (UnicodeDecodeError, ValueError):
            return None
        if not text:
            return None

        chars = []
        for c in text:
            chars.append('\n' if c == '\r' else c)

        first = chars[0]
        rest_chars = chars[1:]

        if first == '\x1b':
            seq = first + ''.join(rest_chars)
            if len(seq) == 1:
                try:
                    more_ready, _, _ = select.select([sys.stdin], [], [], 0.05)
                except (ValueError, OSError):
                    more_ready = []
                if more_ready:
                    try:
                        extra = os.read(fd, 15)
                    except OSError:
                        extra = b''
                    if extra:
                        try:
                            seq += extra.decode('utf-8', errors='ignore').replace('\r', '\n')
                        except (UnicodeDecodeError, ValueError):
                            pass
            parsed = self._parse_escape_sequence(seq)
            if parsed:
                return parsed
            if len(seq) == 1:
                return '\x1b'
            tail = seq[1:]
            for c in tail:
                if c not in ('[', 'O', ';') and not c.isdigit():
                    self._pending_keys.append(c)
            return self._pending_keys.pop(0) if self._pending_keys else None

        for c in rest_chars:
            self._pending_keys.append(c)
        return first

    def _stdin_fd(self):
        try:
            if sys.stdin.isatty():
                return sys.stdin.fileno()
        except (AttributeError, ValueError, OSError, IOError):
            pass
        return None

    def _setup_cbreak(self):
        self.old_settings = None
        self._pending_keys = []
        if IS_WINDOWS or not HAS_TERMIOS:
            return False
        fd = self._stdin_fd()
        if fd is None:
            return False
        try:
            self.old_settings = termios.tcgetattr(fd)
            tty.setcbreak(fd)
            termios.tcflush(fd, termios.TCIFLUSH)
            return True
        except (termios.error, ValueError, OSError):
            self.old_settings = None
            return False

    def _restore_input(self):
        if IS_WINDOWS or not HAS_TERMIOS:
            return
        if self.old_settings is None:
            return
        fd = self._stdin_fd()
        target = fd if fd is not None else sys.stdin
        try:
            termios.tcsetattr(target, termios.TCSANOW, self.old_settings)
        except (termios.error, ValueError, OSError):
            pass
        finally:
            self.old_settings = None

    def loop_for_song(self, player, song_time, playlist):

        self._setup_cbreak()
        print("\033[?25l", end="")

        try:
            while True:
                self.now_real_time = datetime.datetime.now().strftime("%d %b %Y %I:%M")
                key = self.check_key_presses()

                if key:
                    if key in (' ', "k"):
                        if self.play_pause == "▶":
                            self.play_pause = "⏸"
                        else:
                            self.play_pause = "▶"
                        self.click_sound.play()
                        player.pause()

                    elif key in ('d', "l", "RIGHT"):
                        self.click_sound.play()
                        new_ms = min(player.get_time() + 10000, int(song_time * 1000))
                        player.set_time(new_ms)
                        self.sync_timeline(song_time, new_ms)

                    elif key in ('a', "j", "LEFT"):
                        self.click_sound.play()
                        new_ms = max(player.get_time() - 10000, 0)
                        player.set_time(new_ms)
                        self.sync_timeline(song_time, new_ms)

                    elif key in ("p", "UP"):
                        if self.volume_level < 10:
                            self.click_sound.play()
                            self.volume_level += 1
                            self.update_volume_bar()
                            player.audio_set_volume(self.volume_level * 10)
                            self.save_data_to_last_play()

                    elif key in ("o", "DOWN"):
                        if self.volume_level > 0:
                            self.click_sound.play()
                            self.volume_level -= 1
                            self.update_volume_bar()
                            player.audio_set_volume(self.volume_level * 10)
                            self.save_data_to_last_play()

                    elif key == "s":
                        self.click_sound.play()
                        if self.shuffle:
                            self.shuffle = False
                            self.shuffle_symbol = "⇉"
                            self.save_data_to_last_play()
                        else:
                            self.shuffle = True
                            self.shuffle_symbol = "⤭"
                            self.save_data_to_last_play()

                    elif key == "e":
                        self.click_sound.play()
                        if self.loop_type == "one":
                            self.loop_type = "auto"
                            self.loop_type_symbol = "↬"
                            self.save_data_to_last_play()
                        else:
                            self.loop_type = "one"
                            self.loop_type_symbol = "⥁"
                            self.save_data_to_last_play()

                    elif key == "m":
                        player, song_time, self.current_index = self.next_song(player, playlist, self.current_index, self.shuffle)
                        self.save_data_to_last_play()

                    elif key == "n":

                        if self.total_sec and self.total_sec > 5:
                            player, song_time, self.current_index = self.song_player(player, self.current_index, playlist)
                        else:
                            player, song_time, self.current_index = self.previous_song(player, playlist, self.current_index,
                                                                                  self.shuffle)
                            self.save_data_to_last_play()

                    elif key == 'q':
                        player.stop()
                        self.click_sound.play()
                        self.hard_clear_screen()
                        self.save_data_to_last_play()
                        break

                    elif key == '0':
                        if not self.mute_on_off:
                            self.click_sound.play()
                            self.previous_vol_lvl = self.volume_level
                            self.volume_level = 0
                            self.update_volume_bar()
                            player.audio_set_volume(self.volume_level * 10)
                            self.save_data_to_last_play()
                            self.mute_on_off = True
                        else:
                            self.click_sound.play()
                            self.volume_level = self.previous_vol_lvl
                            self.update_volume_bar()
                            player.audio_set_volume(self.volume_level * 10)
                            self.save_data_to_last_play()
                            self.mute_on_off = False

                    elif key == "c":
                        player.pause()
                        self.click_sound.play()
                        self.import_songs_prompt()
                        player.play()
                        self.play_pause = "⏸"

                    elif key == "x":
                        player.pause()
                        self.click_sound.play()
                        player, song_time, playlist, self.current_index = self.select_playlist(player, playlist, song_time,
                                                                                          self.current_index)
                        self.save_data_to_last_play()
                        player.play()
                        self.play_pause = "⏸"

                    elif key == "z":
                        self.click_sound.play()
                        player, song_time, playlist, self.current_index = self.select_songs(player, playlist, song_time,
                                                                                       self.current_index)
                        self.save_data_to_last_play()
                        player.play()
                        self.play_pause = "⏸"

                    elif key == "v":
                        player.pause()
                        self.click_sound.play()
                        self.create_virtual_playlist()
                        player.play()
                        self.play_pause = "⏸"

                    elif key == "b":
                        player.pause()
                        self.click_sound.play()
                        player, song_time, playlist, self.current_index = self.delete_playlist_prompt(player, playlist, song_time,
                                                                                                 self.current_index)
                        player.play()
                        self.play_pause = "⏸"

                    elif key == "i":
                        player.pause()
                        self.click_sound.play()
                        playlist = self.import_single_song_prompt(playlist)
                        player.play()
                        self.play_pause = "⏸"

                    elif key == "r":
                        player.pause()
                        self.click_sound.play()
                        player, song_time, playlist, self.current_index = self.delete_song_prompt(player, playlist, song_time,
                                                                                             self.current_index)
                        self.save_data_to_last_play()
                        player.play()
                        self.play_pause = "⏸"

                    elif key == "h":
                        if self.help_menu_toggle == False:
                            self.help_menu_toggle = True
                        else:
                            self.help_menu_toggle = False

                if player.is_playing():
                    time.sleep(0.1)
                    self.current_ms = max(0, player.get_time())
                    self.total_sec = int(self.current_ms / 1000)
                    self.current_min = int(self.total_sec / 60)
                    self.current_sec = self.total_sec % 60
                    self.sync_timeline(song_time, self.current_ms)
                    self.seconds_for_vinyl += 0.1
                    if self.seconds_for_vinyl >= 1.0:
                        self.change_vinyl()
                        self.seconds_for_vinyl = 0
                    self.render(song_time, self.current_index, playlist)
                else:
                    self.render(song_time, self.current_index, playlist)
                    time.sleep(0.1)

                if player.get_state() == vlc.State.Ended:
                    self.new_timeline = "========================="
                    self.play_pause = "▶"
                    self.render(song_time, self.current_index, playlist)
                    if self.loop_type == "one":
                        player, song_time, self.current_index = self.loop(player, playlist, self.current_index)
                        self.save_data_to_last_play()
                    else:
                        player, song_time, self.current_index = self.next_song(player, playlist, self.current_index, self.shuffle)
                        self.save_data_to_last_play()
        finally:
            self._restore_input()
            print("\033[?25h\n")

    def sync_timeline(self, song_time, current_ms):
        current_sec = max(0, min(current_ms / 1000, song_time))
        progress_ratio = current_sec / song_time if song_time > 0 else 0

        total_units = progress_ratio * len(self.line_list)
        filled_units = int(total_units)

        self.current_timeline_part = filled_units
        self.line_list = ["="] * filled_units + ["-"] * (len(self.line_list) - filled_units)
        self.new_timeline = "".join(self.line_list)

    def change_vinyl(self):
        self.current_vinyl = self.vinyl[self.current_vinyl_frame]
        if self.current_vinyl_frame < 3:
            self.current_vinyl_frame += 1
        else:
            self.current_vinyl_frame = 0

    def import_songs_prompt(self):
        self.disable_cbreak(self.old_settings)
        self.hard_clear_screen()
        print("+==================================+")
        print("          IMPORT PLAYLIST           ")
        print("+==================================+")

        print("Please paste folder path where music is located: ", end="", flush=True)
        user_directory = input().strip()

        if user_directory == "`":
            print("Returning back...")
            time.sleep(0.5)
            self.hard_clear_screen()
            self.enable_cbreak()
            return

        print("Please provide a name for the playlist: ", end="", flush=True)
        user_playlist_name = input().strip()

        if user_playlist_name == "`":
            print("Returning back...")
            self.hard_clear_screen()
            self.enable_cbreak()
            time.sleep(0.5)
            return

        if user_directory and user_playlist_name:
            ##ADD TO SUPABSE TOO!
            self.playlist_added = append_folder_to_songs_path(user_directory, user_playlist_name)
            name = get_uid()
            if name != "guest":
                try:
                    #PREVENT DUPLICATES
                    response = supabase.table("users").select("songs").eq("id", name).maybe_single().execute()
                    playlists = response.data.get("songs") or [] if response.data else []
                    if not any(
                        playlist.get("name") == user_playlist_name 
                        for playlist in playlists
                    ):
                        playlists.append({
                            "name":user_playlist_name, 
                            "path": user_directory
                        })
                        supabase.table("users").upsert({
                            "id":name, 
                            "songs": playlists
                        }).execute()
                    else:
                        time.sleep(1)
                        self.hard_clear_screen()
                        self.enable_cbreak()
                except Exception as e:
                    print(f"Sorry something went wrong : {e}") 

    
        else:
            print("Directory not found returning back...")

        time.sleep(1)
        self.hard_clear_screen()
        self.enable_cbreak()
    def render(self, song_time, current_song_index, playlist):
        cur_song_index = current_song_index
        cur_playlist = playlist

        self.hard_clear_screen()

        if self.help_menu_toggle == True:
            try:
                with open("help_keybinds.txt", "r") as help_data:
                    print(help_data.read())
            except FileNotFoundError:
                print("help_keybinds.txt not found.")
        else:
            total_min = int(song_time // 60)
            total_sec = int(song_time % 60)
            total_time_str = f"{total_min}:{total_sec:02d}"

            lines = [
                "+=================================================+",
                "",
                f"[ {self.current_vinyl} {self.song}]",
                f"[{self.new_timeline}] [{self.current_min}:{self.current_sec:02d}|{total_time_str}] ",
                f"[ {self.loop_type_symbol} {self.play_pause} {self.shuffle_symbol} ] [{''.join(self.volume_list)} {self.volume_level * 10}%] [{current_song_index + 1}/{len(playlist)}]",
                f"[{self.now_real_time}]",
                "",
                "+=================================================+",
                "",
                "[H] Help menu"
            ]

            for line in lines:
                print(f"\x1b[2K\r{line}")
            print(f"\x1b[{len(lines)}A", end="", flush=True)
    def wait_for_song_length(self, new_player):
        waited = 0
        while new_player.get_length() <= 0:
            if waited >= 5 or new_player.get_state() == vlc.State.Error:
                return False
            time.sleep(0.1)
            waited += 0.1
        return True

    def reset(self, song_name):
        self.song = song_name
        self.current_sec = 0
        self.current_min = 0
        self.current_timeline_part = 0
        self.seconds_for_vinyl = 0
        self.new_timeline = "-------------------------"
        self.line_list = ["-"] * 25
        self.play_pause = "⏸"

    def disable_cbreak(self, old_settings):
        if IS_WINDOWS or not HAS_TERMIOS:
            print("\033[?25h", end="", flush=True)
            return
        fd = self._stdin_fd()
        target = fd if fd is not None else sys.stdin
        try:
            termios.tcflush(target, termios.TCIFLUSH)
        except (termios.error, ValueError, OSError):
            pass
        if old_settings is not None:
            try:
                termios.tcsetattr(target, termios.TCSANOW, old_settings)
            except (termios.error, ValueError, OSError):
                pass
        print("\033[?25h", end="", flush=True)

    def enable_cbreak(self):
        if IS_WINDOWS or not HAS_TERMIOS:
            self._pending_keys = []
            print("\033[?25l", end="", flush=True)
            return
        fd = self._stdin_fd()
        if fd is None:
            return
        try:
            tty.setcbreak(fd)
        except (termios.error, ValueError, OSError):
            return
        print("\033[?25l", end="", flush=True)
        try:
            termios.tcflush(fd, termios.TCIFLUSH)
        except (termios.error, ValueError, OSError):
            pass
        self._pending_keys = []

    def _searchable_pick(self, title, names, multi=False):
        all_songs = list(enumerate(names))
        filtered = all_songs
        query = ""
        searching = False
        sel = 0
        start = 0
        caret = True
        last = time.monotonic()
        chosen = set()
        needs_redraw = True
        

        def refilter():
            nonlocal filtered, sel, start, needs_redraw, caret, last
            q = query.strip().lower()
            filtered = all_songs if not q else [(i, n) for i, n in all_songs if q in n.lower()]
            sel = 0
            start = 0
            caret = True
            last = time.monotonic()
            needs_redraw = True

        self.hard_clear_screen()
        while True:
            total = len(filtered)
            start = max(0, min(start, max(0, total - 10)))
            end = min(start + 10, total)

            if searching and time.monotonic() - last >= 0.5:
                caret = not caret
                last = time.monotonic()
                needs_redraw = True

            if needs_redraw:
                lines = []
                border = "+" + "-" * LIST_BOX_WIDTH + "+"
                lines.append(border)

                if title:
                    t = (" " + truncate(str(title), LIST_BOX_WIDTH - 1)).ljust(LIST_BOX_WIDTH)[:LIST_BOX_WIDTH]
                    lines.append(f" {t} ")

                if searching:
                    c = "▌" if caret else " "
                    left = f" {query[-66:]}{c}"
                    right = f"{total}/{len(all_songs)}"
                    ml = LIST_BOX_WIDTH - len(right) - 1
                    if len(left) > ml:
                        left = left[-ml:]
                    gap = LIST_BOX_WIDTH - len(left) - len(right)
                    lines.append(f" {left}{' ' * max(gap, 1)}{DIM}{right}{RESET} ")
                else:
                    lines.append(f" {' Search: [press /]'.ljust(LIST_BOX_WIDTH)[:LIST_BOX_WIDTH]} ")

                lines.append(border)

                if total == 0:
                    inner = " No match found!".ljust(LIST_BOX_WIDTH)[:LIST_BOX_WIDTH]
                    lines.append(f" {inner} ")

                for pos in range(start, end):
                    orig, name = filtered[pos]
                    mark = "[x] " if orig in chosen else ("[ ] " if multi else "")
                    inner = f"{pos + 1:>2}. {truncate(mark + name, 68)}".ljust(LIST_BOX_WIDTH)[:LIST_BOX_WIDTH]
                    if pos == sel:
                        lines.append(f" {REV}{inner}{RESET} ")
                    else:
                        lines.append(f" {inner} ")

                for _ in range(10 - (end - start)):
                    lines.append(" " * LIST_BOX_WIDTH)

                marks = ("▲" if start > 0 else "") + ("▼" if end < total else "")
                if multi:
                    ctl = "[Type] filter | [↩] mark | [F] finish | [Q] back"
                elif searching:
                    ctl = "[Type] filter | [⌫] del | [Up/Down] move | [↩] select | [ESC] exit"
                else:
                    ctl = "[/] Search | [Up/N] Up | [Down/M] Down | [↩] Select | [Q] Back"
                if marks:
                    ctl = f"{ctl} {marks}"
                inner = (" " + truncate(ctl, LIST_BOX_WIDTH - 1)).ljust(LIST_BOX_WIDTH)[:LIST_BOX_WIDTH]
                lines.append(f" {DIM}{inner}{RESET} ")

                for line in lines:
                    print(f"\x1b[2K\r{line}")
                print(f"\x1b[{len(lines)}A", end="", flush=True)
                needs_redraw = False

            keys = []
            for _ in range(5):
                k = self.check_key_presses()
                if k is None:
                    break

                keys.append(k)

            if not keys:
                time.sleep(0.01)
                continue

            for key in keys:
                total = len(filtered)
                if key == "f" and multi and not searching:
                    if chosen:
                        self.click_sound.play()
                        return sorted(chosen)
                    continue

                if searching:
                    if key in ("ESC", "\x1b"):
                        self.click_sound.play()
                        searching = False
                        query = ""
                        filtered = all_songs
                        sel, start = 0, 0
                        needs_redraw = True
                        continue

                    if key in ("\n", "\r") or (isinstance(key, str) and len(key) == 1 and ord(key) in (10, 13)):
                        if multi:
                            if filtered and sel < len(filtered):
                                self.click_sound.play()

                                o = filtered[sel][0]
                                if o in chosen:
                                    chosen.remove(o)
                                else:
                                    chosen.add(o)

                                needs_redraw = True
                            continue

                        if filtered and sel < len(filtered):
                            self.click_sound.play()
                            return filtered[sel][0]
                        
                        continue

                    if key in ("\x08", "\x7f"):
                        self.click_sound.play()
                        query = query[:-1]
                        refilter()
                        continue

                    if key == "UP" or key == "DOWN":
                        if key == "DOWN" and sel < total - 1:
                            sel += 1
                            if sel >= end:
                                start += 1

                            needs_redraw = True
                            last = time.monotonic()

                        elif key == "UP" and sel > 0:
                            sel -= 1
                            if sel < start:
                                start -= 1

                            needs_redraw = True
                            last = time.monotonic()
                        
                        continue

                    if key in ("LEFT", "RIGHT"):
                        continue

                    if isinstance(key, str) and len(key) == 1 and 32 <= ord(key) <= 126:
                        self.click_sound.play()
                        query += key
                        refilter()
                        continue

                    continue

                if key in ("q", "`"):
                    self.click_sound.play()
                    self.hard_clear_screen()
                    return None

                if key == "/":
                    self.click_sound.play()
                    searching = True
                    query = ""
                    caret = True
                    last = time.monotonic()
                    filtered = all_songs
                    sel, start = 0, 0
                    needs_redraw = True
                    continue

                if key in ("m", "DOWN"):
                    if sel < total - 1:
                        sel += 1
                        if sel >= end:
                            start += 1

                        needs_redraw = True
                    continue

                if key in ("n", "UP"):
                    if sel > 0:
                        sel -= 1
                        if sel < start:
                            start -= 1

                        needs_redraw = True
                    continue

                if key in ("\n", "\r") or (isinstance(key, str) and len(key) == 1 and ord(key) in (10, 13)):
                    if multi:
                        if filtered and sel < len(filtered):
                            self.click_sound.play()
                            o = filtered[sel][0]

                            if o in chosen:
                                chosen.remove(o)
                            else:
                                chosen.add(o)

                            needs_redraw = True
                        continue

                    if filtered and sel < len(filtered):
                        self.click_sound.play()
                        return filtered[sel][0]

                    continue


    def select_playlist(self, player, playlist, song_time, current_index): # line 598
        names = get_playlists()
        if not names:
            self.hard_clear_screen()
            print("No playlists found.")

            time.sleep(1)
            self.hard_clear_screen()
            return player, song_time, playlist, current_index

        res = self._searchable_pick("SELECT A PLAYLIST", names, multi=False)
        if res is None:
            self.hard_clear_screen()
            return player, song_time, playlist, current_index

        new_playlist = getattr(songs_path, names[res])

        if not new_playlist:
            self.hard_clear_screen()
            print("That playlist is empty :( Returning to player...")
            time.sleep(0.5)
            self.hard_clear_screen()
            return player, song_time, playlist, current_index

        player.stop()
        self.name_of_playlist = names[res]
        current_song = new_playlist[0]
        new_song_name = _song_name(current_song)
        new_player = vlc.MediaPlayer(current_song)
        new_player.audio_set_volume(self.volume_level * 10)
        new_player.play()

        if not self.wait_for_song_length(new_player):
            new_song_name = new_song_name + " (could not load) :("

        new_song_time = max(0, new_player.get_length()) / 1000
        self.reset(new_song_name)
        self.hard_clear_screen()
        return new_player, new_song_time, new_playlist, 0

    def select_songs(self, player, playlist, song_time, current_index):
        names = [_song_name(s) for s in playlist]
        res = self._searchable_pick(None, names, multi=False)
        
        if res is None:
            self.hard_clear_screen()
            return player, song_time, playlist, current_index
        
        self.hard_clear_screen()
        player, song_time, res = self.song_player(player, res, playlist)
        return player, song_time, playlist, res

    def select_song_list(self, song_paths, multi, title, select_index=0):
        names = [_song_name(s) for s in song_paths]
        res = self._searchable_pick(title, names, multi=multi)
        
        if res is None:
            self.hard_clear_screen()
            return None
        
        self.hard_clear_screen()
        if multi:
            return res
        
        return [res]

    def create_virtual_playlist(self):
        self.disable_cbreak(self.old_settings)
        self.hard_clear_screen()
        print("+==================================+")
        print("       NEW VIRTUAL PLAYLIST         ")
        print("+==================================+")

        print("Please provide a name for the playlist: ", end="", flush=True)
        user_playlist_name = input().strip()

        if user_playlist_name == "`":
            print("Returning back...")
            time.sleep(0.5)
            self.hard_clear_screen()
            self.enable_cbreak()
            return
        if " " in user_directory_name:
            user_directory_name = user_directory_name.replace(" ", "_")
        if not is_valid_playlist_name(user_playlist_name):
            print("Playlist name can only use letters, numbers and underscores, and can't start with a number.")
            time.sleep(1.5)
            self.hard_clear_screen()
            self.enable_cbreak()
            return

        if user_playlist_name in get_playlists():
            print("this name is already taken please try something else!")
            time.sleep(1.5)
            self.hard_clear_screen()
            self.enable_cbreak()
            return

        all_songs = []
        for playlist_name in get_playlists():
            for song in getattr(songs_path, playlist_name):
                if song not in all_songs:
                    all_songs.append(song)

        self.enable_cbreak()
        chosen_list = self.select_song_list(all_songs, True, f"SELECT SONGS FOR '{user_playlist_name}'")

        self.hard_clear_screen()
        if chosen_list is not None:
            chosen_songs = []
            for song_index in chosen_list:
                chosen_songs.append(all_songs[song_index])

            create_virtual_playlist_in_songs_path(user_playlist_name, chosen_songs)
            time.sleep(1)
            self.hard_clear_screen()
            self.enable_cbreak()

    def force_import_loop(self):
        while get_playlists() == []:
            self.hard_clear_screen()
            print("+==================================+")
            print("          IMPORT PLAYLIST           ")
            print("+==================================+")
            print("No playlists left. Import a folder to continue.")

            print("Please paste folder path where music is located: ", end="", flush=True)
            user_directory = input().strip()

            print("Please provide a name for the playlist: ", end="", flush=True)
            user_playlist_name = input().strip()

            if user_directory and user_playlist_name:
                self.playlist_added = append_folder_to_songs_path(user_directory, user_playlist_name)
            else:
                print("Directory not found try again...")

            time.sleep(1)

        self.hard_clear_screen()

    def play_playlist(self, name_of_playlist):
        self.name_of_playlist = name_of_playlist
        new_playlist = getattr(songs_path, name_of_playlist)
        current_song = new_playlist[0]

        new_song_name = _song_name(current_song)
        new_player = vlc.MediaPlayer(current_song)

        new_player.audio_set_volume(self.volume_level * 10)
        new_player.play()

        if not self.wait_for_song_length(new_player):
            new_song_name = new_song_name + " (could not load)"

        new_song_time = max(0, new_player.get_length()) / 1000
        self.reset(new_song_name)

        return new_player, new_song_time, new_playlist, 0
    def delete_playlist_prompt(self, player, playlist, song_time, current_index): # line 904
        
        self.enable_cbreak()
        self.hard_clear_screen()

        names = get_playlists()
        res = self._searchable_pick("DELETE A PLAYLIST", names, multi=False)

        if res is None:
            self.hard_clear_screen()
            return player, song_time, playlist, current_index
        
        delete_name = names[res]

        print(f"Delete playlist '{delete_name}'? Your music files will not be deleted.")
        answer = input("Type y to confirm: ").strip().lower()

        if answer != "y":
            print("Returning back...")
            time.sleep(0.5)
            self.hard_clear_screen()
            self.enable_cbreak()
            return player, song_time, playlist, current_index

        if not delete_playlist_from_songs_path(delete_name):
            time.sleep(1.5)
            self.hard_clear_screen()
            self.enable_cbreak()
            return player, song_time, playlist, current_index
        delete_from_supabase(self.name_of_playlist)
        time.sleep(1)
        if delete_name == self.name_of_playlist:
            player.stop()

            if get_playlists() == []:
                with open("last_played.json", "w") as user_save:
                    json.dump({}, user_save, indent=4)

                self.force_import_loop()
                player, song_time, playlist, current_index = self.play_playlist(get_playlists()[0])
                self.hard_clear_screen()
                self.enable_cbreak()
            else:
                while self.name_of_playlist == delete_name:
                    player, song_time, playlist, current_index = self.select_playlist(player, playlist, song_time,
                                                                                      current_index)

            self.shuffled_song_list = []
            self.current_index = current_index
            self.save_data_to_last_play()
            return player, song_time, playlist, current_index

        self.hard_clear_screen()
        self.enable_cbreak()
        return player, song_time, playlist, current_index

    def delete_song_prompt(self, player, playlist, song_time, current_index):
        if is_folder_playlist(self.name_of_playlist):
            self.hard_clear_screen()
            print("This playlist stays in sync with its folder, so songs can't be removed here.")
            print("Only virtual playlists can be edited.")
            time.sleep(2)
            self.hard_clear_screen()
            return player, song_time, playlist, current_index

        chosen_list = self.select_song_list(playlist, False, f"DELETE A SONG FROM '{self.name_of_playlist}'", current_index)

        if chosen_list is None:
            self.hard_clear_screen()
            return player, song_time, playlist, current_index

        delete_index = chosen_list[0]
        song_name = _song_name(playlist[delete_index])

        self.disable_cbreak(self.old_settings)
        self.hard_clear_screen()
        print("+==================================+")
        print("            DELETE SONG             ")
        print("+==================================+")

        print(f"Remove '{song_name}' from '{self.name_of_playlist}'? The music file will not be deleted.")
        answer = input("Type y to confirm: ").strip().lower()

        if answer != "y":
            print("Returning back...")
            time.sleep(0.5)
            self.hard_clear_screen()
            self.enable_cbreak()
            return player, song_time, playlist, current_index

        if not delete_song_from_playlist(self.name_of_playlist, delete_index):
            time.sleep(1.5)
            self.hard_clear_screen()
            self.enable_cbreak()
            return player, song_time, playlist, current_index

        new_playlist = getattr(songs_path, self.name_of_playlist)
        self.shuffled_song_list = []

        if delete_index < current_index:
            current_index -= 1
        elif delete_index == current_index:
            current_index = current_index % len(new_playlist)
            player, song_time, current_index = self.song_player(player, current_index, new_playlist)

        time.sleep(1)
        self.hard_clear_screen()
        self.enable_cbreak()
        return player, song_time, new_playlist, current_index

    def import_single_song_prompt(self, playlist):
        if is_folder_playlist(self.name_of_playlist):
            self.hard_clear_screen()
            print("This playlist stays in sync with its folder, so songs can't be added here.")
            print("Only virtual playlists can be edited.")
            time.sleep(2)
            self.hard_clear_screen()
            return playlist

        self.disable_cbreak(self.old_settings)
        self.hard_clear_screen()
        print("+==================================+")
        print("            IMPORT SONG             ")
        print("+==================================+")

        print(f"Adding to playlist: {self.name_of_playlist}")
        print("Please paste the path of the song file: ", end="", flush=True)
        user_song_path = input().strip()

        if user_song_path == "`":
            print("Returning back...")
            time.sleep(0.5)
            self.hard_clear_screen()
            self.enable_cbreak()
            return playlist

        if user_song_path:
            if add_song_to_playlist(self.name_of_playlist, user_song_path):
                playlist = getattr(songs_path, self.name_of_playlist)
        else:
            print("No path given returning back...")

        time.sleep(1)
        self.hard_clear_screen()
        self.enable_cbreak()
        return playlist

    def next_song(self, player, playlist, current_index, shuffle):
        if shuffle:
            self.shuffled_song_list.append(current_index)
            next_index = random.randint(0, len(playlist) - 1)
        else:
            next_index = (current_index + 1) % len(playlist)

        return self.song_player(player, next_index, playlist)


    def previous_song(self, player, playlist, current_index, shuffle):
        if shuffle:
            if self.shuffled_song_list != []:
                previous_index = self.shuffled_song_list.pop(-1)
            else:
                previous_index = (current_index - 1) % len(playlist)
        else:
            previous_index = (current_index - 1) % len(playlist)
        return self.song_player(player, previous_index, playlist)


    def loop(self, player, playlist, current_index):
        return self.song_player(player, current_index, playlist)


    def update_volume_bar(self):
        self.volume_list = ["⏹"] * self.volume_level + [" "] * (10 - self.volume_level)

    def hard_clear_screen(self):
        sys.stdout.write("\033[2J\033[3J\033[H\033[0m")
        sys.stdout.flush()

    def save_data_to_last_play(self):
        data_to_save = {
            "self.volume_level": self.volume_level,
            "playlist": self.name_of_playlist,
            "index_of_song": self.current_index,
            "shuffle": self.shuffle,
            "auto": self.loop_type
        }
        with open("last_played.json", "w") as user_save:
            json.dump(data_to_save, user_save, indent=4)

    def song_player(self, player, index, playlist ):

        player.stop()
        self.click_sound.play()
        if index >= len(playlist):
            index = 0
        song_path = playlist[index]

        song_name = _song_name(song_path)

        new_player = vlc.MediaPlayer(song_path)
        new_player.audio_set_volume(self.volume_level * 10)
        new_player.play()

        if not self.wait_for_song_length(new_player):
            song_name = song_name + " (could not load)"

        new_song_time = max(0, new_player.get_length()) / 1000
        self.reset(song_name)

        return new_player, new_song_time, index
def get_cur_song():
    return [cur_song_index,cur_playlist]