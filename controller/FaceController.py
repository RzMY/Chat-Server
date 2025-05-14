from util.ImageUtil import *
from django.http import JsonResponse
import cv2
import face_recognition
from util.RandomUtil import *
import pymysql
import os
import numpy as np

face_url = "C:\\Users\\RateMY\\Documents\\Code\\test2\\Test\\faceimage\\"

def faceCollect(request):
    if request.method == 'POST':
        image_array = get_image_array(request)
        image = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(image)
        if len(face_locations) == 0:
            data = {
                "code": 500,
                "msg": "未检测到人脸",
            }
            return JsonResponse(data)
        else:
            try:
                new_face_encoding = face_recognition.face_encodings(image)[0]
                
                face_dir = os.listdir(face_url)
                for face_file in face_dir:
                    image_path = os.path.join(face_url, face_file)
                    known_face = face_recognition.load_image_file(image_path)
                    known_face_encoding = face_recognition.face_encodings(known_face)
                        
                    distance = np.linalg.norm(new_face_encoding - known_face_encoding)
                    
                    if distance < 0.5:
                        id = face_file.split(".")[0]
                        user_info = query_face(id)
                        if user_info:
                            data = {
                                "code": 400,
                                "msg": f"该人脸已采集，编号为{id}，姓名：{user_info[1]}",
                            }
                            return JsonResponse(data)
            except Exception as e:
                print("检查人脸时出错:", str(e))
            
            image_bytes = get_image_byte(request)
            id = generate_unique_random(1, 1000)
            
            data = json.loads(request.body.decode('utf-8'))
            name = data['name']
            age = data['age']
            phone = data['phone']
            
            if not face_insert(id, name, age, phone):
                data = {
                    "code": 500,
                    "msg": "数据库插入失败",
                }
                return JsonResponse(data)
            else:
                try:
                    with open(face_url + str(id) + ".jpg", "wb") as f:
                        f.write(image_bytes)
                    data = {
                        "code": 200,
                        "msg": "人脸信息采集成功",
                    }
                    return JsonResponse(data)
                except Exception as e:
                    face_delete(id)
                    data = {
                        "code": 500,
                        "msg": "图像文件保存失败",
                    }
                    return JsonResponse(data)
    else:
        data = {
            "code": 500,
            "msg": "请求方式错误",
        }
        return JsonResponse(data)

def face_insert(id, name, age, phone):
    db = None
    try:
        db = pymysql.connect(host="localhost", user="root", password="root", database="face")
        cursor = db.cursor()
        sql = "INSERT INTO user_info (id, user_name, age, phone) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (id, name, age, phone))
        db.commit()
        return True
    except Exception as e:
        print("Error: ", e)
        if db:
            db.rollback()
        return False
    finally:
        if db:
            db.close()

def query_face(id):
    try:
        db = pymysql.connect(host="localhost", user="root", password="root", database="face")
        cursor = db.cursor()
        sql = "SELECT * FROM user_info WHERE id = %s"
        cursor.execute(sql, (id,))
        result = cursor.fetchone()
        return result if result else None
    except Exception as e:
        print("Error querying record: ", e)
        return None

def face_delete(id):
    db = None
    try:
        db = pymysql.connect(host="localhost", user="root", password="root", database="face")
        cursor = db.cursor()
        sql = "DELETE FROM user_info WHERE id = %s"
        cursor.execute(sql, (id,))
        db.commit()
    except Exception as e:
        print("Error deleting record: ", e)
        if db:
            db.rollback()
    finally:
        if db:
            db.close()

def faceDetect(request):
    if request.method == 'POST':
        image_array = get_image_array(request)
        image = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(image)
        if len(face_locations) == 0:
            data = {
                "code": 500,
                "msg": "未检测到人脸",
            }
            return JsonResponse(data)
        else:
            v1 = face_recognition.face_encodings(image)[0]
            face_dir = os.listdir(face_url)
            for face_file in face_dir:
                image_path = os.path.join(face_url, face_file)
                image = face_recognition.load_image_file(image_path)
                v2 = face_recognition.face_encodings(image)[0]
                d = np.linalg.norm(v1 - v2)
                if d < 0.5:
                    id = face_file.split(".")[0]
                    user_info = query_face(id)
                    data = {
                        "code": 200,
                        "msg": f"编号为{id}的用户，欢迎您！,你的信息如下：姓名：{user_info[1]},年龄：{user_info[2]},电话：{user_info[3]}",
                    }
                    return JsonResponse(data)
            data = {
                "code": 500,
                "msg": "未找到匹配的人脸",
            }
            return JsonResponse(data)
    else:
        data = {
            "code": 500,
            "msg": "请求方式错误",
        }
        return JsonResponse(data)