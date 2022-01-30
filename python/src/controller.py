import multiprocessing as mp
import subprocess as sp
import sys

from src.enums import Command, Mode
from src.player_interface import PlayerInterface
from src.radio_player import RadioPlayer

class BarskapetController:
    def __init__(self, buffer:mp.Queue):
        self.player : PlayerInterface

        self.buffer = buffer

        self.mode = Mode.NONE 
        self.volume = 50
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
            self.mode = mode
            self.update_mode()

        if command is Command.VOLUME_UP or command is Command.VOLUME_DOWN:
            self.volume = int(params)
            self.update_volume()

        if self.mode is not Mode.NONE:
            if command is Command.NEXT_SONG:
                # self.player.next_song()
                pass
            elif command is Command.PREVIOUS_SONG:
                # self.player.previous_song()
                pass
            elif command is Command.PREVIOUS_CHANNEL or command is Command.NEXT_CHANNEL:
                # self.player.next_channel()
                self.channel_percentage = int(params)
                self.update_playlist()

            elif command is Command.PLAY_PAUSE:
                # self.player.play_pause()
                pass

    def update_mode(self):
        if self.mode is Mode.SPOTIFY:
            pass
        elif self.mode is Mode.RADIO:
            self.player = RadioPlayer()
        elif self.mode is Mode.NONE:
            pass

    def update_volume(self):
        command = ["amixer", "-Mq" , "sset", "Headphone", "{}%".format(self.volume)]
        sp.Popen(command)

    def update_playlist(self):
        if self.channel_percentage is not None:
            new_idx = int(self.channel_percentage*self.player.number_of_channels/100)

            if self.index is None or new_idx != self.index:
                self.index = new_idx
                self.set_playlist()

    def set_playlist(self):
        print("Changing channel: {}".format(self.player.channels[self.index][0]))
        self.player.set_playlist(self.index)
