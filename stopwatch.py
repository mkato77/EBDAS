import time
class StopwatchApp:
    def __init__(self):
        self.start_time = None
        self.stop_time = None
        self.elapsed_time = 0
        
    def start(self):
        self.start_time = time.perf_counter()

    def stop(self):
        if self.start_time == None:
            return("-1.0")
        self.stop_time = time.perf_counter()
        self.elapsed_time = self.stop_time - self.start_time
        return(f"{self.elapsed_time:.3f}")
    
    def reset(self):
        self.start_time = None
        self.stop_time = None
        self.elapsed_time = 0