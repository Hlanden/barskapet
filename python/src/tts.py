import time
import psutil
import os
from src.enums import Mode
    
modes = {
    Mode.OFF: 'off',
    Mode.RADIO: 'radio',
    Mode.SPOTIFY: 'spotify',
}


def speak(sentence):
    os.system('pkill -9 espeak > /dev/null 2>&1')
    os.system('espeak -s 150 -a 200 "{}" > /dev/null 1>&1'.format(sentence))

def change_mode(mode):
    speak('Changing mode to: {}'.format(modes[mode]))

def change_channel(channel):
    speak(str(channel))
