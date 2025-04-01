```python
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.image import Image

import os
import cv2
import numpy as np
import tensorflow as tf
import threading
import time

class AnimeConverterApp(App):
    def build(self):
        self.title = 'Video to Anime Converter'
        self.model = None
        self.converting = False
        
        # Main layout
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Title
        title = Label(text='Video to Anime Converter', size_hint=(1, 0.1), font_size='20sp')
        layout.add_widget(title)
        
        # File chooser
        self.file_chooser = FileChooserListView(filters=['*.mp4', '*.avi', '*.mov'], 
                                               size_hint=(1, 0.5))
        layout.add_widget(self.file_chooser)
        
        # Preview image
        self.preview = Image(size_hint=(1, 0.3))
        layout.add_widget(self.preview)
        
        # Progress bar
        self.progress = ProgressBar(max=100, size_hint=(1, 0.1))
        layout.add_widget(self.progress)
        
        # Status label
        self.status = Label(text='Select a video file', size_hint=(1, 0.1))
        layout.add_widget(self.status)
        
        # Buttons layout
        btn_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.1), spacing=10)
        
        # Convert button
        self.convert_btn = Button(text='Convert', on_press=self.start_conversion)
        btn_layout.add_widget(self.convert_btn)
        
        # Cancel button
        self.cancel_btn = Button(text='Cancel', on_press=self.cancel_conversion, disabled=True)
        btn_layout.add_widget(self.cancel_btn)
        
        layout.add_widget(btn_layout)
        
        # Load the TFLite model
        Clock.schedule_once(self.load_model, 1)
        
        return layout
    
    def load_model(self, dt):
        self.status.text = 'Loading model...'
        
        def load():
            try:
                app_dir = self.user_data_dir
                model_path = os.path.join(app_dir, 'animegenv3.tflite')
                
                if not os.path.exists(model_path):
                    self.status.text = 'Model not found!'
                    return
                
                self.interpreter = tf.lite.Interpreter(model_path=model_path)
                self.interpreter.allocate_tensors()
                self.input_details = self.interpreter.get_input_details()
                self.output_details = self.interpreter.get_output_details()
                
                Clock.schedule_once(lambda dt: setattr(self.status, 'text', 'Model loaded successfully!'))
            except Exception as e:
                Clock.schedule_once(lambda dt: setattr(self.status, 'text', f'Error loading model: {str(e)}'))
        
        threading.Thread(target=load).start()
    
    def start_conversion(self, instance):
        if not self.file_chooser.selection:
            self.status.text = 'Please select a video file first!'
            return
        
        if self.interpreter is None:
            self.status.text = 'Model not loaded yet. Please wait.'
            return
        
        self.video_path = self.file_chooser.selection[0]
        self.converting = True
        self.convert_btn.disabled = True
        self.cancel_btn.disabled = False
        
        threading.Thread(target=self.convert_video).start()
    
    def convert_video(self):
        try:
            self.status.text = 'Processing video...'
            cap = cv2.VideoCapture(self.video_path)
            
            if not cap.isOpened():
                Clock.schedule_once(lambda dt: setattr(self.status, 'text', 'Error opening video file!'))
                self.reset_ui()
                return
            
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            output_path = os.path.splitext(self.video_path)[0] + '_anime.mp4'
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            frame_count = 0
            
            while cap.isOpened() and self.converting:
                ret, frame = cap.read()
                
                if not ret:
                    break
                
                anime_frame = self.process_frame(frame)
                out.write(anime_frame)
                
                frame_count += 1
                progress = int(100 * frame_count / total_frames)
                Clock.schedule_once(lambda dt, p=progress: self.update_progress(p))
                
                if frame_count % 10 == 0:
                    Clock.schedule_once(lambda dt, f=anime_frame: self.update_preview(f))
            
            cap.release()
            out.release()
            
            if self.converting:
                Clock.schedule_once(lambda dt: setattr(self.status, 'text', f'Conversion completed! Saved to: {output_path}'))
            
            self.reset_ui()
            
        except Exception as e:
            Clock.schedule_once(lambda dt: setattr(self.status, 'text', f'Error: {str(e)}'))
            self.reset_ui()
    
    def reset_ui(self):
        Clock.schedule_once(lambda dt: setattr(self.convert_btn, 'disabled', False))
        Clock.schedule_once(lambda dt: setattr(self.cancel_btn, 'disabled', True))
        self.converting = False

if __name__ == '__main__':
    AnimeConverterApp().run()
