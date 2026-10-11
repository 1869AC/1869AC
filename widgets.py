import time
import sys
import os
import vlc
import datetime
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
    import tty
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

IS_WINDOWS = (os.name == "nt" or sys.platform == "win32") and HAS_MSVCRT

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
        if ch in ('\x00', '\xe0'):
            try:
                ch2 = msvcrt.getwch()
            except (AttributeError, ValueError, OSError, IOError):
                return None
            return {'H': 'UP', 'P': 'DOWN', 'K': 'LEFT', 'M': 'RIGHT'}.get(ch2, None)
        if ch == '\r':
            return '\n'
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
            self.playlist_added = append_folder_to_songs_path(user_directory, user_playlist_name)
        else:
            print("Directory not found returning back...")

        time.sleep(1)
        self.hard_clear_screen()
        self.enable_cbreak()

    def render(self, song_time, current_song_index, playlist):
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
                f"[ {self.loop_type_symbol} {self.play_pause} {self.shuffle_symbol} ] [{"".join(self.volume_list)} {self.volume_level * 10}%] [{current_song_index + 1}/{len(playlist)}]",
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

    def select_playlist(self, player, playlist, song_time, current_index):
        self.disable_cbreak(self.old_settings)
        self.hard_clear_screen()

        playlists_list = []

        for variable_name in dir(songs_path):
            if not variable_name.startswith("__"):
                playlists_list.append(variable_name)

        print("+==================================+")
        print("         SELECT A PLAYLIST          ")
        print("+==================================+")

        for index in range(0, len(playlists_list)):
            print(f"{index}. {playlists_list[index]}")

        print("\nPlease enter the number next to the playlist you want to play: ")
        playlist_index = input("").strip()

        if playlist_index == "`":
            print("Returning back...")
            time.sleep(0.5)
            self.hard_clear_screen()
            self.enable_cbreak()
            return player, song_time, playlist, current_index

        if not playlist_index.isdigit() or int(playlist_index) >= len(playlists_list):
            print("Invalid selection. Returning to player...")
            time.sleep(0.5)
            self.hard_clear_screen()
            self.enable_cbreak()
            return player, song_time, playlist, current_index

        if not getattr(songs_path, playlists_list[int(playlist_index)]):
            print("That playlist is empty. Returning to player...")
            time.sleep(0.5)
            self.hard_clear_screen()
            self.enable_cbreak()
            return player, song_time, playlist, current_index

        player.stop()

        self.name_of_playlist = playlists_list[int(playlist_index)]
        new_playlist = getattr(songs_path, self.name_of_playlist)
        current_song_index = 0
        current_song = new_playlist[current_song_index]

        new_song_name = current_song.split("/")[-1]
        new_player = vlc.MediaPlayer(current_song)

        new_player.audio_set_volume(self.volume_level * 10)
        new_player.play()

        if not self.wait_for_song_length(new_player):
            new_song_name = new_song_name + " (could not load)"

        new_song_time = max(0, new_player.get_length()) / 1000
        self.reset(new_song_name)

        self.hard_clear_screen()
        self.enable_cbreak()

        return new_player, new_song_time, new_playlist, 0

    def select_songs(self, player, playlist, song_time, current_index):
        self.hard_clear_screen()

        start = current_index - 5
        end = current_index + 5
        select_index = current_index
        temp_select_list = []
        for song in playlist:
            temp_select_list.append(song.split("/")[-1])

        while True:
            self.hard_clear_screen()

            if start >= len(temp_select_list) - 10:
                start = max(0, len(temp_select_list) - 10)
            elif start <= 0:
                start = 0

            if end >= len(temp_select_list):
                end = len(temp_select_list)
            elif end <= 10:
                end = min(10, len(temp_select_list))

            safe_end = min(end, len(temp_select_list))

            for line_index in range(start, safe_end):
                song_name = temp_select_list[line_index]

                if line_index == select_index:
                    print(f"\x1b[2K\r        > {song_name} <")
                else:
                    print(f"\x1b[2K\r  {song_name}  ")
            print("")
            print("[Up/N] Up | [Down/M] Down | [Enter] Play | [Q] Back")
            print(f"\x1b[{safe_end - start}A", end="", flush=True)
            print(f"")

            key = self.check_key_presses()

            if key == "s":
                pass

            if key == 'q':
                self.click_sound.play()
                break

            if key == 'm' or key == 'DOWN':
                self.click_sound.play()
                if select_index < len(temp_select_list) - 1:
                    select_index += 1
                    if start < len(temp_select_list) - 10 and select_index > start:
                        start += 1
                        end += 1

            if key == 'n' or key == 'UP':
                self.click_sound.play()
                if select_index > 0:
                    select_index -= 1
                    if select_index < start:
                        start -= 1
                        end -= 1

            if key in ('\n', '\r') or (key and len(key) == 1 and ord(key) in (10, 13)):
                self.hard_clear_screen()
                player, song_time, select_index = self.song_player(player, select_index, playlist)
                return player, song_time, playlist, select_index

            time.sleep(0.1)

        self.hard_clear_screen()
        return player, song_time, playlist, current_index


    def select_song_list(self, song_paths, multi, title, select_index=0):
        self.hard_clear_screen()

        temp_select_list = []
        for song in song_paths:
            temp_select_list.append(song.split("/")[-1])

        chosen_list = []

        while True:
            self.hard_clear_screen()

            start = max(0, min(select_index - 5, len(temp_select_list) - 10))
            end = min(start + 10, len(temp_select_list))

            print(f"\x1b[2K\r{title}")
            print("")

            for line_index in range(start, end):
                song_name = temp_select_list[line_index]

                if multi:
                    if line_index in chosen_list:
                        song_name = f"[x] {song_name}"
                    else:
                        song_name = f"[ ] {song_name}"

                if line_index == select_index:
                    print(f"\x1b[2K\r        > {song_name} <")
                else:
                    print(f"\x1b[2K\r  {song_name}  ")
            print("")

            if multi:
                print(f"Selected: {len(chosen_list)}")
                print("[N] Up | [M] Down | [Enter] Mark/Unmark | [F] Finish | [Q] Back")
            else:
                print("[N] Up | [M] Down | [Enter] Select | [Q] Back")

            key = self.check_key_presses()

            if key == 'q':
                self.click_sound.play()
                return None

            if key == 'm' or key == 'DOWN':
                self.click_sound.play()
                if select_index < len(temp_select_list) - 1:
                    select_index += 1

            if key == 'n' or key == 'UP':
                self.click_sound.play()
                if select_index > 0:
                    select_index -= 1

            if key in ('\n', '\r') or (key and len(key) == 1 and ord(key) in (10, 13)):
                self.click_sound.play()
                if multi:
                    if select_index in chosen_list:
                        chosen_list.remove(select_index)
                    else:
                        chosen_list.append(select_index)
                else:
                    return [select_index]

            if key == 'f' and multi:
                if chosen_list:
                    self.click_sound.play()
                    return chosen_list
                else:
                    print("Please select at least one song first.")
                    time.sleep(1)

            time.sleep(0.1)

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

        if not is_valid_playlist_name(user_playlist_name):
            print("Playlist name can only use letters, numbers and underscores, and can't start with a number.")
            time.sleep(1.5)
            self.hard_clear_screen()
            self.enable_cbreak()
            return

        if user_playlist_name in get_playlists():
            print("this name is already taken please try something other")
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

        new_song_name = current_song.split("/")[-1]
        new_player = vlc.MediaPlayer(current_song)

        new_player.audio_set_volume(self.volume_level * 10)
        new_player.play()

        if not self.wait_for_song_length(new_player):
            new_song_name = new_song_name + " (could not load)"

        new_song_time = max(0, new_player.get_length()) / 1000
        self.reset(new_song_name)

        return new_player, new_song_time, new_playlist, 0

    def delete_playlist_prompt(self, player, playlist, song_time, current_index):
        self.disable_cbreak(self.old_settings)
        self.hard_clear_screen()

        playlists_list = get_playlists()

        print("+==================================+")
        print("          DELETE A PLAYLIST         ")
        print("+==================================+")

        for index in range(0, len(playlists_list)):
            print(f"{index}. {playlists_list[index]}")

        print("\nPlease enter the number next to the playlist you want to delete: ")
        playlist_index = input("").strip()

        if playlist_index == "`":
            print("Returning back...")
            time.sleep(0.5)
            self.hard_clear_screen()
            self.enable_cbreak()
            return player, song_time, playlist, current_index

        if not playlist_index.isdigit() or int(playlist_index) >= len(playlists_list):
            print("Invalid selection. Returning to player...")
            time.sleep(0.5)
            self.hard_clear_screen()
            self.enable_cbreak()
            return player, song_time, playlist, current_index

        delete_name = playlists_list[int(playlist_index)]

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
        song_name = playlist[delete_index].split("/")[-1]

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

        path_parts = song_path.split('/')
        file_name_with_extension = path_parts[-1]
        song_name = file_name_with_extension

        new_player = vlc.MediaPlayer(song_path)
        new_player.audio_set_volume(self.volume_level * 10)
        new_player.play()

        if not self.wait_for_song_length(new_player):
            song_name = song_name + " (could not load)"

        new_song_time = max(0, new_player.get_length()) / 1000
        self.reset(song_name)

        return new_player, new_song_time, index