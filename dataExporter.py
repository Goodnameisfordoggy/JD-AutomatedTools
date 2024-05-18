'''
Author: HDJ
StartDate: 2024-05-15 00:00:00
LastEditTime: 2024-05-19 00:48:57
FilePath: \pythond:\LocalUsers\Goodnameisfordoggy-Gitee\jd-data-exporter\dataExporter.py
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
import time
import json
import asyncio
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

with open('config.json', 'r', encoding='utf-8') as jf:
    config = json.load(jf)


def wait_for_loading(driver) -> bool | None:
    """等待用户登录"""
    try:
        element = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, '//*[@id="J_user"]/div/div[1]/div/p[1]/a')))
        if config.get('user_name') and element.text == config.get('user_name'):
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
            return element
    except TimeoutException:
        print("超时未找到组件，请重试！")

def get_d_values():
    # 
    d_values = [date_range_dict.get(quantum) for quantum in config['date_range'] if date_range_dict.get(quantum)]
    d_values = list(set(d_values))
    
    if -1 in d_values:
        d_values = [value for value in date_range_dict.values() if value not in [-1, 1]]

    d_values.sort()
    return d_values

def main():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--start-maximized') # 最大化浏览器
    chrome_options.add_argument('--disable-infobars')   # 禁用信息栏
    driver = webdriver.Chrome(options = chrome_options)

    url_login = "https://passport.jd.com/new/login.aspx"
    driver.get(url_login)

    html_source = []
    if wait_for_loading(driver):
        for d in get_d_values():
            page = 1
            while(True):
                target_url = f"https://order.jd.com/center/list.action?d={d}&s=4096&page={page}"
                driver.get(target_url)
                wait_for_element(driver, 10, By.XPATH, '//*[@id="order02"]/div[2]/table')  # 等待表单出现
                finish_tip = wait_for_element(driver, 5, By.XPATH, '//*[@id="order02"]/div[2]/div[2]/div/h5')
                if finish_tip:
                    print("订单数据获取结束！")
                    break
                
                time.sleep(2)
                html_source.append([driver.page_source])
                print(driver.page_source)
                print(f"------------page{page}结束---------------")
                page += 1
            page = 1
            print(f"------------d{d}结束---------------")
            # print("=================================================")
            # print(html_source)

    time.sleep(2)
    driver.quit()

date_range_dict = {
    "ALL": -1,
    "近三个月订单": 1,
    "今年内订单": 2,
    "2023年订单": 2023,
    "2022年订单": 2022,
    "2021年订单": 2021,
    "2020年订单": 2020,
    "2019年订单": 2019,
    "2018年订单": 2018,
    "2017年订单": 2017,
    "2016年订单": 2016,
    "2015年订单": 2015,
    "2014年订单": 2014,
    "2014年以前订单": 3,
} 
         



    
        
if __name__ == "__main__":
    main()