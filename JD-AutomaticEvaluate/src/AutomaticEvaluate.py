'''
Author: HDJ
StartDate: please fill in
LastEditTime: 2024-09-28 22:45:40
FilePath: \pythond:\LocalUsers\Goodnameisfordoggy-Gitee\JD-Automated-Tools\JD-AutomaticEvaluate\src\AutomaticEvaluate.py
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
import random
import logging
import requests
from PIL import Image, ImageFilter
from .logInWithCookies import logInWithCookies
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from src.logger import get_logger
LOG = get_logger()


WORKING_DIRECTORY_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGE_DIRECTORY_PATH = os.path.join(WORKING_DIRECTORY_PATH, 'image')


class AutomaticEvaluate():
    
    def __init__(self) -> None:
        self.__page, browser = logInWithCookies()
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
                if self.__page.wait_for_selector('xpath=/html/body/div[4]/div/div/div[2]/div[2]/div[2]/div/div/div/h5', timeout=2000):
                    LOG.info('识别到结束标志，所有待评价页面url获取结束！')
                    break
            except PlaywrightTimeoutError:
                LOG.info('结束标志未出现！')
            self.__page.goto(url)

            # 订单的tbody
            tbody_elements = self.__page.locator('xpath=//*[@id="main"]/div[2]/div[2]/table/tbody').element_handles()
            for i in range(1, len(tbody_elements) + 1):
                # 单号
                order_id_element = self.__page.wait_for_selector(f'xpath=//*[@id="main"]/div[2]/div[2]/table/tbody[{i}]/tr[2]/td/span[3]/a', timeout=2000)
                order_id = order_id_element.inner_text()
                # 订单评价页面url
                btn_element = self.__page.wait_for_selector(f'xpath=//*[@id="main"]/div[2]/div[2]/table/tbody[{i}]/tr[3]/td[4]/div/a[2]', timeout=2000)
                orderVouche_url = 'https:' + btn_element.get_attribute('href')
                # 商品详情页面url
                p_name_elements = self.__page.locator(f'xpath=//*[@id="main"]/div[2]/div[2]/table/tbody[{i}]/tr/td/div/div/div[@class="p-name"]/a').element_handles()
                product_html_url_list = ['https:' + p_name_element.get_attribute('href') for p_name_element in p_name_elements]
                info_list.append(dict(order_id=order_id, orderVouche_url=orderVouche_url, product_html_url_list=product_html_url_list))

            page += 1
        return info_list
    
    def getText(self, product_url: str):
        """ 从网页上获取已有的评价文本 """
        if self.__page.goto(product_url):
            LOG.trace(f'getText({product_url})')
        # 点击“商品评价”
        element_to_click_1 = self.__page.wait_for_selector('li[data-tab="trigger"][data-anchor="#comment"]', timeout=2000)
        element_to_click_1.click()
        time.sleep(1)
        # 点击“只看当前商品”
        element_to_click_2 = self.__page.wait_for_selector('#comm-curr-sku', timeout=2000)
        element_to_click_2.click()

        text_list = []
        for page in range(1, 4):
            LOG.trace(f'Turn to page {page}')
            time.sleep(1) # QwQ适当停顿避免触发反爬验证, 同时等待资源加载完毕
            try:
                comment_con_elements = self.__page.locator('.comment-con').element_handles()
                for comment_con_element in comment_con_elements:
                    text_list.append(comment_con_element.inner_text())
            except Exception as err:
                if page == 1:
                    LOG.info('当前商品暂无评价')
                    break
            # 翻页
            try:
                pager_next_element = self.__page.wait_for_selector('.ui-pager-next', timeout=2000)
                pager_next_element.click()
            except PlaywrightTimeoutError:
                LOG.info('已到最后一页，抓取页数小于设定数！')
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
                LOG.info('未找到当前商品相关的评论文本！')
                return
            selected_value = random.choice(text_list)
            if len(selected_value) > 60 and is_bmp_compliant(selected_value): # 取长度大于规定个字符的评价。JD:60字以上为优质评价
                return selected_value
            else:
                return get_random_text(text_list)
        
        try:
            text = get_random_text(text_list[int(len(text_list) / 2):]) # 取后半部分评价                
        except RecursionError:
            LOG.info('未找到当前商品下符合要求的评论文本！')
            return
        
        return text 
    
    def getImage(self, order_id: str, product_url: str):
        """ 
        根据商品从网页上获取已有的评价图片(部分)，筛选(随机取一组)后以订单编号为命名依据，并储存到本地。
        
        return: image_files_path(list) 储存到本地的(image目录下)隶属一个订单编号下的所有图片文件路径。
        """
        if self.__page.goto(product_url):
            LOG.trace(f'getImage({order_id}, {product_url})')
        # 点击“商品评价”
        element_to_click_1 = self.__page.wait_for_selector('li[data-tab="trigger"][data-anchor="#comment"]', timeout=2000)
        element_to_click_1.click()
        time.sleep(1)
        # 点击“只看当前商品”
        element_to_click_2 = self.__page.wait_for_selector('#comm-curr-sku', timeout=2000)
        element_to_click_2.click()

        image_url_lists = []
        previous_image_url = ''

        for page in range(1, 4):
            LOG.trace(f'Turn to page {page}')
            time.sleep(4) # QwQ适当停顿避免触发反爬验证, 同时等待资源加载完毕
            # 评价主体组件
            comment_item_elements = self.__page.locator('.comment-item').element_handles()
            for comment_item_element in comment_item_elements:
                image_url_list = []
                # 图片预览组件(小图)
                thumb_img_elements = comment_item_element.query_selector_all('.J-thumb-img')
                for thumb_img_element in thumb_img_elements:
                    LOG.debug(f'Visible: {thumb_img_element.is_visible()}')
                    thumb_img_element.click() # 模拟点击后会出现更大的图片预览组件
                    time.sleep(0.2)
                    # 图片预览组件(大图)
                    pic_view_elements = comment_item_element.query_selector_all('xpath=//div[@class="pic-view J-pic-view"]/img')
                    if pic_view_elements: # 起始预览组件为非image组件会导致pic_view_elements为空
                        pic_view_element = pic_view_elements[-1] # 该组件出现后不会消失，故每次点击后均选取最新的组件
                        image_url = 'https:' + pic_view_element.get_attribute('src')
                        if image_url and image_url != previous_image_url: #评论的视频文件也会出现在预览位置，但是预览组件类型不是img；在该策略中(每次点击后均选取最新的组件)出现非img组件会导致前一个img组件的src重复获取，故进行url的重复检测。
                            image_url_list.append(image_url)
                            previous_image_url = image_url
                image_url_lists.append(image_url_list)

            # 翻页
            try:
                pager_next_element = self.__page.wait_for_selector('.ui-pager-next', timeout=2000)
                pager_next_element.click()
            except PlaywrightTimeoutError:
                LOG.info('已到最后一页，抓取页数小于设定数！')
                break
            
        # 取随机评价的图片组
        def get_random_image_group(image_url_lists: list):
            if not image_url_lists:
                LOG.info('未找到当前商品相关的评论图片！')
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
                    # 处理图片
                    img = Image.open(image_file_path)
                    img = img.resize((img.width * 5, img.height * 5), Image.LANCZOS) # 提高分辨率
                    img = img.filter(ImageFilter.SHARPEN) # 增加清晰度
                    img.save(image_file_path)
                else:
                    LOG.error(f'{image_file_name} 文件下载失败！Status code: {response.status_code}')
        except RecursionError:
            LOG.info('未找到当前商品下符合要求的图片组！')
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
            # if index < 5: # 起始 1 
            #     continue
            LOG.info('正在生成任务......')
            text_to_input = self.getText(order_info['product_html_url_list'][0])
            image_path_to_input = self.getImage(order_info['order_id'], order_info['product_html_url_list'][0])
            task = dict(index=index, order_id=order_info['order_id'], orderVouche_url=order_info['orderVouche_url'], text_to_input=text_to_input, image_path_to_input=image_path_to_input)
            self.__task_queue.append(task)
            LOG.trace(f'当前任务：{json.dumps(task, indent=4, ensure_ascii=False)}')
            yield task
            

    def automaticEvaluate(self, order_id: str, url: str, text_input: str, image_files_path: list):
        """ 自动评价操作，限单个评价页面"""
        self.__page.goto(url)
        # 商品评价文本
        if not text_input:
            text_input = '非常满意这次购物体验，商品质量非常好，物超所值。朋友们看到后也纷纷称赞。客服服务热情周到，物流也非常给力，发货迅速，收到货物时包装完好。商品设计也符合我的预期，非常愉快的购物经历，强烈推荐！'
            LOG.warning(f'单号{order_id}的订单使用默认文本。')
        try:
            text_input_element = self.__page.wait_for_selector('xpath=/html/body/div[4]/div/div/div[2]/div[1]/div[7]/div[2]/div[2]/div[2]/div[1]/textarea', timeout=3000)
            text_input_element.fill(text_input)
        except PlaywrightTimeoutError:
            LOG.error("超时，未识别到评价文本输入框！")
            return
        
        # 星级评分
        try:
            commstar_elements =  self.__page.locator('.commstar').element_handles()
            star5_elements = [el for el in commstar_elements if el.get_attribute("class") == "commstar"] # 筛选出类名完全匹配 'commstar' 的元素
            for star5_element in star5_elements:
                # 获取元素的大小和位置
                bounding_box = star5_element.bounding_box()
                if bounding_box:
                    x = bounding_box['x']
                    y = bounding_box['y']
                    width = bounding_box['width']
                    height = bounding_box['height']
                    
                    # 计算相对位置（第五颗星）
                    x_offset = x + int(width / 5 * 4) + int(width / 5 * 1) / 2   # 星条元素第五颗星 X 坐标中值
                    y_offset = y + (height / 2)  # 星条元素 Y 坐标中值
                    
                    # 模拟点击
                    self.__page.mouse.move(x_offset, y_offset)
                    self.__page.mouse.click(x_offset, y_offset)
            LOG.info(f'单号{order_id}识别到{len(star5_elements)}个星级评分组件, 全部给予五星好评。')
        except Exception as err:
            LOG.error("未识别到星级评分组件！")

        # 商品评价图片
        if not image_files_path:
            LOG.warning(f'单号{order_id}的订单未上传评价图片。')
            return
        try:
            file_input_element = self.__page.wait_for_selector('xpath=//input[@type="file"]', timeout=2000) # 查找隐藏的文件上传输入框
            # 发送文件路径到文件上传输入框
            for path in image_files_path:
                file_input_element.set_input_files(path)
        
        except Exception as err:
            LOG.error("未识别到评价图片路径输入框！")

        LOG.success(f'单号{order_id}的订单评价页面填充完成。')
        # 提交评价
        time.sleep(8) # QWQ:尚未想到更好的检测所有图片上传完成的方法
        try:
            btn_submit = self.__page.wait_for_selector('.btn-submit', timeout=2000)
            btn_submit.hover()
            # btn_submit.click()
        except Exception as err:
            LOG.error("未识别到提交按钮！")

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
                    LOG.error(f"Error deleting {file_path}: {e}")

    def execute(self):
        self.init_image_directory(IMAGE_DIRECTORY_PATH)
        for task in self.generate_task_queue():
            self.automaticEvaluate(
                order_id=task['order_id'], url=task['orderVouche_url'], 
                text_input=task['text_to_input'], image_files_path=task['image_path_to_input']) 
            time.sleep(10)
        LOG.info('QwQ脚本运行结束，如有遗漏订单请再次运行！')