import time
class StopwatchApp:
    def __init__(self):
        self.start_time = None
        self.stop_time = None
        self.elapsed_time = 0
        
    def start(self):
        self.start_time = time.time()

    def stop(self):
        if self.start_time == None:
            return("-")
        self.stop_time = time.time()
        self.elapsed_time = self.stop_time - self.start_time
        return(f"{self.elapsed_time:.3f}sec")
    
    def reset(self):
        self.start_time = None
        self.stop_time = None
        self.elapsed_time = 0