# backend/api/views/face_views.py
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from util.ImageUtil import *
from util.RandomUtil import *
import cv2
import face_recognition
import os
import numpy as np
import json
import jwt
import datetime
from ..models import User

# 人脸图像存储路径
FACE_URL = "C:\\Users\\RateMY\\Documents\\Code\\chat-server\\Chat-Server\\faceimage\\"
# JWT密钥
JWT_SECRET = "7f8786d9d74bc8bd19f92d0448ef6b2fecf11adf8ea8285fc2d9b9374fef2417"
JWT_ALGORITHM = "HS256"

@csrf_exempt
def faceCollect(request):
    if request.method == 'POST':
        image_array = get_image_array(request)
        if image_array is None:
            return JsonResponse({"code": 500, "msg": "图像处理失败"})
            
        image = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(image)
        
        if len(face_locations) == 0:
            return JsonResponse({"code": 500, "msg": "未检测到人脸"})
        
        try:
            new_face_encoding = face_recognition.face_encodings(image)[0]
            
            # 检查是否已存在相同人脸
            face_dir = os.listdir(FACE_URL)
            for face_file in face_dir:
                image_path = os.path.join(FACE_URL, face_file)
                known_face = face_recognition.load_image_file(image_path)
                known_face_encoding = face_recognition.face_encodings(known_face)[0]
                    
                distance = np.linalg.norm(new_face_encoding - known_face_encoding)
                
                if distance < 0.5:
                    id = face_file.split(".")[0]
                    user_info = query_face(id)
                    if user_info:
                        return JsonResponse({
                            "code": 400,
                            "msg": f"该人脸已采集，编号为{id}，姓名：{user_info[1]}"
                        })
        except Exception as e:
            print("检查人脸时出错:", str(e))
        
        # 处理新人脸注册
        image_bytes = get_image_byte(request)
        id = generate_unique_random(1, 1000)
        
        data = json.loads(request.body.decode('utf-8'))
        name = data['name']
        age = data['age']
        phone = data['phone']
        
        if not face_insert(id, name, age, phone):
            return JsonResponse({"code": 500, "msg": "数据库插入失败"})
            
        try:
            with open(FACE_URL + str(id) + ".jpg", "wb") as f:
                f.write(image_bytes)
            return JsonResponse({"code": 200, "msg": "人脸信息采集成功"})
        except Exception as e:
            face_delete(id)
            return JsonResponse({"code": 500, "msg": "图像文件保存失败"})
    else:
        return JsonResponse({"code": 500, "msg": "请求方式错误"})

@csrf_exempt
def faceDetect(request):
    if request.method == 'POST':
        image_array = get_image_array(request)
        if image_array is None:
            return JsonResponse({"code": 500, "msg": "图像处理失败"})
            
        image = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(image)
        
        if len(face_locations) == 0:
            return JsonResponse({"code": 500, "msg": "未检测到人脸"})
        
        v1 = face_recognition.face_encodings(image)[0]
        face_dir = os.listdir(FACE_URL)
        
        for face_file in face_dir:
            image_path = os.path.join(FACE_URL, face_file)
            image = face_recognition.load_image_file(image_path)
            v2 = face_recognition.face_encodings(image)[0]
            d = np.linalg.norm(v1 - v2)
            
            if d < 0.5:
                id = face_file.split(".")[0]
                user_info = query_face(id)
                if user_info:
                    # 创建JWT令牌
                    token = generate_token(id)
                    
                    # 构建用户信息
                    userInfo = {
                        "id": user_info[0],
                        "name": user_info[1],
                        "age": user_info[2],
                        "phone": user_info[3],
                        "avatar": f"https://10.0.0.2:8887/static/avatar/{id}" + ".png",
                    }
                    
                    return JsonResponse({
                        "code": 200,
                        "msg": f"登录成功，欢迎您！",
                        "userInfo": userInfo,
                        "token": token
                    })
        
        return JsonResponse({"code": 500, "msg": "未找到匹配的人脸"})
    else:
        return JsonResponse({"code": 500, "msg": "请求方式错误"})
    
def get_user_info(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        user_id = data.get('user_id')
        
        if not user_id:
            return JsonResponse({"code": 400, "msg": "缺少用户ID"})
        
        user_info = query_face(user_id)
        if user_info:
            userInfo = {
                "id": user_info[0],
                "name": user_info[1],
                "age": user_info[2],
                "phone": user_info[3],
                "avatar": f"https://10.0.0.2:8887/static/avatar/{user_info[0]}.png",
            }
            return JsonResponse({
                "code": 200,
                "msg": "获取用户信息成功",
                "userInfo": userInfo
            })
        else:
            return JsonResponse({"code": 404, "msg": "用户信息不存在"})

def face_avatar(request, user_id):
    """获取用户头像"""
    try:
        image_path = os.path.join(FACE_URL, f"{user_id}.jpg")
        with open(image_path, "rb") as f:
            return HttpResponse(f.read(), content_type="image/jpeg")
    except:
        # 返回默认头像
        return HttpResponse(status=404)

# 修改数据库操作函数
def face_insert(id, name, age, phone):
    try:
        # 使用统一的User模型
        User.objects.create(
            id=id,
            user_name=name,
            age=age,
            phone=phone,
            avatar_path=f"{id}.jpg"  # 保存头像路径
        )
        return True
    except Exception as e:
        print("Error: ", e)
        return False

def query_face(id):
    try:
        user = User.objects.filter(id=id).first()
        if user:
            return (user.id, user.user_name, user.age, user.phone)
        return None
    except Exception as e:
        print("Error querying record: ", e)
        return None

def face_delete(id):
    try:
        user = User.objects.get(id=id)
        user.delete()
    except Exception as e:
        print("Error deleting record: ", e)

# 修改 JWT 令牌生成函数，添加更多用户信息
def generate_token(user_id):
    user = User.objects.get(id=user_id)
    payload = {
        'user_id': user_id,
        'user_name': user.user_name,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
        'iat': datetime.datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)