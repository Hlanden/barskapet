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
