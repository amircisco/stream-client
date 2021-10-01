from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.uix.videoplayer import VideoPlayer


class CustomVideoPlayer():
    def __init__(self,address):
        self.address=address
    def show_video_dialog(self):
        layout=BoxLayout(orientation="vertical")
        self.popupLabel= Label(text=self.address,font_size=14,size_hint=(None,None),width=640,height=15)
        layout.add_widget(self.popupLabel)
        self.vid=VideoPlayer(source=self.address,state='play',options={'allow_stretch':False,'eos':'loop'},size_hint=(None,None),width=640,height=480)
        layout.add_widget(self.vid)
        self.popup = Popup(content=layout,size_hint=(None,None),width=664,height=510,auto_dismiss = True,padding=10)
        self.popup.open()


    def close(self):
        try:
            self.popup.dismiss()
        except:
            print("pop up dont run")


