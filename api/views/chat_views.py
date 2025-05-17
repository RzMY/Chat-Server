# backend/api/views/chat_views.py
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from openai import OpenAI
import requests
import json
import jwt
import time
from ..models import User, Conversation, Message
import datetime

# JWT密钥
JWT_SECRET = "7f8786d9d74bc8bd19f92d0448ef6b2fecf11adf8ea8285fc2d9b9374fef2417"
JWT_ALGORITHM = "HS256"

def get_user_id_from_token(request):
    """从请求头中的token获取用户ID"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    print(f"接收到的token: {token}")
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get('user_id')
        return user_id
    except Exception as e:
        print(f"JWT解码错误: {str(e)}")
        return None

@csrf_exempt
def sendMessage(request):
    """使用DeepSeek API处理聊天请求"""
    # 验证令牌
    user_id = get_user_id_from_token(request)
    if not user_id:
        return JsonResponse({"code": 401, "msg": "未授权访问"})
    
    try:
        data = json.loads(request.body.decode('utf-8'))
        message = data.get('message', '')
        conversation_id = data.get('conversationId', '')
        
        # 验证会话是否存在且属于该用户
        try:
            user = User.objects.get(id=user_id)
            conversation = Conversation.objects.get(id=conversation_id, user=user)
        except (User.DoesNotExist, Conversation.DoesNotExist):
            return JsonResponse({"code": 404, "msg": "会话不存在或不属于当前用户"})
        
        # 调用DeepSeek API
        client = OpenAI(api_key="", base_url="https://api.deepseek.com")

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": "" + message},
            ],
            stream=False
        )
        
        ai_response = response.choices[0].message.content
        
        # 保存用户消息到数据库
        user_msg_id = int(data.get('userMessageId', 0))
        if user_msg_id:
            Message.objects.create(
                id=user_msg_id,
                conversation=conversation,
                role="user",
                content=message,
                time=data.get('userMessageTime', '')
            )
        
        # 生成AI响应消息ID
        ai_msg_id = int(time.time() * 1000)
        
        # 保存AI响应到数据库
        Message.objects.create(
            id=ai_msg_id,
            conversation=conversation,
            role="assistant",
            content=ai_response,
            time=datetime.datetime.now().strftime('%H:%M:%S')
        )

        return JsonResponse({
            "code": 200,
            "msg": ai_response,
            "messageId": ai_msg_id,
            "conversationId": conversation_id
        })
    except Exception as e:
        print(f"DeepSeek API 错误: {str(e)}")
        return JsonResponse({
            "code": 500,
            "msg": f"处理请求时发生错误: {str(e)}",
            "conversationId": data.get('conversationId', '') if 'data' in locals() else ''
        })

@csrf_exempt
def sendMessageOllama(request):
    """使用本地Ollama模型处理聊天请求"""
    # 验证令牌
    user_id = get_user_id_from_token(request)
    if not user_id:
        return JsonResponse({"code": 401, "msg": "未授权访问"})
    
    try:
        data = json.loads(request.body.decode('utf-8'))
        message = data.get('message', '')
        conversation_id = data.get('conversationId', '')
        
        # 验证会话是否存在且属于该用户
        try:
            user = User.objects.get(id=user_id)
            conversation = Conversation.objects.get(id=conversation_id, user=user)
        except (User.DoesNotExist, Conversation.DoesNotExist) as e:
            print(f"会话验证错误: {str(e)}")
            return JsonResponse({"code": 404, "msg": "会话不存在或不属于当前用户"})
        
        param = {
            "model": "deepseek-r1:1.5b",
            "prompt": message,
            "stream": False,
        }
        response = requests.post("http://localhost:11434/api/generate", json=param)
        result = response.json()

        ai_response = result['response']
        print(f"AI响应: {ai_response}")
        # 保存用户消息到数据库
        user_msg_id = int(data.get('userMessageId', 0))
        if user_msg_id:
            try:
                Message.objects.create(
                    id=user_msg_id,
                    conversation=conversation,
                    role="user",
                    content=message,
                    time=data.get('userMessageTime', '')
                )
            except Exception as e:
                print(f"保存用户消息错误: {str(e)}")
                # 如果用户消息已存在，跳过保存但不中断处理
                pass
                
        import random
        ai_msg_id = int(time.time() * 1000) + random.randint(1, 999)
        
        # 确保ID唯一
        while Message.objects.filter(id=ai_msg_id).exists():
            ai_msg_id = int(time.time() * 1000) + random.randint(1, 999)
            
        Message.objects.create(
            id=ai_msg_id,
            conversation=conversation,
            role="assistant",
            content=ai_response,
            time=datetime.datetime.now().strftime('%H:%M:%S')
        )
        
        return JsonResponse({
            "code": 200,
            "msg": ai_response,
            "messageId": ai_msg_id,  # 返回消息ID
            "conversationId": conversation_id
        })
    except Exception as e:
        print(f"Ollama API 错误: {str(e)}")
        return JsonResponse({
            "code": 500,
            "msg": f"处理请求时发生错误: {str(e)}",
            "conversationId": data.get('conversationId', '') if 'data' in locals() else ''
        })

@csrf_exempt
def streamMessage(request):
    """流式返回消息，模拟打字效果"""
    # 验证令牌
    user_id = get_user_id_from_token(request)
    if not user_id:
        return JsonResponse({"code": 401, "msg": "未授权访问"})
    
    try:
        data = json.loads(request.body.decode('utf-8'))
        message = data.get('message', '')
        conversation_id = data.get('conversationId', '')
        
        # 验证会话是否存在且属于该用户
        try:
            user = User.objects.get(id=user_id)
            conversation = Conversation.objects.get(id=conversation_id, user=user)
        except (User.DoesNotExist, Conversation.DoesNotExist) as e:
            print(f"会话验证错误: {str(e)}")
            return JsonResponse({"code": 404, "msg": "会话不存在或不属于当前用户"})
        
        # 保存用户消息到数据库
        user_msg_id = int(data.get('userMessageId', 0))
        if user_msg_id:
            try:
                Message.objects.create(
                    id=user_msg_id,
                    conversation=conversation,
                    role="user",
                    content=message,
                    time=data.get('userMessageTime', '')
                )
            except Exception as e:
                print(f"保存用户消息错误: {str(e)}")
                # 消息可能已存在，跳过保存但不中断处理
                pass
        
        # 创建AI消息ID
        import random
        ai_msg_id = int(time.time() * 1000) + random.randint(1, 999)
        # 确保ID唯一
        while Message.objects.filter(id=ai_msg_id).exists():
            ai_msg_id = int(time.time() * 1000) + random.randint(1, 999)
        
        client = OpenAI(api_key="", base_url="https://api.deepseek.com")

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": "" + message},
            ],
            stream=True
        )
        
        def event_stream():
            full_response = ""
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    chunk_text = chunk.choices[0].delta.content
                    full_response += chunk_text
                    yield f"data: {json.dumps({'text': chunk_text, 'messageId': ai_msg_id})}\n\n"
                    time.sleep(0.01)  # 小延迟，模拟打字效果
            
            # 保存完整回复到数据库
            try:
                Message.objects.create(
                    id=ai_msg_id,
                    conversation=conversation,
                    role="assistant",
                    content=full_response,
                    time=datetime.datetime.now().strftime('%H:%M:%S')
                )
            except Exception as e:
                print(f"保存AI消息错误: {str(e)}")
            
            yield f"data: {json.dumps({'done': True, 'messageId': ai_msg_id})}\n\n"
            
        return StreamingHttpResponse(event_stream(), content_type='text/event-stream')
    except Exception as e:
        print(f"流式API错误: {str(e)}")
        return JsonResponse({
            "code": 500,
            "msg": f"处理请求时发生错误: {str(e)}",
        })

@csrf_exempt
def streamMessageOllama(request):
    """使用本地Ollama模型处理流式聊天请求"""
    # 验证令牌
    user_id = get_user_id_from_token(request)
    if not user_id:
        return JsonResponse({"code": 401, "msg": "未授权访问"})
    
    try:
        data = json.loads(request.body.decode('utf-8'))
        message = data.get('message', '')
        conversation_id = data.get('conversationId', '')
        
        # 验证会话是否存在且属于该用户
        try:
            user = User.objects.get(id=user_id)
            conversation = Conversation.objects.get(id=conversation_id, user=user)
        except (User.DoesNotExist, Conversation.DoesNotExist) as e:
            print(f"会话验证错误: {str(e)}")
            return JsonResponse({"code": 404, "msg": "会话不存在或不属于当前用户"})
        
        # 保存用户消息到数据库
        user_msg_id = int(data.get('userMessageId', 0))
        if user_msg_id:
            try:
                Message.objects.create(
                    id=user_msg_id,
                    conversation=conversation,
                    role="user",
                    content=message,
                    time=data.get('userMessageTime', '')
                )
            except Exception as e:
                print(f"保存用户消息错误: {str(e)}")
                # 消息可能已存在，跳过保存但不中断处理
                pass
        
        # 创建AI消息ID
        import random
        ai_msg_id = int(time.time() * 1000) + random.randint(1, 999)
        # 确保ID唯一
        while Message.objects.filter(id=ai_msg_id).exists():
            ai_msg_id = int(time.time() * 1000) + random.randint(1, 999)
        
        # 设置Ollama API参数
        param = {
            "model": "deepseek-r1:1.5b",
            "prompt": message,
            "stream": True,  # 启用流式输出
        }
        
        # 使用stream=True设置流式响应
        response = requests.post("http://localhost:11434/api/generate", json=param, stream=True)
        
        def event_stream():
            full_response = ""
            for line in response.iter_lines():
                if line:
                    json_data = json.loads(line.decode('utf-8'))
                    
                    # Ollama流式API会返回一个response字段包含生成的文本块
                    if 'response' in json_data:
                        chunk_text = json_data['response']
                        full_response += chunk_text
                        yield f"data: {json.dumps({'text': chunk_text, 'messageId': ai_msg_id})}\n\n"
                        time.sleep(0.01)  # 小延迟，模拟打字效果
                    
                    # 检查是否完成生成
                    if json_data.get('done', False):
                        # 保存完整回复到数据库
                        try:
                            Message.objects.create(
                                id=ai_msg_id,
                                conversation=conversation,
                                role="assistant",
                                content=full_response,
                                time=datetime.datetime.now().strftime('%H:%M:%S')
                            )
                        except Exception as e:
                            print(f"保存AI消息错误: {str(e)}")
                        
                        yield f"data: {json.dumps({'done': True, 'messageId': ai_msg_id})}\n\n"
                        break
            
        return StreamingHttpResponse(event_stream(), content_type='text/event-stream')
    except Exception as e:
        print(f"Ollama流式API错误: {str(e)}")
        return JsonResponse({
            "code": 500,
            "msg": f"处理请求时发生错误: {str(e)}",
            "conversationId": conversation_id if 'conversation_id' in locals() else ''
        })

@csrf_exempt
def get_conversations(request):
    """获取用户的所有会话"""
    user_id = get_user_id_from_token(request)
    if not user_id:
        return JsonResponse({"code": 401, "msg": "未授权访问"})
    
    try:
        user = User.objects.get(id=user_id)
        conversations = Conversation.objects.filter(user=user)
        
        result = []
        for conv in conversations:
            result.append({
                "id": conv.id,
                "title": conv.title,
                "date": conv.created_at.strftime('%Y-%m-%d'),
                "messages": []  # 不在列表页加载消息内容，减少数据传输
            })
        
        return JsonResponse({
            "code": 200,
            "conversations": result
        })
    except User.DoesNotExist:
        return JsonResponse({"code": 404, "msg": "用户不存在"})
    except Exception as e:
        return JsonResponse({"code": 500, "msg": f"服务器错误: {str(e)}"})

@csrf_exempt
def get_conversation_messages(request, conversation_id):
    """获取特定会话的所有消息"""
    user_id = get_user_id_from_token(request)
    if not user_id:
        return JsonResponse({"code": 401, "msg": "未授权访问"})
    
    try:
        user = User.objects.get(id=user_id)
        conversation = Conversation.objects.get(id=conversation_id, user=user)
        messages = conversation.messages.all()
        
        message_list = []
        for msg in messages:
            message_list.append({
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "time": msg.time
            })
        
        return JsonResponse({
            "code": 200,
            "messages": message_list
        })
    except User.DoesNotExist:
        return JsonResponse({"code": 404, "msg": "用户不存在"})
    except Conversation.DoesNotExist:
        return JsonResponse({"code": 404, "msg": "会话不存在"})
    except Exception as e:
        return JsonResponse({"code": 500, "msg": f"服务器错误: {str(e)}"})

@csrf_exempt
def create_conversation(request):
    """创建新会话"""
    if request.method != 'POST':
        return JsonResponse({"code": 405, "msg": "方法不允许"})
    
    user_id = get_user_id_from_token(request)
    if not user_id:
        return JsonResponse({"code": 401, "msg": "未授权访问"})
    
    try:
        data = json.loads(request.body.decode('utf-8'))
        conversation_id = data.get('id')
        title = data.get('title', '新对话')
        
        user = User.objects.get(id=user_id)
        
        # 创建会话
        conversation = Conversation.objects.create(
            id=conversation_id,
            user=user,
            title=title
        )
        
        return JsonResponse({
            "code": 200,
            "msg": "会话创建成功",
            "conversation": {
                "id": conversation.id,
                "title": conversation.title,
                "date": conversation.created_at.strftime('%Y-%m-%d')
            }
        })
    except User.DoesNotExist:
        return JsonResponse({"code": 404, "msg": "用户不存在"})
    except Exception as e:
        return JsonResponse({"code": 500, "msg": f"服务器错误: {str(e)}"})

@csrf_exempt
def save_message(request):
    """保存消息"""
    if request.method != 'POST':
        return JsonResponse({"code": 405, "msg": "方法不允许"})
    
    user_id = get_user_id_from_token(request)
    if not user_id:
        return JsonResponse({"code": 401, "msg": "未授权访问"})
    
    try:
        data = json.loads(request.body.decode('utf-8'))
        conversation_id = data.get('conversationId')
        message = data.get('message', {})
        
        user = User.objects.get(id=user_id)
        conversation = Conversation.objects.get(id=conversation_id, user=user)
        
        # 保存消息
        new_message = Message.objects.create(
            id=message.get('id'),
            conversation=conversation,
            role=message.get('role'),
            content=message.get('content'),
            time=message.get('time')
        )
        
        return JsonResponse({
            "code": 200,
            "msg": "消息保存成功",
            "messageId": new_message.id
        })
    except User.DoesNotExist:
        return JsonResponse({"code": 404, "msg": "用户不存在"})
    except Conversation.DoesNotExist:
        return JsonResponse({"code": 404, "msg": "会话不存在"})
    except Exception as e:
        return JsonResponse({"code": 500, "msg": f"服务器错误: {str(e)}"})

@csrf_exempt
def update_conversation_title(request, conversation_id):
    """更新会话标题"""
    if request.method != 'PUT':
        return JsonResponse({"code": 405, "msg": "方法不允许"})
    
    user_id = get_user_id_from_token(request)
    if not user_id:
        return JsonResponse({"code": 401, "msg": "未授权访问"})
    
    try:
        data = json.loads(request.body.decode('utf-8'))
        title = data.get('title')
        
        user = User.objects.get(id=user_id)
        conversation = Conversation.objects.get(id=conversation_id, user=user)
        
        # 更新标题
        conversation.title = title
        conversation.save()
        
        return JsonResponse({
            "code": 200,
            "msg": "会话标题更新成功"
        })
    except User.DoesNotExist:
        return JsonResponse({"code": 404, "msg": "用户不存在"})
    except Conversation.DoesNotExist:
        return JsonResponse({"code": 404, "msg": "会话不存在"})
    except Exception as e:
        return JsonResponse({"code": 500, "msg": f"服务器错误: {str(e)}"})

@csrf_exempt
def delete_conversation(request, conversation_id):
    """删除会话"""
    if request.method != 'DELETE':
        return JsonResponse({"code": 405, "msg": "方法不允许"})
    
    user_id = get_user_id_from_token(request)
    if not user_id:
        return JsonResponse({"code": 401, "msg": "未授权访问"})
    
    try:
        user = User.objects.get(id=user_id)
        conversation = Conversation.objects.get(id=conversation_id, user=user)
        
        # 删除会话及关联的所有消息
        conversation.delete()
        
        return JsonResponse({
            "code": 200,
            "msg": "会话删除成功"
        })
    except User.DoesNotExist:
        return JsonResponse({"code": 404, "msg": "用户不存在"})
    except Conversation.DoesNotExist:
        return JsonResponse({"code": 404, "msg": "会话不存在"})
    except Exception as e:
        return JsonResponse({"code": 500, "msg": f"服务器错误: {str(e)}"})

# JWT令牌验证
def verify_token(token):
    """验证JWT令牌"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return True
    except:
        return False