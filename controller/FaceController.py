from util.ImageUtil import *
from django.http import JsonResponse
import cv2
import face_recognition
from util.RandomUtil import *
import pymysql

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
                        "msg": "success",
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