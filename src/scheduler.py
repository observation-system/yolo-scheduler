import os
import shutil
import pafy
import cv2
import datetime
import subprocess
from subprocess import PIPE
import mysql.connector
from dotenv import load_dotenv

load_dotenv()
CONNECTION = mysql.connector.connect(
    host = os.getenv("MYSQL_HOST"),
    user = os.getenv("MYSQL_USER"),
    password = os.getenv("MYSQL_PASSWORD"),
    database = os.getenv("MYSQL_DATABASE"))

def select_databese():
    cursor = CONNECTION.cursor(dictionary=True)
    cursor.execute("SELECT * FROM spots")
    spot_data = cursor.fetchall()
    CONNECTION.commit()
    cursor.close()

    return spot_data

def extract_image(spot_data):
    dir_path = 'yolov5/data/images/'
    basename = 'camera_capture_cycle'
    ext = 'jpg'

    if os.path.isdir('yolov5/data/images/'):
        shutil.rmtree('yolov5/data/images/')

    for i in range(len(spot_data)):
        video = pafy.new(spot_data[i]["spots_url"])
        best = video.getbest(preftype="mp4")
        cap = cv2.VideoCapture(best.url)
            
        if not cap.isOpened():
            return

        os.makedirs(dir_path, exist_ok=True)
        base_path = os.path.join(dir_path, basename)
        ret, frame = cap.read()
        cv2.imwrite('{}_{}.{}'.format(base_path, datetime.datetime.now().strftime('%Y%m%d%H%M%S%f'), ext), frame)

def detect_image():
    proc = subprocess.run(["python", "yolov5/detect.py"], stdout=PIPE, stderr=PIPE)
    proc_str = proc.stdout.decode("utf-8").split()
    proc_int = [int(i) for i in proc_str]
    shutil.rmtree("yolov5/runs")
    print(proc_int)

def main():
    spot_data = select_databese()
    extract_image(spot_data)
    detect_image()

main()