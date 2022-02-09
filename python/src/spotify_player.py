from dataclasses import dataclass
from threading import Thread
import os
from pathlib import Path
import time
from typing import List

import spotipy
from spotipy.client import Spotify
from spotipy.exceptions import SpotifyException
from spotipy.oauth2 import SpotifyOauthError
import spotipy.util as util

import src.tts as tts
try:
    from src.player_interface import PlayerInterface
except:
    from player_interface import PlayerInterface
# from playlist import Playlist, Song


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
    
    def _handle_spotify_exceptions(func):
        def wrapper(self, *args, **kwargs):
            try:
                result = func(self, *args, **kwargs)
            except SpotifyOauthError:
                self.get_token(self.username)
                result = func(self, *args, **kwargs)
            except SpotifyException as e:
                result = False
                if e.http_status == 404:
                    self.playback_devices = self.get_devices()
                    for pd in self.playback_devices:
                        if str(pd).__contains__('barskapet'):
                            self.set_active_device(pd.id)
                            self.device_is_active = True
                            result = func(self, *args, **kwargs)
                            break
                    if self.device_is_active:
                        Thread(target=tts.speak('No active spotify device found. Start spotify and try again')).start()
                    self.device_is_active = False
                    print('No active device found')

                elif e.http_status == 401:
                    self.get_token(self.username)
                    result = func(self, *args, **kwargs)

                    # HARDCODED SOLUTION FOR TESTING PURPOSES
                    # self.set_active_device(self.playback_devices[1].id)
                    # result = func(self, *args, **kwargs)
            return result
        return wrapper

    @_handle_spotify_exceptions
    def __init__(self, username, **kwargs):
        self.username = username
        self.token: str = ''
        self.device_is_active = True

        try:
            self.token = self.get_token(self.username)
            super().__init__(auth=self.token, **kwargs)
        except Exception as e:
            raise SpotifyInitException('Could not initialize spotify client: ' + str(e))
        self.playback_devices = self.get_devices()
        print('Active devices: ', self.playback_devices)
        for pd in self.playback_devices:
            if str(pd).__contains__('barskapet'):
                self.device_is_active = True
                self.set_active_device(pd.id)
                self.volume(100)
                self.pause()
                self.shuffle(state=True)
        if not self.device_is_active:
            self.device_is_active = False
            print('Barskapet is not active')


    @_handle_spotify_exceptions
    def get_token(self, username:str):
        cache_dir=os.path.join(
            os.path.abspath(dirname),
            '.tokens'
        )
        Path(cache_dir).mkdir(parents=True, exist_ok=True)
        cache_path= os.path.join(cache_dir, '.cache-{}'.format(username))

        self.oauth_manager = spotipy.SpotifyOAuth(
            client_id='d81b64e171bb48469b1be83e50810677',
            client_secret='f9f297fb119148cc8b734d0e25a9f356',
            redirect_uri='http://localhost:8080/',
            cache_path=cache_path,
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
            username=username,
            show_dialog=False
        )
        token = util.prompt_for_user_token(oauth_manager=self.oauth_manager)
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
    def set_active_device(self, device_id):
        try:
            super().transfer_playback(device_id=device_id)
        except SpotifyException as e:
            raise SetDeviceException('Coiuld not activate given device: ' + str(e))

    @_handle_spotify_exceptions
    def set_volume(self, vol):
        self.volume(vol)

    @_handle_spotify_exceptions
    def is_playing(self):
        return self.current_playback()['is_playing']

    @_handle_spotify_exceptions
    def play_pause(self, **kwargs):
        try:
            if self.is_playing():
                super().pause_playback(**kwargs)
            else:
                super().start_playback(**kwargs)
        except spotipy.SpotifyException as e:
            if e.http_status == 403:
                # Already paused
                return
            else:
                raise e

    @_handle_spotify_exceptions
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

    @_handle_spotify_exceptions
    def next(self):
        self.next_track()

    @_handle_spotify_exceptions
    def previous(self):
        self.previous_track()

class SpotifyPlayer(PlayerInterface):

    def __init__(self, client:SpotifyClient):
        self.client = client
        self.channels = client.get_playlists()
        self.number_of_channels = len(self.channels)
        self.player_process = None
        self.idx = int(self.number_of_channels / 2) # Temporary
        self.playbackDevices = self.client.get_devices()
        self.active_device = self.client.get_active_device()

    def get_channels(self):
        self.client.get_playlists()

    def previous_channel(self):
        return None

    def next_channel(self):
        return None
        
    def previous_song(self):
        self.client.previous()

    def next_song(self):
        self.client.next()

    def play_pause(self):
        self.client.play_pause()
        
    def kill_process(self):
        self.client.pause()

    def set_playlist(self, idx):
        self.client.start_playlist(context_uri=self.channels[idx][1])
        self.idx = idx
        
if __name__=='__main__':
    username = 'jorgen-1998'
    sp = SpotifyClient(username=username)
    player = SpotifyPlayer(sp)
