import threading
import time
class PageViewCounter:
    def __init__(self):
        self.views = 0
    def increment(self):
        self.views = self.views + 1
        time.sleep(0.0000001)
    def get_views(self):
        return self.views

counter = PageViewCounter()
threads = [threading.Thread(target=counter.increment) for _ in range(5000)]

for t in threads:
    t.start()

for t in threads:
    t.join()
    
print(counter.get_views())