import time
class TimeGroup():
    def __init__(self, label="no label"):
        self.label = label
    def __enter__(self):
        self.start = time.time()
        return self.start
    def __exit__(self, type, value, traceback):
         duration = time.time()-self.start
         print "[TimeGroup] %s: %.4fs (%.4fms)"%(self.label, duration, duration*1000);