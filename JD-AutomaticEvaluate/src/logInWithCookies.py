'''
Author: HDJ
StartDate: please fill in
LastEditTime: 2024-11-12 17:58:35
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
Copyright (c) 2024-2025 by HDJ, All Rights Reserved. 
'''
import os
import sys
import time
import json
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

from .logger import get_logger
LOG = get_logger()

LOGIN_URL = 'https://passport.jd.com/new/login.aspx'  # 京东登录页面
COOKIES_SAVE_PATH = "cookies.json"  # 保存 cookies 的路径

def logInWithCookies(target_url: str = "https://www.jd.com/"):
    """ 
    使用保存的 cookies 模拟登录 
    """
    p = sync_playwright().start()
    if getattr(sys, 'frozen', False): # 打包模式
        temp_dir = os.path.join(sys._MEIPASS, "chromium")
        browser = p.chromium.launch(
            headless=False, 
            args=["--disable-blink-features","--disable-blink-features=AutomationControlled"],
            executable_path=os.path.join(temp_dir, "chrome.exe")
        )
    else:
        browser = p.chromium.launch(
            headless=False,
            args=["--disable-blink-features","--disable-blink-features=AutomationControlled"]
        )
    
    # 没有 Cookies 先登录获取
    if not os.path.exists(COOKIES_SAVE_PATH):
        LOG.info("未找到Cookies文件，请先手动登录！")
        page = browser.new_page()
        page.goto(LOGIN_URL)  # 打开登录界面
        LOG.info("登录页面已跳转，建议使用手机验证码登录以获得较长有效期的 Cookies。")
        # 等待用户手动登录京东
        while True:
            try:
                # 检查页面是否已经跳转到京东主页
                page.wait_for_url('https://www.jd.com/', timeout=3000)
                LOG.success("手动登录成功！")
                break
            except PlaywrightTimeoutError:
                LOG.info("等待用户完成登录...")
        # 获取 Cookies 并保存到文件
        cookies = page.context.cookies()
        with open(COOKIES_SAVE_PATH, 'w', encoding='utf-8') as f:
            json.dump(cookies, f, ensure_ascii=False, indent=4)
            LOG.info(f'Cookies 已保存到 {os.getcwd()}/cookies.json')
        page.close() # 关闭网页
        time.sleep(2) # 避免重复登录过快

    page = browser.new_page()
    page.goto(target_url)  # 打开目标页面
    with open(COOKIES_SAVE_PATH, 'r', encoding='utf-8') as f:
        cookies = json.load(f) # 读取文件中的 cookies
        page.context.add_cookies(cookies) # 加载 cookies 到页面上下文
    page.reload()  # 刷新页面以应用 cookies
    # 检查是否成功登录
    try:
        page.wait_for_url(target_url, timeout=10000)
        LOG.success('使用已保存的 Cookies 登录')
    except PlaywrightTimeoutError:
        LOG.warning('模拟登录超时，请检查 Cookies 是否有效，或删除旧的 Cookies.json 文件重新运行！')

    return page, browser  # 返回页面和浏览器实例
