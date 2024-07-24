import  os
import time
import json
import logging
from selenium import webdriver

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__) # 日志记录器

cookie_file = 'cookies.json'
with webdriver.Chrome() as driver:
    if os.path.exists(cookie_file): # 检查是否存在cookie文件
        driver.maximize_window()
        driver.get(f"https://www.jd.com/")
        time.sleep(2)
        with open(cookie_file, 'r') as f:
            # 读取文件中的 cookie
            cookies = json.load(f)
            # 加载cookie信息
            for cookie in cookies:
                driver.add_cookie(cookie)
        logging.info('使用已保存的cookie登录')
        driver.refresh()
        time.sleep(5)