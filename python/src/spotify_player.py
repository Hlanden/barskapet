import os
import spotipy
from spotipy.client import Spotify
from spotipy.exceptions import SpotifyException
import spotipy.util as util
from spotipy.oauth2 import SpotifyOauthError
from dataclasses import dataclass
from typing import List
import time
try:
    from src.player_interface import PlayerInterface
except:
    from player_interface import PlayerInterface
# from playlist import Playlist, Song
from pathlib import Path

dirname = os.path.dirname(__file__)

class SpotifyInitException(Exception):
    pass

class GetDevicesException(Exception):
    pass

class SetDeviceException(Exception):
    pass

@dataclass
class PlaybackDevice: 
    name: str
    type: str
    id: str
    is_active: bool
    volume_percent: int
    is_private_session: bool
    is_restricted: bool

    def __repr__(self) -> str:
        return '{} ({})'.format(self.name, self.type)

class SpotifyClient(spotipy.Spotify):
    def __init__(self, username, **kwargs):
        self.username = username
        self.token: str = ''

        try:
            self.token = self.get_token(self.username)
            super().__init__(auth=self.token, **kwargs)
        except Exception as e:
            raise SpotifyInitException('Could not initialize spotify client: ' + str(e))
        self.playback_devices = self.get_devices()

    def _handle_spotify_exceptions(func):
        def wrapper(self, *args, **kwargs):
            try:
                result = func(self, *args, **kwargs)
            except SpotifyOauthError:
                self.get_token(self.username)
                result = func(self, *args, **kwargs)
            except SpotifyException as e:
                if e.http_status == 404:
                    self.playback_devices = self.get_devices()
                    # for pd in self.playback_devices:
                    #     if str(pd) == 'barskapet':
                    #         self.set_active_device(pd.id)
                    #         result = func(self, *args, **kwargs)
                    #         break

                    # HARDCODED SOLUTION FOR TESTING PURPOSES
                    self.set_active_device(self.playback_devices[1].id)
                    result = func(self, *args, **kwargs)
            return result
        return wrapper

    def get_token(self, username:str):
        cache_dir=os.path.join(
            os.path.abspath(dirname),
            '.tokens'
        )
        Path(cache_dir).mkdir(parents=True, exist_ok=True)
        cache_path= os.path.join(cache_dir, '.cache-{}'.format(username))
        token = util.prompt_for_user_token(username,
            scope=('user-modify-playback-state '
                'user-read-currently-playing '
                'user-read-playback-state '
                'user-read-playback-position',
                'user-read-currently-playing ',
                'user-library-read ',
                'user-top-read ',
                'user-modify-playback-state ',
                'playlist-read-private ',
                'playlist-modify-public ',
                'playlist-modify-private ',
                'playlist-read-collaborative '
            ),
            client_id='d81b64e171bb48469b1be83e50810677',
            client_secret='f9f297fb119148cc8b734d0e25a9f356',
            redirect_uri='http://localhost:8080/',
            cache_path=cache_path
        )
        return token                                       

    @_handle_spotify_exceptions
    def get_devices(self):
        try:
            devices = [PlaybackDevice(**dev) for dev in self.devices()['devices']]
        except Exception as e:
            raise GetDevicesException('Could not get active devices from spotify client: \n' + str(e))

        return devices

    @_handle_spotify_exceptions
    def get_active_device(self):
        for dev in self.get_devices():
            if dev.is_active:
                self.active_device = dev
                return dev
        return None

    @_handle_spotify_exceptions
    def set_active_device(self, device_id: str):
        try:
            super().transfer_playback(device_id=device_id)
        except SpotifyException as e:
            raise SetDeviceException('Coiuld not activate given device: ' + str(e))

    @_handle_spotify_exceptions
    def set_volume(self, vol):
        self.volume(vol)

    @_handle_spotify_exceptions
    def play_pause(self, **kwargs):
        try:
            super().pause_playback(**kwargs)
        except spotipy.SpotifyException as e:
            if e.http_status == 403:
                # Already paused
                super().start_playback(**kwargs)
                return
            else:
                raise e
    def pause(self, **kwargs):
        try:
            super().pause_playback(**kwargs)
        except spotipy.SpotifyException as e:
            if e.http_status == 403:
                # Already paused
                return
            else:
                raise e


    @_handle_spotify_exceptions
    def get_current_volume(self):
        volume = self.current_playback()['device']['volume_percent']
        return volume

    @_handle_spotify_exceptions
    def get_playlists(self):
        spotify_playlists = self.current_user_playlists(limit=30)['items']
        playlists = [(p['name'], p['uri']) for p in spotify_playlists]
        return playlists

    @_handle_spotify_exceptions
    def start_playlist(self, **kwargs):
        self.shuffle(state=True)
        self.start_playback(**kwargs)

class SpotifyPlayer(PlayerInterface):

    def __init__(self, client:SpotifyClient):
        self.client = client
        self.channels = client.get_playlists()
        self.number_of_channels = len(self.channels)
        self.player_process = None
        self.idx = None
        self.playbackDevices = self.client.get_devices()
        self.active_device = self.client.get_active_device()
        print('Playback devices: \n{}'.format(self.playbackDevices))

    def get_channels(self):
        return self.client.get_playlists()

    def previous_channel(self):
        return None

    def next_channel(self):
        return None
        
    def previous_song(self):
        return self.client.previous_track()

    def next_song(self):
        return self.client.next_track()

    def play_pause(self):
        return self.client.play_pause()
        
    def kill_process(self):
        return self.client.pause()

    def set_playlist(self, idx):
        self.client.start_playlist(context_uri=self.channels[idx][1])
        self.idx = idx
        
if __name__=='__main__':
    res = handler.get_cached_token()
    sp = SpotifyClient(username=username)
    player = SpotifyPlayer(sp)
    #sp.play_for_time_duration()
    #sp.pause_playback()
