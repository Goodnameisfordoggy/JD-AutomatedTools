'''
Author: HDJ
StartDate: please fill in
LastEditTime: 2024-07-01 20:58:37
FilePath: \pythond:\LocalUsers\Goodnameisfordoggy-Gitee\jd-pers-data-exporter\src\orderDetailsCapture.py
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
import re
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from concurrent.futures import ThreadPoolExecutor, as_completed

from .dataPortector import ConfigManager

class JDOrderDetailsCapture:
    
    def __init__(self, url: str = '', driver: webdriver = None) -> None:
        # 日志记录器
        self.logger = logging.getLogger(__name__)

        self.__url = url
        self.__driver = driver            
        self.__configManager = ConfigManager()
        self.__config = self.__configManager.get_config() # 获取配置文件
        self.__func_dict = {
            "shop_name": self.get_shop_name,
            "product_id": self.get_product_id,
            "jingdou": self.get_jingdou,
            "courier_services_company": self.get_courier_services_company,
            "courier_number": self.get_courier_number
        }
        self.header_owned = list(self.__func_dict.keys())
        self.__header_needed = [header for header in self.__config.get('header', '') if header in self.header_owned]
        self.__order_type = None
        self.__loading()

    def __loading(self):
        if self.__driver and self.__url:
            # 打开目标网页
            self.__driver.get(self.__url)
            # 等待动态内容加载
            # self.__driver.implicitly_wait(2)

    def extract_data(self):
        """ 
        数据提取 

        Returns: 
            返回一个数据表 form (Form)
        """
        row = {}    # 行数据，一个字典存一个订单全部数据 
        self.get_order_type()
        for item in self.__header_needed:
            try:
                row[item] = self.__func_dict.get(item)()
            except TypeError:
                    row[item] = '暂无'
        # print(row)
        return row
    
    def get_order_type(self):
        """ 获取订单类型"""
        find_sign = False
        wait_an_element = WebDriverWait(self.__driver, 5).until(EC.presence_of_element_located((By.XPATH, '/html/body/div')))
        try:
            self.__driver.find_element(By.XPATH, '/html/body/div[@id="container"]')
            self.__order_type = '普通订单'
            find_sign = True
        except TimeoutException:
            pass
        except Exception as e:
            self.logger.error(f'订单类型获取失败：{e}')
        
        try:
            self.__driver.find_element(By.XPATH, '/html/body/div[2]/div[1]/a[@class="logo"]')
            self.__order_type = '京东国际'
            find_sign = True
        except TimeoutException:
            pass
        except Exception as e:
            self.logger.error(f'订单类型获取失败：{e}')
        if not find_sign:
            self.logger.error(f'TimeoutException: get_order_type')

    def get_shop_name(self):
        """ 获取店铺名称 """
        if self.__order_type == '普通订单':
            try:
                element = WebDriverWait(self.__driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, "shop-name")))
                return element.text
            except TimeoutException:
                self.logger.error(f'TimeoutException: get_shop_name')
        elif self.__order_type == '京东国际':
            return '京东国际自营'
    
    def get_product_id(self):
        """ 获取商品编号 """
        if self.__order_type == '普通订单':
            try:
                element = WebDriverWait(self.__driver, 3).until(EC.presence_of_element_located((By.XPATH, '//*[@id="container"]/div[2]/div/div[5]/div[2]/div[1]/table/tbody/tr[1]/td[3]')))
                return element.text
            except TimeoutException:
                self.logger.error(f'TimeoutException: get_product_id')
        elif self.__order_type == '京东国际':
            return None
        
    def get_jingdou(self):
        """ 获取订单返京豆数量 """
        if self.__order_type == '普通订单':
            try:
                element = WebDriverWait(self.__driver, 3).until(EC.presence_of_element_located((By.XPATH, '//*[@id="container"]/div[2]/div/div[5]/div[2]/div[1]/table/tbody/tr[1]/td[contains(@id,"jingdou")]')))
                return element.text
            except TimeoutException:
                self.logger.error(f'TimeoutException: get_jingdou')
        elif self.__order_type == '京东国际':
            return None

    def get_courier_services_company(self):
        """ 获取物流公司 """
        find_sign = False
        if self.__order_type == '普通订单':
            try:
                element = WebDriverWait(self.__driver, 2).until(EC.presence_of_element_located((By.CLASS_NAME, "track-rcol")))
                find_sign = True
            except TimeoutException:
                pass
            match = re.search(r'交付([\u4e00-\u9fa5]+)，', element.text) # 匹配物流信息列表中的物流公司名称
            if match:
                return match.group(1)
            else:
                try:
                    element = WebDriverWait(self.__driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, "p-info")))
                    print(element.text)
                except TimeoutException:
                    pass
                match = re.search(r'承运人：(.*?)(快递咨询|包裹|\n|$)', element.text)
                if match:
                    return match.group(1)
        elif self.__order_type == '京东国际':
            time.sleep(0.2)
            try:
                element = WebDriverWait(self.__driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, "eps-process")))
                find_sign = True
            except TimeoutException:
                pass
            match1 = re.search(r'国际物流承运方：(.*?)\.*?货运单号：(.*?)(\n|$)', element.text)
            match2 = re.search(r'国内物流承运方：(.*?)\.*?货运单号：(.*?)(点击查询|\n|$)', element.text)
            if match1 and match2:
                return match1.group(1).strip() + ' | ' + match2.group(1).strip()
            elif match2:
                return match2.group(1).strip()
        if not find_sign:
            self.logger.error(f'TimeoutException: get_courier_services_company')

    def get_courier_number(self):
        """ 获取快递单号 """
        find_sign = False
        def masking(data):
            """ 快递单号覆盖脱敏 """
            masking_intensity = self.__config.get('masking_intensity').get('courier_number', 2)
            try: 
                if masking_intensity == 0:
                    return data
                elif masking_intensity == 1:
                    return data[:4] + '*' * (len(data) - 8) + data[-4:]
                elif masking_intensity == 2:
                    return '*' * (len(data) - 4) + data[-4:]
                else:
                    raise ValueError
            except ValueError:
                self.logger.warning('请选择正确的覆盖脱敏强度！')

        if self.__order_type == '普通订单':
            try:
                element = WebDriverWait(self.__driver, 2).until(EC.presence_of_element_located((By.CLASS_NAME, "track-rcol")))
                find_sign = True
            except TimeoutException:
                pass
            match = re.search(r'运单号为([a-zA-Z0-9]+)', element.text) # 匹配物流信息列表中的物流单号
            if match:
                return masking(match.group(1))
            else:
                try:
                    element = WebDriverWait(self.__driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, "p-info")))
                    find_sign = True
                except TimeoutException:
                    pass
                match  = re.search(r'货运单号：(\b[A-Za-z0-9]+\b)', element.text)
                if match:
                    return masking(match.group(1))
        elif self.__order_type == '京东国际':
            time.sleep(0.2)
            try:
                element = WebDriverWait(self.__driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, "eps-process")))
                find_sign = True
            except TimeoutException:
                pass
            match1 = re.search(r'国际物流承运方：(.*?)\.*?货运单号：(.*?)(\n|$)', element.text)
            match2 = re.search(r'国内物流承运方：(.*?)\.*?货运单号：(.*?)(点击查询|\n|$)', element.text)
            if match1 and match2:
                return masking(match1.group(2).strip()) + ' | ' + masking(match2.group(2).strip())
            elif match2:
                return masking(match2.group(2).strip())
        if not find_sign:
            self.logger.error(f'TimeoutException: get_courier_services_company')
    
    def get(self):
        try:
            element = WebDriverWait(self.__driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, "track-rcol")))
            print(element.text)
        except TimeoutException:
            pass