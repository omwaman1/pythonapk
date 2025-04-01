import os
import psutil
import multiprocessing
from threading import Thread
from queue import Queue

class DeviceCapabilityDetector:
    @staticmethod
    def get_available_memory_mb():
        return psutil.virtual_memory().available / (1024 * 1024)
    
    @staticmethod
    def get_optimal_threads():
        cores = multiprocessing.cpu_count()
        memory_mb = DeviceCapabilityDetector.get_available_memory_mb()
        
        if memory_mb < 1000:  # Less than 1GB available
            return max(1, min(cores // 4, 2))
        elif memory_mb < 2000:  # 1-2GB available
            return max(1, min(cores // 2, 4))
        else:  # More than 2GB available
            return max(1, min(cores - 1, 8))

class ThreadedFrameProcessor:
    def __init__(self, converter, num_threads=None):
        self.converter = converter
        self.num_threads = num_threads or DeviceCapabilityDetector.get_optimal_threads()
        self.input_queue = Queue(maxsize=self.num_threads * 2)
        self.output_queue = Queue()
        self.workers = []
        self.running = False
    
    def worker_function(self):
        while self.running:
            try:
                frame_id, frame = self.input_queue.get(timeout=1)
                if frame is None:
                    self.input_queue.task_done()
                    break
                
                processed = self.converter.process_frame(frame)
                self.output_queue.put((frame_id, processed))
                self.input_queue.task_done()
            except Exception as e:
                pass
    
    def start(self):
        if self.running:
            return
        
        self.running = True
        self.workers = []
        
        for _ in range(self.num_threads):
            thread = Thread(target=self.worker_function)
            thread.daemon = True
            thread.start()
            self.workers.append(thread)
    
    def stop(self):
        self.running = False
        
        for _ in range(self.num_threads):
            self.input_queue.put((None, None))
        
        for worker in self.workers:
            worker.join(timeout=2)
        
        self.workers = []
    
    def add_frame(self, frame_id, frame):
        self.input_queue.put((frame_id, frame))
    
    def get_processed_frame(self, block=True, timeout=None):
        return self.output_queue.get(block=block, timeout=timeout)
    
    def task_done(self):
        self.output_queue.task_done()
