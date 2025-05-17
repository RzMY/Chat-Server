from django.urls import path
from .views import face_views, chat_views

urlpatterns = [
    # 人脸相关接口
    path('faceCollect/', face_views.faceCollect, name='face-collect'),
    path('faceDetect/', face_views.faceDetect, name='face-detect'),
    path('face/avatar/<str:user_id>', face_views.face_avatar, name='face-avatar'),
    path('getUserInfo/', face_views.get_user_info, name='get-user-info'),
    
    # 聊天相关接口
    path('sendMessage/', chat_views.sendMessage, name='send-message'),
    path('sendMessageOllama/', chat_views.sendMessageOllama, name='send-message-ollama'),
    path('streamMessage/', chat_views.streamMessage, name='stream-message'),
    path('streamMessageOllama/', chat_views.streamMessageOllama, name='stream-message-ollama'),

    # 聊天记录存储相关接口
    path('conversations/', chat_views.get_conversations, name='get-conversations'),
    path('conversations/<str:conversation_id>/messages/', chat_views.get_conversation_messages, name='get-conversation-messages'),
    path('conversations/create/', chat_views.create_conversation, name='create-conversation'),
    path('conversations/message/save/', chat_views.save_message, name='save-message'),
    path('conversations/<str:conversation_id>/update-title/', chat_views.update_conversation_title, name='update-conversation-title'),
    path('conversations/<str:conversation_id>/delete/', chat_views.delete_conversation, name='delete-conversation'),
]