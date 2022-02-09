import time
import multiprocessing as mp
import subprocess as sp
import sys
from threading import Thread

from src.enums import Command, Mode
from src.player_interface import PlayerInterface
from src.radio_player import RadioPlayer
from src.spotify_player import SpotifyPlayer, SpotifyClient
import src.tts as tts

class BarskapetController:
    def __init__(self, buffer:mp.Queue):
        self.spotify_client = None
        self.player = None

        self.buffer = buffer
        self.initialized = False

        self.mode = Mode.NONE 
        self.volume = None
        self.index = None
        self.channel_percentage = 50 # Temporary

    def wait_for_commands(self):
        while True:
            msg = self.buffer.get()
            if msg:
                self.parse_input(msg)
                print('Got command: {}'.format(msg))
                sys.stdout.flush()

    def parse_input(self, msg:str):
        mode, command, params = msg

        if mode != self.mode:
            self.update_mode(mode)

        if command is Command.VOLUME_UPDATE:
            self.volume = int(params)
            self.update_volume()
        elif command is Command.CHANNEL_UPDATE:
            self.update_channel(int(params))
            if (self.mode is Mode.RADIO or self.mode is Mode.SPOTIFY):
                is_changed = self.update_index()
                if is_changed:
                    self.set_playlist()
                    Thread(daemon=True, target=tts.change_channel, args=(self.player.channels[self.index][0],)).start()


        if self.mode is Mode.RADIO or self.mode is Mode.SPOTIFY:
            if command is Command.NEXT_SONG:
                self.player.next_song()
            elif command is Command.PREVIOUS_SONG:
                self.player.previous_song()
            elif command is Command.PLAY_PAUSE:
                self.player.play_pause()

    def update_mode(self, mode):
        if isinstance(self.player, PlayerInterface):
            self.player.kill_process()
            
        tts_change_mode = Thread(daemon=True, target=tts.change_mode, args=(mode,))
        tts_change_mode.start()
        if mode is Mode.SPOTIFY:
            self.spotify_client = SpotifyClient(username='jorgen1998')
            self.player = SpotifyPlayer(self.spotify_client)
        elif mode is Mode.RADIO:
            self.player = RadioPlayer()
        elif mode is Mode.OFF or mode is Mode.NONE:
            self.player = None

        if isinstance(self.player, PlayerInterface) and self.channel_percentage is not None:
            self.update_index()
            while tts_change_mode.is_alive():
                time.sleep(0.1)
            Thread(daemon=True, target=tts.change_channel, args=(self.player.channels[self.index][0],)).start()
            self.set_playlist()
        self.mode = mode

    def update_volume(self):
        command = ["amixer", "-Mq" , "sset", "Headphone", "{}%".format(self.volume)]
        sp.Popen(command)

    def update_index(self):
        new_idx = int(self.channel_percentage*(self.player.number_of_channels - 1)/100)
        if self.index != new_idx:
            self.index = new_idx
            return True
        return False

    def update_channel(self, channel_percentage):
        if self.channel_percentage is None or self.channel_percentage != channel_percentage:
            self.channel_percentage = channel_percentage
            return True
        return False
     
    def set_playlist(self):
        self.player.set_playlist(self.index)
