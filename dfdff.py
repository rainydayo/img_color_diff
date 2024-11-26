import firebase_admin
from firebase_admin import credentials, db
import cv2
import numpy as np
import base64
import schedule
import time

cred = credentials.Certificate("hopesmartbin-firebase-adminsdk-zw7ni-04f06cd57a.json")
firebase_admin.initialize_app(cred, {"databaseURL": "https://hopesmartbin-default-rtdb.asia-southeast1.firebasedatabase.app/"})

def fetch_base64_data():
    ref = db.reference("foodCurr/state")
    base64_string = ref.get()
    return base64_string

def decode_base64_image(base64_string):
    img_data = base64.b64decode(base64_string)
    np_arr = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    return img

def process_image(img):
    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower_green = np.array([0, 52, 0])
    upper_green = np.array([179, 255, 255])
    mask = cv2.inRange(hsv_img, lower_green, upper_green)
    green_pixels = cv2.countNonZero(mask)
    total_pixels = img.shape[0] * img.shape[1]
    percentage = (green_pixels / total_pixels) * 100
    print("Percentage: {:.2f}%".format(percentage))

    percentage_ref = db.reference("food/state")
    percentage_ref.set(int(percentage))

    # cv2.imshow('Green Mask', mask)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

def task():
    try:
        base64_data = fetch_base64_data()
        img = decode_base64_image(base64_data)
        process_image(img)
    except Exception as e:
        print(f"Error: {e}")

schedule.every().minute.at(":30").do(task)

if __name__ == "__main__":
    print("Scheduler is running. Press Ctrl+C to exit.")
    while True:
        schedule.run_pending()
        time.sleep(1)
