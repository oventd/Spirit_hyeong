import numpy as np
import sys
import cv2
try:
    from PySide6.QtCore import Qt, QTimer
    from PySide6.QtGui import QImage, QPixmap
    from PySide6.QtWidgets import QLabel
except:
    from PySide2.QtCore import Qt, QTimer
    from PySide2.QtGui import QImage, QPixmap
    from PySide2.QtWidgets import QLabel


class VideoPlayer(QLabel):
    def __init__(self, img_path):
        super().__init__()


        # 비디오 캡처 객체 (동영상 파일 경로 설정)
        self.cap = cv2.VideoCapture(img_path)
        

        # 비디오가 열렸는지 확인
        if not self.cap.isOpened():
            print("Error: Unable to open video.")
            sys.exit()

        # 타이머 설정 (프레임 업데이트)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(1000 / 24)  # 30fps로 업데이트
        self.save_frame()

    def save_frame(self):
        ret, frame = self.cap.read()

        if ret:
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            return rgb_image



    def update_frame(self):
        ret, frame = self.cap.read()

        if ret:
            # BGR에서 RGB로 변환
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # QImage로 변환
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qimg = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)

            # QPixmap으로 변환하여 QLabel에 설정
            pixmap = QPixmap.fromImage(qimg).scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)

            
            self.setPixmap(pixmap)

        else:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # 동영상 끝나면 처음으로 돌아가기

    def closeEvent(self, event):
        self.cap.release()  # 비디오 캡처 객체 해제
        event.accept()

class VideoToImageExtractor(QLabel):
    def __init__(self, img_path):
        super().__init__()


        # 비디오 캡처 객체 (동영상 파일 경로 설정)
        self.cap = cv2.VideoCapture(img_path)

    def save_frame(self):
        ret, frame = self.cap.read()
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image_array = np.array(rgb_image, dtype=np.uint8)

     
        height, width, channels = image_array.shape
        bytes_per_line = channels * width
        qimg = QImage(image_array.data, width, height, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)
        return pixmap
 





   