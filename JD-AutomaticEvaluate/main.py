import os
import time
import json
import random
import logging
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from logInWithCookies import logInWithCookies

WORKING_DIRECTORY_PATH = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIRECTORY_PATH = os.path.join(WORKING_DIRECTORY_PATH, 'image')


class AutomaticEvaluate():
    
    def __init__(self) -> None:
        # 日志记录器
        self.logger = logging.getLogger(__name__)

        self.__driver = logInWithCookies()
        self.__driver.maximize_window()
        self.__task_queue = [] # 任务队列
    
    def getOrderVoucherInfo(self):
        """ 
        获取所有待评价订单部分必要信息 
        
        info_list = [
            {order_id:, orderVouche_url:, product_html_url_list:}, {}, ...
        ]
        """
        info_list = []
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

            # 订单的tbody
            tbody_elements = self.__driver.find_elements(By.XPATH, '//*[@id="main"]/div[2]/div[2]/table/tbody')
            # print('tbody_elements:', len(tbody_elements))
            for i in range(1, len(tbody_elements) + 1):
                # 单号
                order_id_element = self.__driver.find_element(By.XPATH, f'//*[@id="main"]/div[2]/div[2]/table/tbody[{i}]/tr[2]/td/span[3]/a')
                order_id = order_id_element.text
                # 订单评价页面url
                btn_element = self.__driver.find_element(By.XPATH, f'//*[@id="main"]/div[2]/div[2]/table/tbody[{i}]/tr[3]/td[4]/div/a[2]')
                orderVouche_url = btn_element.get_attribute('href')
                # 商品详情页面url
                p_name_elements = self.__driver.find_elements(By.XPATH, f'//*[@id="main"]/div[2]/div[2]/table/tbody[{i}]/tr/td/div/div/div[@class="p-name"]/a')
                product_html_url_list = [p_name_element.get_attribute('href') for p_name_element in p_name_elements]
                info_list.append(dict(order_id=order_id, orderVouche_url=orderVouche_url, product_html_url_list=product_html_url_list))

            page += 1
        # print(json.dumps(info_list, indent=4, ensure_ascii=False))
        return info_list
    
    def getText(self, product_url: str):
        """ 从网页上获取已有的评价文本 """
        self.__driver.get(product_url)
        # 点击“商品评价”
        element_to_click_1 = WebDriverWait(self.__driver, 2).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'li[data-tab="trigger"][data-anchor="#comment"]')))
        element_to_click_1.click()
        time.sleep(1)
        # 点击“只看当前商品”
        element_to_click_2 = WebDriverWait(self.__driver, 2).until(EC.presence_of_element_located((By.ID, 'comm-curr-sku')))
        element_to_click_2.click()

        text_list = []
        for page in range(3):
            time.sleep(0.5) # QwQ适当停顿避免触发反爬验证
            try:
                comment_con_elements = self.__driver.find_elements(By.CLASS_NAME, 'comment-con')
                for comment_con_element in comment_con_elements:
                    text_list.append(comment_con_element.text)
                    # print(comment_con_element.text)
                    # print()
            except NoSuchElementException:
                if page == 0:
                    self.logger.info('当前商品暂无评价')
                    break
            # 翻页
            try:
                pager_next_element = WebDriverWait(self.__driver, 2).until(EC.presence_of_element_located((By.CLASS_NAME, 'ui-pager-next')))
                pager_next_element.click()
            except TimeoutException:
                self.logger.info('已到最后一页，抓取页数小于设定数！')
                break
            
        def is_bmp_compliant(text: str):
            """ 检测所有字符是否符合基本多文种平面 BMP(Basic Multilingual Plane)"""
            for char in text:
                if ord(char) > 0xFFFF:
                    return False
            return True
        
        # 取随机评价
        def get_random_text(text_list):
            if not text_list:
                self.logger.info('get_random_text：未找到当前商品相关的评论文本！')
                return
            selected_value = random.choice(text_list)
            if len(selected_value) > 60 and is_bmp_compliant(selected_value): # 取长度大于规定个字符的评价。JD:60字以上为优质评价
                return selected_value
            else:
                return get_random_text(text_list)
        
        try:
            text = get_random_text(text_list[int(len(text_list) / 2):]) # 取后半部分评价                
        except RecursionError:
            self.logger.info('get_random_text：未找到当前商品下符合要求的评论文本！')
            return
        
        return text 
    
    def getImage(self, order_id: str, product_url: str):
        """ 
        根据商品从网页上获取已有的评价图片(部分)，筛选(随机取一组)后以订单编号为命名依据，并储存到本地。
        
        return: image_files_path(list) 储存到本地的(image目录下)隶属一个订单编号下的所有图片文件路径。
        """
        self.__driver.get(product_url)
        # 点击“商品评价”
        element_to_click_1 = WebDriverWait(self.__driver, 2).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'li[data-tab="trigger"][data-anchor="#comment"]')))
        element_to_click_1.click()
        time.sleep(1)
        # 点击“只看当前商品”
        element_to_click_2 = WebDriverWait(self.__driver, 2).until(EC.presence_of_element_located((By.ID, 'comm-curr-sku')))
        element_to_click_2.click()

        image_url_lists = []
        previous_image_url = ''
        for page in range(3):
            time.sleep(0.5) # QwQ适当停顿避免触发反爬验证
            # 评价主体组件
            comment_item_elements = self.__driver.find_elements(By.CLASS_NAME, 'comment-item')
            for comment_item_element in comment_item_elements:
                image_url_list = []
                # 图片预览组件(小图)
                thumb_img_elements = comment_item_element.find_elements(By.CLASS_NAME, 'J-thumb-img')
                for thumb_img_element in thumb_img_elements:
                    thumb_img_element.click() # 模拟点击后会出现更大的图片预览组件
                    time.sleep(0.2)
                    # 图片预览组件(大图)
                    pic_view_elements = comment_item_element.find_elements(By.XPATH, '//div[@class="pic-view J-pic-view"]/img')
                    if pic_view_elements: # 起始预览组件为非image组件会导致pic_view_elements为空
                        pic_view_element = pic_view_elements[-1] # 该组件出现后不会消失，故每次点击后均选取最新的组件
                        image_url = pic_view_element.get_attribute('src')
                        if image_url and image_url != previous_image_url: #评论的视频文件也会出现在预览位置，但是预览组件类型不是img；在该策略中(每次点击后均选取最新的组件)出现非img组件会导致前一个img组件的src重复获取，故进行url的重复检测。
                            image_url_list.append(image_url)
                            previous_image_url = image_url
                image_url_lists.append(image_url_list)

            # 翻页
            try:
                pager_next_element = WebDriverWait(self.__driver, 2).until(EC.presence_of_element_located((By.CLASS_NAME, 'ui-pager-next')))
                pager_next_element.click()
            except TimeoutException:
                self.logger.info('已到最后一页，抓取页数小于设定数！')
                break
            
        # 取随机评价的图片组
        def get_random_image_group(image_url_lists: list):
            if not image_url_lists:
                self.logger.info('get_random_image_group：未找到当前商品相关的评论图片！')
                return
            selected_value = random.choice(image_url_lists)
            if len(selected_value) >= 2: # 组内图片数量 
                return selected_value
            else:
                return get_random_image_group(image_url_lists)
            
        # 下载图片到image目录
        image_files_path = []
        try:
            for index, image_url in enumerate(get_random_image_group(image_url_lists), start=1):
                image_file_name = f'{order_id}_{index}.jpg'
                image_file_path = os.path.join(IMAGE_DIRECTORY_PATH, image_file_name)
                response = requests.get(image_url)
                if response.status_code == 200:
                    # 保存图片到本地文件
                    with open(image_file_path, 'wb') as f:
                        f.write(response.content)
                    image_files_path.append(image_file_path)
                else:
                    self.logger.error(f'{image_file_name} 文件下载失败！Status code: {response.status_code}')
        except RecursionError:
            self.logger.info('get_random_image_group：未找到当前商品下符合要求的图片组！')
        except TypeError: # get_random_image_group返回结果为None时忽略
            pass

        return image_files_path
                
    def generate_task_queue(self):
        """ 
        生成任务队列
        
        task_queue = [
            {
                index: ,
                orderVouche_url: ,
                order_id: ,
                text_to_input: ,
                image_path_to_input: ,
            }, ...
        ]
        """
        info_list = self.getOrderVoucherInfo()
        for index, order_info in enumerate(info_list, start=1):
            text_to_input = self.getText(order_info['product_html_url_list'][0])
            image_path_to_input = self.getImage(order_info['order_id'], order_info['product_html_url_list'][0])
            task = dict(index=index, order_id=order_info['order_id'], orderVouche_url=order_info['orderVouche_url'], text_to_input=text_to_input, image_path_to_input=image_path_to_input)
            self.__task_queue.append(task)
            print(json.dumps(task, indent=4, ensure_ascii=False))
            yield task
            # if index == 1:
            #     break

    def automaticEvaluate(self, order_id: str, url: str, text_input: str, image_files_path: list):
        """ 自动评价操作，限单个评价页面"""
        self.__driver.get(url)
        # 商品评价文本
        if not text_input:
            text_input = '非常满意这次购物体验，商品质量非常好，物超所值。朋友们看到后也纷纷称赞。客服服务热情周到，物流也非常给力，发货迅速，收到货物时包装完好。商品设计也符合我的预期，非常愉快的购物经历，强烈推荐！'
            self.logger.info(f'单号{order_id}的订单使用默认文本。')
        try:
            text_input_element = WebDriverWait(self.__driver, 3).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[4]/div/div/div[2]/div[1]/div[7]/div[2]/div[2]/div[2]/div[1]/textarea')))
            text_input_element.send_keys(text_input)
        except TimeoutException:
            self.logger.error("automaticEvaluate：超时，未识别到评价文本输入框！")
            return
        
        # 星级评分
        try:
            commstar_element =  self.__driver.find_elements(By.CLASS_NAME, 'commstar')
            star5_elements = [el for el in commstar_element if el.get_attribute("class") == "commstar"] # 筛选出类名完全匹配 'commstar' 的元素
            for star5_element in star5_elements:
                # 获取元素的位置
                location = star5_element.location
                size = star5_element.size
                # 在特定位置（第五颗星）点击元素
                x_offset = int(size['width'] / 5 * 4 * 0.5) # 相对于待点击元素中心点的 X 坐标
                y_offset = 0 # 相对于待点击元素中心点的 Y 坐标
                actions = ActionChains(self.__driver)
                actions.move_to_element_with_offset(star5_element, x_offset, y_offset).click().perform() # 使用相对元素位移模拟点击
            self.logger.info(f'单号{order_id}识别到{len(star5_elements)}个五星级评分组件, 全部给予五星好评。')
        except NoSuchElementException:
            self.logger.error("automaticEvaluate：未识别到星级评分组件！")

        # 商品评价图片
        if not image_files_path:
            self.logger.info(f'单号{order_id}的订单未上传评价图片。')
            return
        try:
            file_input_element = self.__driver.find_element(By.XPATH, '//input[@type="file"]') # 查找隐藏的文件上传输入框
            # 发送文件路径到文件上传输入框
            for path in image_files_path:
                file_input_element.send_keys(path)
        except NoSuchElementException:
            self.logger.error("automaticEvaluate：未识别到评价图片路径输入框！")

        # 提交评价
        time.sleep(5) # QWQ:尚未想到更好的检测所有图片上传完成的方法
        try:
            btn_submit = self.__driver.find_element(By.CLASS_NAME, 'btn-submit')
            ActionChains(self.__driver).move_to_element_with_offset(btn_submit, 0, 0).perform()
            btn_submit.click()
        except NoSuchElementException:
            self.logger.error("automaticEvaluate：未识别到提交按钮！")

    def init_image_directory(self, directory_path):
        # 确保目标路径存在
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
            return
        # 确保目标是路径指向目录
        if not os.path.isdir(directory_path):
            return
        # 清空目录文件
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            if os.path.isfile(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    self.logger.error(f"Error deleting {file_path}: {e}")

    def execute(self):
        self.init_image_directory(IMAGE_DIRECTORY_PATH)
        self.generate_task_queue()
        for task in self.generate_task_queue():
            self.automaticEvaluate(
                order_id=task['order_id'], url=task['orderVouche_url'], 
                text_input=task['text_to_input'], image_files_path=task['image_path_to_input']) 
            time.sleep(3)
        self.logger.info('QwQ脚本运行结束，如有遗漏订单请再次运行！')

if __name__ == '__main__':
    automaticEvaluate = AutomaticEvaluate()
    automaticEvaluate.execute()












