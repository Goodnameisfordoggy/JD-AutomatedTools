import os 
import sys
import time
from selenium import webdriver

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.orderDetailsCapture import JDOrderDetailsCapture

if __name__ == '__main__':

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--start-maximized')  # 最大化浏览器
    driver = webdriver.Chrome(options=chrome_options)

    url = r'https://home.jd.hk/order.html?orderId=293165945693'
    orderDetailsCapture = JDOrderDetailsCapture(url=url, driver=driver)
    time.sleep(10)
    # orderDetailsCapture.get_order_type()
    orderDetailsCapture.extract_data()
    # print(orderDetailsCapture.get_courier_services_company())