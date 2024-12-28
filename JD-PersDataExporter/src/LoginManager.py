'''
Author: HDJ
StartDate: please fill in
LastEditTime: 2024-12-29 00:52:20
FilePath: \pythond:\LocalUsers\Goodnameisfordoggy-Gitee\JD-Automated-Tools\JD-PersDataExporter\src\LoginManager.py
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
import re
import sys
import json
import time
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from src.logger import get_logger
from src import JD_ACCOUNT_COOKIES_DIR

LOG = get_logger()

class LoginManager:
    """
    **Usage**
    ```py
    loginManager = LoginManager()
    loginManager.login_with_cookies()
    page = loginManager.page
    ```
    """
    LOGIN_URL = 'https://passport.jd.com/new/login.aspx'
    BASE_URL = "https://www.jd.com/"
    USER_INFO_URL = "https://i.jd.com/user/info"

    def __init__(self, *, headless:bool, cookie_file: str = ""):
        self.headless = headless
        if cookie_file:
            self.cookie_save_path = os.path.join(JD_ACCOUNT_COOKIES_DIR, cookie_file)
        self.playwright = sync_playwright().start()
        self.browser = None
        self.page = None

    def login_with_cookies(self) -> "LoginManager":
        """使用 Cookies 登录"""
        if self.browser is None:
            self._launch_browser()
        self.page = self.browser.new_page()
        # 检查是否已有 cookies
        cookies = self._load_cookies()
        if not cookies:
            LOG.info("未找到Cookies文件，请先手动登录！")
            self.login_new_account()
        else:
            # 有cookie文件直接登录
            self.page.context.add_cookies(cookies)
            self.page.goto(self.BASE_URL)
            self.page.reload()
        # 登录状态检测
        try:
            self.page.wait_for_url(self.BASE_URL, timeout=10000)
            LOG.success('使用已保存的 Cookies 登录')
            return self
        except PlaywrightTimeoutError:
            LOG.warning('模拟登录超时，请检查 Cookies 是否有效，或删除旧的 Cookies.json 文件重新运行！')

    def close(self):
        """关闭所有连接"""
        if self.page:
            self.page.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
    
    def login_new_account(self):
        """
        添加新账号
        
        :return: 账号信息(dict)
        """
        if self.browser is None:
            self._launch_browser() # 启动浏览器
        self.page = self.browser.new_page() # 打开新网页
        self.page.goto(self.LOGIN_URL)
        LOG.info("登录页面已跳转，建议使用手机验证码登录以获得较长有效期的 Cookies。")
        # 等待手动登录
        while True:
            try:
                self.page.wait_for_url("https://www.jd.com/", timeout=3000)
                LOG.success("手动登录成功！")
                break
            except PlaywrightTimeoutError:
                LOG.info("等待用户完成登录...")
        cookies = self.page.context.cookies() # 获取 cookies
        
        # 获取账号信息
        self.page.goto("https://i.jd.com/user/info")
        try:
            # 昵称
            nick_name_element = self.page.wait_for_selector('input#nickName', timeout=3000)
            nick_name = nick_name_element.get_attribute("value")
            LOG.debug(f"nick_name: {nick_name}")
            # 账号名
            user_name_element = self.page.wait_for_selector('div.info-m div b', timeout=3000)
            user_name_match = re.search(r"账号名：([\w\-]+)", user_name_element.inner_text())
            if user_name_match:
                user_name = user_name_match.group(1)
            LOG.debug(f"user_name: {user_name}")
            # 用户头像 url
            user_picture_element = self.page.wait_for_selector('div.u-pic img[alt="用户头像"]', timeout=30000)
            user_picture_url = user_picture_element.get_attribute("src")
            LOG.debug(f"user_picture_url: {user_picture_url}")
        except PlaywrightTimeoutError as err:
            LOG.error("账号信息获取失败")
            raise err
        finally:
            self.close()
            
        if nick_name:
            # 账号对应的数据表名
            sheet_name = nick_name +"_Sheet"
            # 账号 cookies 储存位置
            cookie_save_path = nick_name + "_cookies.json"
        
        self.cookie_save_path = os.path.join(JD_ACCOUNT_COOKIES_DIR, cookie_save_path)
        self._save_cookies(cookies) # 保存新的 cookies

        return {
            "user_name": user_name,
            "nick_name": nick_name,
            "sheet_name": sheet_name,
            "cookies_path": cookie_save_path,   # 存相对路径
            "user_picture_url": "https:" + user_picture_url,
        }
    
    def _launch_browser(self):
        """启动浏览器"""
        if getattr(sys, 'frozen', False):  # 打包模式
            temp_dir = os.path.join(sys._MEIPASS, "chromium-1134/chrome-win")
            self.browser = self.playwright.chromium.launch(
                headless=self.headless,
                args=["--disable-blink-features", "--disable-blink-features=AutomationControlled"],
                executable_path=os.path.join(temp_dir, "chrome.exe")
            )
        else:
            self.browser = self.playwright.chromium.launch(
                headless=self.headless,
                args=["--disable-blink-features", "--disable-blink-features=AutomationControlled"]
            )

    def _save_cookies(self, cookies):
        """将 cookies 储存到 JSON 文件"""
        with open(self.cookie_save_path, 'w', encoding='utf-8') as f:
            json.dump(cookies, f, ensure_ascii=False, indent=4)
        LOG.info(f'Cookies 已保存到 {self.cookie_save_path}')

    def _load_cookies(self):
        """从 JSON 文件中获取 cookies"""
        if os.path.exists(self.cookie_save_path):
            with open(self.cookie_save_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None


