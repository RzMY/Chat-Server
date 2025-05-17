from django.db import models

# 用户模型
class User(models.Model):
    id = models.IntegerField(primary_key=True)
    user_name = models.CharField(max_length=100)
    password = models.CharField(max_length=100, blank=True, null=True)
    age = models.IntegerField(default=0)
    phone = models.CharField(max_length=20, blank=True, null=True)
    avatar_path = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user'

# 对话模型
class Conversation(models.Model):
    id = models.CharField(primary_key=True, max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations')
    title = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'conversation'

# 消息模型
class Message(models.Model):
    id = models.BigIntegerField(primary_key=True)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=20)
    content = models.TextField()
    time = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'message'
        ordering = ['id']