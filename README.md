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

## 项目目录结构

```
Chat-Server/
├── api/
│   ├── migrations/
│   │   ├── __init__.py
│   │   └── 0001_initial.py
│   ├── __init__.py
│   ├── models.py
│   ├── urls.py
│   └── views/
│       ├── __init__.py
│       ├── chat_views.py
│       └── face_views.py
├── chatweb/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── faceimage/
├── static/
├── util/
│   ├── __init__.py
│   ├── ImageUtil.py
│   └── RandomUtil.py
├── .gitignore
├── cert.crt
├── cert.key
├── db.sqlite3
├── manage.py
├── requirements.txt
└── start.py
```

### 主要目录和文件说明

- `api/`: 包含与API相关的所有代码。
  - `migrations/`: 数据库迁移文件。
  - `models.py`: 定义数据库模型。
  - `urls.py`: 定义API的URL路由。
  - `views/`: 包含处理API请求的视图函数。
- `chatweb/`: 包含Django项目的设置和配置文件。
  - `settings.py`: 项目的主要设置文件。
  - `urls.py`: 项目的URL路由配置。
- `faceimage/`: 存储人脸图像的目录。
- `static/`: 存储静态文件的目录。
- `util/`: 包含一些实用工具函数。
- `.gitignore`: Git忽略文件配置。
- `cert.crt` 和 `cert.key`: SSL证书文件。
- `db.sqlite3`: SQLite数据库文件。
- `manage.py`: Django项目的管理脚本。
- `requirements.txt`: 项目依赖文件。
- `start.py`: 启动项目的脚本。
