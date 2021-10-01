from kivy.app import App
import time
from kivy.uix.image import Image
from kivy.core.window import Window
import cv2
from kivy.graphics.texture import Texture
import threading
from popup import PopUp
from dateutil import parser
import config
import base64
import numpy as np
import CustomTime
import os
from queue import Queue
from Encoding import encrypt_cisco
from kivy.uix.screenmanager import ScreenManager,Screen
from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
import arabic_reshaper
import bidi.algorithm
import datetime
import socket
from messagebox import MessageBox
from CustomVideoPlayer import CustomVideoPlayer
import translate
from initConfig import initConfig
import traceback
import re
from generate_key import GenerateKey
import subprocess
from functools import partial
from kivy.uix.popup import Popup

class VideoPlayerNoCrl(Image):
    def __init__(self, **kwargs):
        super(VideoPlayerNoCrl, self).__init__(**kwargs)
        self.start()
    def pr1(self):
        Clock.schedule_interval(self.update,1.0/30)

    def start(self):
        self.capture=cv2.VideoCapture("Assets/video/1.mp4")
        th1=threading.Thread(target=self.pr1)
        th1.daemon=True
        th1.start()

    def update(self,dt):
        ret,frame=self.capture.read()
        if ret:
            frame=cv2.resize(frame,(self.width,self.height))
            texture = self.texture
            w, h = frame.shape[1], frame.shape[0]
            if not texture or texture.width != w or texture.height != h:
                self.texture = texture = Texture.create(size=(w, h))
                texture.flip_vertical()
            texture.blit_buffer(frame.tobytes(), colorfmt='bgr')
            self.canvas.ask_update()
        else:
            time.sleep(2)
            Clock.unschedule(self.update)
            self.source="none.jpg"
            Window.maximize()
            MainKivyApp.my_screenmanager.current="KivyShowVideoFrames"

class DataViewItem():

    def get_layout(self,crp_img,org_img,date_time,camera_number,camera_name):
        self.layout=BoxLayout()
        self.layout.orientation="vertical"
        self.layout.size_hint_x=1
        self.layout.spacing=8
        self.layout.padding=20

        self.cam_name=Label()
        self.cam_name.size_hint_x=1
        self.cam_name.size_hint_y=0.15
        self.cam_name.text=MainKivyApp.app.init_persian_text(camera_name)
        self.cam_name.font_name="Assets/Fonts/BKoodakBold.ttf"
        self.cam_name.font_size=18
        self.layout.add_widget(self.cam_name)

        self.img=Image()
        self.img.size_hint_x=1
        self.img.size_hint_y=0.7
        self.img.source=crp_img
        self.layout.add_widget(self.img)

        self.date_time=Label()
        self.date_time.size_hint_x=1
        self.date_time.size_hint_y=0.15
        self.date_time.text=date_time
        self.layout.add_widget(self.date_time)

        self.btn=Button(on_press=lambda *args: self.clicked_btn(self.btn))
        self.btn.font_name="Assets/Fonts/BKoodakBold.ttf"
        self.btn.size_hint_x=1
        self.btn.size_hint_y=0.20
        self.btn.id=org_img
        self.btn.text=MainKivyApp.app.init_persian_text("مشاهده تصویر اصلی")
        self.layout.add_widget(self.btn)

        return self.layout

    def clicked_btn(self,instance):
        org_img=instance.id
        frame=cv2.imread(org_img)
        frame=cv2.resize(frame,config.size_show_img_in_history)
        name=os.getcwd()+"/"+org_img
        cv2.imshow(name,frame)

class IconButtonZoom(ButtonBehavior, Image):

    def __init__(self, angle=0, **kwargs):
        super(IconButtonZoom, self).__init__(**kwargs)

    def on_press(self):
        print("from on_press Zoom")

class IconButtonArrow(ButtonBehavior, Image):

    def __init__(self, angle=0, **kwargs):
        super(IconButtonArrow, self).__init__(**kwargs)

    def on_press(self):
        print("from on_press Arrow")

class IconButtonFullScreen(ButtonBehavior, Image):
    def __init__(self, angle=0, **kwargs):
        super(IconButtonFullScreen, self).__init__(**kwargs)

    def on_press(self):
        try:
            if self.id_id.startswith("full_screen"):
                if self.id_id=="full_screen1":
                    ret=1
                    MainKivyApp.my_screenmanager.ids.qrcam.handle_full_screen_frame(ret)
                elif self.id_id=="full_screen2":
                    ret=2
                    MainKivyApp.my_screenmanager.ids.qrcam.handle_full_screen_frame(ret)
                elif self.id_id=="full_screen3":
                    ret=3
                    MainKivyApp.my_screenmanager.ids.qrcam.handle_full_screen_frame(ret)
                elif self.id_id=="full_screen4":
                    ret=4
                    MainKivyApp.my_screenmanager.ids.qrcam.handle_full_screen_frame(ret)
        except:
            pass

class KivyCamera(Image):
    def init_data(self):
        try:
            self.flg_video=True
            self.out1=cv2.VideoWriter
            self.out2=cv2.VideoWriter
            self.out3=cv2.VideoWriter
            self.out4=cv2.VideoWriter
            self.index_detect_face_pelak=1
            self.q_show=Queue()
            self.FRAME_SHOW=b""
            self.q_save=Queue()
            self.q_detect=Queue()
            self.th_start=True
            self.wait=0.020
            self.i=0
            self.flg_add_face=False
            self.flg_add_person=False
            self.flg_add_pelak=False
            HOST = MainKivyApp.conf.get_update_config('sender_ip')
            PORT = int(MainKivyApp.conf.get_update_config('port_rec_video_frame'))
            self.ip_port=(HOST,PORT)
            self.buf_size=1024*60
            self.w=config.def_width
            self.h=config.def_height
            none_frame=cv2.imread(config.img_none)
            self.none_frame=cv2.resize(none_frame,(config.def_width,config.def_height))
            self.stop_tcp=False
            self.stop_rec_data=False
            self.ip_port_tcp=(config.reciver_ip,config.port_rec_detect_frame)
            self.socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket_tcp.bind(self.ip_port_tcp)
            self.socket_tcp.listen()
            self.show_tak_frame=0
            self.show_camera=int(MainKivyApp.conf.get_update_config('show_camera'))
            self.NEW_FRAME_TIME=datetime.datetime.now()
            self.LAST_FRAME_TIME=datetime.datetime.now()
            self.queue_face=Queue()
            self.queue_pelak=Queue()
            self.queue_person=Queue()
            self.soojeh_name=MainKivyApp.conf.get_update_config('soojeh_name')
            self.camera_name1=MainKivyApp.conf.get_update_config('camera_name_1').split('::@@::')[1]
            self.camera_name2=MainKivyApp.conf.get_update_config('camera_name_2').split('::@@::')[1]
            self.camera_name3=MainKivyApp.conf.get_update_config('camera_name_3').split('::@@::')[1]
            self.camera_name4=MainKivyApp.conf.get_update_config('camera_name_4').split('::@@::')[1]
            self.LAST_TIME_SAVE_VIDEO=datetime.datetime.now()
            self.START_TIME_SAVE_VIDEO=datetime.datetime.now()
            self.do_save_video_int=int(MainKivyApp.conf.get_update_config('do_save_video'))
        except:
            traceback.print_exc()
    def __init__(self, **kwargs):
        super(KivyCamera, self).__init__(**kwargs)
    def update_vars(self):
        self.soojeh_name=MainKivyApp.conf.get_update_config('soojeh_name')
        self.camera_name1=MainKivyApp.conf.get_update_config('camera_name_1').split('::@@::')[1]
        self.camera_name2=MainKivyApp.conf.get_update_config('camera_name_2').split('::@@::')[1]
        self.camera_name3=MainKivyApp.conf.get_update_config('camera_name_3').split('::@@::')[1]
        self.camera_name4=MainKivyApp.conf.get_update_config('camera_name_4').split('::@@::')[1]
        self.show_camera=int(MainKivyApp.conf.get_update_config('show_camera'))
        self.do_save_video_int=int(MainKivyApp.conf.get_update_config('do_save_video'))
    def pr1(self):
        Clock.schedule_interval(self.show_images,1.0/20)
        Clock.schedule_interval(self.show_person,1.0/2)
        Clock.schedule_interval(self.show_pelak,1.0/2)
        Clock.schedule_interval(self.show_face,1.0/2)
        if str(config.do_save_video) == "1":
            Clock.schedule_interval(self.save_video,1.0/16)


    def pr2(self):
        self.run()

    def pr3(self):
        self.init_tcp_socket()

    def start(self):
        th1=threading.Thread(target=self.pr1)
        #th1.daemon=True
        th2=threading.Thread(target=self.pr2)
        #th2.daemon=True
        th3=threading.Thread(target=self.pr3)
        #th3.daemon=True
        th1.start()
        th2.start()
        th3.start()


    def stop(self):
        try:
            title='ارتباط با فرستنده قطع شد'
            print("stop connection...")
            self.stop_rec_data=True
            MainKivyApp.reciveing_frames=False
            self.stop_tcp=True
            self.socket.close()
            self.socket_tcp.close()
            Clock.unschedule(self.show_images)
            Clock.unschedule(self.show_person)
            Clock.unschedule(self.show_pelak)
            Clock.unschedule(self.save_video)
            self.stop_video()
            messagebox=MessageBox('توجه',title,MainKivyApp.app)
            messagebox.show_message_box()
        except:
            print("error inside stop def")
            traceback.print_exc()


    def init_tcp_socket(self):
        while self.stop_tcp==False:
            try:
                conn, addr = self.socket_tcp.accept()
                client_ip=addr[0]
                client_port=addr[1]
                client_handler= threading.Thread(target=self.handle_connection,args=(conn,client_ip,client_port,))
                client_handler.start()
            except:
                self.socket_tcp.close()

    def handle_connection(self,conn,client_ip,client_port):
        source=""
        while True:
            data = conn.recv(self.buf_size)
            if not data:
                break
            source+=data.decode('utf-8')
        arr=source.split('aaaaa')
        if len(arr)==4:
            camera_number=arr[0]
            what=arr[1]
            crp=arr[2]
            org=arr[3]
            if camera_number=="1":
                pre_dir="media/"+self.soojeh_name+"/cam1/"
                camera_name=self.camera_name1
            elif camera_number=="2":
                pre_dir="media/"+self.soojeh_name+"/cam2/"
                camera_name=self.camera_name2
            elif camera_number=="3":
                pre_dir="media/"+self.soojeh_name+"/cam3/"
                camera_name=self.camera_name3
            elif camera_number=="4":
                pre_dir="media/"+self.soojeh_name+"/cam4/"
                camera_name=self.camera_name4

            enc_frm=base64.b64decode(crp)
            frame=MainKivyApp.encoding.decrypt(enc_frm)
            nparr=np.fromstring(frame, dtype='int8')
            crp=cv2.imdecode(nparr,cv2.IMREAD_COLOR)

            enc_frm=base64.b64decode(org)
            frame=MainKivyApp.encoding.decrypt(enc_frm)
            nparr=np.fromstring(frame, dtype='int8')
            org=cv2.imdecode(nparr,cv2.IMREAD_COLOR)

            if what=="plate":
                dir_org_pelak,dir_crp_pelak=self.check_dir_pelak(pre_dir)
                cur=CustomTime.get_j_time_micro()
                name_plate=dir_org_pelak+"/"+str(cur)+".jpg"
                name_crop=dir_crp_pelak+"/"+str(cur)+".jpg"
                cv2.imwrite(name_plate,org)
                cv2.imwrite(name_crop,crp)
                tmp_data=[name_plate,name_crop,camera_number,camera_name]
                self.queue_pelak.put(tmp_data)
                #self.show_pelak(name_crop,name_plate,camera_number,camera_name)

            elif what=="face":
                dir_org_face,dir_crp_face=self.check_dir_face(pre_dir)
                cur=CustomTime.get_j_time_micro()
                name_face=dir_org_face+"/"+str(cur)+".jpg"
                name_crop=dir_crp_face+"/"+str(cur)+".jpg"
                cv2.imwrite(name_face,org)
                cv2.imwrite(name_crop,crp)
                tmp_data=[name_face,name_crop,camera_number,camera_name]
                self.queue_face.put(tmp_data)
                #self.show_face(name_crop,name_face,camera_number,camera_name)
            elif what=="person":
                dir_org_person,dir_crp_person=self.check_dir_person(pre_dir)
                cur=CustomTime.get_j_time_micro()
                name_person=dir_org_person+"/"+str(cur)+".jpg"
                name_crop=dir_crp_person+"/"+str(cur)+".jpg"
                cv2.imwrite(name_person,org)
                cv2.imwrite(name_crop,crp)
                tmp_data=[name_person,name_crop,camera_number,camera_name]
                self.queue_person.put(tmp_data)
                #self.show_person(name_crop,name_person,camera_number,camera_name)

        conn.close()

    def init_and_connect_socket(self):
        ret=False
        data="abcdef".encode(encoding='utf-8')
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(self.ip_port)
        self.socket.sendall(data)
        while True:
            data = self.socket.recv(1024)
            data=data.decode()
            if(data=="rtxz" or data=="bqyu"):
                ret=True
                break
        self.socket.close()
        return ret

    def run(self):
        title="برقراری ارتباط با فرستنده"
        self.popup=PopUp(title,"pleas wait...",MainKivyApp.app)
        self.popup.show_popup_loading()
        self.flg_popup=True
        self.stop_video_save=False
        if(self.init_and_connect_socket()==True):
            timer=3
            print('connect after {} secondes'.format(timer))
            while timer>0:
                print(timer)
                time.sleep(1)
                timer-=1
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect(self.ip_port)
            self.socket.sendall(str("zxcvbn+"+str(self.show_camera)).encode())
            tmp=""
            start=config.start_spl
            end=config.end_spl
            frm_num=0
            while self.stop_rec_data==False:
                try:
                    data=self.socket.recv(self.buf_size)
                    rec=data.decode('utf-8')
                    tmp+=rec
                    if tmp.find(end) > -1:
                        frm_num+=1
                        spl=tmp.split(end)
                        source=spl[0].split(start)[1]
                        tmp=spl[1]
                        enc_frm=base64.b64decode(source)
                        frame=MainKivyApp.encoding.decrypt(enc_frm)
                        #nparr=np.frombuffer(frame,np.uint8)
                        nparr=np.fromstring(frame, dtype='int8')
                        frame=cv2.imdecode(nparr,cv2.IMREAD_COLOR)
                        #self.q_show.put(frame)
                        self.FRAME_SHOW=frame
                        self.NEW_FRAME_TIME=datetime.datetime.now()
                        #if(MainKivyApp.conf.get_update_config('do_save_video')=="1"):
                            #self.q_save.put(frame)
                except:
                    #traceback.print_exc()
                    continue


    def handle_full_screen_frame(self, ret):
        if self.show_tak_frame==0:
            self.show_tak_frame=ret
            self.hide_visible_frames()
        elif self.show_tak_frame>0:
            self.check_visible_frames()
            self.show_tak_frame=0

    def on_touch_down(self, touch):
        if touch.is_double_tap:
            if self.show_tak_frame>0:
                self.handle_full_screen_frame(None)


    def show_images(self,dt):
        #if(self.q_show.qsize()>0):
        cur=self.NEW_FRAME_TIME
        if cur>self.LAST_FRAME_TIME:
            try:
                if(self.flg_popup):
                    self.flg_popup=False
                    self.popup.close()
                    MainKivyApp.my_screenmanager.ids.parent_grid_tbls.opacity=1
                    self.check_visible_frames()
                #frame=self.q_show.get()
                frame=self.FRAME_SHOW

                if int(self.show_tak_frame)==0:
                    if int(self.show_camera)==1:
                        tm0=frame
                        tm1=np.concatenate((self.none_frame,self.none_frame),axis=1)
                        frame=np.concatenate((tm0,tm1),axis=0)
                    elif (self.show_camera)==2:
                        tm0=np.concatenate((self.none_frame,self.none_frame),axis=1)
                        tm1=frame
                        frame=np.concatenate((tm0,tm1),axis=0)
                    frame=cv2.resize(frame,(int(self.width),int(self.height)))

                elif int(self.show_tak_frame)>0:
                    self.hide_visible_frames()
                    if int(self.show_camera)==0:
                        if int(self.show_tak_frame)==1:
                            a="a"
                        elif int(self.show_tak_frame)==2:
                            a="b"
                        elif int(self.show_tak_frame)==3:
                            a="c"
                        elif int(self.show_tak_frame)==4:
                            a="d"

                    elif int(self.show_camera)==1 or int(self.show_camera)==2:
                        if int(self.show_tak_frame)==1:
                            a="a"
                        elif int(self.show_tak_frame)==2:
                            a="b"
                        elif int(self.show_tak_frame)==3:
                            a="a"
                        elif int(self.show_tak_frame)==4:
                            a="b"


                    az_x,ta_x,az_y,ta_y=self.crop_img_for_sections(a,config.def_width,config.def_height)
                    frame=frame[az_y:ta_y,az_x:ta_x]
                    frame=cv2.resize(frame,config.tak_frame_size)

                if len(frame):
                    texture = self.texture
                    w, h = frame.shape[1], frame.shape[0]
                    if not texture or texture.width != w or texture.height != h:
                        self.texture = texture = Texture.create(size=(w, h))
                        texture.flip_vertical()
                    texture.blit_buffer(frame.tobytes(), colorfmt='bgr')
                    self.canvas.ask_update()
            except:
                traceback.print_exc()
            self.LAST_FRAME_TIME=cur


    def stop_video(self):
        self.stop_video_save=True
        if self.flg_video==False:
            try:
                self.out1.release()
            except:
                print("camera 2 dont releas because dont start")
            try:
                self.out2.release()
            except:
                print("camera 2 dont releas because dont start")
            try:
                self.out3.release()
            except:
                print("camera 3 dont releas because dont start")
            try:
                self.out4.release()
            except:
                print("camera 4 dont releas because dont start")

            self.flg_video=True


    def check_for_save_video(self):
        diff=(self.LAST_TIME_SAVE_VIDEO-self.START_TIME_SAVE_VIDEO).total_seconds()
        if diff>3600:
            try:
                self.stop_video()
                self.START_TIME_SAVE_VIDEO=self.LAST_TIME_SAVE_VIDEO
                self.stop_video_save=False
            except:
                traceback.print_exc()

    def save_video(self,dt):

        if self.NEW_FRAME_TIME>self.LAST_FRAME_TIME:
            self.check_for_save_video()
            frame=self.FRAME_SHOW
            frame=cv2.resize(frame,(int(self.width),int(self.height)))
            az_x,ta_x,az_y,ta_y=self.crop_img_for_sections("a",int(self.width/2),int(self.height/2))
            frame1=frame[az_y:ta_y,az_x:ta_x]
            az_x,ta_x,az_y,ta_y=self.crop_img_for_sections("b",int(self.width/2),int(self.height/2))
            frame2=frame[az_y:ta_y,az_x:ta_x]
            az_x,ta_x,az_y,ta_y=self.crop_img_for_sections("c",int(self.width/2),int(self.height/2))
            frame3=frame[az_y:ta_y,az_x:ta_x]
            az_x,ta_x,az_y,ta_y=self.crop_img_for_sections("d",int(self.width/2),int(self.height/2))
            frame4=frame[az_y:ta_y,az_x:ta_x]
            if(self.flg_video):
                pre_dir1="media/"+self.soojeh_name+"/cam1/"
                pre_dir2="media/"+self.soojeh_name+"/cam2/"
                pre_dir3="media/"+self.soojeh_name+"/cam3/"
                pre_dir4="media/"+self.soojeh_name+"/cam4/"
                dir1=self.check_dir_video(pre_dir1)
                dir2=self.check_dir_video(pre_dir2)
                dir3=self.check_dir_video(pre_dir3)
                dir4=self.check_dir_video(pre_dir4)
                file_video1=dir1+"/"+CustomTime.get_j_time()+".avi"
                file_video2=dir2+"/"+CustomTime.get_j_time()+".avi"
                file_video3=dir3+"/"+CustomTime.get_j_time()+".avi"
                file_video4=dir4+"/"+CustomTime.get_j_time()+".avi"
                if self.show_camera==1 or self.show_camera==0:
                    self.out1=cv2.VideoWriter(file_video1,cv2.VideoWriter_fourcc('M','J','P','G'),15,(int(self.width/2),int(self.height/2)))
                    self.out2=cv2.VideoWriter(file_video2,cv2.VideoWriter_fourcc('M','J','P','G'),15,(int(self.width/2),int(self.height/2)))
                if self.show_camera==2 or self.show_camera==0:
                    self.out3=cv2.VideoWriter(file_video3,cv2.VideoWriter_fourcc('M','J','P','G'),15,(int(self.width/2),int(self.height/2)))
                    self.out4=cv2.VideoWriter(file_video4,cv2.VideoWriter_fourcc('M','J','P','G'),15,(int(self.width/2),int(self.height/2)))
                self.flg_video=False

            if self.do_save_video_int==1 and self.stop_video_save==False:
                if self.show_camera==1 or self.show_camera==0:
                    self.out1.write(frame1)
                    self.out2.write(frame2)
                if self.show_camera==2 or self.show_camera==0:
                    self.out3.write(frame3)
                    self.out4.write(frame4)
                self.LAST_TIME_SAVE_VIDEO=datetime.datetime.now()

    def detect_pre_dir(self,t):
        if t=="a":
            ret="media/"+self.soojeh_name+"/cam1/"
        elif t=="b":
            ret="media/"+self.soojeh_name+"/cam2/"
        elif t=="c":
            ret="media/"+self.soojeh_name+"/cam3/"
        elif t=="d":
            ret="media/"+self.soojeh_name+"/cam4/"
        return ret

    def crop_img_for_sections(self,t,ww,hh):
        w=ww
        h=hh
        ret=""
        if t == "a":
            az_x=0
            ta_x=int(w)
            az_y=0
            ta_y=int(h)
            ret= az_x,ta_x,az_y,ta_y
        elif t== "b":
            az_x=int(w)
            ta_x=int(w*2)
            az_y=0
            ta_y=int(h)
            ret= az_x,ta_x,az_y,ta_y
        elif t== "c":
            az_x=0
            ta_x=int(w)
            az_y=int(h)
            ta_y=int(h*2)
            ret= az_x,ta_x,az_y,ta_y
        elif t== "d":
            az_x=int(w)
            ta_x=int(w*2)
            az_y=int(h)
            ta_y=int(h*2)
            ret= az_x,ta_x,az_y,ta_y

        return ret

    def show_face(self,dt):
        if(self.queue_face.qsize()>0):
            arr=self.queue_face.get()
            name_face=arr[0]
            name_crop=arr[1]
            camera_number=arr[2]
            camera_name=arr[3]

            count=len(MainKivyApp.my_screenmanager.ids.data_grid_face.children)
            if(self.flg_add_face==False):
                if(count<config.count_tbl_face):
                    date_time=self.get_date_from_name(name_face,"faces")
                    cls=DataViewItem()
                    layout=cls.get_layout(name_crop,name_face,date_time,camera_number,camera_name)
                    MainKivyApp.my_screenmanager.ids.data_grid_face.add_widget(layout)
                elif(count>=config.count_tbl_face and self.flg_add_face==False ):
                    self.flg_add_face=True
                    self.index_show_face=count-1
                    cam_name=MainKivyApp.my_screenmanager.ids.data_grid_face.children[self.index_show_face].children[3]
                    cam_name.text=MainKivyApp.app.init_persian_text(camera_name)
                    img=MainKivyApp.my_screenmanager.ids.data_grid_face.children[self.index_show_face].children[2]
                    img.source=name_crop
                    img.reload()
                    text=self.get_date_from_name(name_face,"faces")
                    date_time=MainKivyApp.my_screenmanager.ids.data_grid_face.children[self.index_show_face].children[1]
                    date_time.text=text
                    MainKivyApp.my_screenmanager.ids.data_grid_face.children[self.index_show_face].children[0].id=name_face
                    self.index_show_face-=1
            elif(self.flg_add_face==True):
                if(self.index_show_face<0):
                    self.index_show_face=count-1
                cam_name=MainKivyApp.my_screenmanager.ids.data_grid_face.children[self.index_show_face].children[3]
                cam_name.text=MainKivyApp.app.init_persian_text(camera_name)
                img=MainKivyApp.my_screenmanager.ids.data_grid_face.children[self.index_show_face].children[2]
                img.source=name_crop
                img.reload()
                text=self.get_date_from_name(name_face,"faces")
                date_time=MainKivyApp.my_screenmanager.ids.data_grid_face.children[self.index_show_face].children[1]
                date_time.text=text
                MainKivyApp.my_screenmanager.ids.data_grid_face.children[self.index_show_face].children[0].id=name_face
                self.index_show_face-=1



    def show_pelak(self,dt):
        if(self.queue_pelak.qsize()>0):
            arr=self.queue_pelak.get()
            name_pelak=arr[0]
            name_crop=arr[1]
            camera_number=arr[2]
            camera_name=arr[3]
            #frame=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
            count=len(MainKivyApp.my_screenmanager.ids.data_grid_pelak.children)
            if(self.flg_add_pelak==False):
                if(count<config.count_tbl_pelak):
                    date_time=self.get_date_from_name(name_pelak,"pelak")
                    cls=DataViewItem()
                    layout=cls.get_layout(name_crop,name_pelak,date_time,camera_number,camera_name)
                    MainKivyApp.my_screenmanager.ids.data_grid_pelak.add_widget(layout)
                elif(count>=config.count_tbl_pelak and self.flg_add_pelak==False ):
                    self.flg_add_pelak=True
                    self.index_show_pelak=count-1
                    cam_name=MainKivyApp.my_screenmanager.ids.data_grid_pelak.children[self.index_show_pelak].children[3]
                    cam_name.text=MainKivyApp.app.init_persian_text(camera_name)
                    img=MainKivyApp.my_screenmanager.ids.data_grid_pelak.children[self.index_show_pelak].children[2]
                    img.source=name_crop
                    img.reload()
                    text=self.get_date_from_name(name_pelak,"pelak")
                    date_time=MainKivyApp.my_screenmanager.ids.data_grid_pelak.children[self.index_show_pelak].children[1]
                    date_time.text=text
                    MainKivyApp.my_screenmanager.ids.data_grid_pelak.children[self.index_show_pelak].children[0].id=name_pelak
                    self.index_show_pelak-=1
            elif(self.flg_add_pelak==True):
                if(self.index_show_pelak<0):
                    self.index_show_pelak=count-1
                cam_name=MainKivyApp.my_screenmanager.ids.data_grid_pelak.children[self.index_show_pelak].children[3]
                cam_name.text=MainKivyApp.app.init_persian_text(camera_name)
                img=MainKivyApp.my_screenmanager.ids.data_grid_pelak.children[self.index_show_pelak].children[2]
                img.source=name_crop
                img.reload()
                text=self.get_date_from_name(name_pelak,"pelak")
                date_time=MainKivyApp.my_screenmanager.ids.data_grid_pelak.children[self.index_show_pelak].children[1]
                date_time.text=text
                MainKivyApp.my_screenmanager.ids.data_grid_pelak.children[self.index_show_pelak].children[0].id=name_pelak
                self.index_show_pelak-=1

    def show_person(self,dt):
        if(self.queue_person.qsize()>0):
            arr=self.queue_person.get()
            name_person=arr[0]
            name_crop=arr[1]
            camera_number=arr[2]
            camera_name=arr[3]
            count=len(MainKivyApp.my_screenmanager.ids.data_grid_person.children)
            if(self.flg_add_person==False):
                if(count<config.count_tbl_person):
                    date_time=self.get_date_from_name(name_person,"person")
                    cls=DataViewItem()
                    layout=cls.get_layout(name_crop,name_person,date_time,camera_number,camera_name)
                    MainKivyApp.my_screenmanager.ids.data_grid_person.add_widget(layout)
                elif(count>=config.count_tbl_person and self.flg_add_person==False ):
                    self.flg_add_person=True
                    self.index_show_person=count-1
                    cam_name=MainKivyApp.my_screenmanager.ids.data_grid_person.children[self.index_show_person].children[3]
                    cam_name.text=MainKivyApp.app.init_persian_text(camera_name)
                    img=MainKivyApp.my_screenmanager.ids.data_grid_person.children[self.index_show_person].children[2]
                    img.source=name_crop
                    img.reload()
                    text=self.get_date_from_name(name_person,"person")
                    date_time=MainKivyApp.my_screenmanager.ids.data_grid_person.children[self.index_show_person].children[1]
                    date_time.text=text
                    MainKivyApp.my_screenmanager.ids.data_grid_person.children[self.index_show_person].children[0].id=name_person
                    self.index_show_person-=1
            elif(self.flg_add_person==True):
                if(self.index_show_person<0):
                    self.index_show_person=count-1
                cam_name=MainKivyApp.my_screenmanager.ids.data_grid_person.children[self.index_show_person].children[3]
                cam_name.text=MainKivyApp.app.init_persian_text(camera_name)
                img=MainKivyApp.my_screenmanager.ids.data_grid_person.children[self.index_show_person].children[2]
                img.source=name_crop
                img.reload()
                text=self.get_date_from_name(name_person,"person")
                date_time=MainKivyApp.my_screenmanager.ids.data_grid_person.children[self.index_show_person].children[1]
                date_time.text=text
                MainKivyApp.my_screenmanager.ids.data_grid_person.children[self.index_show_person].children[0].id=name_person
                self.index_show_person-=1

    def get_date_from_name(self,name,what):
        data=name.split(what)[1].split('org')[0]
        arr=data.split('/')
        arr.pop(0)
        arr.pop()
        data=arr[0]+"-"+arr[1]+"-"+arr[2]

        saat=name.split(what)[1].split('org')[1].split('.')[0]
        arr=saat.split('/')
        arr.pop(0)
        _tmp=arr[0].split('-')
        milisec=_tmp[3][0:2]
        saat=_tmp[0]+"-"+_tmp[1]+"-"+_tmp[2]+"-"+milisec

        return data+" "+saat

    def check_dir_video(self,pre_dir):
        year=CustomTime.get_j_year()
        month=CustomTime.get_j_month()
        day=CustomTime.get_j_day()
        dir=pre_dir+"video/"+year+"/"+month+"/"+day
        os.makedirs(dir,exist_ok=True)
        return dir


    def check_dir_face(self,pre_dir):
        year=CustomTime.get_j_year()
        month=CustomTime.get_j_month()
        day=CustomTime.get_j_day()
        hour=CustomTime.get_j_hour()
        dir1=pre_dir+"faces/"+year+"/"+month+"/"+day+"/"+hour+"/org"
        dir2=pre_dir+"faces/"+year+"/"+month+"/"+day+"/"+hour+"/crp"
        os.makedirs(dir1,exist_ok=True)
        os.makedirs(dir2,exist_ok=True)
        return dir1,dir2
    def check_dir_pelak(self,pre_dir):
        year=CustomTime.get_j_year()
        month=CustomTime.get_j_month()
        day=CustomTime.get_j_day()
        hour=CustomTime.get_j_hour()
        dir1=pre_dir+"pelak/"+year+"/"+month+"/"+day+"/"+hour+"/org"
        dir2=pre_dir+"pelak/"+year+"/"+month+"/"+day+"/"+hour+"/crp"
        os.makedirs(dir1,exist_ok=True)
        os.makedirs(dir2,exist_ok=True)
        return dir1,dir2

    def check_dir_person(self,pre_dir):
        year=CustomTime.get_j_year()
        month=CustomTime.get_j_month()
        day=CustomTime.get_j_day()
        hour=CustomTime.get_j_hour()
        dir1=pre_dir+"person/"+year+"/"+month+"/"+day+"/"+hour+"/org"
        dir2=pre_dir+"person/"+year+"/"+month+"/"+day+"/"+hour+"/crp"
        os.makedirs(dir1,exist_ok=True)
        os.makedirs(dir2,exist_ok=True)
        return dir1,dir2

    def hide_visible_frames(self):
        MainKivyApp.my_screenmanager.ids.grid_box_1.opacity=0
        MainKivyApp.my_screenmanager.ids.grid_box_2.opacity=0
        MainKivyApp.my_screenmanager.ids.grid_box_3.opacity=0
        MainKivyApp.my_screenmanager.ids.grid_box_4.opacity=0

    def check_visible_frames(self):
        if self.show_camera==1:
            MainKivyApp.my_screenmanager.ids.grid_box_4.opacity=0
            MainKivyApp.my_screenmanager.ids.grid_box_3.opacity=0
            MainKivyApp.my_screenmanager.ids.grid_box_1.opacity=1
            MainKivyApp.my_screenmanager.ids.grid_box_2.opacity=1

        elif self.show_camera==2:
            MainKivyApp.my_screenmanager.ids.grid_box_3.opacity=1
            MainKivyApp.my_screenmanager.ids.grid_box_4.opacity=1
            MainKivyApp.my_screenmanager.ids.grid_box_1.opacity=0
            MainKivyApp.my_screenmanager.ids.grid_box_2.opacity=0

        elif self.show_camera==0:
            MainKivyApp.my_screenmanager.ids.grid_box_1.opacity=1
            MainKivyApp.my_screenmanager.ids.grid_box_2.opacity=1
            MainKivyApp.my_screenmanager.ids.grid_box_3.opacity=1
            MainKivyApp.my_screenmanager.ids.grid_box_4.opacity=1

    def get_click(self):
        print("ssss")

# all screens sort ......

class Tizer(Screen):
    pass

class Users(Screen):

    def on_enter(self, *args):
        MainKivyApp.my_screenmanager.ids.sp_select_users.text='...'
        MainKivyApp.my_screenmanager.ids.sp_select_users.values=self.get_list_accept_users()

    def send_user_to_sender(self,sender_data):
        ret=False
        MainKivyApp.app.show_popup()
        s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        address=(MainKivyApp.conf.get_update_config('sender_ip'),int(MainKivyApp.conf.get_update_config('port_rec_video_frame')))
        s.connect(address)
        s.sendall('d@d@d@'.encode('utf-8'))
        do=True
        try:
            encoding=encrypt_cisco('qwe!@#rty$%^uio&*(oiuytrewq(*&^%$#@!')
            while do:
                recive=s.recv(1024)
                recive=encoding.decrypt(recive)
                recive=recive.decode('utf-8')
                if recive=="88":
                    data_str=sender_data.encode('utf-8')
                    data=encoding.encrypt(data_str)
                    s.sendall(data)
                    while True:
                        recive=s.recv(1024)
                        recive=encoding.decrypt(recive)
                        recive=recive.decode('utf-8')
                        if recive=="88":
                            ret=True
                            MainKivyApp.app.close_popup()
                        do=False
                        break
        except:
            MainKivyApp.app.close_popup()
            traceback.print_exc()
        return ret

    def before_sabte(self):
        txt_new_user_ip=MainKivyApp.my_screenmanager.ids.txt_new_user_ip.text
        if len(txt_new_user_ip.split('.'))==4:
            if len(MainKivyApp.conf.get_update_config('list_accept_users'))>1:
                arr=MainKivyApp.conf.get_update_config('list_accept_users').split(',')
            else:
                arr=list()
            arr.append(txt_new_user_ip)
            last_data=','.join(arr)
            ret=self.send_user_to_sender(last_data)
            if ret:
                MainKivyApp.conf.set_new_val_data('list_accept_users',last_data)
                MainKivyApp.my_screenmanager.ids.txt_new_user_ip.text=""
                MainKivyApp.app.change_screen_for_refresh('KivyShowVideoFrames','users')
                msg=MessageBox(translate.mytr.get('done'),'با موفقیت انجام شد',MainKivyApp.app)
                msg.show_message_box()
            else:
                msg=MessageBox(translate.mytr.get('warning'),'ارتباط با سرور انجام نشد',MainKivyApp.app)
                msg.show_message_box()

        else:
            msg=MessageBox('انجام نشد','لطفا آیپی وارد شده را بررسی کنید',MainKivyApp.app)
            msg.show_message_box()

    def clicked_sabte_karbar(self):
        threading.Thread(target=self.before_sabte).start()

    def clicked_hazfe_karbar(self):
        sp_select_users=MainKivyApp.my_screenmanager.ids.sp_select_users.text
        if not sp_select_users=="...":
            arr=MainKivyApp.conf.get_update_config('list_accept_users').split(',')
            arr.remove(sp_select_users)
            last_data=','.join(arr)
            ret=self.send_user_to_sender(last_data)
            if ret:
                MainKivyApp.conf.set_new_val_data('list_accept_users',last_data)
                msg=MessageBox(translate.mytr.get('done'),'با موفقیت انجام شد',MainKivyApp.app)
                msg.show_message_box()
                MainKivyApp.app.change_screen_for_refresh('KivyShowVideoFrames','users')
            else:
                msg=MessageBox(translate.mytr.get('warning'),'ارتباط با سرور انجام نشد',MainKivyApp.app)
                msg.show_message_box()
        else:
            msg=MessageBox(translate.mytr.get('warning'),translate.mytr.get('for_delete_select_ip_before'),MainKivyApp.app)
            msg.show_message_box()

    def clicked_back_to_menu(self):
        MainKivyApp.my_screenmanager.current="KivyShowVideoFrames"

    def get_list_accept_users(self):
        arr =MainKivyApp.conf.get_update_config('list_accept_users').split(',')
        return arr

class History(Screen):

    def on_enter(self, *args):
        MainKivyApp.my_screenmanager.ids.btn_exit_lhistory.text=MainKivyApp.app.init_persian_text('بازگشت')
        MainKivyApp.my_screenmanager.ids.lbl_tab_item_cam_name1.text=MainKivyApp.app.init_persian_text(MainKivyApp.conf.get_update_config('camera_name_1').split('::@@::')[1])
        MainKivyApp.my_screenmanager.ids.lbl_tab_cam1_title.text=MainKivyApp.app.init_persian_text(MainKivyApp.conf.get_update_config('camera_name_1').split('::@@::')[1])
        MainKivyApp.my_screenmanager.ids.lbl_tab_item_cam_name2.text=MainKivyApp.app.init_persian_text(MainKivyApp.conf.get_update_config('camera_name_2').split('::@@::')[1])
        MainKivyApp.my_screenmanager.ids.lbl_tab_cam2_title.text=MainKivyApp.app.init_persian_text(MainKivyApp.conf.get_update_config('camera_name_2').split('::@@::')[1])
        MainKivyApp.my_screenmanager.ids.lbl_tab_item_cam_name3.text=MainKivyApp.app.init_persian_text(MainKivyApp.conf.get_update_config('camera_name_3').split('::@@::')[1])
        MainKivyApp.my_screenmanager.ids.lbl_tab_cam3_title.text=MainKivyApp.app.init_persian_text(MainKivyApp.conf.get_update_config('camera_name_3').split('::@@::')[1])
        MainKivyApp.my_screenmanager.ids.lbl_tab_item_cam_name4.text=MainKivyApp.app.init_persian_text(MainKivyApp.conf.get_update_config('camera_name_4').split('::@@::')[1])
        MainKivyApp.my_screenmanager.ids.lbl_tab_cam4_title.text=MainKivyApp.app.init_persian_text(MainKivyApp.conf.get_update_config('camera_name_4').split('::@@::')[1])

    def update_view_by_clock(self,img,src,*args):
        img.source=src
        img.reload()

    def clicked_btn_search(self,wich):
        msg=MessageBox(translate.mytr.get('warning'),translate.mytr.get('select_soojeh_first'),MainKivyApp.app)
        if wich==1:
            if MainKivyApp.my_screenmanager.ids.txt_select_soojeh1.text=="../":
                msg.show_message_box()
            else:
                threading.Thread(target=self.start_btn_search,args=(wich,)).start()
        elif wich==2:
            if MainKivyApp.my_screenmanager.ids.txt_select_soojeh2.text=="../":
                msg.show_message_box()
            else:
                threading.Thread(target=self.start_btn_search,args=(wich,)).start()
        elif wich==3:
            if MainKivyApp.my_screenmanager.ids.txt_select_soojeh3.text=="../":
                msg.show_message_box()
            else:
                threading.Thread(target=self.start_btn_search,args=(wich,)).start()
        elif wich==4:
            if MainKivyApp.my_screenmanager.ids.txt_select_soojeh4.text=="../":
                msg.show_message_box()
            else:
                threading.Thread(target=self.start_btn_search,args=(wich,)).start()


    def start_btn_search(self,wich):
        try:
            if wich==1:
                MainKivyApp.my_screenmanager.ids.grid_result_search1.clear_widgets()
            elif wich==2:
                MainKivyApp.my_screenmanager.ids.grid_result_search2.clear_widgets()
            elif wich==3:
                MainKivyApp.my_screenmanager.ids.grid_result_search3.clear_widgets()
            elif wich==4:
                MainKivyApp.my_screenmanager.ids.grid_result_search4.clear_widgets()
        except:
            pass
        title="در حال جستجو"
        content="لطفا صبر کنید"
        self.popup=PopUp(title,content,MainKivyApp.app)
        self.popup.show_popup_loading_dynamic()
        if wich==1:
            soojeh_name=MainKivyApp.my_screenmanager.ids.txt_select_soojeh1.text
            if MainKivyApp.my_screenmanager.ids.txt_ch_box_history_face1.active:
                patern="faces"
            elif MainKivyApp.my_screenmanager.ids.txt_ch_box_history_pelak1.active:
                patern="pelak"
            elif MainKivyApp.my_screenmanager.ids.txt_ch_box_history_person1.active:
                patern="person"
            elif MainKivyApp.my_screenmanager.ids.txt_ch_box_history_video1.active:
                patern="video"
            az_sal=MainKivyApp.my_screenmanager.ids.az_sal_sp1.text
            az_mah=MainKivyApp.my_screenmanager.ids.az_mah_sp1.text
            if len(az_mah)<2:
                az_mah="0"+az_mah
            az_rooz=MainKivyApp.my_screenmanager.ids.az_rooz_sp1.text
            if len(az_rooz)<2:
                az_rooz="0"+az_rooz
            ta_sal=MainKivyApp.my_screenmanager.ids.ta_sal_sp1.text
            ta_mah=MainKivyApp.my_screenmanager.ids.ta_mah_sp1.text
            if len(ta_mah)<2:
                ta_mah="0"+ta_mah
            ta_rooz=MainKivyApp.my_screenmanager.ids.ta_rooz_sp1.text
            if len(ta_rooz)<2:
                ta_rooz="0"+ta_rooz
            az_saat=MainKivyApp.my_screenmanager.ids.az_saat_sp1.text
            ta_saat=MainKivyApp.my_screenmanager.ids.ta_saat_sp1.text
        if wich==2:
            soojeh_name=MainKivyApp.my_screenmanager.ids.txt_select_soojeh2.text
            if MainKivyApp.my_screenmanager.ids.txt_ch_box_history_face2.active:
                patern="faces"
            elif MainKivyApp.my_screenmanager.ids.txt_ch_box_history_pelak2.active:
                patern="pelak"
            elif MainKivyApp.my_screenmanager.ids.txt_ch_box_history_person2.active:
                patern="person"
            elif MainKivyApp.my_screenmanager.ids.txt_ch_box_history_video2.active:
                patern="video"
            az_sal=MainKivyApp.my_screenmanager.ids.az_sal_sp2.text
            az_mah=MainKivyApp.my_screenmanager.ids.az_mah_sp2.text
            if len(az_mah)<2:
                az_mah="0"+az_mah
            az_rooz=MainKivyApp.my_screenmanager.ids.az_rooz_sp2.text
            if len(az_rooz)<2:
                az_rooz="0"+az_rooz
            ta_sal=MainKivyApp.my_screenmanager.ids.ta_sal_sp2.text
            ta_mah=MainKivyApp.my_screenmanager.ids.ta_mah_sp2.text
            if len(ta_mah)<2:
                ta_mah="0"+ta_mah
            ta_rooz=MainKivyApp.my_screenmanager.ids.ta_rooz_sp2.text
            if len(ta_rooz)<2:
                ta_rooz="0"+ta_rooz
            az_saat=MainKivyApp.my_screenmanager.ids.az_saat_sp2.text
            ta_saat=MainKivyApp.my_screenmanager.ids.ta_saat_sp2.text
        if wich==3:
            soojeh_name=MainKivyApp.my_screenmanager.ids.txt_select_soojeh3.text
            if MainKivyApp.my_screenmanager.ids.txt_ch_box_history_face3.active:
                patern="faces"
            elif MainKivyApp.my_screenmanager.ids.txt_ch_box_history_pelak3.active:
                patern="pelak"
            elif MainKivyApp.my_screenmanager.ids.txt_ch_box_history_person3.active:
                patern="person"
            elif MainKivyApp.my_screenmanager.ids.txt_ch_box_history_video3.active:
                patern="video"
            az_sal=MainKivyApp.my_screenmanager.ids.az_sal_sp3.text
            az_mah=MainKivyApp.my_screenmanager.ids.az_mah_sp3.text
            if len(az_mah)<2:
                az_mah="0"+az_mah
            az_rooz=MainKivyApp.my_screenmanager.ids.az_rooz_sp3.text
            if len(az_rooz)<2:
                az_rooz="0"+az_rooz
            ta_sal=MainKivyApp.my_screenmanager.ids.ta_sal_sp3.text
            ta_mah=MainKivyApp.my_screenmanager.ids.ta_mah_sp3.text
            if len(ta_mah)<2:
                ta_mah="0"+ta_mah
            ta_rooz=MainKivyApp.my_screenmanager.ids.ta_rooz_sp3.text
            if len(ta_rooz)<2:
                ta_rooz="0"+ta_rooz
            az_saat=MainKivyApp.my_screenmanager.ids.az_saat_sp3.text
            ta_saat=MainKivyApp.my_screenmanager.ids.ta_saat_sp3.text
        if wich==4:
            soojeh_name=MainKivyApp.my_screenmanager.ids.txt_select_soojeh4.text
            if MainKivyApp.my_screenmanager.ids.txt_ch_box_history_face4.active:
                patern="faces"
            elif MainKivyApp.my_screenmanager.ids.txt_ch_box_history_pelak4.active:
                patern="pelak"
            elif MainKivyApp.my_screenmanager.ids.txt_ch_box_history_person4.active:
                patern="person"
            elif MainKivyApp.my_screenmanager.ids.txt_ch_box_history_video4.active:
                patern="video"
            az_sal=MainKivyApp.my_screenmanager.ids.az_sal_sp4.text
            az_mah=MainKivyApp.my_screenmanager.ids.az_mah_sp4.text
            if len(az_mah)<2:
                az_mah="0"+az_mah
            az_rooz=MainKivyApp.my_screenmanager.ids.az_rooz_sp4.text
            if len(az_rooz)<2:
                az_rooz="0"+az_rooz
            ta_sal=MainKivyApp.my_screenmanager.ids.ta_sal_sp4.text
            ta_mah=MainKivyApp.my_screenmanager.ids.ta_mah_sp4.text
            if len(ta_mah)<2:
                ta_mah="0"+ta_mah
            ta_rooz=MainKivyApp.my_screenmanager.ids.ta_rooz_sp4.text
            if len(ta_rooz)<2:
                ta_rooz="0"+ta_rooz
            az_saat=MainKivyApp.my_screenmanager.ids.az_saat_sp4.text
            ta_saat=MainKivyApp.my_screenmanager.ids.ta_saat_sp4.text

        cam="cam"+str(wich)
        arr=self.get_dayse_between_two_date(az_sal,az_mah,az_rooz,az_saat,ta_sal,ta_mah,ta_rooz,ta_saat)
        arr_video=self.get_dayse_between_two_date_without_saat(az_sal,az_mah,az_rooz,ta_sal,ta_mah,ta_rooz)
        radif=0

        if patern=="video":
            for item in arr_video:
                path=os.getcwd()+"/media/"+soojeh_name+"/"+cam+"/"+patern+"/"+item
                if os.path.isdir(path):
                    dir_files=os.listdir(path)
                    for file in dir_files:
                        radif+=1
                        org_file=path+"/"+file
                        saat=file.split('.')[0]
                        tarikh=item.split('/')[0]+"-"+item.split('/')[1]+"-"+item.split('/')[2]
                        #btn_show=Button(on_press=lambda *args: self.clicked_btn_show_video(btn_show))
                        btn_show=Button(on_press=self.clicked_btn_show_video)
                        btn_show.text=MainKivyApp.app.init_persian_text('مشاهده ویدئو')
                        btn_show.padding=(10,10)
                        btn_show.size_hint=(.1,.02)
                        btn_show.height=40
                        btn_show.font_name=config.font_farsi
                        btn_show.id=org_file
                        lbl_saat=Label(text=saat)
                        lbl_saat.size_hint_x=.2
                        lbl_tarikh=Label(text=tarikh)
                        lbl_tarikh.size_hint_x=.2
                        img=Image()
                        img.size_hint_x=.2
                        img.width=100
                        img.height=100
                        Clock.schedule_once(partial(self.update_view_by_clock,img,os.getcwd()+"/"+MainKivyApp.conf.get_update_config('video_alt')),0.005 )
                        lbl_radif=Label(text=str(radif))
                        lbl_radif.size_hint_x=.02
                        if wich==1:
                            MainKivyApp.my_screenmanager.ids.grid_result_search1.add_widget(btn_show)
                            MainKivyApp.my_screenmanager.ids.grid_result_search1.add_widget(lbl_saat)
                            MainKivyApp.my_screenmanager.ids.grid_result_search1.add_widget(lbl_tarikh)
                            MainKivyApp.my_screenmanager.ids.grid_result_search1.add_widget(img)
                            MainKivyApp.my_screenmanager.ids.grid_result_search1.add_widget(lbl_radif)
                        elif wich==2:
                            MainKivyApp.my_screenmanager.ids.grid_result_search2.add_widget(btn_show)
                            MainKivyApp.my_screenmanager.ids.grid_result_search2.add_widget(lbl_saat)
                            MainKivyApp.my_screenmanager.ids.grid_result_search2.add_widget(lbl_tarikh)
                            MainKivyApp.my_screenmanager.ids.grid_result_search2.add_widget(img)
                            MainKivyApp.my_screenmanager.ids.grid_result_search2.add_widget(lbl_radif)
                        elif wich==3:
                            MainKivyApp.my_screenmanager.ids.grid_result_search3.add_widget(btn_show)
                            MainKivyApp.my_screenmanager.ids.grid_result_search3.add_widget(lbl_saat)
                            MainKivyApp.my_screenmanager.ids.grid_result_search3.add_widget(lbl_tarikh)
                            MainKivyApp.my_screenmanager.ids.grid_result_search3.add_widget(img)
                            MainKivyApp.my_screenmanager.ids.grid_result_search3.add_widget(lbl_radif)
                        elif wich==4:
                            MainKivyApp.my_screenmanager.ids.grid_result_search4.add_widget(btn_show)
                            MainKivyApp.my_screenmanager.ids.grid_result_search4.add_widget(lbl_saat)
                            MainKivyApp.my_screenmanager.ids.grid_result_search4.add_widget(lbl_tarikh)
                            MainKivyApp.my_screenmanager.ids.grid_result_search4.add_widget(img)
                            MainKivyApp.my_screenmanager.ids.grid_result_search4.add_widget(lbl_radif)

        else:
            for item in arr:
                path=os.getcwd()+"/media/"+soojeh_name+"/"+cam+"/"+patern+"/"+item+"/org"
                if os.path.isdir(path):
                    dir_files=os.listdir(path)
                    for file in dir_files:
                        radif+=1
                        org_file=path+"/"+file
                        crp_file=path.replace('org','crp')+"/"+file
                        saat=file.split('.')[0]
                        tarikh=item.split('/')[0]+"-"+item.split('/')[1]+"-"+item.split('/')[2]
                        #btn_show=Button(on_press=lambda *args: self.clicked_btn_show(btn_show))
                        btn_show=Button(on_press=self.clicked_btn_show)
                        btn_show.text=MainKivyApp.app.init_persian_text('مشاهده تصویر اصلی')
                        btn_show.padding=(10,10)
                        btn_show.size_hint=(.1,.02)
                        btn_show.height=40
                        btn_show.font_name=config.font_farsi
                        btn_show.id=org_file
                        lbl_saat=Label(text=saat)
                        lbl_saat.size_hint_x=.2
                        lbl_tarikh=Label(text=tarikh)
                        lbl_tarikh.size_hint_x=.2
                        img=Image()
                        img.size_hint_x=.2
                        img.width=100
                        img.height=100
                        Clock.schedule_once(partial(self.update_view_by_clock,img,crp_file),0.005 )
                        lbl_radif=Label(text=str(radif))
                        lbl_radif.size_hint_x=.02
                        if wich==1:
                            MainKivyApp.my_screenmanager.ids.grid_result_search1.add_widget(btn_show)
                            MainKivyApp.my_screenmanager.ids.grid_result_search1.add_widget(lbl_saat)
                            MainKivyApp.my_screenmanager.ids.grid_result_search1.add_widget(lbl_tarikh)
                            MainKivyApp.my_screenmanager.ids.grid_result_search1.add_widget(img)
                            MainKivyApp.my_screenmanager.ids.grid_result_search1.add_widget(lbl_radif)
                        elif wich==2:
                            MainKivyApp.my_screenmanager.ids.grid_result_search2.add_widget(btn_show)
                            MainKivyApp.my_screenmanager.ids.grid_result_search2.add_widget(lbl_saat)
                            MainKivyApp.my_screenmanager.ids.grid_result_search2.add_widget(lbl_tarikh)
                            MainKivyApp.my_screenmanager.ids.grid_result_search2.add_widget(img)
                            MainKivyApp.my_screenmanager.ids.grid_result_search2.add_widget(lbl_radif)
                        elif wich==3:
                            MainKivyApp.my_screenmanager.ids.grid_result_search3.add_widget(btn_show)
                            MainKivyApp.my_screenmanager.ids.grid_result_search3.add_widget(lbl_saat)
                            MainKivyApp.my_screenmanager.ids.grid_result_search3.add_widget(lbl_tarikh)
                            MainKivyApp.my_screenmanager.ids.grid_result_search3.add_widget(img)
                            MainKivyApp.my_screenmanager.ids.grid_result_search3.add_widget(lbl_radif)
                        elif wich==4:
                            MainKivyApp.my_screenmanager.ids.grid_result_search4.add_widget(btn_show)
                            MainKivyApp.my_screenmanager.ids.grid_result_search4.add_widget(lbl_saat)
                            MainKivyApp.my_screenmanager.ids.grid_result_search4.add_widget(lbl_tarikh)
                            MainKivyApp.my_screenmanager.ids.grid_result_search4.add_widget(img)
                            MainKivyApp.my_screenmanager.ids.grid_result_search4.add_widget(lbl_radif)

        if wich==1:
            MainKivyApp.my_screenmanager.ids.grid_header_result_search1.opacity=1
        elif wich==2:
            MainKivyApp.my_screenmanager.ids.grid_header_result_search2.opacity=1
        elif wich==3:
            MainKivyApp.my_screenmanager.ids.grid_header_result_search3.opacity=1
        elif wich==4:
            MainKivyApp.my_screenmanager.ids.grid_header_result_search4.opacity=1
        self.popup.close()



    def clicked_btn_show(self,instance):
        org_img=instance.id
        frame=cv2.imread(org_img)
        frame=cv2.resize(frame,(640,480))
        cv2.imshow(org_img,frame)

    def show_video(self,org_video):
        org_video=org_video.replace('/','\\')
        with open('before-run.bat','r') as file:
            data=file.read()
            file.close()
        pre_dir=os.getcwd().replace('/','\\')
        data=data.replace('pre_dir',pre_dir)
        data=data.replace('movie_address',org_video)
        with open('run.bat','w') as file:
            file.write(data)
            file.close()
        subprocess.call([r'run.bat'])

    def clicked_btn_show_video(self,instance):
        org_video=instance.id
        threading.Thread(target=self.show_video,args=(org_video,)).start()

    def clicked_btn_exit(self):
        MainKivyApp.my_screenmanager.current="KivyShowVideoFrames"

    def get_dayse_between_two_date(self,d1_y,d1_m,d1_d,d1_azsaat,d2_y,d2_m,d2_d,d2_tasaat):
        start = datetime.datetime(int(d1_y),int(d1_m), int(d1_d))
        end = datetime.datetime(int(d2_y),int(d2_m),int( d2_d))

        delta = end - start
        arr=list()
        for i in range(delta.days + 1):
            d=str(start + datetime.timedelta(days=i)).split(' ')[0].split('-')
            for j in range(int(d1_azsaat),int(d2_tasaat)):
                if j<10:
                    dir=d[0]+"/"+d[1]+"/"+d[2]+"/0"+str(j)
                else:
                    dir=d[0]+"/"+d[1]+"/"+d[2]+"/"+str(j)
                arr.append(dir)

        return arr

    def get_dayse_between_two_date_without_saat(self,d1_y,d1_m,d1_d,d2_y,d2_m,d2_d):
        start = datetime.datetime(int(d1_y),int(d1_m), int(d1_d))
        end = datetime.datetime(int(d2_y),int(d2_m),int( d2_d))

        delta = end - start
        arr=list()
        for i in range(delta.days + 1):
            d=str(start + datetime.timedelta(days=i)).split(' ')[0].split('-')
            dir=d[0]+"/"+d[1]+"/"+d[2]
            arr.append(dir)

        return arr


class CustomSetting(Screen):
    def on_enter(self, *args):
        self.data_setting=""
        threading.Thread(target=self.get_first_info_setting_before).start()

    def get_first_info_setting_before(self):
        self.init_lbl_text()
        try:
            MainKivyApp.app.show_popup()
            s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            address=(MainKivyApp.conf.get_update_config('sender_ip'),int(MainKivyApp.conf.get_update_config('port_rec_video_frame')))
            s.connect(address)
            s.sendall('a@a@a@'.encode('utf-8'))
            while True:
                data=s.recv(5214)
                encoding=encrypt_cisco('qwe!@#rty$%^uio&*(oiuytrewq(*&^%$#@!')
                data=encoding.decrypt(data)
                data= data.decode('utf-8')
                data=data.split('br=""')[0]

                self.data_setting=data
                key_code=str(self.parse_setting(self.data_setting,'key')).strip()
                qu=int(str(self.parse_setting(self.data_setting,'qu')).strip())
                count_frame_detect=int(str(self.parse_setting(self.data_setting,'count_frame_detect')).strip())
                do_save_video_in_sender=int(str(self.parse_setting(self.data_setting,'do_save_video_in_sender')).strip())
                soojeh_name=str(self.parse_setting(self.data_setting,'soojeh_name')).strip()
                MainKivyApp.my_screenmanager.ids.txt_soojeh_name.text=soojeh_name
                MainKivyApp.conf.set_new_val_data('key',key_code)
                MainKivyApp.conf.set_new_val_data('do_save_video_in_sender',do_save_video_in_sender)
                MainKivyApp.conf.set_new_val_data('qu',qu)
                MainKivyApp.conf.set_new_val_data('count_frame_detect',count_frame_detect)
                MainKivyApp.app.close_popup()
                if not soojeh_name==MainKivyApp.conf.get_update_config('soojeh_name'):
                    msg="نام کیس در سیستم فرستنده با نام کیس در مرکز فرماندهی یکسان نیست"
                    msg+="\r\n"
                    msg+="در صورتی که نامی که فرستنده مشخص کرده را تایید میکنید یکبار دکمه ذخیره را زده و در غیر اینصورت نام کیس را اصلاح و سپس ذخیره کنید"
                    MainKivyApp.app.ShowMessageBox('توجه',msg)
                break
        except:
            MainKivyApp.app.close_popup()
            MainKivyApp.app.ShowMessageBox('توجه','ارتباط با فرستنده برقرار نشد، ممکن است اطلاعات این بخش به روز نباشد')


        self.fill_data()
        self.old_camera1=MainKivyApp.app.init_persian_text(MainKivyApp.conf.get_update_config('camera_name_1').split('::@@::')[1])
        self.old_camera2=MainKivyApp.app.init_persian_text(MainKivyApp.conf.get_update_config('camera_name_2').split('::@@::')[1])
        self.old_camera3=MainKivyApp.app.init_persian_text(MainKivyApp.conf.get_update_config('camera_name_3').split('::@@::')[1])
        self.old_camera4=MainKivyApp.app.init_persian_text(MainKivyApp.conf.get_update_config('camera_name_4').split('::@@::')[1])

    def update_names_camera(self):
        if MainKivyApp.app.check_persian_char(MainKivyApp.conf.get_update_config('camera_name_1').split('::@@::')[1])=="fa":
            self.c1=MainKivyApp.conf.get_update_config('camera_name_1').split('::@@::')[1]
        elif MainKivyApp.app.check_persian_char(MainKivyApp.conf.get_update_config('camera_name_1').split('::@@::')[1])=="fa_k":
            self.c1=MainKivyApp.app.init_persian_text(MainKivyApp.conf.get_update_config('camera_name_1').split('::@@::')[1])
        if MainKivyApp.app.check_persian_char(MainKivyApp.conf.get_update_config('camera_name_2').split('::@@::')[1])=="fa":
            self.c2=MainKivyApp.conf.get_update_config('camera_name_2').split('::@@::')[1]
        elif MainKivyApp.app.check_persian_char(MainKivyApp.conf.get_update_config('camera_name_2').split('::@@::')[1])=="fa_k":
            self.c2=MainKivyApp.app.init_persian_text(MainKivyApp.conf.get_update_config('camera_name_2').split('::@@::')[1])
        if MainKivyApp.app.check_persian_char(MainKivyApp.conf.get_update_config('camera_name_3').split('::@@::')[1])=="fa":
            self.c3=MainKivyApp.conf.get_update_config('camera_name_3').split('::@@::')[1]
        elif MainKivyApp.app.check_persian_char(MainKivyApp.conf.get_update_config('camera_name_3').split('::@@::')[1])=="fa_k":
            self.c3=MainKivyApp.app.init_persian_text(MainKivyApp.conf.get_update_config('camera_name_3').split('::@@::')[1])
        if MainKivyApp.app.check_persian_char(MainKivyApp.conf.get_update_config('camera_name_4').split('::@@::')[1])=="fa":
            self.c4=MainKivyApp.conf.get_update_config('camera_name_4').split('::@@::')[1]
        elif MainKivyApp.app.check_persian_char(MainKivyApp.conf.get_update_config('camera_name_4').split('::@@::')[1])=="fa_k":
            self.c4=MainKivyApp.app.init_persian_text(MainKivyApp.conf.get_update_config('camera_name_4').split('::@@::')[1])

    def init_lbl_text(self):
        MainKivyApp.my_screenmanager.ids.btn_save_lsetting.text=MainKivyApp.app.init_persian_text('ذخیره')
        MainKivyApp.my_screenmanager.ids.btn_exit_lsetting.text=MainKivyApp.app.init_persian_text('بازگشت')
        MainKivyApp.my_screenmanager.ids.lbl_reciver_ip.text=MainKivyApp.app.init_persian_text('آی پی مرکز فرماندهی')
        MainKivyApp.my_screenmanager.ids.lbl_sender_ip.text=MainKivyApp.app.init_persian_text('آی پی فرستنده')
        MainKivyApp.my_screenmanager.ids.lbl_do_save_video.text=MainKivyApp.app.init_persian_text('ذخیره ویدئوها')
        MainKivyApp.my_screenmanager.ids.lbl_enbale_3g.text=MainKivyApp.app.init_persian_text('فعال کردن حالت 3 جی')
        MainKivyApp.my_screenmanager.ids.lbl_count_tbl_face.text=MainKivyApp.app.init_persian_text('تعداد تصاویر قابل نمایش در جدول چهره')
        MainKivyApp.my_screenmanager.ids.lbl_count_tbl_pelak.text=MainKivyApp.app.init_persian_text('تعداد تصاویر قابل نمایش در جدول پلاک')
        MainKivyApp.my_screenmanager.ids.lbl_count_tbl_person.text=MainKivyApp.app.init_persian_text('تعداد تصاویر قابل نمایش در جدول افراد')
        MainKivyApp.my_screenmanager.ids.lbl_cam_name1.text=MainKivyApp.app.init_persian_text('نام مستعار دوربین اول')
        MainKivyApp.my_screenmanager.ids.lbl_cam_name2.text=MainKivyApp.app.init_persian_text('نام مستعار دوربین دوم')
        MainKivyApp.my_screenmanager.ids.lbl_cam_name3.text=MainKivyApp.app.init_persian_text('نام مستعار دوربین سوم')
        MainKivyApp.my_screenmanager.ids.lbl_cam_name4.text=MainKivyApp.app.init_persian_text('نام مستعار دوربین چهارم')
        MainKivyApp.my_screenmanager.ids.lbl_show_camera.text=MainKivyApp.app.init_persian_text('کدام دوربین ها در حالت 3 جی نمایش داده شوند')
        MainKivyApp.my_screenmanager.ids.lbl_soojeh_name.text=MainKivyApp.app.init_persian_text('نام کیس در حال انجام(لطفا نام کیس را انگلیسی وارد کنید)')

        self.update_names_camera()
        MainKivyApp.my_screenmanager.ids.lbl_ch_box_show_camera1.text=self.c1+" - "+self.c2
        MainKivyApp.my_screenmanager.ids.lbl_ch_box_show_camera2.text=self.c3+" - "+self.c4

    def fill_data(self):
        if len(MainKivyApp.conf.get_update_config('reciver_ip'))>1:
            MainKivyApp.my_screenmanager.ids.txt_reciver_ip.text=MainKivyApp.conf.get_update_config('reciver_ip') # config.reciver_ip
        if len(MainKivyApp.conf.get_update_config('sender_ip'))>1:
            MainKivyApp.my_screenmanager.ids.txt_sender_ip.text=MainKivyApp.conf.get_update_config('sender_ip') #config.sender_ip
        if int(MainKivyApp.conf.get_update_config('do_save_video'))==1:
            MainKivyApp.my_screenmanager.ids.txt_do_save_video.active=True
        if int(MainKivyApp.conf.get_update_config('do_save_video_in_sender'))==1:
            MainKivyApp.my_screenmanager.ids.txt_do_save_video_in_sender.active=True
        if MainKivyApp.conf.get_update_config('qu')=="90":
            MainKivyApp.my_screenmanager.ids.txt_qu_frame_up.state="down"
        elif MainKivyApp.conf.get_update_config('qu')=="70":
            MainKivyApp.my_screenmanager.ids.txt_qu_frame_middle.state="down"
        elif MainKivyApp.conf.get_update_config('qu')=="50":
            MainKivyApp.my_screenmanager.ids.txt_qu_frame_down.state="down"
        if MainKivyApp.conf.get_update_config('count_frame_detect')=="5":
            MainKivyApp.my_screenmanager.ids.txt_cont_detect_high.state="down"
        elif MainKivyApp.conf.get_update_config('count_frame_detect')=="10":
            MainKivyApp.my_screenmanager.ids.txt_cont_detect_middle.state="down"
        elif MainKivyApp.conf.get_update_config('count_frame_detect')=="15":
            MainKivyApp.my_screenmanager.ids.txt_cont_detect_low.state="down"


        MainKivyApp.my_screenmanager.ids.txt_count_tbl_face.text=MainKivyApp.conf.get_update_config('count_tbl_face')
        MainKivyApp.my_screenmanager.ids.txt_count_tbl_person.text= MainKivyApp.conf.get_update_config('count_tbl_person')
        MainKivyApp.my_screenmanager.ids.txt_count_tbl_pelak.text=MainKivyApp.conf.get_update_config('count_tbl_person')
        #MainKivyApp.my_screenmanager.ids.txt_soojeh_name.text=MainKivyApp.conf.get_update_config('soojeh_name')
        MainKivyApp.my_screenmanager.ids.txt_key.text=MainKivyApp.conf.get_update_config('key')
        MainKivyApp.my_screenmanager.ids.txt_cam_name1.text=self.c1
        MainKivyApp.my_screenmanager.ids.txt_cam_name2.text=self.c2
        MainKivyApp.my_screenmanager.ids.txt_cam_name3.text=self.c3
        MainKivyApp.my_screenmanager.ids.txt_cam_name4.text=self.c4
        if int(MainKivyApp.conf.get_update_config('show_camera'))==0:
            MainKivyApp.my_screenmanager.ids.txt_enbale_3g.active=False
            MainKivyApp.my_screenmanager.ids.txt_ch_box_show_camera1.active=False
            MainKivyApp.my_screenmanager.ids.txt_ch_box_show_camera2.active=False
        else:
            MainKivyApp.my_screenmanager.ids.txt_enbale_3g.active=True
            if int(MainKivyApp.conf.get_update_config('show_camera'))==1:
                MainKivyApp.my_screenmanager.ids.txt_ch_box_show_camera1.active=True
            elif int(MainKivyApp.conf.get_update_config('show_camera'))==2:
                MainKivyApp.my_screenmanager.ids.txt_ch_box_show_camera2.active=True

    def clicked_btn_save_before(self):
        threading.Thread(target=self.clicked_btn_save).start()

    def clicked_btn_save(self):
        if re.match("^[A-Za-z0-9_-]*$", MainKivyApp.my_screenmanager.ids.txt_soojeh_name.text):
            if len(MainKivyApp.my_screenmanager.ids.txt_soojeh_name.text)>0:
                if MainKivyApp.my_screenmanager.ids.txt_enbale_3g.active==True and MainKivyApp.my_screenmanager.ids.txt_ch_box_show_camera1.active==False and MainKivyApp.my_screenmanager.ids.txt_ch_box_show_camera2.active==False:
                    msg=MessageBox('ذخیره نشد','وقتی حالت 3 جی فعال است باید مشخص شود کدام دوربین ها نمایش داده شوند',MainKivyApp.app)
                    msg.show_message_box()
                else:
                    MainKivyApp.app.show_popup()
                    data=MainKivyApp.conf.get_data()
                    last=data.split('br=""')[1]
                    change_data=""
                    txt_reciver_ip=MainKivyApp.my_screenmanager.ids.txt_reciver_ip.text
                    if len(txt_reciver_ip)>1:
                        change_data+='reciver_ip="'+txt_reciver_ip+'"'
                        change_data+='\n'
                        MainKivyApp.conf.set_new_val_data('reciver_ip',txt_reciver_ip)
                    txt_sender_ip=MainKivyApp.my_screenmanager.ids.txt_sender_ip.text
                    if len(txt_sender_ip)>1:
                        change_data+='sender_ip="'+txt_sender_ip+'"'
                        change_data+='\n'
                        MainKivyApp.conf.set_new_val_data('sender_ip',txt_sender_ip)
                    txt_do_save_video=MainKivyApp.my_screenmanager.ids.txt_do_save_video.active
                    if txt_do_save_video:
                        change_data+='do_save_video=1'
                        change_data+='\n'
                        MainKivyApp.conf.set_new_val_data('do_save_video','1')
                    if txt_do_save_video==False:
                        change_data+='do_save_video=0'
                        change_data+='\n'
                        MainKivyApp.conf.set_new_val_data('do_save_video','0')

                    txt_do_save_video_in_sender=MainKivyApp.my_screenmanager.ids.txt_do_save_video_in_sender.active
                    if txt_do_save_video_in_sender:
                        change_data+='do_save_video_in_sender=1'
                    elif txt_do_save_video==False:
                        change_data+='do_save_video_in_sender=0'
                    change_data+='\n'
                    if MainKivyApp.my_screenmanager.ids.txt_qu_frame_up.state=="down":
                        change_data+='qu=90'
                    elif MainKivyApp.my_screenmanager.ids.txt_qu_frame_middle.state=="down":
                        change_data+='qu=70'
                    elif MainKivyApp.my_screenmanager.ids.txt_qu_frame_down.state=="down":
                        change_data+='qu=50'
                    change_data+='\n'
                    if MainKivyApp.my_screenmanager.ids.txt_cont_detect_high.state=="down":
                        change_data+='count_frame_detect=5'
                    elif MainKivyApp.my_screenmanager.ids.txt_cont_detect_middle.state=="down":
                        change_data+='count_frame_detect=10'
                    elif MainKivyApp.my_screenmanager.ids.txt_cont_detect_low.state=="down":
                        change_data+='count_frame_detect=15'
                    change_data+='\n'
                    txt_count_tbl_face=MainKivyApp.my_screenmanager.ids.txt_count_tbl_face.text
                    if len(txt_count_tbl_face)>0 and type(eval(txt_count_tbl_face))==int:
                        change_data+='count_tbl_face='+txt_count_tbl_face
                        change_data+='\n'
                        MainKivyApp.conf.set_new_val_data('count_tbl_face',txt_count_tbl_face)
                    txt_count_tbl_person=MainKivyApp.my_screenmanager.ids.txt_count_tbl_person.text
                    if len(txt_count_tbl_person)>0 and type(eval(txt_count_tbl_person))==int:
                        change_data+='count_tbl_person='+txt_count_tbl_person
                        change_data+='\n'
                        MainKivyApp.conf.set_new_val_data('count_tbl_person',txt_count_tbl_person)
                    txt_count_tbl_pelak=MainKivyApp.my_screenmanager.ids.txt_count_tbl_pelak.text
                    if len(txt_count_tbl_pelak)>0 and type(eval(txt_count_tbl_pelak))==int:
                        change_data+='count_tbl_pelak='+txt_count_tbl_pelak
                        change_data+='\n'
                        MainKivyApp.conf.set_new_val_data('count_tbl_pelak',txt_count_tbl_pelak)
                    txt_cam_name1=MainKivyApp.my_screenmanager.ids.txt_cam_name1.text
                    if len(txt_cam_name1)>1:
                        if self.old_camera1==txt_cam_name1:
                            change_data+='camera_name_1="1::@@::'+self.old_camera1+'"'
                        else:
                            change_data+='camera_name_1="1::@@::'+txt_cam_name1+'"'
                            MainKivyApp.conf.set_new_val_data('camera_name_1','1::@@::'+txt_cam_name1)
                    else:
                        change_data+='camera_name_1="1::@@::'+self.old_camera1+'"'
                    change_data+='\n'
                    txt_cam_name2=MainKivyApp.my_screenmanager.ids.txt_cam_name2.text
                    if len(txt_cam_name2)>1:
                        if self.old_camera2==txt_cam_name2:
                            change_data+='camera_name_2="2::@@::'+self.old_camera2+'"'
                        else:
                            change_data+='camera_name_2="2::@@::'+txt_cam_name2+'"'
                            MainKivyApp.conf.set_new_val_data('camera_name_2','2::@@::'+txt_cam_name2)
                    else:
                        change_data+='camera_name_2="2::@@::'+self.old_camera2+'"'
                    change_data+='\n'
                    txt_cam_name3=MainKivyApp.my_screenmanager.ids.txt_cam_name3.text
                    if len(txt_cam_name3)>1:
                        if self.old_camera3==txt_cam_name3:
                            change_data+='camera_name_3="3::@@::'+self.old_camera3+'"'
                        else:
                            change_data+='camera_name_3="3::@@::'+txt_cam_name3+'"'
                            MainKivyApp.conf.set_new_val_data('camera_name_3','3::@@::'+txt_cam_name3)
                    else:
                        change_data+='camera_name_3="3::@@::'+self.old_camera3+'"'
                    change_data+='\n'
                    txt_cam_name4=MainKivyApp.my_screenmanager.ids.txt_cam_name4.text
                    if len(txt_cam_name4)>1:
                        if self.old_camera4==txt_cam_name4:
                            change_data+='camera_name_4="4::@@::'+self.old_camera4+'"'
                        else:
                            change_data+='camera_name_4="4::@@::'+txt_cam_name4+'"'
                            MainKivyApp.conf.set_new_val_data('camera_name_4','4::@@::'+txt_cam_name4)
                    else:
                        change_data+='camera_name_4="4::@@::'+self.old_camera4+'"'
                    change_data+='\n'
                    if MainKivyApp.my_screenmanager.ids.txt_enbale_3g.active==False:
                        change_data+='show_camera="0"'
                        change_data+='\n'
                        MainKivyApp.conf.set_new_val_data('show_camera','0')
                    elif MainKivyApp.my_screenmanager.ids.txt_enbale_3g.active==True:
                        if MainKivyApp.my_screenmanager.ids.txt_ch_box_show_camera1.active==True:
                            change_data+='show_camera="1"'
                            change_data+='\n'
                            MainKivyApp.conf.set_new_val_data('show_camera','1')
                        elif MainKivyApp.my_screenmanager.ids.txt_ch_box_show_camera2.active==True:
                            change_data+='show_camera="2"'
                            change_data+='\n'
                            MainKivyApp.conf.set_new_val_data('show_camera','2')
                    change_data+='soojeh_name="'+MainKivyApp.my_screenmanager.ids.txt_soojeh_name.text+'"'
                    change_data+='\n'
                    MainKivyApp.conf.set_new_val_data('soojeh_name',MainKivyApp.my_screenmanager.ids.txt_soojeh_name.text)
                    change_data+='key='+MainKivyApp.conf.get_update_config('key')
                    change_data+='\n'
                    data=change_data+'\n\n\n'+'br=""'+last
                    MainKivyApp.conf.write_data(data)

                    txt_do_save_video_in_sender=MainKivyApp.my_screenmanager.ids.txt_do_save_video_in_sender.active
                    data_str=self.data_setting
                    az=data_str.find('key=')
                    ta=data_str.find('\n',az)
                    tmp=data_str[az:ta]
                    new_data='key='+str(MainKivyApp.my_screenmanager.ids.txt_key.text).strip()
                    data_str=data_str.replace(tmp,new_data)
                    if txt_do_save_video_in_sender:
                        new_data='do_save_video_in_sender=1'
                    elif txt_do_save_video==False:
                        new_data='do_save_video_in_sender=0'
                    az=data_str.find('do_save_video_in_sender=')
                    ta=data_str.find('\n',az)
                    tmp=data_str[az:ta]
                    data_str=data_str.replace(tmp,new_data)
                    if MainKivyApp.my_screenmanager.ids.txt_qu_frame_up.state=="down":
                        new_data='qu=90'
                    elif MainKivyApp.my_screenmanager.ids.txt_qu_frame_middle.state=="down":
                        new_data='qu=70'
                    elif MainKivyApp.my_screenmanager.ids.txt_qu_frame_down.state=="down":
                        new_data='qu=50'
                    az=data_str.find('qu=')
                    ta=data_str.find('\n',az)
                    tmp=data_str[az:ta]
                    data_str=data_str.replace(tmp,new_data)

                    new_data='soojeh_name="'+MainKivyApp.conf.get_update_config('soojeh_name')+'"'
                    az=data_str.find('soojeh_name=')
                    ta=data_str.find('\n',az)
                    tmp=data_str[az:ta]
                    data_str=data_str.replace(tmp,new_data)



                    if MainKivyApp.my_screenmanager.ids.txt_cont_detect_high.state=="down":
                        new_data='count_frame_detect=5'
                    elif MainKivyApp.my_screenmanager.ids.txt_cont_detect_middle.state=="down":
                        new_data='count_frame_detect=10'
                    elif MainKivyApp.my_screenmanager.ids.txt_cont_detect_low.state=="down":
                        new_data='count_frame_detect=15'
                    az=data_str.find('count_frame_detect')
                    ta=data_str.find('\n',az)
                    tmp=data_str[az:ta]
                    data_str=data_str.replace(tmp,new_data)

                    try:
                        s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        address=(MainKivyApp.conf.get_update_config('sender_ip'),int(MainKivyApp.conf.get_update_config('port_rec_video_frame')))
                        s.connect(address)
                        s.sendall('b@b@b@'.encode('utf-8'))
                        do=True
                        try:
                            encoding=encrypt_cisco('qwe!@#rty$%^uio&*(oiuytrewq(*&^%$#@!')
                            while do:
                                recive=s.recv(1024)
                                recive=encoding.decrypt(recive)
                                recive=recive.decode('utf-8')
                                if recive=="88":
                                    data_str=data_str.encode('utf-8')
                                    data=encoding.encrypt(data_str)
                                    s.sendall(data)
                                    while True:
                                        recive=s.recv(1024)
                                        recive=encoding.decrypt(recive)
                                        recive=recive.decode('utf-8')
                                        if recive=="88":
                                            kk=int(str(MainKivyApp.my_screenmanager.ids.txt_key.text).strip())
                                            MainKivyApp.conf.set_new_val_data('key',kk)
                                            MainKivyApp.app.close_popup()
                                            msg=MessageBox(translate.mytr.get('done'),'با موفقیت انجام شد',MainKivyApp.app)
                                            msg.show_message_box()

                                        else:
                                            msg=MessageBox(translate.mytr.get('warning'),'ارتباط با سرور انجام نشد',MainKivyApp.app)
                                            msg.show_message_box()
                                        do=False
                                        break
                        except:
                            MainKivyApp.app.close_popup()
                            traceback.print_exc()
                    except:
                        MainKivyApp.app.close_popup()
                        MainKivyApp.app.ShowMessageBox('توجه','اطلاعات برای فرستنده ارسال نشد اما در سیستم ذخیره شد')
                MainKivyApp.app.close_popup()
            else:
                msg=MessageBox('اطلاعات نادرست','ننام کیس نمیتواند خالی باشد',MainKivyApp.app)
                msg.show_message_box()

        else:
            msg=MessageBox('اطلاعات نادرست','نام کیس فقط میتواند شامل عدد و حروف باشد',MainKivyApp.app)
            msg.show_message_box()
    def clicked_btn_exit(self):
        MainKivyApp.my_screenmanager.current="KivyShowVideoFrames"

    def parse_setting(self,data,key):
        try:
            az=data.find(key+'=')
            ta=data.find('\n',az)
            tmp=data[az:ta]
            if tmp.find('"') > -1 :
                return tmp.split('"')[1]
            else:
                return tmp.split('=')[1]
        except:
            traceback.print_exc()


class KivyShowVideoFrames(Screen):

    def clicked_users(self):
        MainKivyApp.my_screenmanager.current="users"

    def clicked_setting(self):
        MainKivyApp.my_screenmanager.current="customsetting"

    def clicked_history(self):
        MainKivyApp.my_screenmanager.current="history"

    def clicked_dissconnect(self):
        if MainKivyApp.reciveing_frames==True:
            MainKivyApp.my_screenmanager.ids.qrcam.stop()

    def clicked_connect(self):
        if len(MainKivyApp.conf.get_update_config('soojeh_name'))>1:
            if MainKivyApp.reciveing_frames==False:
                MainKivyApp.reciveing_frames=True
                path=os.getcwd()+"/media/"+MainKivyApp.conf.get_update_config('soojeh_name')
                if not os.path.isdir(path):
                    os.makedirs(path,exist_ok=True)
                MainKivyApp.my_screenmanager.ids.qrcam.init_data()
                MainKivyApp.my_screenmanager.ids.qrcam.start()
        else:
            MainKivyApp.app.ShowMessageBox(translate.mytr.get('warning'),translate.mytr.get('before_any_connection_select_soojeh_name'))



    def on_enter(self, *args):
        MainKivyApp.my_screenmanager.ids.qrcam.update_vars()
        if MainKivyApp.flg_commuinicate==False:
            thread_cmmunicate=threading.Thread(target=MainKivyApp.app.init_socket_cmmunicate)
            thread_cmmunicate.start()
            MainKivyApp.flg_commuinicate=True

        MainKivyApp.app.check_and_update_state_connection()
        MainKivyApp.my_screenmanager.ids.cam1_name1.text= MainKivyApp.app.init_persian_text(MainKivyApp.conf.get_update_config('camera_name_1').split('::@@::')[1])
        MainKivyApp.my_screenmanager.ids.cam2_name2.text= MainKivyApp.app.init_persian_text(MainKivyApp.conf.get_update_config('camera_name_2').split('::@@::')[1])
        MainKivyApp.my_screenmanager.ids.cam3_name3.text= MainKivyApp.app.init_persian_text(MainKivyApp.conf.get_update_config('camera_name_3').split('::@@::')[1])
        MainKivyApp.my_screenmanager.ids.cam4_name4.text= MainKivyApp.app.init_persian_text(MainKivyApp.conf.get_update_config('camera_name_4').split('::@@::')[1])

        MainKivyApp.my_screenmanager.ids.menu_btn_connect.text= MainKivyApp.app.init_persian_text("اتصال")
        MainKivyApp.my_screenmanager.ids.menu_btn_disconnect.text= MainKivyApp.app.init_persian_text("قطع اتصال")
        MainKivyApp.my_screenmanager.ids.menu_btn_history.text= MainKivyApp.app.init_persian_text("تاریخچه")
        MainKivyApp.my_screenmanager.ids.menu_btn_setting.text= MainKivyApp.app.init_persian_text("تنظیمات")
        MainKivyApp.my_screenmanager.ids.menu_btn_users.text= MainKivyApp.app.init_persian_text("مدیریت کاربران")
        MainKivyApp.my_screenmanager.ids.reset_sender.text= MainKivyApp.app.init_persian_text("راه اندازی مجدد فرستنده")

        MainKivyApp.my_screenmanager.ids.label_person.text= MainKivyApp.app.init_persian_text("افراد")
        MainKivyApp.my_screenmanager.ids.label_face.text= MainKivyApp.app.init_persian_text("چهره")
        MainKivyApp.my_screenmanager.ids.label_pelak.text= MainKivyApp.app.init_persian_text("پلاک")


class WindowManager(ScreenManager):
    def __init__(self):
        super(WindowManager, self).__init__()
        #self.add_widget(Tizer(name='Tizer'))
        #self.add_widget(KivyShowVideoFrames(name='KivyShowVideoFrames'))

# end all screens sort .........

class MainKivyApp(App):
    my_screenmanager=None
    app=None
    conf=initConfig()
    encoding=None
    gen=GenerateKey()
    reciveing_frames=False
    flg_commuinicate=False
    def build(self):
        MainKivyApp.app=self
        self.icon="Assets/icons/logo.jpg"
        MainKivyApp.my_screenmanager=WindowManager()
        key= MainKivyApp.conf.get_update_config('key')
        MainKivyApp.encoding=encrypt_cisco(MainKivyApp.gen.get_uniq_key(key))
        return MainKivyApp.my_screenmanager

    def init_socket_cmmunicate(self):
        ip=self.conf.get_update_config('reciver_ip')
        if len(ip)<2:
            list_ip=self.get_ip_list()
            MainKivyApp.conf.set_new_val_data('reciver_ip',list_ip[0])
            msg="آی پی شما "+list_ip[0]+" میباشد"+"\r\n"+"این آی پی در سیستم ذخیره شد.برای تغیر آن به تنظیمات بروید"
            self.ShowMessageBox('با موفقیت انجام شد',msg)
            time.sleep(1)
        try:
            self.socket_communication = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            ip=self.conf.get_update_config('reciver_ip')
            port=eval(self.conf.get_update_config('port_communicate'))
            address=(ip,port)
            self.socket_communication.bind(address)
            self.socket_communication.listen()
            print("listen on ip {} and port {} ".format(ip,port))
            MainKivyApp.flg_commuinicate=True
            while True:
                try:
                    conn, addr = self.socket_communication.accept()
                    client_ip=addr[0]
                    client_port=addr[1]
                    client_handler= threading.Thread(target=self.handle_connection,args=(conn,client_ip,client_port,))
                    client_handler.start()
                except:
                    try:
                        conn.close()
                    except:
                        traceback.print_exc()
        except:
            MainKivyApp.flg_commuinicate=False
            list_ip=socket.gethostbyname_ex(socket.gethostname())[2]
            if list_ip[0]==MainKivyApp.conf.get_update_config('reciver_ip'):
                self.ShowMessageBox('توجه','نرم افزار را دوبار اجرا کرده اید')
            else:
                self.ShowMessageBox('توجه',' لطفا از قسمت تنظیمات آی پی مرکز فرماندهی را اصلاح کنید')

    def handle_connection(self,conn,client_ip,client_port):
        data=conn.recv(5124)
        encoding=encrypt_cisco('qwe!@#rty$%^uio&*(oiuytrewq(*&^%$#@!')
        data=encoding.decrypt(data)
        data=data.decode('utf-8')
        arr=data.split(config.communicate_spliter)
        data_from=arr[0]
        data_action=arr[1]
        if data_from=="user":
            if data_action=="get_sender_ip":
                accept_list=MainKivyApp.conf.get_update_config('list_accept_users').split(',')
                if client_ip in accept_list:
                    data='ok'+MainKivyApp.conf.get_update_config('communicate_spliter')+MainKivyApp.conf.get_update_config('sender_ip')+MainKivyApp.conf.get_update_config('communicate_spliter')+MainKivyApp.conf.get_update_config('key')
                    print("recive req from ip {} and is exsist in accept list".format(client_ip))
                else:
                    data='not'+config.communicate_spliter+'no_your_ip_in_server'
                    print("recive req from ip {} and is not valid ip in list".format(client_ip))
                data=data.encode('utf-8')
                data=encoding.encrypt(data)
                conn.send(data)
        elif data_from=="sender":
            if data_action=="every_time_send":
                MainKivyApp.conf.set_new_val_data('last_time_recive',str(datetime.datetime.now()))
                MainKivyApp.conf.set_new_val_data('sender_ip',str(client_ip))
                MainKivyApp.conf.set_new_val_data('key',int(arr[2]))
                size_sender=arr[3]+","+arr[4]+","+arr[5]
                MainKivyApp.conf.set_new_val_data('size_sender',size_sender)
                MainKivyApp.app.check_and_update_state_connection()

        conn.close()


    def init_persian_text(self,text):
        reshaped_text = arabic_reshaper.reshape(text)
        bidi_text = bidi.algorithm.get_display(reshaped_text)
        return bidi_text

    def get_list_sal(self):
        list_sal=[str(x) for x in range(1398,1420)]
        return list_sal
    def get_list_mah(self):
        list_mah=[str(x) for x in range(1,13)]
        return list_mah
    def get_list_rooz(self):
        list_rooz=[str(x) for x in range(1,32)]
        return list_rooz
    def get_list_saat(self):
        list_saat=list()
        for i in range(0,24):
            s=str(i)
            if i< 10:
                s="0"+str(i)
            list_saat.append(s)
        return list_saat

    def get_list_soojeh(self):
        path=os.getcwd()+"/media"
        if os.path.isdir(path):
            dirs=os.listdir(path)
            return dirs
        else:
            return list()

    def get_list_up_middle_down(self):
        ls=list()
        ls.append(self.init_persian_text('بالا'))
        ls.append(self.init_persian_text('متوسط'))
        ls.append(self.init_persian_text('پایین'))
        return ls

    def convert_code_string(self,key):
        return self.init_persian_text(translate.mytr.get(key))

    def change_screen_for_refresh(self,first,second):
        MainKivyApp.my_screenmanager.current=first
        MainKivyApp.my_screenmanager.current=second

    def check_persian_char(self,body):
        ret=""
        for x in body:
            if 0>ord(x) > 500 :
                ret="en"
                break
            elif 1500>ord(x)>2000:
                ret="fa"
                break
            elif 60000>ord(x)<70000:
                ret="fa_k"
                break

        return ret

    def update_state_icon(self,dt):
        MainKivyApp.my_screenmanager.ids.state_connection.source=self.src_state_icon
        MainKivyApp.my_screenmanager.ids.state_connection.reload()
    def check_and_update_state_connection(self):
        now=datetime.datetime.now()
        before=MainKivyApp.conf.get_update_config('last_time_recive')
        if len(before)>0:
            before=parser.parse(before)
            diff=(now-before).total_seconds()
            text=""
            if 65>diff>0:
                self.src_state_icon=str(config.state_icon_green)
                Clock.schedule_once(self.update_state_icon,1.0/30)
                zaman=str(int(diff))
                if diff>1:
                    text=MainKivyApp.app.init_persian_text(" ثانیه قبل ")+zaman+MainKivyApp.app.init_persian_text(" ارتباط برقرار است ")
                else:
                    text=MainKivyApp.app.init_persian_text(" ارتباط برقرار است ")
            elif 3600>diff>65:
                self.src_state_icon=str(config.state_icon_silver)
                Clock.schedule_once(self.update_state_icon,1.0/30)
                zaman=str(int(diff/60))
                text=MainKivyApp.app.init_persian_text(" دقیقه قبل ")+zaman+MainKivyApp.app.init_persian_text(" ارتباط قطع است ")
            elif diff>3600:
                self.src_state_icon=str(config.state_icon_red)
                Clock.schedule_once(self.update_state_icon,1.0/30)
                zaman=str(int(diff/3600))
                text=MainKivyApp.app.init_persian_text(" ساعت قبل ")+zaman+MainKivyApp.app.init_persian_text(" ارتباط قطع است ")
            MainKivyApp.my_screenmanager.ids.txt_info_last_time.text=text
        else:
            self.src_state_icon=str(config.state_icon_red)
            Clock.schedule_once(self.update_state_icon,1.0/30)
            MainKivyApp.my_screenmanager.ids.txt_info_last_time.text=MainKivyApp.app.init_persian_text("ارتباط قطع است")

        if len(MainKivyApp.conf.get_update_config('soojeh_name'))>0:
            MainKivyApp.my_screenmanager.ids.txt_info_soojeh_name.text=MainKivyApp.conf.get_update_config('soojeh_name')
        size_sender=MainKivyApp.conf.get_update_config('size_sender')
        if len(size_sender)>0:
            gb=MainKivyApp.app.init_persian_text(" گیگ ")
            total=MainKivyApp.app.init_persian_text("کل حافظه:")
            total+="\r\n"
            tmp=str(eval(size_sender.split(',')[0]))
            if tmp.find('.')>-1:
                arr=tmp.split('.')
                tmp=arr[0]+'.'+arr[1][0:3]
            total+=gb+tmp
            used=MainKivyApp.app.init_persian_text("حافظه پر شده:")
            used+="\r\n"
            tmp=str(eval(size_sender.split(',')[1]))
            if tmp.find('.')>-1:
                arr=tmp.split('.')
                tmp=arr[0]+'.'+arr[1][0:3]
            used+=gb+tmp

            free=MainKivyApp.app.init_persian_text("حافظه خالی:")
            free+="\r\n"
            tmp=str(eval(size_sender.split(',')[2]))
            if tmp.find('.')>-1:
                arr=tmp.split('.')
                tmp=arr[0]+'.'+arr[1][0:3]
            free+=gb+tmp

            MainKivyApp.my_screenmanager.ids.txt_info_total_hard_size.text=total
            MainKivyApp.my_screenmanager.ids.txt_info_used_hard_size.text=used
            MainKivyApp.my_screenmanager.ids.txt_info_free_hard_size.text=free
            if eval(size_sender.split(',')[2])<int(config.min_size_sender_for_alert):
                min_size=str(int(config.min_size_sender_for_alert))
                msg='فضای خالی در سیستم فرستنده کمتر از '+min_size+' گیگ میباشد '
                MainKivyApp.app.ShowMessageBox('هشدار',msg)



    def clicked_reset(self):
        threading.Thread(target=self.init_reset).start()
    def init_reset(self):
        layout=BoxLayout(padding=10,orientation="vertical")
        text=self.init_persian_text('آیا میخواهید سیستم فرستنده راه اندازی مجدد شود؟')
        popupLabel= Label(text=text,font_size=20,font_name="Assets/Fonts/BKoodakBold.ttf",size_hint=(1,.4))
        layout.add_widget(popupLabel)
        layout_btn=BoxLayout(padding=30,orientation="horizontal",size_hint=(1,.6))
        btn_cancel=Button(text=self.init_persian_text("انصراف"),font_size=20,font_name="Assets/Fonts/BKoodakBold.ttf",size_hint=(.4,1))
        btn_cancel.on_press=self.click_cancel_restart
        btn_ok=Button(text=self.init_persian_text("تایید"),font_size=20,font_name="Assets/Fonts/BKoodakBold.ttf",size_hint=(.4,1))
        btn_ok.on_press=self.click_ok_restart
        layout_btn.add_widget(btn_cancel)
        layout_btn.add_widget(btn_ok)
        layout.add_widget(layout_btn)
        self.popup_rest = Popup(title=self.init_persian_text('توجه'),content=layout,size_hint=(.7,.3),auto_dismiss = False)
        self.popup_rest.title_font="Assets/Fonts/BKoodakBold.ttf"
        self.popup_rest.title_size=20
        self.popup_rest.title_align="right"

        self.popup_rest.open()
    def click_cancel_restart(self):
        self.popup_rest.dismiss()
    def click_ok_restart(self):
        self.popup_rest.dismiss()
        threading.Thread(target=self.do_restart).start()

    def do_restart(self):
        try:
            self.show_popup()
            encoding1=encrypt_cisco('qwe!@#rty$%^uio&*(oiuytrewq(*&^%$#@!')
            data="qazxsw".encode(encoding='utf-8')
            socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            ip_port=(str(config.sender_ip),int(config.port_remote))
            socket1.connect(ip_port)
            socket1.sendall(data)
            do=True
            while do:
                try:
                    data = socket1.recv(1024)
                    data=encoding1.decrypt(data)
                    data=data.decode('utf-8')
                    key=int(data)
                    key_code=MainKivyApp.gen.get_uniq_key(key)
                    encoding2=encrypt_cisco(key_code)
                    sender_data='re@1234se78#$%90t'.encode('utf-8')
                    sender_data=encoding2.encrypt(sender_data)
                    socket1.sendall(sender_data)
                    while True:
                        data=socket1.recv(1024)
                        data=data.decode('utf-8')
                        if data=="88":
                            self.close_popup()
                            MainKivyApp.app.ShowMessageBox('توجه','راه اندازی مجدد فرستنده با موفقیت انجام شد')
                            socket1.close()
                        elif data=="77":
                            self.close_popup()
                            MainKivyApp.app.ShowMessageBox('توجه','متاسفانه انجام نشد')
                            socket1.close()
                        do=False
                        break
                except:
                    self.close_popup()
                    socket1.close()
                    do=False
                    break
        except:
            socket1.close()
            self.close_popup()
            traceback.print_exc()

    def get_ip_list(self):
        try:
            list_ip=socket.gethostbyname_ex(socket.gethostname())[2]
            return list_ip
        except:
            return 0

    def ShowMessageBox(self,title,message):
        msg=MessageBox(title,message,MainKivyApp.app)
        msg.show_message_box()

    def go_to_page(self,page_name):
        MainKivyApp.my_screenmanager.current=page_name

    def show_popup(self):
        try:
            self.popup=PopUp('در حال اتصال','لطفا صبر کنید',MainKivyApp.app)
            self.popup.show_popup_loading_dynamic()
        except:
            pass
    def close_popup(self):
        try:
            self.popup.close()
        except:
            pass

if __name__=="__main__":
    main=MainKivyApp()
    main.run()

