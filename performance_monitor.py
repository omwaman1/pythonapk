import psutil
import threading
import time

class PerformanceMonitor:
    def __init__(self, update_interval=1.0):
        self.update_interval = update_interval
        self.running = False
        self.thread = None
        
        self.cpu_usage = 0
        self.memory_usage = 0
        self.battery_level = 100
        self.temperature = 0
        
        self.callbacks = []
    
    def start(self):
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop)
        self.thread.daemon = True
        self.thread.start()
    
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
            self.thread = None
    
    def add_callback(self, callback):
        if callable(callback) and callback not in self.callbacks:
            self.callbacks.append(callback)
    
    def remove_callback(self, callback):
        if callback in self.callbacks:
            self.callbacks.remove(callback)
    
    def _monitor_loop(self):
        while self.running:
            self.cpu_usage = psutil.cpu_percent(interval=None)
            self.memory_usage = psutil.virtual_memory().percent
            
            try:
                battery = psutil.sensors_battery()
                if battery:
                    self.battery_level = battery.percent
            except:
                pass
            
            try:
                temps = psutil.sensors_temperatures()
                if temps:
                    for name, entries in temps.items():
                        for entry in entries:
                            if entry.current > self.temperature:
                                self.temperature = entry.current
            except:
                pass
            
            for callback in self.callbacks:
                try:
                    callback(self)
                except Exception as e:
                    print(f"Error in performance callback: {e}")
            
            time.sleep(self.update_interval)
    
    def get_status_dict(self):
        return {
            "cpu_usage": self.cpu_usage,
            "memory_usage": self.memory_usage,
            "battery_level": self.battery_level,
            "temperature": self.temperature
        }
