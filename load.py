import time
import json
import asyncio
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

with open('personal.json', 'r') as jf:
    pers = json.load(jf)


def wait_for_loading(driver) -> bool | None:
    """等待用户登录"""
    try:
        element = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, '//*[@id="J_user"]/div/div[1]/div/p[1]/a')))
        if pers.get('user_name') and element.text == pers.get('user_name'):
            # 条件满足时，跳出循环
            print("登录成功")
            return True
        else:
            print("用户名不匹配，登录失败")
    except TimeoutException:
        print("登录超时，请重试！")

def wait_for_element(driver, duration, attribute, value):
    """
    等待页面元素出现，并返回该元素对象。

    Args:
        driver: WebDriver对象。
        duration (int): 最长等待时间（秒）。
        attribute (str): 元素属性，如 'id'、'class name'、'xpath' 等。
        value (str): 元素属性值，用于定位元素。

    Returns:
        element: 如果元素出现，则返回该元素对象；否则返回 None。
    """
    try:
        # 使用WebDriverWait等待元素出现
        element = WebDriverWait(driver, duration).until(EC.presence_of_element_located((attribute, value)))
        if element:
            # 条件满足时，跳出循环
            print(f"{element.tag_name}: {element.text}")  # 如果元素出现，打印元素的标签和文本内容
            return element
    except TimeoutException:
        print("超时，请重试！")

def get_order_information():
    pass

def main():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--start-maximized') # 最大化浏览器
    chrome_options.add_argument('--disable-infobars')   # 禁用信息栏
    driver = webdriver.Chrome(chrome_options)
    url = "https://passport.jd.com/new/login.aspx"  # 京东登录页面
    driver.get(url)

    if wait_for_loading(driver):    
        button_my_order = wait_for_element(driver, 10, By.XPATH, '//*[@id="shortcut"]/div/ul[3]/li[3]/div/a')
        if button_my_order:
            time.sleep(3)
            button_my_order.click()


            # wait = WebDriverWait(driver, 10)
            # button_previous_page = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="order02"]/div[2]/div[2]/div[1]/span')))
            # if button_previous_page:
            #     print("button_previous_page")



    driver.quit()
        
if __name__ == "__main__":
    main()