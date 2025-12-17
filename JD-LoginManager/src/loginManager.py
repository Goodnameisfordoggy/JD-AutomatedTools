'''
Author: HDJ @https://github.com/Goodnameisfordoggy
LastEditTime: 2025-12-17 17:06:55
FilePath: \pythond:\LocalUsers\Goodnameisfordoggy-Gitee\JD-Automated-Tools\JD-GetCookie\loginManager.py
Description: @VSCode

				|	早岁已知世事艰，仍许飞鸿荡云间；
				|	曾恋嘉肴香绕案，敲键弛张荡波澜。
				|					 
				|	功败未成身无畏，坚持未果心不悔；
				|	皮囊终作一抔土，独留屎山贯寰宇。

Copyright (c) 2024-2025 by HDJ, All Rights Reserved. 
'''
import os
import sys
import time
import json
from playwright.sync_api import (
    sync_playwright, 
    Browser, 
    BrowserContext, 
    Page, 
    TimeoutError as PlaywrightTimeoutError
)
from src import COOKIES_DIR
from src.data import NetworkError
from src.logger import LOG
from src.utils import sync_retry
# LOG = get_logger()

class JDCookieLogin:
    """
    JD Cookies 登录
    """
    LOGIN_URL = "https://passport.jd.com/new/login.aspx"  # 京东登录页面
    TARGET_URL = "https://www.jd.com/"
    COOKIES_SAVE_PATH = os.path.join(COOKIES_DIR, "cookies.json")  # 保存 cookies 的路径

    def __init__(self):
        self.playwright = None
        self.browser: Browser = None
        self.context: BrowserContext = None
        self.page: Page = None
        os.makedirs(COOKIES_DIR, exist_ok=True)  # 确保Cookies目录存在
        # 初始化 playwright
        self.playwright = sync_playwright().start()
        # 初始化浏览器对象
        if getattr(sys, 'frozen', False): # 打包模式
            temp_dir = os.path.join(sys._MEIPASS, "chromium")
            self.browser = self.playwright.chromium.launch(
                headless=False, 
                args=["--disable-blink-features","--disable-blink-features=AutomationControlled"],
                executable_path=os.path.join(temp_dir, "chrome.exe")
            )
        else:
            self.browser = self.playwright.chromium.launch(
                headless=False,
                args=["--disable-blink-features","--disable-blink-features=AutomationControlled"]
            )

        self.context = self.browser.new_context(
            no_viewport=None    # 不限制视口大小
        )

    @sync_retry(max_retries=3, retry_delay=2, exceptions=(PlaywrightTimeoutError,))
    def __load_page(self, url: str, timeout: float):
        response = self.page.goto(url, timeout=timeout)
        if response and response.status != 200:
            raise NetworkError(f"页面加载失败，状态码：{response.status} - URL: {url}")

    def _get_cookies(self):
        """
        获取当前上下文的Cookies
        """
        if not self.context:
            raise RuntimeError("浏览器上下文未初始化")
        return self.context.cookies(self.TARGET_URL)
    
    def _save_cookies(self, cookies: list[dict]):
        """
        保存Cookies到JSON文件
        """
        with open(self.COOKIES_SAVE_PATH, 'w', encoding='utf-8') as f:
            json.dump(cookies, f, ensure_ascii=False, indent=4)
        LOG.success(f"Cookies已保存到: {self.COOKIES_SAVE_PATH}")

    def _load_cookies_from_file(self):
        """
        从文件加载Cookies
        """
        if not os.path.exists(self.COOKIES_SAVE_PATH):
            raise FileNotFoundError(f"Cookies文件不存在: {self.COOKIES_SAVE_PATH}")
        with open(self.COOKIES_SAVE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _delete_cookies_file(self):
        """
        删除Cookies文件
        """
        # 每个账号的 cookies 对应一个 JSON 件，需要确保删除的是文件
        if os.path.isfile(self.COOKIES_SAVE_PATH):
            os.remove(self.COOKIES_SAVE_PATH)
            LOG.warning(f"已删除Cookies文件: {self.COOKIES_SAVE_PATH}")

    def logInWithCookies(self, cookies_string: str | None = None):
        """
        使用 cookies 模拟登录
        Args:
            cookies_string (str, optional): 字符串格式的Cookies
        Returns:
            登录成功时返回 tuple[Page, BrowserContext], 失败则程序退出。
        """
        self.page = self.context.new_page()
        # 加载登录页面
        try:
            self.__load_page(self.TARGET_URL, timeout=10000)
        except PlaywrightTimeoutError:
            raise NetworkError(message=f"页面加载超时: {self.TARGET_URL}")
        # 加载 cookies 装填到页面
        if cookies_string:
            cookies = json.loads(cookies_string.strip())
        else:
            cookies = self._load_cookies_from_file()
        self.page.context.add_cookies(cookies) # 加载 cookies 到页面上下文
        self.page.reload()  # 刷新页面以应用 cookies
        # 检查是否成功登录
        try:
            self.page.wait_for_selector('.nickname', timeout=10000) # 查找一个登录后特有的元素
            LOG.success('使用已保存的 Cookies 登录')
            return self.page, self.context
        except PlaywrightTimeoutError:
            self._delete_cookies_file()
            LOG.warning('Cookies 已失效，请重新手动登录！')
            # 视觉效果优化，以便使用者查看提示信息并进行下一步操作
            self.page.close()
            time.sleep(2)

    def manualLogInAndGetCookies(self):
        """ 
        手动登录获取 Cookies，若有存有旧 cookies 优先使用旧的进行模拟登录。

        Returns:
            登录成功时返回 tuple[Page, BrowserContext], 失败则程序退出。
        """
        retry = 0
        while retry < 2:
            # 没有 Cookies 先登录获取
            if not os.path.exists(self.COOKIES_SAVE_PATH):
                LOG.info("未找到 Cookies 文件，将跳转手动登录！")
                self.page = self.context.new_page()
                try:
                    self.__load_page(self.LOGIN_URL, timeout=10000)  # 打开登录界面
                    LOG.info("登录页面已跳转，建议使用手机验证码登录以获得较长有效期的 Cookies")
                except PlaywrightTimeoutError:
                    raise NetworkError(message=f"页面加载超时：{self.LOGIN_URL}")
                # 等待用户手动登录京东
                while True:
                    try:
                        # 检查页面是否已经跳转到京东主页
                        self.page.wait_for_url(self.TARGET_URL, timeout=3000)
                        LOG.success("手动登录成功！")
                        break
                    except PlaywrightTimeoutError:
                        LOG.info("等待用户完成登录...")
                # 获取 Cookies 并保存到文件
                cookies = self.page.context.cookies("https://www.jd.com/")
                self._save_cookies(cookies)
                # 视觉效果优化，以便使用者查看日志信息并进行下一步操作
                self.page.close()
                time.sleep(2) 

            # 用 Cookies 登录
            try:
                return self.logInWithCookies() # 考虑到 Cookies 失效自动删除后需再次手动登录
            except PlaywrightTimeoutError:
                retry += 1

if __name__ == '__main__':
    jdLoginManager = JDCookieLogin()
    
    # jdLoginManager.manualLogInAndGetCookies()
    # jdLoginManager.logInWithCookies(ck)