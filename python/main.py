import multiprocessing as mp
from src.simulator import Simulator
from src.controller import BarskapetController
import sys
import time
from threading import Timer

def main():
    use_sim = True
    buffer = mp.Queue(maxsize=10)

    controller = BarskapetController(buffer)
    input_device = Simulator(buffer) #  if use_sim else None 

    controller_process = mp.Process(target=controller.wait_for_commands, args=())

    if use_sim:
        Timer(interval=1, function=input_device.generate_player_command, args=('r')).start()
        Timer(interval=1.5, function=input_device.generate_player_command, args=('b')).start()
        
    controller_process.start()
    input_device.listen_to_inputs()

    controller_process.join()


if __name__ == "__main__":
    main()
