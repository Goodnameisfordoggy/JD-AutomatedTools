'''
Author: HDJ
StartDate: please fill in
LastEditTime: 2024-08-02 00:18:56
FilePath: \pythond:\LocalUsers\Goodnameisfordoggy-Gitee\JD-Automated-Tools\JD-AutomaticEvaluate\logInWithCookies.py
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
import  os
import time
import json
import logging
from selenium import webdriver

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__) # 日志记录器

def logInWithCookies(target_url: str = "https://www.jd.com/"):
    """ 
    使用保存的cookies模拟登录 
    
    Return: webdriver
    """
    cookie_file = 'cookies.json'
    driver = webdriver.Chrome()
    if os.path.exists(cookie_file): # 检查是否存在cookie文件
        driver.maximize_window()
        driver.get(target_url)
        # time.sleep(2)
        with open(cookie_file, 'r') as f:
            # 读取文件中的 cookie
            cookies = json.load(f)
            # 加载cookie信息
            for cookie in cookies:
                driver.add_cookie(cookie)
        logging.info('使用已保存的cookie登录')
        # time.sleep(1)
        driver.refresh()
        # time.sleep(2)
        return driver
        


if __name__ == '__main__':
    logInWithCookies()