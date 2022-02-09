import multiprocessing as mp
try:
    from src.enums import Command, Mode
except Exception:
    from enums import Command, Mode
import serial
import glob
from threading import Thread
import time

class SerialClient:
    def __init__(self, buffer:mp.Queue):
        self.port = glob.glob("/dev/ttyUSB*")[0]
        print('Connecting to: ', self.port)
        self.buffer = buffer
        self.ser = serial.Serial(port=self.port, baudrate=9600)
    
    def listen_to_inputs(self):
        data_str = ''
        while (True):
            if (self.ser.inWaiting() > 0):
                data_str += self.ser.read(self.ser.inWaiting()).decode('ascii') 

            if data_str.__contains__('\n'):
                msg, data_str = data_str.split('\n', 1)
                Thread(target=self.generate_player_command, args=(msg,)).start()
            time.sleep(0.01)

    
    def generate_player_command(self, cmd:str):
        commands = list(map(int, cmd.split(',')))

        while len(commands) < 3:
            commands.append(0)

        mode = Mode(commands[0])
        command = Command(commands[1])
        param = commands[2]
        
        msg = [mode, command, param]
        self.send_commands(msg)

    def send_commands(self, msg):
        self.buffer.put(msg)

if __name__ == "__main__":
    buffer = mp.Queue()
    test = [1,3,0]

    sim = SerialClient(buffer)
    sim.listen_to_inputs()

