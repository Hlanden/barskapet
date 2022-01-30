from enum import Enum

class Mode(Enum):     
    NONE                = 0
    OFF                 = 1
    SPOTIFY             = 2
    RADIO               = 3
class Command(Enum):    
    NONE                = 0
    VOLUME_UPDATE       = 1
    NEXT_SONG           = 2
    PLAY_PAUSE          = 3
    PREVIOUS_SONG       = 4
    CHANNEL_UPDATE      = 5
