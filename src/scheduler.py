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

def update_databese(spot_data, detect_data):
    cursor = CONNECTION.cursor(dictionary=True)
    
    for i in range(len(spot_data)):
        day_list = spot_data[i]["spots_day_count"].split(",")
        day_list.append(detect_data[i])
        cursor.execute("UPDATE spots SET spots_count = '%s' WHERE id = %s" % (detect_data[i], spot_data[i]["id"]))
        
        if len(day_list) >= 25:
            week_count = spot_data[i]["spots_week_count"] + "," + str(detect_data[i])
            month_count = spot_data[i]["spots_month_count"] + "," + str(detect_data[i])
            update_week_count = week_count.split(",")
            update_month_count = month_count.split(",")
            update_week_count.pop(0)
            update_month_count.pop(0)
            week_count = ",".join(update_week_count)
            month_count = ",".join(update_month_count)
            cursor.execute("UPDATE spots SET spots_day_count = '%s' WHERE id = %s" % (detect_data[i], spot_data[i]["id"]))
            cursor.execute("UPDATE spots SET spots_week_count = '%s' WHERE id = %s" % (week_count, spot_data[i]["id"]))
            cursor.execute("UPDATE spots SET spots_month_count = '%s' WHERE id = %s" % (month_count, spot_data[i]["id"]))            
        else:
            day_count = spot_data[i]["spots_day_count"] + "," + str(detect_data[i])
            cursor.execute("UPDATE spots SET spots_day_count = '%s' WHERE id = %s" % (day_count, spot_data[i]["id"]))
    
    CONNECTION.commit()
    cursor.close()

def extract_image(spot_data):
    dir_path = "yolov5/data/images/"
    basename = "camera_capture_cycle"
    ext = "jpg"

    if os.path.isdir(dir_path):
        shutil.rmtree(dir_path)

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
    dir_path = "yolov5/runs/"

    if os.path.isdir(dir_path):
        shutil.rmtree(dir_path)

    proc = subprocess.run(["python", "yolov5/detect.py"], stdout=PIPE, stderr=PIPE)
    proc_data = proc.stdout.decode("utf-8").split()
    
    return proc_data

def main():
    spot_data = select_databese()
    extract_image(spot_data)
    detect_data = detect_image()
    update_databese(spot_data, detect_data)

main()