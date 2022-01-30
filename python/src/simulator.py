import termios, fcntl, sys, os
import multiprocessing as mp

class Simulator:
    
    def __init__(self, buffer:mp.Queue):
        self.buffer = buffer
        print(
            """
            Welcome to the simulator!

            This simulates the input from the arduino mounted in barskapet.
            Control:
                - [o]: Off
                - [s]: Spotify
                - [r]: Radio
                - [n]: Next station/next playlist
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
                        # print("Got character", repr(c))
                        self.buffer.put(c)
                except IOError: pass
        finally:
            termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
            fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)

if __name__ == "__main__":
    buffer = mp.Queue()
    sim = Simulator(buffer)

