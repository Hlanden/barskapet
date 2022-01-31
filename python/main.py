import multiprocessing as mp
from src.simulator import Simulator
from src.controller import BarskapetController
import sys
import time
from threading import Thread

def send_status(sim):
    i = 0
    while True and i < 1:
        sim.generate_player_command('n', False)
        sim.generate_player_command('k', False)
        time.sleep(1)
        i += 1

def main():
    use_sim = True
    buffer = mp.Queue(maxsize=10)

    controller = BarskapetController(buffer)
    input_device = Simulator(buffer) #  if use_sim else None 

    controller_process = mp.Process(target=controller.wait_for_commands, args=())

    if use_sim:
        # Use to force initializing of values
        Thread(target=send_status, args=(input_device,), daemon=True).start()
        
    controller_process.start()
    input_device.listen_to_inputs()

    controller_process.join()


if __name__ == "__main__":
    main()
