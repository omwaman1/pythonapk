import os
import cv2
import numpy as np
from threading import Thread
from queue import Queue
from optimizations import ThreadedFrameProcessor, DeviceCapabilityDetector

class ThreadedVideoConverter:
    def __init__(self, model_interpreter, progress_callback=None, status_callback=None):
        self.interpreter = model_interpreter
        self.progress_callback = progress_callback
        self.status_callback = status_callback
        
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        
        self.input_height = self.input_details[0]['shape'][1]
        self.input_width = self.input_details[0]['shape'][2]
        
        self.num_threads = DeviceCapabilityDetector.get_optimal_threads()
    
    def preprocess_frame(self, frame):
        resized = cv2.resize(frame, (self.input_width, self.input_height))
        normalized = resized.astype(np.float32) / 127.5 - 1.0
        return np.expand_dims(normalized, axis=0)
    
    def postprocess_frame(self, output_data):
        output = np.squeeze(output_data)
        output = (output + 1.0) * 127.5
        output = np.clip(output, 0, 255).astype(np.uint8)
        return output
    
    def process_frame(self, frame):
        input_data = self.preprocess_frame(frame)
        self.interpreter.set_tensor(self.input_details[0]['index'], input_data)
        self.interpreter.invoke()
        output_data = self.interpreter.get_tensor(self.output_details[0]['index'])
        return self.postprocess_frame(output_data)
    
    def convert_video(self, video_path):
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise Exception("Could not open video file")
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        output_path = os.path.splitext(video_path)[0] + "_anime.mp4"
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        if self.status_callback:
            self.status_callback(f"Processing video with {total_frames} frames using {self.num_threads} threads")
        
        processor = ThreadedFrameProcessor(self, self.num_threads)
        processor.start()
        
        read_thread = Thread(target=self._read_frames, args=(cap, total_frames, processor))
        read_thread.daemon = True
        read_thread.start()
        
        processed_count = 0
        frame_buffer = {}
        next_frame_to_write = 0
        
        while processed_count < total_frames:
            try:
                frame_id, processed_frame = processor.get_processed_frame(timeout=1)
                processor.task_done()
                
                frame_buffer[frame_id] = cv2.resize(processed_frame, (width, height))
                
                while next_frame_to_write in frame_buffer:
                    out.write(frame_buffer[next_frame_to_write])
                    del frame_buffer[next_frame_to_write]
                    next_frame_to_write += 1
                    processed_count += 1
                    
                    if self.progress_callback:
                        progress = int((processed_count / total_frames) * 100)
                        self.progress_callback(progress)
            except Exception as e:
                if processed_count >= total_frames:
                    break
        
        processor.stop()
        cap.release()
        out.release()
        
        return output_path
    
    def _read_frames(self, cap, total_frames, processor):
        for frame_id in range(total_frames):
            ret, frame = cap.read()
            if not ret:
                break
            
            processor.add_frame(frame_id, frame)
