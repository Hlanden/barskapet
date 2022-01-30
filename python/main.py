import multiprocessing as mp
from src.simulator import Simulator
from src.controller import BarskapetController
import sys
import time



def main():
    use_sim = True
    buffer = mp.Queue(maxsize=10)
    controller = BarskapetController(buffer)


    p = mp.Process(target=controller.listen_to_inputs, args=())
    p.start()

    if use_sim:
        sim = Simulator(buffer)
        sim.listen_to_inputs()
        # p = mp.Process(target=sim.listen_to_inputs, args=())
        # p.start()
    else:
        pass
        # listen to serial inputs

    p.join()

if __name__ == "__main__":
    main()
