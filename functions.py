import tkinter as tk
import cv2
from PIL import ImageTk
from PIL import Image
import config
import time
from multiprocessing import Queue


q1_show=Queue()
q1_face=Queue()
q1_face_crop=Queue()
q1_save=Queue()

q2_show=Queue()
q2_face=Queue()
q2_face_crop=Queue()
q2_save=Queue()

q3_show=Queue()
q3_face=Queue()
q3_face_crop=Queue()
q3_save=Queue()

q4_show=Queue()
q4_face=Queue()
q4_face_crop=Queue()
q4_save=Queue()

def setting():
    print("ok settings...")

def generate_tbl2(row_count,column_count,w,tbl):
    for i in range(row_count):
        for j in range(column_count):
            l=tk.Label(tbl)
            l.grid(row=i,column=j)
            """frame=cv2.imread("1.jpg")
            frame=cv2.resize(frame,(w,w))
            frame=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
            img=ImageTk.PhotoImage(image=Image.fromarray(frame))
            l.image=img
            l.configure(image=img)"""

def generate_list(tbl1,arr):
    txt=tk.Text(tbl1,width=15)
    txt.grid(row=0,column=0,sticky="wnsnwsw")
    scroll_y=tk.Scrollbar(tbl1,orient="vertical",command=txt.yview)
    scroll_y.grid(row=0,column=1,sticky="ensnese")
    txt.configure(yscrollcommand=scroll_y.set)
    long_list="\n".join([item for item in arr])
    txt.insert("1.0",long_list)
    txt.configure(state="disabled",relief="flat",bg=tbl1.cget("bg"))




arr=[]
arr.append("amir")
arr.append("jahani")
arr.append("beyg")
arr.append("harki")
arr.append("cher")
arr.append("masalan")
arr.append("harchi")
arr.append("amir")
arr.append("jahani")
arr.append("beyg")
arr.append("harki")
arr.append("cher")
arr.append("masalan")
arr.append("harchi")
arr.append("amir")
arr.append("jahani")
arr.append("beyg")
arr.append("harki")
arr.append("cher")
arr.append("masalan")
arr.append("harchi")
arr.append("amir")
arr.append("jahani")
arr.append("beyg")
arr.append("harki")
arr.append("cher")
arr.append("masalan")
arr.append("harchi")
arr.append("amir")
arr.append("jahani")
arr.append("beyg")
arr.append("harki")
arr.append("cher")
arr.append("masalan")
arr.append("harchi")
