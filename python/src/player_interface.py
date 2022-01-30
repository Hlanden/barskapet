from abc import ABC, abstractmethod

class PlayerInterface(ABC):
    # @property
    # @abstractmethod
    # def player_process(self):
    #     return NotImplementedError
        
    # @property
    # @abstractmethod
    # def channels(self):
    #     return NotImplementedError

    @abstractmethod
    def __init__(self):
        return None

    @abstractmethod
    def get_channels(self):
        return None

    @abstractmethod
    def previous_channel(self):
        return None

    @abstractmethod
    def next_channel(self):
        return None
        
    @abstractmethod
    def previous_song(self):
        return None

    @abstractmethod
    def next_song(self):
        return None

    @abstractmethod
    def play_pause(self):
        return None
        
    @abstractmethod
    def kill_process(self):
        return None

    @abstractmethod
    def set_playlist(self):
        return None
