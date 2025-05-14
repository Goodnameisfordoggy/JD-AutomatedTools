'''
Author: HDJ
StartDate: please fill in
LastEditTime: 2025-05-10 23:14:37
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
from playwright.sync_api import sync_playwright, Browser, TimeoutError as PlaywrightTimeoutError

from .logger import get_logger
LOG = get_logger()

LOGIN_URL = 'https://passport.jd.com/new/login.aspx'  # 京东登录页面
COOKIES_SAVE_PATH = "cookies.json"  # 保存 cookies 的路径

def logInWithCookies(target_url: str = "https://www.jd.com/", retry: int = 0, browser: Browser | None = None):
    """ 
    使用 cookies 模拟登录

    Params:
        retry: 重新尝试登录的次数
        browser: 每次重新尝试登录通用一个 Browser 对象，减少了其初始化的开支
    Returns:
        登录成功时返回 tuple[Page, Browser], 失败则程序退出。
    """
    # 初始化 playwright
    if retry == 0:
        playwright = sync_playwright().start()
        # 初始化浏览器对象
        if getattr(sys, 'frozen', False): # 打包模式
            temp_dir = os.path.join(sys._MEIPASS, "chromium")
            browser = playwright.chromium.launch(
                headless=False, 
                args=["--disable-blink-features","--disable-blink-features=AutomationControlled"],
                executable_path=os.path.join(temp_dir, "chrome.exe")
            )
        else:
            browser = playwright.chromium.launch(
                headless=False,
                args=["--disable-blink-features","--disable-blink-features=AutomationControlled"]
            )
    
    # 没有 Cookies 先登录获取
    if not os.path.exists(COOKIES_SAVE_PATH):
        LOG.info("未找到 Cookies 文件，将跳转手动登录！")
        page = browser.new_page()
        try:
            response = page.goto('https://passport.jd.com/new/login.aspx', timeout=10000)  # 打开登录界面
            if response.status != 200:
                LOG.error(f"请求错误，状态码：{response.status}")
            else:
                LOG.info("登录页面已跳转，建议使用手机验证码登录以获得较长有效期的 Cookies")
        except PlaywrightTimeoutError:
            LOG.warning("登录页面跳转失败，请检查网络/代理是否正常！")
            sys.exit()
        # 等待用户手动登录京东
        while True:
            try:
                # 检查页面是否已经跳转到京东主页
                page.wait_for_url(target_url, timeout=3000)
                LOG.success("手动登录成功！")
                break
            except PlaywrightTimeoutError:
                LOG.info("等待用户完成登录...")
        # 获取 Cookies 并保存到文件
        cookies = page.context.cookies()
        with open(COOKIES_SAVE_PATH, 'w', encoding='utf-8') as f:
            json.dump(cookies, f, ensure_ascii=False, indent=4)
            LOG.info(f'Cookies 已保存到 {os.getcwd()}/cookies.json')
        # 视觉效果优化，以便使用者查看日志信息并进行下一步操作
        page.close()
        time.sleep(2) 

    # 用 Cookies 登录
    page = browser.new_page()
    page.goto(target_url)  # 打开目标页面
    with open(COOKIES_SAVE_PATH, 'r', encoding='utf-8') as f:
        cookies = json.load(f) # 读取文件中的 cookies
        page.context.add_cookies(cookies) # 加载 cookies 到页面上下文
    page.reload()  # 刷新页面以应用 cookies
    # 检查是否成功登录
    try:
        page.wait_for_selector('.nickname', timeout=10000) # 查找一个登录后特有的元素
        LOG.success('使用已保存的 Cookies 登录')
        return page, browser
    except PlaywrightTimeoutError:
        if os.path.isfile(COOKIES_SAVE_PATH): # 每个账号的 cookies 对应一个文件，需要确保删除的是文件
            os.remove(COOKIES_SAVE_PATH)
            LOG.warning('Cookies 已失效，请重新手动登录！')
            # 视觉效果优化，以便使用者查看日志信息并进行下一步操作
            page.close()
            time.sleep(2)
        if retry >= 3: # 防止无限递归，但暂未想到发生异常的情况
            LOG.critical("登录异常")
            sys.exit()
        else:
            return logInWithCookies(retry=retry + 1, browser=browser) # 尾递归，语义明了
