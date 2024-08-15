'''
Author: HDJ
StartDate: please fill in
LastEditTime: 2024-08-03 00:44:53
FilePath: \pythond:\LocalUsers\Goodnameisfordoggy-Gitee\JD-Automated-Tools\JD-AutomaticEvaluate\getCookies.py
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
import time
import json
import logging
from selenium import webdriver

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__) # 日志记录器

login_url='https://passport.jd.com/new/login.aspx' # 京东登录页面
save_path ="cookies.json" 

def getCookies():
    """ 获取登录后的cookies """
    with webdriver.Chrome() as driver:
        driver.maximize_window()
        driver.get(login_url) #打开登录界面
        logger.info("登录页面已跳转，建议使用手机验证码登录以获得较长有效期的cookies。")
        driver.delete_all_cookies() #清空登录前的cookies
        # time.sleep(2)
        while driver.current_url != 'https://www.jd.com/': # 登录后的主页url
            time.sleep(1)
        cookies = driver.get_cookies()
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(cookies, f, ensure_ascii=False, indent=4)
            logger.info(f'cookies已保存到{os.getcwd()}/cookies.json')


if __name__ == '__main__':
    getCookies()