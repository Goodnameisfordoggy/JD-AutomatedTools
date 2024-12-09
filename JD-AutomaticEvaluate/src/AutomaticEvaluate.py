'''
Author: HDJ
StartDate: please fill in
LastEditTime: 2024-12-09 22:55:45
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
import random
import requests
from PIL import Image, ImageFilter
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError, Locator, ElementHandle 

from .logInWithCookies import logInWithCookies
from .api_service import get_response_xai
from .data import EvaluationTask, DEFAULT_COMMENT_TEXT_LIST
from .logger import get_logger
LOG = get_logger()

WORKING_DIRECTORY_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGE_DIRECTORY_PATH = os.path.join(WORKING_DIRECTORY_PATH, 'image')


class AutomaticEvaluate():
    
    MIN_EXISTING_PRODUCT_DESCRIPTIONS: int = None  # 商品已有文案的最少数量 | 真实评论文案多余这个数脚本才会正常获取已有文案。
    MIN_EXISTING_PRODUCT_IMAGES: int = None        # 商品已有图片的最少数量 | 真实评论图片多余这个数脚本才会正常获取已有图片。
    MIN_DESCRIPTION_CHAR_COUNT: int = None         # 评论文案的最少字数 | 在已有评论中随机筛选文案的限制条件，JD:优质评价要求60字以上。
    SELECT_CURRENT_PRODUCT_CLOSE: bool = None      # 关闭仅查看当前商品 | 启用此设置，在获取已有评论文案与图片时将查看商品所有商品评论信息，关闭可能会导致评论准确性降低
    AUTO_COMMIT_CLOSE: bool = None                 # 关闭自动提交 | 启用此设置，在自动填充完评价页面后将不会自动点击提交按钮
    CURRENT_AI_GROUP: str = None                   # AI模型的组别名称 | 使用AI模型生成评论文案
    CURRENT_AI_MODEL: str = None                   # AI模型的名称 | 使用AI模型生成评论文案
    
    def __init__(self) -> None:
        self.__page, browser = logInWithCookies()
        self.__task_list: list[EvaluationTask] = []
        self.__start_time = time.time()
        
    def exec_(self):
        self.__init_image_directory(IMAGE_DIRECTORY_PATH)
        
        for task in self.__generate_task():
            LOG.trace(f"任务已生成：{task}")
            self.__automatic_evaluate(task)

        LOG.success(f"脚本运行结束--耗时:{int(time.time()-self.__start_time)}秒")
    
    def __step_1(self):
        """
        创建任务，获取 `orderVoucher_url`
        """
        page = 1 # 起始页
        while True:
            url_1 = f'https://club.jd.com/myJdcomments/myJdcomment.action?sort=0&page={page}' # 待评价订单页面
            try:
                # 等待结束标志
                if self.__page.wait_for_selector('.tip-icon', timeout=5000):
                    LOG.info('识别到结束标志，所有待评价页面url获取结束！')
                    break
            except PlaywrightTimeoutError:
                LOG.info('结束标志未出现！')

            self.__page.goto(url_1)
            btn_elements: list = self.__page.locator('.btn-def').element_handles()
            for btn_element in btn_elements:
                orderVoucher_url: str = 'https:' + btn_element.get_attribute('href')
                task = EvaluationTask()
                task.orderVoucher_url = orderVoucher_url
                # LOG.debug(f"{task}")
                self.__task_list.append(task)
            page += 1

    def __step_2(self):
        """
        进入评价页面，获取 `order_id` `productHtml_url` `product_name`；
        """
        # new_task_index = len(self.__task_list)
        for task in self.__task_list:
            self.__page.goto(task.orderVoucher_url)
            self.__page.wait_for_timeout(2000)  # 等待加载资源
            order_id_element = self.__page.wait_for_selector('//*[@id="o-info-orderinfo"]/div/div/span[1]/a', timeout=5000)
            order_id = order_id_element.inner_text()  # 评价页面的订单编号
            task.order_id = order_id

            goods_elements: Locator = self.__page.locator('.comment-goods')
            child_task_list: list[EvaluationTask] = [] # 一个评论页面下的所有子商品
            for i in range(goods_elements.count()):
                goods_element: Locator = goods_elements.nth(i)
                try:
                    product_link: Locator = goods_element.locator('div.p-name a[href*="item.jd.com"]').first  # 使用第一个符合条件的 <a> 标签
                    product_link.wait_for(timeout=5000)
                except PlaywrightTimeoutError:
                    LOG.error(f"商品详情页面链接获取超时")
                    continue
                
                productHtml_url = "https:" + product_link.get_attribute("href")  # 获取 href 属性
                product_name = product_link.inner_text()  # 获取文本内容

                child_task = task.copy() # 同步任务信息 order_id, orderVoucher_url
                child_task.productHtml_url = productHtml_url 
                child_task.product_name = product_name
                # LOG.debug(f"{task}")
                child_task_list.append(child_task)
            # self.__task_list.extend(child_task_list)
            yield child_task_list
        # self.__task_list = self.__task_list[new_task_index:]
    
    def __step_3(self, task: EvaluationTask) -> EvaluationTask:
        """
        获取评论文本与图片
        """
        if self.CURRENT_AI_GROUP and self.CURRENT_AI_MODEL:
            input_text: str = self.__get_text_from_ai(task.product_name)
        else:
            input_text: str = self.__getText(task.productHtml_url)
        input_image: list = self.__getImage(task.order_id, task.productHtml_url)
        task.input_text = input_text
        task.input_image = input_image
        # LOG.debug(f"{task}")
        return task
    
    def __generate_task(self):
        self.__step_1()
        # new_task_index = len(self.__task_list)

        for child_task_list in self.__step_2():
            for child_task in child_task_list:
                LOG.info("正在生成任务.....")
                self.__page.wait_for_timeout(2000)
                task = self.__step_3(child_task)
                yield task
        
    def __getText(self, product_url: str) -> (str | None):
        """ 从网页上获取已有的评价文本 """
        if self.__page.goto(product_url):
            LOG.trace(f'getText({product_url})')
        # 点击“商品评价”
        element_to_click_1 = self.__page.wait_for_selector('li[data-tab="trigger"][data-anchor="#comment"]', timeout=2000)
        element_to_click_1.click()
        self.__page.wait_for_timeout(1000)
        
        if self.SELECT_CURRENT_PRODUCT_CLOSE is False:
            # 点击“只看当前商品”
            element_to_click_2 = self.__page.wait_for_selector('#comm-curr-sku', timeout=2000)
            element_to_click_2.click()

        text_list = []
        for page in range(1, 4):
            LOG.trace(f'Turn to page {page}')
            self.__page.wait_for_timeout(1000) # QwQ适当停顿避免触发反爬验证, 同时等待资源加载完毕
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
            if len(text_list) * 2 < self.MIN_EXISTING_PRODUCT_DESCRIPTIONS:
                LOG.info("当前商品已有评论文案过少，暂不获取！")
                return
            selected_value = random.choice(text_list)
            if len(selected_value) > self.MIN_DESCRIPTION_CHAR_COUNT and is_bmp_compliant(selected_value): # 取长度大于规定个字符的评价文案。
                return selected_value
            else:
                return get_random_text(text_list)
        
        try:
            text = get_random_text(text_list[int(len(text_list) / 2):]) # 取后半部分评价进行筛选            
        except RecursionError:
            LOG.info('未筛出当前商品下符合要求的评论文案！')
            return
        
        return text 
    
    def __get_text_from_ai(self, product_name):
        content = f"""
        背景：我在京东上购买了一款商品 "{product_name}"
        角色：消费者
        任务：请用一段陈述来评价这个商品
        要求：
            [1] 禁止过多的重复商品别名
            [2] 大约需要120个汉字的文本，且文本长度不少于80个字符
        """
        while True:
            time.sleep(2)
            match self.CURRENT_AI_MODEL:
                case "grok-beta":
                    text = get_response_xai(content, "grok-beta")
                case "grok-vision-beta":
                    text = get_response_xai(content, "grok-vision-beta")
                case _:
                    LOG.error(f"使用了未支持的AI模型：{self.CURRENT_AI_GROUP}:{self.CURRENT_AI_MODEL}")
            if len(text) > self.MIN_DESCRIPTION_CHAR_COUNT:
                LOG.success(f"成功使用{self.CURRENT_AI_GROUP}:{self.CURRENT_AI_MODEL}生成商品评论。")
                return text
    
    def __getImage(self, order_id: str, product_url: str) -> list:
        """ 
        根据商品从网页上获取已有的评价图片(部分)，筛选(随机取一组)后以订单编号为命名依据，并储存到本地。
        
        return: image_files_path(list) 储存到本地的(image目录下)隶属一个订单编号下的所有图片文件路径。
        """
        if self.__page.goto(product_url):
            LOG.trace(f'getImage({order_id}, {product_url})')
        # 点击“商品评价”
        element_to_click_1 = self.__page.wait_for_selector('li[data-tab="trigger"][data-anchor="#comment"]', timeout=2000)
        element_to_click_1.click()
        self.__page.wait_for_timeout(1000)

        if self.SELECT_CURRENT_PRODUCT_CLOSE is False:
            # 点击“只看当前商品”
            element_to_click_2 = self.__page.wait_for_selector('#comm-curr-sku', timeout=2000)
            element_to_click_2.click()

        image_url_lists: list[list] = []
        previous_image_url = ''

        for page in range(1, 4):
            LOG.trace(f'Turn to page {page}')
            self.__page.wait_for_timeout(4000) # QwQ适当停顿避免触发反爬验证, 同时等待资源加载完毕
            # 评价主体组件
            comment_item_elements = self.__page.locator('.comment-item').element_handles()
            for comment_item_element in comment_item_elements:
                image_url_list = []
                # 图片预览组件(小图)
                thumb_img_elements = comment_item_element.query_selector_all('.J-thumb-img')
                for thumb_img_element in thumb_img_elements:
                    # LOG.debug(f'Visible: {thumb_img_element.is_visible()}')
                    thumb_img_element.click() # 模拟点击后会出现更大的图片预览组件
                    self.__page.wait_for_timeout(200)
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
            if sum(len(image_url_list) for image_url_list in image_url_lists) < self.MIN_EXISTING_PRODUCT_IMAGES:
                LOG.info("当前商品已有评论图片过少，暂不获取！")
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
            LOG.info('未筛出当前商品下符合要求的图片组！')
        except TypeError: # get_random_image_group返回结果为None时忽略
            pass

        return image_files_path
    
    def __automatic_evaluate(self, task: EvaluationTask):
        """ 自动评价操作，限单个评价页面"""
        self.__page.goto(task.orderVoucher_url)
        # 商品评价文本
        if not task.input_text:
            task.input_text = random.choice(DEFAULT_COMMENT_TEXT_LIST)
            LOG.warning(f'单号{task.order_id}的订单使用默认评价方式。')
        try:
            text_input_element = self.__page.wait_for_selector('xpath=/html/body/div[4]/div/div/div[2]/div[1]/div[7]/div[2]/div[2]/div[2]/div[1]/textarea', timeout=3000)
            text_input_element.fill(task.input_text)
        except PlaywrightTimeoutError:
            LOG.error("超时，未识别到评价文本输入框！")
            return False
        
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
            LOG.info(f'单号{task.order_id}识别到{len(star5_elements)}个星级评分组件, 全部给予五星好评。')
        except Exception as err:
            LOG.error("未识别到星级评分组件！")

        
        try:
            file_input_element = self.__page.wait_for_selector('xpath=//input[@type="file"]', timeout=2000) # 查找隐藏的文件上传输入框
            # 商品评价图片
            if file_input_element and not task.input_image:
                LOG.warning(f'单号{task.order_id}的订单未上传评价图片，跳过该任务。')
                return False
            # 发送文件路径到文件上传输入框
            for path in task.input_image:
                file_input_element.set_input_files(path)
        
        except Exception as err:
            LOG.error("未识别到评价图片路径输入框！")

        LOG.success(f'单号{task.order_id}的订单评价页面填充完成。')
        # 提交评价
        self.__page.wait_for_timeout(max(5, len(task.input_image) * 2.5) * 1000)
        try:
            btn_submit = self.__page.wait_for_selector('.btn-submit', timeout=2000)
            btn_submit.hover()
            if self.AUTO_COMMIT_CLOSE is False:
                btn_submit.click()
            self.__page.wait_for_timeout(5000)
            return True
        except Exception as err:
            LOG.error("未识别到提交按钮！")

    def __init_image_directory(self, directory_path):
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
