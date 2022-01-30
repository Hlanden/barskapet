import csv
import multiprocessing as mp
import os
import subprocess as sp
import time

try:
    from src.player_interface import PlayerInterface
except:
    from player_interface import PlayerInterface
dirname = os.path.dirname(__file__)

class RadioPlayer(PlayerInterface):

    def __init__(self):
        self.channels = self.get_channels()
        self.number_of_channels = len(self.channels)
        # self.player_process = self.set_playlist(idx)
        self.player_process = None

    def set_playlist(self, idx):
        if isinstance(self.player_process, sp.Popen):
            self.kill_process()
        self.player_process = sp.Popen(
            ['mplayer', '{}'.format(self.channels[idx][1])],
            stdin=sp.PIPE,
            stdout=sp.PIPE,
            stderr=sp.STDOUT
        )
        
    def kill_process(self):
        if self.player_process.poll() is None:
            self.player_process.kill()
        
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
        return None

    def next_song(self):
        return None

    def play_pause(self):
        return None

if __name__ == "__main__":
    print('start')
    player = RadioPlayer()
    player.set_playlist(5)
    time.sleep(10)
    player.kill_process()


