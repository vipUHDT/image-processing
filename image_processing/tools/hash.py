import hashlib
from typing import Optional

def hashFile(file_path: str, algorithm: str ="md5", chunk_size: int = 8192) -> str:
    h = hashlib.new(algorithm)

    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(chunk_size), b''):
            h.update(chunk)

    return h.hexdigest()

if __name__ == "__main__":
    print(hashFile("/Users/plegaspi/Documents/Programming/UHDT/image-processing-validation/yolo11n.pt"))