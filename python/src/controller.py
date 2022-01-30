import sys
import subprocess as sp
import multiprocessing as mp
from enums import Command, Mode

class BarskapetController:
    def __init__(self, buffer:mp.Queue):
        self.buffer = buffer

        self.mode = Mode.NONE 
        self.volume = 50

        self.player = None
        
    def wait_for_commands(self):
        while True:
            msg = self.buffer.get()
            if msg:
                print("Got msg:" + str(msg))
                self.parse_input(msg)
                sys.stdout.flush()

    def parse_input(self, msg:str):
        mode, command, params = msg.split(',')

        if mode != self.mode:
            self.mode = mode
            self.update_mode()

        if command == Command.NONE:
            pass
        elif command == Command.VOLUME_UP or command == Command.VOLUME_DOWN:
            self.volume = int(params)
            self.update_volume()
        elif command == Command.NEXT_SONG:
            # self.player.next_song()
            pass
        elif command == Command.PREVIOUS_SONG:
            # self.player.previous_song()
            pass
        elif command == Command.PREVIOUS_CHANNEL:
            # self.player.previous_channel()
            pass
        elif command == Command.NEXT_CHANNEL:
            # self.player.next_channel()
            pass
        elif command == Command.PLAY_PAUSE:
            # self.player.play_pause()
            pass

    def update_mode(self):
        if self.mode == Mode.SPOTIFY:
            pass
        elif self.mode == Mode.RADIO:
            pass
        elif self.mode == Mode.NONE:
            pass

    def update_volume(self):
        command = ["amixer", "sset", "Master", "{}%".format(self.volume)]
        sp.Popen(command)
