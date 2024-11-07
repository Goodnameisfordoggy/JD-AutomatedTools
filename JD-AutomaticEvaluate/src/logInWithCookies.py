'''
Author: HDJ
StartDate: please fill in
LastEditTime: 2024-11-06 19:36:15
FilePath: \pythond:\LocalUsers\Goodnameisfordoggy-Gitee\JD-Automated-Tools\JD-AutomaticEvaluate\src\logInWithCookies.py
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
import sys
import json
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from src.logger import get_logger
LOG = get_logger()


def logInWithCookies(target_url: str = "https://www.jd.com/"):
    """ 
    使用保存的 cookies 模拟登录 
    """
    cookie_file = 'cookies.json'
    p = sync_playwright().start()
    if getattr(sys, 'frozen', False): # 打包模式
        temp_dir = os.path.join(sys._MEIPASS, "chromium-1134/chrome-win")
        print(temp_dir)
        browser = p.chromium.launch(
            headless=False, 
            args=["--disable-blink-features","--disable-blink-features=AutomationControlled"],
            executable_path=os.path.join(temp_dir, "chrome.exe")
        )  # 启动浏览器
    else:
        browser = p.chromium.launch(
            headless=False,
            args=["--disable-blink-features","--disable-blink-features=AutomationControlled"]
        )
    page = browser.new_page()
    if os.path.exists(cookie_file):  # 检查是否存在 cookie 文件
        page.goto(target_url)  # 打开目标页面
        with open(cookie_file, 'r', encoding='utf-8') as f:
            # 读取文件中的 cookies
            cookies = json.load(f)
            # 加载 cookies 到页面上下文
            page.context.add_cookies(cookies)
        page.reload()  # 刷新页面以应用 cookies
        try:
            # 检查是否成功登录
            page.wait_for_url(target_url, timeout=10000)
            LOG.success('使用已保存的 cookies 登录')
        except PlaywrightTimeoutError:
            LOG.warning('模拟登录超时，请检查 cookies 是否有效')
    else:
        LOG.error('cookie 文件不存在，请先获取并保存 cookies。')
    return page, browser  # 返回页面和浏览器实例


if __name__ == "__main__":
    page, browser = logInWithCookies()