import termios, fcntl, sys, os
import multiprocessing as mp
from src.enums import Command, Mode

class Simulator:
    def __init__(self, buffer:mp.Queue):
        self.volume = 50
        self.channel_percentage = 50
        self.mode = Mode.NONE

        self.buffer = buffer
        print(
            """
            Welcome to the simulator!

            This simulates the input from the arduino mounted in barskapet.
            Control:
                - [o]: Off
                - [s]: Spotify
                - [r]: Radio
                - [b]: Decrease channel percentage by 2
                - [n]: Increase channel percentage by 2
                - [h]: Previous song
                - [p]: Play/pause
                - [l]: Next song
                - [j]: Volume down 1 %
                - [k]: Volume up 1 %
            """
        )
    
    def listen_to_inputs(self):
        fd = sys.stdin.fileno()

        oldterm = termios.tcgetattr(fd)
        newattr = termios.tcgetattr(fd)
        newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
        termios.tcsetattr(fd, termios.TCSANOW, newattr)

        oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)

        try:
            while 1:
                try:
                    c = sys.stdin.read(1)
                    if c:
                        self.generate_player_command(c)
                except IOError: pass
        finally:
            termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
            fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)

    def generate_player_command(self, keyboard_input:str):
        command = Command.NONE
        param = ''

        ### MODES ###
        # Off
        if keyboard_input == 'o':
            self.mode = Mode.OFF
        # Spotify
        elif keyboard_input == 's':
            self.mode = Mode.SPOTIFY
        # Radio
        elif keyboard_input == 'r':
            self.mode = Mode.RADIO

        ### COMMANDS ###
        # Decrease channel percentage by 2
        if keyboard_input == 'b':
            command = Command.PREVIOUS_CHANNEL
            if self.channel_percentage >= 1:
                self.channel_percentage -= 2
            param = self.channel_percentage
        # Increase channel percentage by 2
        elif keyboard_input == 'n':
            command = Command.NEXT_CHANNEL
            if self.channel_percentage <= 99:
                self.channel_percentage += 2
            param = self.channel_percentage
        # Previous song
        elif keyboard_input == 'h':
            command = Command.PREVIOUS_SONG
        # Play/pause
        elif keyboard_input == 'p':
            command = Command.PLAY_PAUSE
        # Next song
        elif keyboard_input == 'l':
            command = Command.NEXT_SONG
        # Volume down 1 %
        elif keyboard_input == 'j':
            command = Command.VOLUME_DOWN
            if self.volume >= 1:
                self.volume -= 1
            param = self.volume
        # Volume up 1 %
        elif keyboard_input == 'k':
            command = Command.VOLUME_UP
            if self.volume <= 99:
                self.volume += 1
            param = self.volume
        # None
        else:
            command = Command.NONE

        msg = [self.mode, command, param]
        self.send_commands(msg)

    def send_commands(self, msg):
        self.buffer.put(msg)

if __name__ == "__main__":
    buffer = mp.Queue()
    sim = Simulator(buffer)

