'''
Author: HDJ
StartDate: please fill in
LastEditTime: 2025-06-03 01:39:56
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
Copyright (c) 2024-2025 by HDJ, All Rights Reserved. 
'''
import os
import re
import sys
import time
import random
import hashlib
import secrets
import requests
from PIL import Image, ImageFilter
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError, Locator, ElementHandle, Page 

from .data import EvaluationTask, TuringVerificationRequiredError, DEFAULT_COMMENT_TEXT_LIST
from .utils import *
from .logger import get_logger
from .api_service import *
from .logInWithCookies import logInWithCookies

LOG = get_logger()
WORKING_DIRECTORY_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGE_DIRECTORY_PATH = os.path.join(WORKING_DIRECTORY_PATH, 'temp-img')


class AutomaticEvaluate():
    
    MIN_EXISTING_PRODUCT_DESCRIPTIONS: int = None  # 商品已有文案的最少数量 | 真实评论文案多余这个数脚本才会正常获取已有文案。
    MIN_EXISTING_PRODUCT_IMAGES: int = None        # 商品已有图片的最少数量 | 真实评论图片多余这个数脚本才会正常获取已有图片。
    MIN_DESCRIPTION_CHAR_COUNT: int = None         # 评论文案的最少字数 | 在已有评论中随机筛选文案的限制条件，JD:优质评价要求60字以上。
    CLOSE_SELECT_CURRENT_PRODUCT: bool = None      # 关闭仅查看当前商品 | 启用此设置，在获取已有评论文案与图片时将查看商品所有商品评论信息，关闭可能会导致评论准确性降低
    CLOSE_AUTO_COMMIT: bool = None                 # 关闭自动提交 | 启用此设置，在自动填充完评价页面后将不会自动点击提交按钮
    DEAL_TURING_VERIFCATION = None                 # 图灵测试的处理 | 0触发测试直接退出，1阻塞等待手动处理
    CURRENT_AI_GROUP: str = None                   # AI模型的组别名称 | 使用AI模型生成评论文案
    CURRENT_AI_MODEL: str = None                   # AI模型的名称 | 使用AI模型生成评论文案
    
    def __init__(self) -> None:
        self.__page, browser = None, None
        self.__task_list: list[EvaluationTask] = []
        self.__start_time = time.time() # 标记初始化时间戳
        self.err_occurred = False

    def exec_(self) -> None:
        """主循环"""
        try:
            self.__page, _ = logInWithCookies()
            self.__init_image_directory(IMAGE_DIRECTORY_PATH)
            
            for task in self.__generate_task():
                LOG.debug(f"任务已生成：{task}")
                self.__automatic_evaluate(task)
            
        except Exception as e:
            self.err_occurred = True
            LOG.error(f"执行过程中发生异常: {str(e)}")
        finally:
            hours, remainder = divmod(int(time.time()-self.__start_time), 3600)
            minutes, seconds = divmod(remainder, 60)
            # 根据是否有异常发生，显示不同的结束信息
            if self.err_occurred:
                LOG.warning(f"JD-AutomaticEvaluate: 意外退出--耗时:{hours:02d}小时-{minutes:02d}分钟-{seconds:02d}秒")
            else:
                LOG.success(f"JD-AutomaticEvaluate: 运行结束--耗时:{hours:02d}小时-{minutes:02d}分钟-{seconds:02d}秒")

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
                    LOG.info('识别到结束标志，所有待评价页面url获取结束！') #检查元素tip-icon，这个元素标识没有待评价的订单了
                    break
            except PlaywrightTimeoutError:
                LOG.info('结束标志未出现！')

            self.__page.goto(url_1)
            btn_elements: list = self.__page.locator('.btn-def').element_handles()
            for btn_element in btn_elements:
                parent_element = btn_element.evaluate_handle("el => el.closest('.operate')")
                # 检查父级元素中是否包含提示“请在手机客户端查看订单详情”
                try:
                    mobile_tip_element = parent_element.query_selector('.tip-box .item-fore h3')
                    if mobile_tip_element and "请在手机客户端查看订单详情" in mobile_tip_element.inner_text():
                        LOG.info("跳过外卖订单")
                        continue  # 跳过该元素
                except Exception as e:
                    LOG.debug(f"检查提示信息时出错: {e}")
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
                    # LOG.debug()
                    LOG.error(f"单号 {task.order_id} 商品详情页面链接获取超时")
                    continue
                
                productHtml_url = "https:" + product_link.get_attribute("href")  # 获取 href 属性
                product_name = product_link.inner_text()  # 获取文本内容

                child_task = task.copy() # 同步任务信息 order_id, orderVoucher_url
                child_task.productHtml_url = productHtml_url 
                child_task.product_name = product_name
                # LOG.debug(f"{task}")
                child_task_list.append(child_task)
            yield child_task_list
    
    def __step_3(self, task: EvaluationTask) -> EvaluationTask:
        """
        获取评论文本与图片
        """
        input_text = ""
        input_image = []
        # 使用 AI 模型生成评价文案
        if self.CURRENT_AI_GROUP and self.CURRENT_AI_MODEL:
            input_text: str = self.__get_text_from_ai(task.product_name)

        # 使用已有的文案
        else:
            if self.__page.goto(task.productHtml_url):
                LOG.debug(f'goto {task.productHtml_url}')
                version = None
                try:
                    if self.__page.wait_for_selector('.all-btn', timeout=2000):
                        version = 2024
                except PlaywrightTimeoutError:
                    # 目前来看JD国际等商品使用的是2014的界面，直接简单粗暴匹配两个关键元素
                    try:
                        if self.__page.wait_for_selector('li[data-tab="trigger"][data-anchor="#comment"]', timeout=2000):
                            version = 2014
                    except PlaywrightTimeoutError:
                        self.__requires_TuringVerification()
                match version:
                    case 2014:
                        input_text: str = self.__get_text_paginated_version()
                        self.__page.goto(task.productHtml_url)
                        input_image: list = self.__get_image_paginated_version()
                    case 2024:
                        input_text: str = self.__get_text_infinite_scroll_version()
                        self.__page.goto(task.productHtml_url)
                        input_image: list = self.__get_image_infinite_scroll_version()
                    case _:
                        if self.__requires_TuringVerification():
                            pass
                        else:
                            # 如果没有跳验证，那么大概率是页面变动了
                            LOG.critical(f"商品 {task.productHtml_url} 页面发生变动，请issue联系作者！")
            else:
                LOG.warning(f"商品 {task.productHtml_url} 页面加载失败！")
            
        task.input_text = input_text
        task.input_image = input_image
        # LOG.debug(f"{task}")
        return task
    
    def __generate_task(self):
        self.__step_1()

        for child_task_list in self.__step_2():
            for child_task in child_task_list:
                LOG.info("正在生成任务......")
                self.__page.wait_for_timeout(2000)
                blacklist = []
                whitelist = []
                if whitelist and child_task.order_id not in whitelist: # 白名单
                    continue
                if blacklist and child_task.order_id in blacklist: # 黑名单
                    continue
                task = self.__step_3(child_task)
                yield task

    @staticmethod
    def is_bmp_compliant(text: str):
        """ 
        检测所有字符是否符合基本多文种平面 BMP(Basic Multilingual Plane)
        """
        for char in text:
            if ord(char) > 0xFFFF:
                return False
        return True
    
    def get_random_text(self, text_list):
        """
        取随机评价
        """
        if not text_list or len(text_list) * 2 < self.MIN_EXISTING_PRODUCT_DESCRIPTIONS:
            LOG.info("已有评论文案过少，无法进行随机筛选！")
            return
        selected_value = random.choice(text_list)
        if len(selected_value) > self.MIN_DESCRIPTION_CHAR_COUNT and self.is_bmp_compliant(selected_value): # 取长度大于规定个字符的评价文案。
            return selected_value
        else:
            return self.get_random_text(text_list)
    
    def __get_text_paginated_version(self) -> (str | None):
        """ 
        从网页上获取已有的评价文本，随机翻页版 
        """
        # 点击“商品评价”
        try:
            element_to_click_1 = self.__page.wait_for_selector('li[data-tab="trigger"][data-anchor="#comment"]', timeout=2000)
            element_to_click_1.click()
            self.__page.wait_for_timeout(1000)
        except PlaywrightTimeoutError:
            LOG.warning("“商品评价” 点击失败")
            self.__requires_TuringVerification()

        try:
            if self.__page.wait_for_selector('img[alt="展示图片"]', timeout=2000):
                LOG.info("检测到展示图片，开始滚动加载")
                # 滚动到底部触发加载
                self.__page.evaluate("""
                    window.scrollTo({
                        top: document.documentElement.scrollHeight,
                        behavior: 'smooth'
                    });
                """)
                self.__page.wait_for_timeout(2000)  # 等待内容加载
                # 获取新的页面高度后滚动到30%位置
                new_height = self.__page.evaluate('document.documentElement.scrollHeight')
                self.__page.evaluate(f"""
                    window.scrollTo({{
                        top: {new_height * 0.3},
                        behavior: 'smooth'
                    }});
                """)
                self.__page.wait_for_timeout(1000)
        except PlaywrightTimeoutError:
            LOG.debug("未检测到展示图片，继续执行")
            #部分采用2014网页的商品，点击全部评论，会先出现“京东工业”图片，影响元素加载
            #需要先滚动到底部，发出请求
            #之后重新滚动新页面高度30%，避免出现加载不完全

        try:
            if self.CLOSE_SELECT_CURRENT_PRODUCT is False:
                # 点击“只看当前商品”
                element_to_click_2 = self.__page.wait_for_selector('#comm-curr-sku', timeout=2000)
                element_to_click_2.click()
        except PlaywrightTimeoutError:
            self.__requires_TuringVerification()

        text_list = []
        for page in range(1, 4):
            LOG.debug(f'Turn to page {page}')
            self.__page.wait_for_timeout(1000) # QwQ适当停顿避免触发反爬验证, 同时等待资源加载完毕
            try:
                comment_con_elements = self.__page.locator('.comment-con').element_handles()
                for comment_con_element in comment_con_elements:
                    text_list.append(comment_con_element.inner_text())
            except Exception as err:
                if page == 1:
                    LOG.info('当前暂无评价')
                    break
            # 翻页
            try:
                pager_next_element = self.__page.wait_for_selector('.ui-pager-next', timeout=2000)
                pager_next_element.click()
            except PlaywrightTimeoutError:
                LOG.info('已到最后一页，抓取页数小于设定数！')
                break
        
        try:
            text = self.get_random_text(text_list[int(len(text_list) / 2):]) # 取后半部分评价进行筛选            
        except RecursionError:
            LOG.info('未筛出符合要求的评论文案！')
            return
        
        return text 
        
    def __get_text_infinite_scroll_version(self) -> (str | None):
        """ 
        从网页上获取已有的评价文本，无限滚动版 
        """        
        # 点击 “全部评价”
        try:
            all_btn_element = self.__page.wait_for_selector('.all-btn', timeout=2000)
            all_btn_element.click()
            self.__page.wait_for_timeout(1000)
        except PlaywrightTimeoutError:
            LOG.critical("'全部评价'点击失败!")
        
        try:
            # 点击 “只看当前商品”
            if self.CLOSE_SELECT_CURRENT_PRODUCT is False:
                current_radio_element = self.__page.wait_for_selector('.all-btn', timeout=2000)
                current_radio_element.click()
            time.sleep(1) # 等待动态加载
        except PlaywrightTimeoutError:
            self.__requires_TuringVerification()

        # 包含评价内容的 div 在滚动时动态刷新，且每次刷新数量较少，可看做逐个刷新；每次获取一个评论元素
        text_group = []
        max_scrolls = 60  # 预设滚动次数，等价于抓取的评论元素个数
        for item_index in range(max_scrolls): # data-item-index 从 0 开始
            try:
                # 获取当前索引的元素
                item = self.__page.wait_for_selector(f'div[data-testid="virtuoso-item-list"] > div[data-item-index="{item_index}"]', state="visible", timeout=2000)
            except PlaywrightTimeoutError:
                LOG.info("相关商品没有评价！")
                break
            # 索引超出，即获取完全部元素
            if not item:
                LOG.info(f"已经滚动到最后一个元素! 需求个数: {max_scrolls} ,实际个数: {item_index + 1}")
                break
            # 向下滚动，将元素平滑滚动到视图中；对 item 元素进行滚动时需要其可见
            self.__page.evaluate("element => element.scrollIntoView({behavior: 'smooth', block: 'center'})", item) 
            # 获取评价文本
            try:
                text_element = item.wait_for_selector('.jdc-pc-rate-card-main-desc', state="visible", timeout=3000) 
                text = text_element.inner_text() # 获取元素属内容前，需等待其可见
                if text:
                    text_group.append(text)
            except Exception as err:
                LOG.debug(".jdc-pc-rate-card-main-desc 获取文本失败")
            
        # 随机筛选出一条评价 
        try:
            text = self.get_random_text(text_group)            
        except RecursionError:
            LOG.info('未筛出符合要求的评论文案！')
            return
        return text 
    
    def __get_text_from_ai(self, product_name):
        content = f"""
        背景：我在京东上购买了一款商品 "{product_name}"
        角色：消费者
        任务：请用一段陈述来评价这个商品
        要求：
            [1] 禁止过多的重复商品别名！
            [2] 大约需要100个汉字的文本，且文本长度不少于80个字符！
            [3] 仅用一段陈述完成，不要换行！
        """
        while True:
            time.sleep(2)
            match self.CURRENT_AI_GROUP:
                case "XAI":
                    text = Http_XAI(content, self.CURRENT_AI_MODEL).get_response()
                case "SparkAI":
                    ws_client = Ws_SparkAI(self.CURRENT_AI_MODEL)
                    ws_client.send_request(content)
                    text = ws_client.get_response()
                case _:
                    LOG.error(f"使用了未支持的AI模型：{self.CURRENT_AI_GROUP}:{self.CURRENT_AI_MODEL}")
            if len(text) > self.MIN_DESCRIPTION_CHAR_COUNT:
                LOG.info(f"{self.CURRENT_AI_GROUP}({self.CURRENT_AI_MODEL}): {text}")
                return text
    
    def get_random_image_group(self, image_url_lists: list) -> list:
        """
        取随机评价的图片组

        Args:
            image_url_lists (list): [[url(str), ...], ...]

        Returns:
            一个图片组(list): [url(str), ...]
        """
        if not image_url_lists or sum(len(image_url_list) for image_url_list in image_url_lists) < self.MIN_EXISTING_PRODUCT_IMAGES:
            LOG.info("已有评论图片过少，无法进行随机筛选！")
            return []
        selected_value = random.choice(image_url_lists)
        if len(selected_value) >= 2: # 组内图片数量 
            return selected_value
        else:
            return self.get_random_image_group(image_url_lists)
    
    def download_image_group(self, image_url_group: list):
        """
        下载图片组到image目录

        Args:
            image_url_group (list): [url(str), ...]

        Returns:
            一个图片组 (list): [absPath(str), ...]
        """
        image_files_path = []
        # 使用随机哈希标识图片组
        random_bytes = secrets.token_bytes(32)  # 生成随机字节
        hash_object = hashlib.sha256()  # 创建一个 SHA-256 哈希对象
        hash_object.update(random_bytes)    # 更新哈希对象的内容
        order_hash_hex = hash_object.hexdigest()  # 获取十六进制格式的哈希值
        try:
            for index, image_url in enumerate(image_url_group, start=1):
                image_file_path = os.path.join(IMAGE_DIRECTORY_PATH, f'{order_hash_hex[-12:]}_{index}.jpg')
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
                    LOG.error(f'{image_url} 文件下载失败！Status code: {response.status_code}')
        except RecursionError:
            LOG.info('未筛出符合要求的图片组！')
        except TypeError: # get_random_image_group返回结果为None时忽略
            pass
        return image_files_path
    
    def __get_image_paginated_version(self) -> list:
        """ 
        获取已有的评价图片(部分)，筛选(随机取一组)后以订单编号为命名依据，并储存到本地。随机翻页版

        Returns:
            image_files_path(list): 储存到本地的(image目录下)隶属一个订单编号下的所有图片文件路径。
        """
        # 点击“商品评价”
        try:
            element_to_click_1 = self.__page.wait_for_selector('li[data-tab="trigger"][data-anchor="#comment"]', timeout=2000)
            element_to_click_1.click()
            self.__page.wait_for_timeout(1000)
        except PlaywrightTimeoutError:
            self.__requires_TuringVerification()

        try:
            if self.__page.wait_for_selector('img[alt="展示图片"]', timeout=2000):
                LOG.info("检测到展示图片，开始滚动加载")
                # 滚动到底部触发加载
                self.__page.evaluate("""
                    window.scrollTo({
                        top: document.documentElement.scrollHeight,
                        behavior: 'smooth'
                    });
                """)
                self.__page.wait_for_timeout(2000)  # 等待内容加载
                # 获取新的页面高度后滚动到30%位置
                new_height = self.__page.evaluate('document.documentElement.scrollHeight')
                self.__page.evaluate(f"""
                    window.scrollTo({{
                        top: {new_height * 0.3},
                        behavior: 'smooth'
                    }});
                """)
                self.__page.wait_for_timeout(1000)
        except PlaywrightTimeoutError:
            LOG.debug("未检测到展示图片，继续执行")
            self.__requires_TuringVerification()
        
        try:
            if self.CLOSE_SELECT_CURRENT_PRODUCT is False:
                # 点击“只看当前商品”
                element_to_click_2 = self.__page.wait_for_selector('#comm-curr-sku', timeout=2000)
                element_to_click_2.click()
        except PlaywrightTimeoutError:
            self.__requires_TuringVerification()

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
        return self.download_image_group(self.get_random_image_group(image_url_lists))

    def __get_image_infinite_scroll_version(self) -> list:
        """ 
        获取已有的评价图片(部分)，筛选(随机取一组)后以订单编号为命名依据，并储存到本地。无限滚动版

        Returns:
            image_files_path(list): 储存到本地的(image目录下)隶属一个订单编号下的所有图片文件路径。
        """
        # 点击 “全部评价”
        try:
            all_btn_element = self.__page.wait_for_selector('.all-btn', timeout=2000)
            all_btn_element.click()
            self.__page.wait_for_timeout(1000)
        except PlaywrightTimeoutError:
            LOG.critical("'全部评价'点击失败!")
            self.__requires_TuringVerification()
        
        # 点击 “只看当前商品”
        try:
            if self.CLOSE_SELECT_CURRENT_PRODUCT is False:
                current_radio_element = self.__page.wait_for_selector('.all-btn', timeout=2000)
                current_radio_element.click()
            time.sleep(1) # 等待动态加载
        except PlaywrightTimeoutError:
            self.__requires_TuringVerification()
        
        # 包含评价内容的 div 在滚动时动态刷新，且每次刷新数量较少，可看做逐个刷新；每次获取一个评论元素
        image_url_group: list[list] = []
        max_scrolls = 100  # 预设滚动次数，等价于抓取的评论元素个数
        for item_index in range(max_scrolls): # data-item-index 从 0 开始
            try:
                # 获取当前索引的元素
                item = self.__page.wait_for_selector(f'div[data-testid="virtuoso-item-list"] > div[data-item-index="{item_index}"]', state="visible", timeout=2000)
            except PlaywrightTimeoutError:
                LOG.info("相关商品没有评价！")
                break
            # 索引超出，即获取完全部元素
            if not item:
                LOG.info(f"已经滚动到最后一个元素! 需求个数: {max_scrolls} ,实际个数: {item_index + 1}")
                break
            # 向下滚动，将元素平滑滚动到视图中；对 item 元素进行滚动时需要其可见
            self.__page.evaluate("element => element.scrollIntoView({behavior: 'smooth', block: 'center'})", item) 
            # 获取图片 url
            image_url_list = []
            image_items = item.query_selector_all('.jd-content-pc-media-list-item') # 一个评论内的全部图片元素，视频与图片都需要点击此元素打开预览元素。其子元素当出现视频时不可点击
            if image_items:
                time.sleep(0.2) # 等待滚动完成；由于使用的 JS 滚动操作时异步的，不能单使用 playwright 判断元素是否稳定来确定滚动是否完成；仅为了视觉效果，不影响下面的内容获取
                item.wait_for_element_state(state="stable", timeout=2000) # 有图片元素，需等待页面元素稳定 
                for image_item in image_items:
                    image_item.click() # 点击后会出现更大的图片预览元素
                    try:
                        preview_image_element = self.__page.wait_for_selector('.jdc-pc-media-preview-image', state="visible", timeout=2000) # 等待预览图可见
                        if preview_image_element:
                            style = self.__page.evaluate("element => element.getAttribute('style')", preview_image_element)
                            # 使用正则表达式提取图片 URL
                            url_match = re.search(r'https://img[^"\']+\.jpg', style)
                            if url_match:
                                url = url_match.group(0)
                                image_url_list.append(url)
                            else:
                                LOG.debug("未获取到图片url")
                    except PlaywrightTimeoutError:
                        # 由于评价视频与图片混放，有的 image_item 点击后是出现视频预览元素，所以在此忽略掉
                        pass
                    except Exception as err:
                        LOG.debug(f"{err}")
                    # 关闭预览图
                    try:
                        preview_close_element = self.__page.wait_for_selector('.jdc-pc-media-preview-close', timeout=2000)
                        preview_close_element.click()
                    except PlaywrightTimeoutError as err:
                        LOG.error("预览图关闭失败！")
                        self.__requires_TuringVerification()
            if image_url_list:
                image_url_group.append(image_url_list)
            if len(image_url_group) >= max(20, self.MIN_EXISTING_PRODUCT_IMAGES): # 评论图片充足，仅取部分; 最差情况，每组一张图也可满足 MIN_EXISTING_PRODUCT_IMAGES
                break
        return self.download_image_group(self.get_random_image_group(image_url_group))
    
    def __automatic_evaluate(self, task: EvaluationTask):
        """自动评价操作，限单个评价页面"""
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
        self.__page.wait_for_timeout(max(5, len(task.input_image) * 2.5) * 1000) # 等待图片上传完成
        try:
            btn_submit = self.__page.wait_for_selector('.btn-submit', timeout=2000)
            btn_submit.hover()
            if self.CLOSE_AUTO_COMMIT is False:
                btn_submit.click()
            self.__page.wait_for_timeout(5000) # 切换下一个评价任务的间隔
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

    def __requires_TuringVerification(self) -> bool:
        """判断是否进入图灵验证界面"""
        # 该方法是通过 timeout 异常调用的，也就是说在自动化流程中出现了元素获取失败的情况，即使在此刻通过了人机验证，也无法回到上一步（获取元素）
        # 1. 所有等待元素的方法都进行retry 2.跳过当前任务，继续往下进行（不适用于连续多个任务都出现人机验证的情况）
        try:
            # 一般来说，进入测试页面时 page 还在等待其他元素，故 timeout 不宜过大，进而确保整体性能。
            if self.__page.wait_for_selector('.verifyBtn', timeout=1500):
                match self.DEAL_TURING_VERIFCATION:
                    case 0:
                        raise TuringVerificationRequiredError
                    case 1:
                        self.__handle_TuringVerification()
                    case _ as e:
                        LOG.error(f"DEAL_TURING_VERIFCATION 所选值 {e} 非法！")
        except PlaywrightTimeoutError:
            pass
        return False
    
    def __handle_TuringVerification(self) -> bool:
        """
        进行图灵测试
        
        Returns:
            图灵测试是否通过(bool):
        """
        turing_url = self.__page.url
        LOG.debug(f"{turing_url}")
        LOG.info("等待人机验证......")
        while True:
            # 检测是否通过验证：1.是否还在验证页面 2.根据验证页面的 url 参数 returnurl 可以获取测试成功后的跳转页面
            # 但是不同类型的的商品最终重定向的页面 url 与 returnurl 不完全匹配，如京东国际等
            try:
                # 持续检测页面 url，一经变动立刻抛出异常
                self.__page.wait_for_url(turing_url, timeout=0.1) # 为了 url 检测的灵敏度更高，超时时长应设置的尽可能小
                time.sleep(0.2) # url 保持在测试时页面会快速的循环，考虑到性能方面建议阻塞
            except PlaywrightTimeoutError:
                # 暂认为，离开验证页面即为验证通过
                LOG.success("人机验证已通过")
                return True