import os 
import sys
from selenium import webdriver

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.orderDetailsCapture import JDOrderDetailsCapture

if __name__ == '__main__':
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--start-maximized')  # 最大化浏览器
    driver = webdriver.Chrome(options=chrome_options)


    orderDetailsCapture = JDOrderDetailsCapture(driver=driver)
    # orderDetailsCapture.get_order_type()
    orderDetailsCapture.extract_data()
    # print(orderDetailsCapture.get_courier_services_company())