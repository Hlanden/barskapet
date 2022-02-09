from enum import Enum

class Mode(Enum):     
    NONE                = -1
    OFF                 = 0
    SPOTIFY             = 1
    RADIO               = 2
class Command(Enum):    
    NONE                = 0
    VOLUME_UPDATE       = 1
    NEXT_SONG           = 2
    PLAY_PAUSE          = 3
    PREVIOUS_SONG       = 4
    CHANNEL_UPDATE      = 5
