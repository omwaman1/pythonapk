from optimizations import DeviceCapabilityDetector

class AdaptiveProcessor:
    QUALITY_LOW = "low"
    QUALITY_MEDIUM = "medium"
    QUALITY_HIGH = "high"
    
    def __init__(self, performance_monitor=None):
        self.performance_monitor = performance_monitor
        self.quality_mode = self.QUALITY_MEDIUM
        
        if self.performance_monitor:
            self.performance_monitor.add_callback(self._on_performance_update)
    
    def _on_performance_update(self, monitor):
        cpu_usage = monitor.cpu_usage
        memory_usage = monitor.memory_usage
        battery_level = monitor.battery_level
        temperature = monitor.temperature
        
        if cpu_usage > 90 or memory_usage > 90 or temperature > 80:
            self.quality_mode = self.QUALITY_LOW
        elif (cpu_usage > 70 or memory_usage > 70 or temperature > 70 or 
              battery_level < 20):
            self.quality_mode = self.QUALITY_MEDIUM
        else:
            self.quality_mode = self.QUALITY_HIGH
    
    def get_frame_scale(self):
        if self.quality_mode == self.QUALITY_LOW:
            return 0.5
        elif self.quality_mode == self.QUALITY_MEDIUM:
            return 0.75
        else:
            return 1.0
    
    def get_processing_threads(self):
        optimal = DeviceCapabilityDetector.get_optimal_threads()
        
        if self.quality_mode == self.QUALITY_LOW:
            return max(1, optimal // 2)
        elif self.quality_mode == self.QUALITY_MEDIUM:
            return max(1, int(optimal * 0.75))
        else:
            return optimal
    
    def should_use_gpu(self):
        return self.quality_mode != self.QUALITY_LOW
