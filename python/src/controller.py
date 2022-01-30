import sys
import subprocess as sp
import multiprocessing as mp
from src.enums import Command, Mode

class BarskapetController:
    def __init__(self, buffer:mp.Queue):
        self.buffer = buffer

        self.mode = Mode.NONE 
        self.volume = 50

        self.player = None

        self.update_volume()
        
    def wait_for_commands(self):
        while True:
            msg = self.buffer.get()
            if msg:
                self.parse_input(msg)
                sys.stdout.flush()

    def parse_input(self, msg:str):
        mode, command, params = msg

        if mode != self.mode:
            self.mode = mode
            self.update_mode()

        if command is Command.NONE:
            pass
        elif command is Command.VOLUME_UP or command is Command.VOLUME_DOWN:
            self.volume = int(params)
            self.update_volume()
        elif command is Command.NEXT_SONG:
            # self.player.next_song()
            pass
        elif command is Command.PREVIOUS_SONG:
            # self.player.previous_song()
            pass
        elif command is Command.PREVIOUS_CHANNEL:
            # self.player.previous_channel()
            pass
        elif command is Command.NEXT_CHANNEL:
            # self.player.next_channel()
            pass
        elif command is Command.PLAY_PAUSE:
            # self.player.play_pause()
            pass

    def update_mode(self):
        if self.mode is Mode.SPOTIFY:
            pass
        elif self.mode is Mode.RADIO:
            pass
        elif self.mode is Mode.NONE:
            pass

    def update_volume(self):
        command = ["amixer", "-Mq" , "sset", "Headphone", "{}%".format(self.volume)]
        sp.Popen(command)
