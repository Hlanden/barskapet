import time
import psutil
import os
from src.enums import Mode
    
modes = {
    Mode.OFF: 'off',
    Mode.RADIO: 'radio',
    Mode.SPOTIFY: 'spotify',
}

def speak(sentence, wait_on_mode_tts=False):
    if not wait_on_mode_tts:
        os.system('pkill -9 espeak')
    else:
        while "espeak" in (p.name() for p in psutil.process_iter()):
            time.sleep(0.1)
    os.system('espeak -s 150 -a 200 "{}"'.format(sentence))

def change_mode(mode, wait_on_mode_tts=False):
    speak('Changing mode to: {}'.format(modes[mode], wait_on_mode_tts=True))

def change_channel(channel, wait_on_mode_tts=False):
    speak(str(channel), wait_on_mode_tts=True)
