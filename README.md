# Chat-Server

## 项目介绍

Chat-Server 是一个基于 Django 框架的聊天和人脸识别项目。该项目包含多个 Django 应用程序和模块，如 `api` 和 `chatweb`，并使用了多个外部库，如 `opencv-python`、`face-recognition`、`requests` 和 `openai`。

## 功能

- 用户管理
- 聊天功能
- 人脸识别功能

## 安装步骤

1. 克隆项目到本地：
   ```bash
   git clone https://github.com/RzMY/Chat-Server.git
   cd Chat-Server
   ```

2. 创建并激活虚拟环境：
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate  # Windows
   ```

3. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

4. 运行数据库迁移：
   ```bash
   python manage.py migrate
   ```

5. 启动开发服务器：
   ```bash
   python manage.py runserver
   ```

## 使用方法

### 用户管理

#### User 模型

- `id`: 用户的唯一标识符
- `user_name`: 用户名
- `password`: 用户密码
- `age`: 用户年龄
- `phone`: 用户电话
- `avatar_path`: 用户头像路径
- `created_at`: 用户创建时间

### 聊天功能

#### Conversation 模型

- `id`: 会话的唯一标识符
- `user`: 关联的用户
- `title`: 会话标题
- `created_at`: 会话创建时间

#### Message 模型

- `id`: 消息的唯一标识符
- `conversation`: 关联的会话
- `role`: 消息发送者的角色（用户或助手）
- `content`: 消息内容
- `time`: 消息发送时间
- `created_at`: 消息创建时间

### API 视图函数

#### `sendMessage`

使用 DeepSeek API 处理聊天请求。

#### `sendMessageOllama`

使用本地 Ollama 模型处理聊天请求。

#### `streamMessage`

流式返回消息，模拟打字效果。

#### `streamMessageOllama`

使用本地 Ollama 模型处理流式聊天请求。

#### `get_conversations`

获取用户的所有会话。

#### `get_conversation_messages`

获取特定会话的所有消息。

#### `create_conversation`

创建新会话。

#### `save_message`

保存消息。

#### `update_conversation_title`

更新会话标题。

#### `delete_conversation`

删除会话。

### 人脸识别功能

#### `faceCollect`

采集人脸信息。

#### `faceDetect`

检测人脸信息。

#### `get_user_info`

获取用户信息。

#### `face_avatar`

获取用户头像。

## URL 路由

### 人脸相关接口

- `faceCollect/`: 采集人脸信息
- `faceDetect/`: 检测人脸信息
- `face/avatar/<str:user_id>`: 获取用户头像
- `getUserInfo/`: 获取用户信息

### 聊天相关接口

- `sendMessage/`: 发送消息
- `sendMessageOllama/`: 发送消息（使用 Ollama 模型）
- `streamMessage/`: 流式返回消息
- `streamMessageOllama/`: 流式返回消息（使用 Ollama 模型）

### 聊天记录存储相关接口

- `conversations/`: 获取所有会话
- `conversations/<str:conversation_id>/messages/`: 获取特定会话的所有消息
- `conversations/create/`: 创建新会话
- `conversations/message/save/`: 保存消息
- `conversations/<str:conversation_id>/update-title/`: 更新会话标题
- `conversations/<str:conversation_id>/delete/`: 删除会话
