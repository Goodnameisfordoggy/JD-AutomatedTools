'''
Author: HDJ
StartDate: please fill in
LastEditTime: 2024-11-25 21:42:03
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
import sys
import json
import time
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from .logger import get_logger

LOG = get_logger()

class LoginManager:
    LOGIN_URL = 'https://passport.jd.com/new/login.aspx'
    COOKIES_SAVE_PATH = "cookies.json"

    def __init__(self, headless=False):
        self.playwright = sync_playwright().start()
        self.headless = headless
        self.browser = None
        self.page = None

    def login_with_cookies(self, target_url="https://www.jd.com/"):
        """使用 Cookies 登录"""
        if self.browser is None:
            self._launch_browser()
        self.page = self.browser.new_page()
        # 检查是否已有 cookies
        cookies = self._load_cookies()
        if not cookies:
            LOG.info("未找到Cookies文件，请先手动登录！")
            self.page.goto(self.LOGIN_URL)
            LOG.info("登录页面已跳转，建议使用手机验证码登录以获得较长有效期的 Cookies。")
            # 等待手动登录
            while True:
                try:
                    self.page.wait_for_url(target_url, timeout=3000)
                    LOG.success("手动登录成功！")
                    break
                except PlaywrightTimeoutError:
                    LOG.info("等待用户完成登录...")
            # 储存 cookies
            cookies = self.page.context.cookies()
            self._save_cookies(cookies)
        else:
            self.page.context.add_cookies(cookies)
            self.page.goto(target_url)
            self.page.reload()
        # 登录状态检测
        try:
            self.page.wait_for_url(target_url, timeout=10000)
            LOG.success('使用已保存的 Cookies 登录')
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
        """Save cookies to a JSON file."""
        with open(self.COOKIES_SAVE_PATH, 'w', encoding='utf-8') as f:
            json.dump(cookies, f, ensure_ascii=False, indent=4)
        LOG.info(f'Cookies 已保存到 {os.getcwd()}/{self.COOKIES_SAVE_PATH}')

    def _load_cookies(self):
        """Load cookies from a JSON file."""
        if os.path.exists(self.COOKIES_SAVE_PATH):
            with open(self.COOKIES_SAVE_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

