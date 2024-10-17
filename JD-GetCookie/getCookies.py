'''
Author: HDJ
StartDate: please fill in
LastEditTime: 2024-10-17 18:24:17
FilePath: \pythond:\LocalUsers\Goodnameisfordoggy-Gitee\JD-Automated-Tools\JD-GetCookie\getCookies.py
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
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError


login_url = 'https://passport.jd.com/new/login.aspx'  # 京东登录页面
save_path = "cookies.json"  # 保存 cookies 的路径

def getCookies():
    """ 获取登录后的 cookies """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # 启动浏览器
        page = browser.new_page()
        page.goto(login_url)  # 打开登录界面
        print("登录页面已跳转，建议使用手机验证码登录以获得较长有效期的 cookies。")
        
        # 等待用户手动登录京东
        while True:
            try:
                # 检查页面是否已经跳转到京东主页
                page.wait_for_url('https://www.jd.com/', timeout=3000)
                print("成功登录京东！")
                break
            except PlaywrightTimeoutError:
                print("等待用户完成登录...")

        # 获取 cookies 并保存到文件
        cookies = page.context.cookies()
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(cookies, f, ensure_ascii=False, indent=4)
            print(f'cookies 已保存到 {os.getcwd()}/cookies.json')

        browser.close()


if __name__ == '__main__':
    getCookies()