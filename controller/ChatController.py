from django.http import JsonResponse
from openai import OpenAI
import requests

def sendMessageOllama(request):
    message = request.GET.get('message')
    param = {
        "model": "deepseek-r1:1.5b",
        "prompt": message,
        "stream": False,
    }
    response = requests.post("http://localhost:11434/api/generate", json=param)
    data = response.json()
    data = {
        "code": 200,
        "msg": data['response'],
    }
    return JsonResponse(data)

def sendMessage(request):
    message = request.GET.get('message')

    client = OpenAI(api_key="sk-b1e42f0761ab4610aed2d21d76bcc53f", base_url="https://api.deepseek.com")

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "" + message},
        ],
        stream=False
    )

    data = {
        "code": 200,
        "msg": response.choices[0].message.content,
    }
    return JsonResponse(data)