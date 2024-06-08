import re
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from .dataPortector import ConfigManager
from .data_type.Form import Form

class JDOrderDetailsCapture:
    
    def __init__(self, url: str = '', driver = None) -> None:
        # 日志记录器
        self.logger = logging.getLogger(__name__)

        self.__url = url
        if __name__ == "__main__":
            self.__url = r'https://details.jd.com/normal/item.action?orderid=296415319787&PassKey=4CF1EE7A07BCD7C14F282E87984C8008'
        self.__driver = driver
        if __name__ == "__main__":
            self.__chrome_options = webdriver.ChromeOptions()
            self.__chrome_options.add_argument('--start-maximized')  # 最大化浏览器
            self.__driver = webdriver.Chrome(options=self.__chrome_options)
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
        self.__loading()

    def __loading(self):
        if self.__driver and self.__url:
            # 打开目标网页
            self.__driver.get(self.__url)
            # 等待动态内容加载并抓取
            self.__driver.implicitly_wait(10)  # 等待最多10秒

    def extract_data(self):
        
        form = Form()   # 表数据
        row = {}    # 行数据，一个字典存一个订单全部数据 
        for item in self.__header_needed:
            try:
                row[item] = self.__func_dict.get(item)()
            except TypeError:
                    row[item] = '暂无'
        print(row)
        return row

    def get_shop_name(self):
        """ 获取店铺名称 """
        element = self.__driver.find_element(By.CLASS_NAME, "shop-name")
        return element.text
    
    def get_product_id(self):
        """ 获取商品编号 """
        element = self.__driver.find_element(By.XPATH, '//*[@id="container"]/div[2]/div/div[5]/div[2]/div[1]/table/tbody/tr[1]/td[3]')
        return element.text
    
    def get_jingdou(self):
        """ 获取订单返京豆数量 """
        element = self.__driver.find_element(By.XPATH, '//*[@id="container"]/div[2]/div/div[5]/div[2]/div[1]/table/tbody/tr[1]/td[contains(@id,"jingdou")]')
        return element.text

    def get_courier_services_company(self):
        """ 获取物流公司 """
        element = self.__driver.find_element(By.CLASS_NAME, 'p-info')
        match = re.search(r'承运人：.*?(\w*快递)', element.text)
        if match:
            return match.group(1)
    
    def get_courier_number(self):
        """ 获取快递单号 """
        element = self.__driver.find_element(By.CLASS_NAME, 'p-info')
        match  = re.search(r'货运单号：(\b[A-Za-z0-9]+\b)', element.text)
        if match:
            return match.group(1)