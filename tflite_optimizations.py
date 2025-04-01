import tensorflow as tf

class TFLiteOptimizer:
    @staticmethod
    def optimize_model(input_model_path, output_model_path):
        converter = tf.lite.TFLiteConverter.from_saved_model(input_model_path)
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
        converter.target_spec.supported_types = [tf.float16]
        tflite_quant_model = converter.convert()
        
        with open(output_model_path, 'wb') as f:
            f.write(tflite_quant_model)
        
        return output_model_path
    
    @staticmethod
    def apply_delegate(interpreter, use_gpu=True, num_threads=None):
        if use_gpu and tf.test.is_gpu_available():
            try:
                interpreter.set_gpu_delegate()
                return True
            except:
                pass
        
        if num_threads is not None:
            try:
                interpreter.set_num_threads(num_threads)
                return True
            except:
                pass
        
        return False
