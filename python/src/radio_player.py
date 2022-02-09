import csv
import multiprocessing as mp
import os
import subprocess as sp
import time
from threading import Thread

try:
    import src.tts as tts
except:
    import tts

try:
    from src.player_interface import PlayerInterface
except:
    from player_interface import PlayerInterface
dirname = os.path.dirname(__file__)

class RadioPlayer(PlayerInterface):

    def __init__(self):
        self.channels = self.get_channels()
        self.number_of_channels = len(self.channels)
        self.player_process = None
        self.idx = int(self.number_of_channels / 2) # Temporary

    def set_playlist(self, idx):
        if isinstance(self.player_process, sp.Popen):
            self.kill_process()
        self.player_process = sp.Popen(
            ['mplayer', '-cache', '640', '{}'.format(self.channels[idx][1])],
            stdin=sp.DEVNULL,
            stdout=sp.DEVNULL,
            stderr=sp.STDOUT
        )
        self.idx = idx
        
    def kill_process(self):
        os.system('pkill -9 mplayer')  
        
    def get_channels(self):
        channels = []
        filename = os.path.join(dirname, 'radio-playlists/norwegian.csv')
        with open(filename, newline='') as csvfile:
            reader = csv.DictReader(
                filter(lambda row: row[0]!='#', csvfile),
                delimiter=',',
                fieldnames=['name', 'url']
            )
            channels = [(rows['name'],rows['url']) for rows in reader]

        return channels

    def previous_channel(self):
        return None

    def next_channel(self):
        return None
        
    def previous_song(self):
        # Temporary
        self.idx = (self.idx - 1) % self.number_of_channels
        self.set_playlist(self.idx)
        Thread(daemon=True, target=tts.change_channel, args=(self.channels[self.idx][0],)).start()

    def next_song(self):
        # Temporary
        self.idx = (self.idx + 1) % self.number_of_channels
        self.set_playlist(self.idx)
        Thread(daemon=True, target=tts.change_channel, args=(self.channels[self.idx][0],)).start()

    def play_pause(self):
        if self.player_process.poll() is None:
            os.system('pkill -9 mplayer')  
        else:
            if self.idx is not None:
                self.set_playlist(self.idx)

if __name__ == "__main__":
    print('start')
    player = RadioPlayer()
    player.set_playlist(5)
    time.sleep(10)
    player.kill_process()


