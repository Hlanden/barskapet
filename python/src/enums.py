from enum import Enum

class Mode(Enum):     
    NONE              = 0
    OFF               = 1
    SPOTIFY           = 2
    RADIO             = 3

class Command(Enum):  
    NONE              = 0
    VOLUME_UP         = 1
    VOLUME_DOWN       = 2
    NEXT_SONG         = 3
    PLAY_PAUSE        = 4
    PREVIOUS_SONG     = 5
    NEXT_CHANNEL      = 6
    PREVIOUS_CHANNEL  = 7
