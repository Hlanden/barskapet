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
        self.channel_percentage = None

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

        if self.mode is Mode.RADIO or self.mode is Mode.SPOTIFY:
            if command is Command.NEXT_SONG:
                self.player.next_song()
            elif command is Command.PREVIOUS_SONG:
                self.player.previous_song()
            elif command is Command.PLAY_PAUSE:
                self.player.play_pause()
            elif command is Command.CHANNEL_UPDATE:
                self.update_channel(int(params))

    def update_mode(self, mode):
        if isinstance(self.player, PlayerInterface):
            self.player.kill_process()
            
        Thread(target=tts.change_mode, args=(mode,)).start()
        if mode is Mode.SPOTIFY:
            self.spotify_client = SpotifyClient(username='jorgen1998')
            self.player = SpotifyPlayer(self.spotify_client)
        elif mode is Mode.RADIO:
            self.player = RadioPlayer()
        elif mode is Mode.OFF or mode is Mode.NONE:
            self.player = None

        if isinstance(self.player, PlayerInterface) and self.index is not None:
            self.set_playlist(wait_on_mode_tts=True)

        self.mode = mode

    def update_volume(self):
        command = ["amixer", "-Mq" , "sset", "Master", "{}%".format(self.volume)]
        sp.Popen(command)

    def update_channel(self, channel_percentage):
        if channel_percentage is not None and (self.mode is Mode.RADIO or self.mode is Mode.SPOTIFY):
            new_idx = int(channel_percentage*(self.player.number_of_channels - 1)/100)
            if self.index is None or new_idx != self.index:
                self.index = new_idx
                self.set_playlist()
    
    def set_playlist(self, wait_on_mode_tts=False):
        Thread(target=tts.change_channel, args=(self.player.channels[self.index][0],wait_on_mode_tts,)).start()
        self.player.set_playlist(self.index)
