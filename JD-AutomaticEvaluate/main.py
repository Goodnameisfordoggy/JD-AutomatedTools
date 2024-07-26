import time
import json
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from logInWithCookies import logInWithCookies

class AutomaticEvaluate():
    
    def __init__(self) -> None:
        # 日志记录器
        self.logger = logging.getLogger(__name__)

        self.__driver = logInWithCookies()
        self.__driver.maximize_window()
    
    def getOrderVoucherUrl(self):
        """ 获取所有待评价订单的页面url """
        url_list = []
        page = 1 # 起始页
        while True:
            url = f'https://club.jd.com/myJdcomments/myJdcomment.action?sort=0&page={page}'
            try:
                # 等待结束标志
                if WebDriverWait(self.__driver, 2).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[4]/div/div/div[2]/div[2]/div[2]/div/div/div/h5'))):
                    self.logger.info('getOrderVoucherUrl：识别到结束标志，所有待评价页面url获取结束！')
                    break
            except TimeoutException:
                self.logger.info('getOrderVoucherUrl： 结束标志未出现！')
            self.__driver.get(url)
            btn_elements = self.__driver.find_elements(By.CLASS_NAME, 'btn-def')
            for btn_element in btn_elements:
                url_list.append(btn_element.get_attribute('href'))
            page += 1
        return url_list

    def automaticEvaluate(self, url: str, text_input: str, image_files_path: list):
        """ 自动评价操作，限单个评价页面"""
        self.__driver.get(url)

        # 商品评价文本
        try:
            text_input_element = WebDriverWait(self.__driver, 3).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[4]/div/div/div[2]/div[1]/div[7]/div[2]/div[2]/div[2]/div[1]/textarea')))
            text_input_element.send_keys(text_input)
        except TimeoutException:
            self.logger.error("automaticEvaluate：超时，未识别到评价文本输入框！")

        # 星级评分
        try:
            commstar_element =  self.__driver.find_elements(By.CLASS_NAME, 'commstar')
            star5_elements = [el for el in commstar_element if el.get_attribute("class") == "commstar"] # 筛选出类名完全匹配 'commstar' 的元素
            logging.info(f'识别到{len(star5_elements)} 个五星级评分组件, 全部给予五星好评。')
            for star5_element in star5_elements:
                # 获取元素的位置
                location = star5_element.location
                size = star5_element.size
                # 使用 ActionChains 在特定位置点击元素
                x_offset = int(location['x'] + size['width'] / 5 * 4) # 相对于元素左上角的 X 坐标
                y_offset = int(location['y'] + size['height'] / 2)  # 相对于元素左上角的 Y 坐标
                actions = ActionChains(self.__driver)
                actions.move_by_offset(x_offset, y_offset).click().perform()
                actions.move_by_offset(-x_offset, -y_offset).perform() # 移动鼠标回到起点，防止影响后续操作
        except NoSuchElementException:
            self.logger.error("automaticEvaluate：未识别到星级评分组件！")

        # 商品评价图片
        try:
            file_input = self.__driver.find_element(By.XPATH, '//input[@type="file"]') # 查找隐藏的文件上传输入框
            # 发送文件路径到文件上传输入框
            for path in image_files_path:
                file_input.send_keys(path)
        except NoSuchElementException:
            self.logger.error("automaticEvaluate：未识别到评价图片路径输入框！")

        # 提交评价
        time.sleep(5) # QWQ:尚未想到更好的检测所有图片上传完成的方法
        try:
            btn_submit = self.__driver.find_element(By.CLASS_NAME, 'btn-submit')
            btn_submit.click()
        except NoSuchElementException:
            self.logger.error("automaticEvaluate：未识别到提交按钮！")

    def execute(self):
        # self.getOrderVoucherUrl()
        self.automaticEvaluate(
            url='https://club.jd.com/myJdcomments/orderVoucher.action?ruleid=298035211718',
            text_input='这款拜杰高硼硅玻璃刻度杯非常实用！500ML的容量适中，刻度清晰方便测量各种液体，耐高温的硼硅玻璃质感很好，耐用且易清洗。透明设计让内容一目了然，适合冷泡饮料和果汁。使用起来很方便，推荐给需要精准测量的朋友们！',
            image_files_path = [r"C:\Users\HDJ\Desktop\1.png",r"C:\Users\HDJ\Desktop\2.png"])
        time.sleep(10)

if __name__ == '__main__':
    automaticEvaluate = AutomaticEvaluate()
    automaticEvaluate.execute()












