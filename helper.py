import cv2
import threading
import os.path
import struct
import socket
import pickle
import datetime

class Helper:
    #face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    face_cascade = cv2.CascadeClassifier('lbpcascade_frontalface.xml')
    kol=0
    #eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')
    client_socket=""
    client_socket_runing=False
    
    @staticmethod
    def detect(img):
        gray=cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = Helper.face_cascade.detectMultiScale(gray, 1.3, 5)
        for (x,y,w,h) in faces:
            Helper.kol+=1
            #cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
            crop= img[ y:h+y,x:w+x]
            Helper.run_send_socket(crop)
            cv2.imshow("croped: ",crop)
            #print(str(Helper.kol))
            """roi_gray = gray[y:y+h, x:x+w]
            roi_color = img[y:y+h, x:x+w]

            eyes = Helper.eye_cascade.detectMultiScale(roi_gray)
            for (ex,ey,ew,eh) in eyes:
                print("bb")
                cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)
                cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)"""


    @staticmethod
    def run_detect(img):
        th=threading.Thread(target=Helper.detect(img),args=())
        th.daemon=True
        th.start()



    @staticmethod
    def check_every_frame(file_path,count):
        index=0
        if(os.path.isfile(file_path)):
            file=open(file_path,"r")
            index=file.read()
        else:
            file=open(file_path,"w+")
            file.write("0")
            file.close()
        if(int(index)>count):
            file=open(file_path,"w+")
            file.write("0")
            file.close()
            #print("yes"+str(index)+" > "+str(count))
            return True
        else:
            index=int(index)+1
            file=open(file_path,"w+")
            file.write(str(index))
            file.close()
            #print("no"+str(index)+" < "+str(count))
            return False

    @staticmethod
    def send_socket(frame):
        #connection = Helper.client_socket.makefile('wb')
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
        result, frame = cv2.imencode('.jpg', frame, encode_param)
        data = pickle.dumps(frame, 0)
        size = len(data)
        Helper.client_socket.sendall(struct.pack(">L", size) + data)


    @staticmethod
    def run_send_socket(frame):
        th=threading.Thread(target=Helper.send_socket,kwargs={'frame':frame})
        th.daemon=True
        th.start()

    @staticmethod
    def init_socket():
        if(Helper.client_socket_runing==False):
            Helper.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            Helper.client_socket.connect(('192.168.1.8', 8485))
            Helper.client_socket_runing=True

    @staticmethod
    def close_socket():
        if(Helper.client_socket_runing==True):
            Helper.client_socket.close()
            Helper.client_socket=False

    @staticmethod
    def resize_img_file(filename,newx,newy):
        oriimage = cv2.imread(filename)
        newimage = cv2.resize(oriimage,(newx,newy))
        return newimage

    @staticmethod
    def resize_img_frame(frame,newx,newy):
        newimage = cv2.resize(frame,(newx,newy))
        return newimage

    @staticmethod
    def scale_img_file(filename,fx_scale,fy_scale):
        image = cv2.imread(filename)
        img = cv2.resize(image, (0,0), fx=fx_scale, fy=fy_scale)
        return img

    @staticmethod
    def scale_img_frame(frame,fx_scale,fy_scale):
        img = cv2.resize(frame, (0,0), fx=fx_scale, fy=fy_scale)
        return img

    @staticmethod
    def get_current_milisec():
        import time
        millis = int(round(time.time() * 1000))
        return millis

    @staticmethod
    def get_time_diff_execute(start,end):
        delta=end-start
        sec=delta.total_seconds()
        mili=int(delta.total_seconds()*1000)
        return sec,mili