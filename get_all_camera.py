import cv2
import numpy as np
import config
import threading,time

class get_all_camera():
    def __init__(self,w,h):
        self.w=w
        self.h=h
        self.DATA=""
        none_frame=cv2.imread(config.none_img)
        none_frame=cv2.resize(none_frame,(self.w,self.h))
        self.frame1=none_frame
        self.frame2=none_frame
        self.frame3=none_frame
        self.frame4=none_frame
        self.stop=False

    def update_w_h(self,w,h):
        self.w=w
        self.h=h
        none_frame=cv2.imread(config.none_img)
        none_frame=cv2.resize(none_frame,(self.w,self.h))
        self.frame1=none_frame
        self.frame2=none_frame
        self.frame3=none_frame
        self.frame4=none_frame

    def run(self):
        self.cap1=cv2.VideoCapture(config.sourc1)
        self.cap2=cv2.VideoCapture(config.sourc2)
        self.cap3=cv2.VideoCapture(config.sourc3)
        self.cap4=cv2.VideoCapture(config.sourc4)
        #threading.Thread(target=self.start1).start()
        #threading.Thread(target=self.start2).start()
        #threading.Thread(target=self.start3).start()
        threading.Thread(target=self.start4).start()
        time.sleep(1)
        threading.Thread(target=self.mix_frame).start()

    def start1(self):
        while self.stop==False:
            ret,frame1=self.cap1.read()
            self.frame1=cv2.resize(frame1,(self.w,self.h))
            cv2.waitKey(1)

    def start2(self):
        while self.stop==False:
            ret,frame2=self.cap2.read()
            self.frame2=cv2.resize(frame2,(self.w,self.h))
            cv2.waitKey(1)

    def start3(self):
        while self.stop==False:
            ret,frame3=self.cap3.read()
            self.frame3=cv2.resize(frame3,(self.w,self.h))
            cv2.waitKey(1)

    def start4(self):
        while self.stop==False:
            ret,frame4=self.cap4.read()
            self.frame4=cv2.resize(frame4,(self.w,self.h))
            cv2.waitKey(1)

    def mix_frame(self):
        while self.stop==False:
            row0=np.concatenate((self.frame1,self.frame2),axis=1)
            row1=np.concatenate((self.frame3,self.frame4),axis=1)
            frame=np.concatenate((row0,row1),axis=0)
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), config.qu]
            if config.is_q==1:
                ret,frame=cv2.imencode('.jpg', frame,encode_param)
            elif config.is_q==0:
                ret,frame=cv2.imencode('.jpg', frame)
            frame=frame.tobytes()
            self.DATA=frame


"""if __name__=="__main__":
    import codecs
    import time
    cl=get_all_camera(800,600)
    cl.run()
    time.sleep(5)
    while True:
        with open('data.json','w') as file:
            file.write(str(cl.DATA))
        print(len(str(cl.DATA)))

        time.sleep(0.050)"""