import os
import urllib.request
import zipfile
import hashlib
import argparse

MODEL_URL = "https://github.com/TachibanaYoshino/AnimeGANv3/releases/download/v1.1.0/AnimeGANv3_Hayao_36.tflite"
MODEL_HASH = "93ef64715d9afadab55d25be92408ed0a18a08e3bab01f398e0c6e5a686ba786"

def download_file(url, output_path):
    try:
        urllib.request.urlretrieve(url, output_path)
        return True
    except Exception as e:
        print(f"Error downloading file: {e}")
        return False

def verify_hash(file_path, expected_hash):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    file_hash = sha256_hash.hexdigest()
    return file_hash == expected_hash

def ensure_model_exists():
    os.makedirs("assets", exist_ok=True)
    model_path = os.path.join("assets", "animegan_v3.tflite")
    
    if os.path.exists(model_path):
        if verify_hash(model_path, MODEL_HASH):
            print("Model file already exists and hash is verified.")
            return True
        else:
            print("Model file exists but hash doesn't match. Redownloading...")
            os.remove(model_path)
    
    print(f"Downloading model from {MODEL_URL}...")
    if download_file(MODEL_URL, model_path):
        if verify_hash(model_path, MODEL_HASH):
            print("Model downloaded and verified successfully.")
            return True
        else:
            print("Downloaded model failed hash verification.")
            return False
    else:
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download AnimeGANv3 TFLite model")
    args = parser.parse_args()
    
    if ensure_model_exists():
        print("Model is ready to use.")
    else:
        print("Failed to download or verify the model.")
