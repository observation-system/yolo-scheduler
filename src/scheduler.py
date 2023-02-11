import subprocess
from subprocess import PIPE

def detect_yolo():
    proc = subprocess.run(['python', 'yolov5/detect.py'], stdout=PIPE, stderr=PIPE)
    proc_str = proc.stdout.decode('utf-8').split()
    proc_int = [int(i) for i in proc_str]
    print(proc_int)

detect_yolo() 