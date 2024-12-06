'''
Author: HDJ
StartDate: please fill in
LastEditTime: 2024-12-05 01:07:44
FilePath: \pythond:\LocalUsers\Goodnameisfordoggy-Gitee\JD-Automated-Tools\JD-AutomaticEvaluate\src\api_service.py
Description: 

				*		写字楼里写字间，写字间里程序员；
				*		程序人员写程序，又拿程序换酒钱。
				*		酒醒只在网上坐，酒醉还来网下眠；
				*		酒醉酒醒日复日，网上网下年复年。
				*		但愿老死电脑间，不愿鞠躬老板前；
				*		奔驰宝马贵者趣，公交自行程序员。
				*		别人笑我忒疯癫，我笑自己命太贱；
				*		不见满街漂亮妹，哪个归得程序员？    
Copyright (c) 2024 by HDJ, All Rights Reserved. 
'''
import os
import requests
from dotenv import load_dotenv
load_dotenv() # 加载换境变量，如果配置了 .env 文件

XAI_API_KEY = os.getenv('XAI_API_KEY')

def get_response_xai(content: str, model: str):
    """调用 api 并返回响应信息的 content"""
    url = 'https://api.x.ai/v1/chat/completions'
    api_key = XAI_API_KEY

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }

    data = {
        'model': f'{model}',
        'messages': [
            {'role': 'system', 'content': "You are Grok, a chatbot inspired by the Hitchhikers Guide to the Galaxy."},
            {'role': 'user', 'content': content}
        ]
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()  # 如果状态码不是 2xx 或 3xx，会抛出 HTTPError
        msg = response.json()['choices'][0]['message']['content']
        return msg
    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 400:
            print(f"HTTP 400 Error: 请检查您的API Key是否正确配置")
            print(f"Response Body: {response.text}")  # 输出返回的错误信息
        else:
            print(f"HTTP {response.status_code} error: {http_err}")
        return ""
    except Exception as err:
        print(f"Other error occurred: {err}")
        return ""
        
    