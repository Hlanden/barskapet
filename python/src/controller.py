import multiprocessing as mp
import subprocess as sp
import sys

from src.enums import Command, Mode
from src.player_interface import PlayerInterface
from src.radio_player import RadioPlayer

class BarskapetController:
    def __init__(self, buffer:mp.Queue):
        self.player = None

        self.buffer = buffer
        self.initialized = False

        self.mode = Mode.NONE 
        self.volume = 10
        self.index = None
        self.channel_percentage = None

        self.update_volume()
        
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

        if command is Command.VOLUME_UP or command is Command.VOLUME_DOWN:
            self.volume = int(params)
            self.update_volume()

        if self.mode is not Mode.NONE:
            if command is Command.NEXT_SONG:
                self.player.next_song()
            elif command is Command.PREVIOUS_SONG:
                self.player.previous_song()
            elif command is Command.PREVIOUS_CHANNEL or command is Command.NEXT_CHANNEL:
                self.update_playlist(int(params))
            elif command is Command.PLAY_PAUSE:
                self.player.play_pause()

    def update_mode(self, mode):
        if isinstance(self.player, PlayerInterface):
            self.player.kill_process()
            
        if mode is Mode.SPOTIFY:
            pass
        elif mode is Mode.RADIO:
            self.player = RadioPlayer()
        elif mode is Mode.OFF or mode is Mode.NONE:
            self.player = None

        if isinstance(self.player, PlayerInterface) and self.index is not None:
            self.set_playlist()

        self.mode = mode

    def update_volume(self):
        command = ["amixer", "-Mq" , "sset", "Headphone", "{}%".format(self.volume)]
        sp.Popen(command)

    def update_playlist(self, channel_percentage):
        if channel_percentage is not None:
            new_idx = int(channel_percentage*(self.player.number_of_channels - 1)/100)

            if self.index is None or new_idx != self.index:
                self.index = new_idx
                self.set_playlist()

    def set_playlist(self):
        print("Changing channel: {}, {}".format(self.index, self.player.number_of_channels))
        self.player.set_playlist(self.index)
