import re
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from .dataPortector import ConfigManager
from .data_type.Form import Form

class JDOrderDetailsCapture:
    
    def __init__(self, url: str = '', driver: webdriver = None) -> None:
        # 日志记录器
        self.logger = logging.getLogger(__name__)

        self.__url = url
        # self.__url = r'https://details.jd.com/normal/item.action?orderid=296415319787&PassKey=4CF1EE7A07BCD7C14F282E87984C8008'
        # self.__url = r"https://home.jd.hk/order.html?orderId=293749423277"
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
        form = Form()   # 表数据
        row = {}    # 行数据，一个字典存一个订单全部数据 
        self.get_order_type()
        for item in self.header_owned:
            try:
                row[item] = self.__func_dict.get(item)()
            except TypeError:
                    row[item] = '暂无'
        # print(row)
        return row
    
    def get_order_type(self):
        """ 获取订单类型"""
        try:
            if self.__driver.find_element(By.XPATH, '/html/body/div[@id="container"]'):
                self.__order_type = '普通订单'
        except NoSuchElementException:
            pass
        except Exception as e:
            self.logger.error(f'订单类型获取失败：{e}')
        
        try:
            if self.__driver.find_element(By.XPATH, '/html/body/div[2]/div[1]/a[@class="logo"]'):
                self.__order_type = '京东国际'
        except NoSuchElementException:
            pass
        except Exception as e:
            self.logger.error(f'订单类型获取失败：{e}')
        # print(self.__order_type)

    def get_shop_name(self):
        """ 获取店铺名称 """
        if self.__order_type == '普通订单':
            element = self.__driver.find_element(By.CLASS_NAME, "shop-name")
            return element.text
        elif self.__order_type == '京东国际':
            return '京东国际自营'
        
    
    def get_product_id(self):
        """ 获取商品编号 """
        if self.__order_type == '普通订单':
            try:
                element = self.__driver.find_element(By.XPATH, '//*[@id="container"]/div[2]/div/div[5]/div[2]/div[1]/table/tbody/tr[1]/td[3]')
                return element.text
            except NoSuchElementException:
                return "NULL"
        elif self.__order_type == '京东国际':
            return 'NULL'
        
    def get_jingdou(self):
        """ 获取订单返京豆数量 """
        if self.__order_type == '普通订单':
            try:
                element = self.__driver.find_element(By.XPATH, '//*[@id="container"]/div[2]/div/div[5]/div[2]/div[1]/table/tbody/tr[1]/td[contains(@id,"jingdou")]')
                return element.text
            except NoSuchElementException:
                return "NULL"
        elif self.__order_type == '京东国际':
            return 'NULL'

    def get_courier_services_company(self):
        """ 获取物流公司 """
        if self.__order_type == '普通订单':
            try:
                element = self.__driver.find_element(By.CLASS_NAME, 'p-info')
                match = re.search(r'承运人：(.*?)快递', element.text)
                if match:
                    return match.group(1) + '快递'
            except NoSuchElementException:
                return "NULL"
        elif self.__order_type == '京东国际':
            return '京东快递'
    
    def get_courier_number(self):
        """ 获取快递单号 """
        if self.__order_type == '普通订单':
            try:
                element = self.__driver.find_element(By.CLASS_NAME, 'p-info')
                match  = re.search(r'货运单号：(\b[A-Za-z0-9]+\b)', element.text)
                if match:
                    return match.group(1)
            except NoSuchElementException:
                return "NULL"
        elif self.__order_type == '京东国际':
            try:
                elements = self.__driver.find_elements(By.CLASS_NAME, 'black')
                if len(elements) == 2:
                    return elements[1].text
                elif len(elements) == 4:
                    return elements[3].text
            except NoSuchElementException:
                return "NULL"
                    