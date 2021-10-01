from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread,Qt,pyqtSlot,pyqtSignal
from PyQt5.QtGui import QImage
import config
from PIL import Image
import cv2,time

class TableWidgetImgs(QtWidgets.QLabel):
    tbl=QtWidgets.QTableWidget
    def __init__(self,tbl,pixmap):
        super().__init__()
        TableWidgetImgs.tbl=tbl
        w=TableWidgetImgs.tbl.width()-config.tbl_face_dec
        self.setMinimumWidth(w)
        self.setMinimumHeight(w)
        self.setMaximumWidth(w)
        self.setMaximumHeight(w)
        self.setAlignment(Qt.AlignCenter)
        self.setPixmap(pixmap)


class TableWidgetPelaks(QtWidgets.QLabel):
    tbl=QtWidgets.QTableWidget
    def __init__(self,tbl,pixmap):
        super().__init__()
        TableWidgetPelaks.tbl=tbl
        #w=TableWidgetPelaks.tbl.width()
        #self.setMinimumWidth(w)
        #self.setMinimumHeight(w)
        #self.setMaximumWidth(w)
        #self.setMaximumHeight(w)
        self.setAlignment(Qt.AlignCenter)
        self.setPixmap(pixmap)


class TableWidgetImgSearchFace(QtWidgets.QLabel):
    tbl=QtWidgets.QTableWidget
    def __init__(self,path,tbl,j):
        super().__init__()
        w=80
        TableWidgetImgSearchFace.tbl=tbl
        TableWidgetImgSearchFace.tbl.setColumnWidth(1,w)
        TableWidgetImgSearchFace.tbl.setRowHeight(j,w)
        self.setMinimumWidth(w-10)
        self.setMinimumHeight(w-10)
        self.setMaximumWidth(w-10)
        self.setMaximumHeight(w-10)
        self.setAlignment(Qt.AlignCenter)
        picmap=QtGui.QPixmap(path)
        self.setPixmap(picmap)

class TableWidgetImgShowSourceImg(QtWidgets.QPushButton):
    def __init__(self,path):
        super().__init__()
        self.path=path
        self.setText("مشاهده تصویر اصلی")
        self.clicked.connect(self.click_btn)
        self.setMaximumHeight(50)

    def click_btn(self):
        img = Image.open(self.path)
        img.show()

class TableWidgetImgShowVideo(QtWidgets.QPushButton):
    def __init__(self,path):
        super().__init__()
        self.path=path
        self.setText("مشاهده ویدئو")
        self.clicked.connect(self.click_btn)

    def click_btn(self):
        wait=int(1000/self.detect_FPS(self.path))
        cap=cv2.VideoCapture(self.path)
        while True:
            ret,frame=cap.read()
            cv2.imshow("Video Playing...",frame)
            cv2.waitKey(wait)

        cap.release()
        cv2.destroyAllWindows()



    @staticmethod
    def detect_FPS(path):
        video = cv2.VideoCapture(path);
        # Find OpenCV version
        (major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')
        # With webcam get(CV_CAP_PROP_FPS) does not work.
        # Let's see for ourselves.
        if int(major_ver)  < 3 :
            fps = video.get(cv2.cv.CV_CAP_PROP_FPS)
            #print "Frames per second using video.get(cv2.cv.CV_CAP_PROP_FPS): {0}".format(fps)
        else :
            fps = video.get(cv2.CAP_PROP_FPS)
            #print "Frames per second using video.get(cv2.CAP_PROP_FPS) : {0}".format(fps)


        # Number of frames to capture
        num_frames = 120
        #print("Capturing {0} frames".format(num_frames))

        # Start time
        start = time.time()

        # Grab a few frames
        for i in range(0, num_frames) :
            ret, frame = video.read()


        # End time
        end = time.time()

        # Time elapsed
        seconds = end - start
        #print("Time taken : {0} seconds".format(seconds))

        # Calculate frames per second
        fps  = num_frames / seconds
        #print("Estimated frames per second : {0}".format(fps))

        # Release video
        video.release()
        print(fps)
        return fps