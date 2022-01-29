import multiprocessing as mp
from simulator import Simulator
import sys
import time

class BarskapetController:

    """Docstring for B. """

    def __init__(self, buffer:mp.Queue):
        self.buffer = buffer
        
    def listen_to_inputs(self):
        while True:
            msg = self.buffer.get()
            if msg:
                print("Got msg:" + str(msg))
                sys.stdout.flush()


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
