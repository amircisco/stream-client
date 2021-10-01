import cv2
import config
import time
from PIL import ImageTk
from PIL import Image
from queue import Queue




def detect_faces(frame,width_img_detect,stack,tbl):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faceCascade_haar=cv2.CascadeClassifier(config.cascPathhaar)
    eye_cascade=cv2.CascadeClassifier(config.cascPatheye)
    faces =faceCascade_haar.detectMultiScale(
    gray,
    scaleFactor=1.1,
    minNeighbors=5,
    minSize=(30, 30),
    flags = cv2.CASCADE_SCALE_IMAGE
    )
    for (x, y, w, h) in faces:
        #cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        roi_gray=gray[y:y+h, x:x+w]
        eyes=eye_cascade.detectMultiScale(roi_gray)
        for(ex,ey,ew,eh) in eyes:
            croped=frame[y:h+y,x:w+x]
            cur=time.time()
            name_face=config.face_1+"face_org_"+str(cur)+".jpg"
            name_crop=config.face_1+"face_crp_"+str(cur)+".jpg"
            show_face(croped,width_img_detect,stack,tbl)
            cv2.imwrite(name_face,frame)
            cv2.imwrite(name_crop,croped)
            break


def show_images(frame,label):
    frame=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
    img=ImageTk.PhotoImage(image=Image.fromarray(frame))
    label.configure(image=img)
    label.photo_ref=img


def show_face(frame,width_img_detect,stack,tbl):
        frame=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        w=width_img_detect
        frame=cv2.resize(frame,(w,w))
        img=ImageTk.PhotoImage(image=Image.fromarray(frame))
        stack.push(img)
        lists=tbl.winfo_children()
        for item in lists:
            if(item.cget("bg")=="red"):
                item.configure(bg="white")
        index=stack.last_index
        index-=1
        lists[index].configure(image=stack.arr[index],bg="red")

def save_video(frame,out):
    out.write(frame)