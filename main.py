import os
import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.progressbar import ProgressBar
from threading import Thread
import numpy as np
import cv2
import tensorflow as tf

class AnimeGANApp(App):
    def build(self):
        self.title = 'AnimeGAN Video Converter'
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        self.status_label = Label(text="Select a video to convert")
        layout.add_widget(self.status_label)
        
        self.file_chooser = FileChooserListView(filters=['*.mp4', '*.avi', '*.mov'])
        layout.add_widget(self.file_chooser)
        
        button_layout = BoxLayout(size_hint=(1, 0.2))
        self.convert_btn = Button(text="Convert to Anime")
        self.convert_btn.bind(on_press=self.start_conversion)
        button_layout.add_widget(self.convert_btn)
        
        layout.add_widget(button_layout)
        
        self.progress_bar = ProgressBar(max=100, value=0)
        layout.add_widget(self.progress_bar)
        
        return layout
    
    def start_conversion(self, instance):
        if not self.file_chooser.selection:
            self.status_label.text = "Please select a video first"
            return
        
        video_path = self.file_chooser.selection[0]
        self.convert_btn.disabled = True
        self.status_label.text = "Starting conversion..."
        
        thread = Thread(target=self.process_video, args=(video_path,))
        thread.daemon = True
        thread.start()
    
    def process_video(self, video_path):
        try:
            converter = VideoConverter(
                progress_callback=self.update_progress,
                status_callback=self.update_status
            )
            output_path = converter.convert_video(video_path)
            self.update_status(f"Conversion complete: {output_path}")
        except Exception as e:
            self.update_status(f"Error: {str(e)}")
        finally:
            self.convert_btn.disabled = False
    
    def update_progress(self, value):
        self.progress_bar.value = value
    
    def update_status(self, message):
        self.status_label.text = message

class VideoConverter:
    def __init__(self, progress_callback=None, status_callback=None):
        self.progress_callback = progress_callback
        self.status_callback = status_callback
        self.interpreter = None
        self.load_model()
    
    def load_model(self):
        try:
            model_path = os.path.join(os.path.dirname(__file__), 'assets', 'animegan_v3.tflite')
            self.interpreter = tf.lite.Interpreter(model_path=model_path)
            self.interpreter.allocate_tensors()
            
            self.input_details = self.interpreter.get_input_details()
            self.output_details = self.interpreter.get_output_details()
            
            self.input_height = self.input_details[0]['shape'][1]
            self.input_width = self.input_details[0]['shape'][2]
            
            if self.status_callback:
                self.status_callback("Model loaded successfully")
        except Exception as e:
            if self.status_callback:
                self.status_callback(f"Failed to load model: {str(e)}")
    
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
        if not self.interpreter:
            raise Exception("Model not loaded")
        
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
            self.status_callback(f"Processing video with {total_frames} frames")
        
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            processed_frame = self.process_frame(frame)
            processed_frame = cv2.resize(processed_frame, (width, height))
            
            out.write(processed_frame)
            
            frame_count += 1
            if self.progress_callback:
                progress = int((frame_count / total_frames) * 100)
                self.progress_callback(progress)
        
        cap.release()
        out.release()
        
        return output_path

def determine_optimal_threads():
    import multiprocessing
    cores = multiprocessing.cpu_count()
    return max(1, min(cores - 1, 4))

if __name__ == '__main__':
    os.environ['NUMEXPR_MAX_THREADS'] = str(determine_optimal_threads())
    AnimeGANApp().run()
