'''
Author: HDJ
StartDate: please fill in
LastEditTime: 2025-03-26 22:58:40
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
Copyright (c) 2024-2025 by HDJ, All Rights Reserved. 
'''
import os
import sys
import ssl
import hmac
import json
import time
import queue
import base64
import typing
import hashlib
import requests
import datetime
import threading
import websocket  # 使用 websocket_client
from loguru import logger
from dotenv import load_dotenv
from abc import ABC, abstractmethod
from urllib.parse import urlparse, urlencode
from wsgiref.handlers import format_date_time

from .logger import get_logger
# 日志配置
LOG = get_logger()
# LOG = logger.bind(file="api_service")
# LOG.remove()
# LOG.add(
#     sink=sys.stdout,
#     format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{file.path}:{line}</cyan> | <level>{message}</level>",
#     level="INFO"
# )

__all__ = ["Http_XAI", "Ws_SparkAI"]

env_path = os.path.join(os.getcwd(), ".env")
if os.path.exists(env_path):
    load_dotenv(dotenv_path=env_path)
    LOG.success(f"从 {env_path} 文件加载了环境变量")
else:
    LOG.critical(f"{env_path} 文件缺失")
    
load_dotenv() # 加载换境变量，如果配置了 .env 文件


class Http_XAI(object):
    
    XAI_API_KEY = os.getenv('XAI_API_KEY')

    def __init__(self, content: str, model: str):
        self.content = content
        self.model = model

    def get_response(self):
        """调用 xAI 的 api 并返回响应信息的 content"""
        url = 'https://api.x.ai/v1/chat/completions'
        api_key = self.XAI_API_KEY

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }

        data = {
            'model': f'{self.model}',
            'messages': [
                {'role': 'system', 'content': "你是一个富家千金，时长在各大购物平台购买各类商品，从不吝啬。乐于在每次购物完成后对商品进行客观的评价。"},
                {'role': 'user', 'content': self.content}
            ],
            "stream": False,
            "temperature": 0.9
        }

        try:
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()  # 如果状态码不是 2xx 或 3xx，会抛出 HTTPError
            msg = response.json()['choices'][0]['message']['content']
            return msg
        except requests.exceptions.HTTPError as http_err:
            if response.status_code == 400:
                LOG.error(f"HTTP 400 Error: 请检查您的API Key是否正确配置")
                print(f"Response Body: {response.text}")  # 输出返回的错误信息
            else:
                LOG.error(f"HTTP {response.status_code} error: {http_err}")
            return ""
        except Exception as err:
            LOG.error(f"Other error occurred: {err}")
            return ""


class _WebSocketClient(ABC):
    """
    WebSocket client encapsulation, custom specification Used to establish a connection to the WebSocket server and to send and receive messages.

    Main functions:
        - Establish a WebSocket connection
        - Send a message to the server
        - Receive messages from the server
        - Handle connection state and messages

    Constructor Args:
        - ws_url (str): The URL of the WebSocket server.
    """
    def __init__(self, ws_url):
        self.ws_url = ws_url
        self.ws: websocket.WebSocketApp = None
        self.is_open_event = threading.Event()  # 用事件标志状态
        self.message_queue = queue.Queue()  # 用于存储服务器发送的消息

    @abstractmethod
    def connect(self):
        """
        Establish a WebSocket connection

        **Useage**

        ```py
        # 判断通道是否存在
        if self.ws is not None:
            LOG.info("WebSocket 连接已存在")
            return

        # 创建 WebSocketApp
        # 设置属性(若需)
        # 在新线程中启动
        
        LOG.info("等待连接建立...")
        if not self.is_open_event.wait(timeout=5): 
            LOG.error("WebSocket 连接超时")
            raise TimeoutError("WebSocket 连接超时")
        ```
        """
        # websocket.enableTrace(False) # 调试信息
        # self.ws = websocket.WebSocketApp(self.ws_url, on_open=_on_open, on_message=_on_message, on_error=_on_error, on_close=_on_close,)
        
        # threading.Thread(
        #     target=self.ws.run_forever,
        #     kwargs={"sslopt": {"cert_reqs": ssl.CERT_NONE}},
        #     daemon=True,  # 守护线程
        # ).start()

    def send(self, message):
        """Sends a message to the server"""
        if self.is_open_event.is_set():  # 确保连接已经建立
            self.ws.send(message)
        else:
            LOG.error("WebSocket not connected, unable to send message")

    def close(self):
        """Closes the WebSocket connection"""
        if self.ws:
            self.ws.close()
            self.ws = None

    def get_message(self, timeout=1):
        """Get the message sent by the server"""
        try:
            return self.message_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def _on_open(self, ws):
        """Callback when the WebSocket connection is successfully established.
    
        Args:
            ws (WebSocket): The WebSocket instance that has successfully connected.
        """
        self.is_open_event.set()  # 设置事件为 True
        LOG.success("WebSocket connection is successfully established")
    
    def _on_message(self, ws, message):
        """Callback when a message is received.
    
        Args:
            ws (WebSocket): The WebSocket instance that received the message.
            message (str): The message received from the WebSocket server.
        """
        LOG.info(f"Receive a message:{message}")
        self.message_queue.put(message)  # 将消息片段直接塞入对列

    def _on_error(self, ws, error):
        """
        Callback when an error occurs.
        
        Args:
            ws (WebSocket) : The WebSocket instance.
            error (Exception) : The error that occurred, containing details such as the error message or exception type.
        """
        LOG.error(f"An error occurs: {error}")

    def _on_close(self, ws, close_status_code, close_msg):
        """
        Callback when the WebSocket connection is closed.

        Args:
            ws (WebSocket) : The WebSocket instance.
            close_status_code (int) : The status code indicating the reason for closure.
            close_msg (str) : A message explaining the reason for closure.
        """
        self.is_open_event.clear()
        LOG.warning("WebSocket connection is closed")



class _Ws_Param_SparkAI(object):
    """调用讯飞星火 api 的 WebSocket url 生成"""
    def __init__(self, APPID, APIKey, APISecret, Spark_url):
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = APISecret
        self.host = urlparse(Spark_url).netloc
        self.path = urlparse(Spark_url).path
        self.Spark_url = Spark_url
    
    def create_url(self):
        """根据目标服务器要求生成鉴权url"""
        # 生成RFC1123格式的时间戳
        now = datetime.datetime.now()
        date = format_date_time(time.mktime(now.timetuple()))

        # 拼接字符串
        signature_origin = "host: " + self.host + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + self.path + " HTTP/1.1"

        # 进行 hmac-sha256 进行加密
        signature_sha: bytes = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'), digestmod=hashlib.sha256).digest()

        signature_sha_base64: str = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = f'api_key="{self.APIKey}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'

        authorization: str = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')

        # 将请求的鉴权参数组合为字典
        v = {
            "authorization": authorization,
            "date": date,
            "host": self.host
        }
        # 拼接鉴权参数，生成url
        url = self.Spark_url + '?' + urlencode(v)
        return url


class Ws_SparkAI(_WebSocketClient):
    """使用 Websocket 调用讯飞星火 api 的客户端"""
    #以下密钥信息从控制台获取  https://console.xfyun.cn/services/bm35
    APP_ID = os.getenv("SparkAI_WS_APP_ID")
    API_SECRET = os.getenv("SparkAI_WS_API_Secret")
    API_KEY = os.getenv("SparkAI_WS_API_KEY")
    # 来源 https://www.xfyun.cn/doc/spark/Web.html
    MODEL_DICT = {
        "4.0-Ultra":{"domain": "4.0Ultra", "Spark_url": "wss://spark-api.xf-yun.com/v4.0/chat"},
        "Max-32K":{"domain": "max-32k", "Spark_url": "wss://spark-api.xf-yun.com/chat/max-32k"},
        "Max":{"domain": "generalv3.5", "Spark_url": "wss://spark-api.xf-yun.com/v3.5/chat"},
        "Pro-128K":{"domain": "pro-128k", "Spark_url": "wss://spark-api.xf-yun.com/chat/pro-128k"},
        "Pro":{"domain": "generalv3", "Spark_url": "wss://spark-api.xf-yun.com/v3.1/chat"},
        "Lite":{"domain": "lite", "Spark_url": "wss://spark-api.xf-yun.com/v1.1/chat"},
    }

    def __init__(self, model: str):
        self.model = model
        # 使用鉴权url初始化
        wsParam = _Ws_Param_SparkAI(self.APP_ID, self.API_KEY, self.API_SECRET, self.MODEL_DICT[self.model]["Spark_url"])
        wsUrl = wsParam.create_url()
        super().__init__(wsUrl)

        # 模型选择
        try:
            self.Spark_url = self.MODEL_DICT[self.model]["Spark_url"]
            self.domain = self.MODEL_DICT[self.model]["domain"]
        except KeyError as err:
            LOG.error(f"不支持的模型：{err}")
            LOG.info("当前使用默认基础模型: Lite ！")

        #初始上下文内容，当前可传 system、user、assistant 等角色，参考 https://www.xfyun.cn/doc/spark/Web.html
        self.text =[
            {"role": "system", "content": ""} , # 设置对话背景或者模型角色，部分模型可用
            # {"role": "user", "content": "你是谁"},  # 用户的历史问题
            # {"role": "assistant", "content": "....."} , # AI的历史回答结果
            # ....... 省略的历史对话
            # {"role": "user", "content": "你会做什么"}  # 最新的一条问题，如无需上下文，可只传最新一条问题
        ]
        
    def gen_params(self, appid, domain, question):
        """
        通过appid和用户的提问来生成请参数
        """
        data = {
            "header": {
                "app_id": appid,
                "uid": "1234"
            },
            "parameter": {

                "chat": {
                    "domain": domain,
                    "temperature": 1,
                    "max_tokens": 2048,
                    "top_k": 5,

                    "auditing": "default"
                }
            },
            "payload": {
                "message": {
                    "text": question
                }
            }
        }
        return data
    
    def addMessage(self, role, content):
        jsoncon = {}
        jsoncon["role"] = role
        jsoncon["content"] = content
        self.text.append(jsoncon)
        return self.text

    def getlength(self, text):
        length = 0
        for content in text:
            temp = content["content"]
            leng = len(temp)
            length += leng
        return length

    def checklen(self, text):
        while (self.getlength(text) > 8000):
            del text[0]
        return text

    @typing.override
    def _on_message(self, ws, message):
        """
        收到 websocket 消息后的回调
        """
        # LOG.debug(f"{message}")
        data = json.loads(message)
        code = data['header']['code']
        if code != 0:
            LOG.error(f'请求错误: {code}, {data}')
            ws.close()
        else:
            self.message_queue.put(data)  # 将消息片段直接塞入对列
    
    @typing.override
    def connect(self):
        """
        建立 WebSocket 连接
        """
        if self.ws is not None:
            LOG.info("WebSocket 连接已存在")
            return
        
        websocket.enableTrace(False) # 调试信息
        self.ws = websocket.WebSocketApp(self.ws_url, on_open=self._on_open, on_message=self._on_message, on_error=self._on_error, on_close=self._on_close)
        
        # 使用线程启动 WebSocket
        threading.Thread(
            target=self.ws.run_forever,
            name="SparkAIRunWebSocketThread",
            kwargs={"sslopt": {"cert_reqs": ssl.CERT_NONE}},
            daemon=True,  # 守护线程
        ).start()
    
        LOG.info("等待连接建立...")
        if not self.is_open_event.wait(timeout=10): 
            LOG.error("WebSocket 连接超时")
            raise TimeoutError("WebSocket 连接超时")
        
    def send_request(self, content: str):
        """
        发送请求
        """
        # 确保连接
        self.connect()
        # 设置属性
        question = self.checklen(self.addMessage("user", content))
        self.ws.appid = self.APP_ID
        self.ws.question = question
        self.ws.domain = self.domain
        data = json.dumps(self.gen_params(appid=self.ws.appid, domain= self.ws.domain, question=self.ws.question), indent=4)
        # print(data)
        # 发送消息
        self.send(message=data)

    def get_response(self) -> str | None:
        """
        获取回复信息, 
        """
        response = ""
        while True:
            message = self.get_message(timeout=0.2) # 消费消息
            if message:
                LOG.debug(f"{message}")
                sid = message["header"]["sid"]
                choices = message["payload"]["choices"]
                status = choices["status"]
                content = choices["text"][0]["content"]
                response += content
                if status == 2: # 状态参考 https://www.xfyun.cn/doc/spark/Web.html
                    return response
            else:
                LOG.debug("没有新的消息")

if __name__ == "__main__":
    # print(Http_XAI("你好", "grok-2-1212").get_response())
    ws_client = Ws_SparkAI(model="Lite")
    ws_client.send_request("你好，请给我讲个故事。")
    text = ws_client.get_response()
    print(text)