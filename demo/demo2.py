import face_recognition
import numpy as np

image1 = face_recognition.load_image_file("C:\\Users\\RateMY\\Documents\\Code\\test2\\Test\\faceimage\\71.jpg")
v1 = face_recognition.face_encodings(image1)[0]
image2 = face_recognition.load_image_file("C:\\Users\\RateMY\\Documents\\Code\\test2\\Test\\faceimage\\541.jpg")
v2 = face_recognition.face_encodings(image2)[0]

d = np.linalg.norm(v1 - v2)

if d < 0.5:
    print("是一个人")
elif d < 1.0:
    print("不是一个人")