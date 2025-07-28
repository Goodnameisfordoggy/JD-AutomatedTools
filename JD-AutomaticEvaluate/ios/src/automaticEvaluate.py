"""
Author: HDJ @https://github.com/Goodnameisfordoggy
Time@IDE: 2025-07-10 00:20:25 @PyCharm
Description: 自动化流程

				|   早岁已知世事艰，仍许飞鸿荡云间；
				|   曾恋嘉肴香绕案，敲键弛张荡波澜。
				|
				|   功败未成身无畏，坚持未果心不悔；
				|   皮囊终作一抔土，独留屎山贯寰宇。

Copyright (c) 2024-2025 by HDJ, All Rights Reserved.
"""
import asyncio
import sys
import time
import random
import hashlib
from PIL import Image
from ascript.ios import action, system, screen, media
from ascript.ios.system import R, device
from ascript.ios.node import Selector, Element
from .data import EvaluationTask, ElementNotFoundError
from .utils import sync_retry, progress_bar
from .selector import WaitForSelector
from .logger import get_logger
LOG = get_logger()
    
class JDAppAutomaticEvaluate(object):
    """JD APP 端自动评价逻辑封装"""

    MIN_EXISTING_PRODUCT_DESCRIPTIONS: int = 15     # 商品已有文案的最少条数 | 真实评论文案多余这个数脚本才会正常获取已有文案。
    MIN_EXISTING_PRODUCT_IMAGES: int = 15           # 商品已有图片的最少张数 | 真实评论图片多余这个数脚本才会正常获取已有图片。
    MIN_DESCRIPTION_CHAR_COUNT: int = 60            # 每条评论文案的最少字数 | 在已有评论中随机筛选文案的限制条件，JD:优质评价要求60字以上。
    MIN_IMAGES_PER_REVIEW: int = 2                  # 每条评论包含的图片张数 | 在已有评论中随机筛选图片组的限制条件；
    SELECT_CURRENT_PRODUCT: bool = True             # 仅查看当前商品 | True：在获取已有评论文案与图片时仅查看当前商品评论信息；False：可能会导致评论准确性降低；
    AUTO_COMMIT: bool = False                       # 自动提交 | True：在自动填充完评价页面后将自动点击提交按钮；False：不自动点击提交按钮，需手动提交；
    GUARANTEE_COMMIT: bool = False                  # 保底评价 | True：在获取不到已有信息时仅使用默认文本评价（无图片）并提交

    def __init__(self):
        self.screen_width, self.screen_height = screen.size()
        self.current_task: EvaluationTask = EvaluationTask()

    def back_to_previous_page(self, msg: str = "") -> None:
        """退回到上一页"""
        # 从屏幕左边缘向右滑动
        action.slide(0, int(self.screen_height * 0.5), int(self.screen_width * 0.3), int(self.screen_height * 0.5))
        if msg:
            LOG.debug(f"{msg}")
        time.sleep(1)  # 等待页面加载

    def scroll_to_visible(self, element: Element, direction: str = "visible", distance: int | float = 1.0) -> bool:
        """
        将元素滚动至可见

        Args:
            direction: 页面内容加载的方向
            distance: 滚动的距离（像素）
        """
        if direction not in ("down", "up", "left", "right", "visible"):
            raise ValueError("direction must be 'down', 'up', 'left', 'right', 'visible'")
        rx, ry, rw, rh = element.rect
        # 根据坐标选择滑动方向
        if direction == "visible":
            direction = "down" if ry > 0 else "up"
            # direction = "right" if rx > 0 else "left"
        if isinstance(distance, float):
            if direction in ("up", "down"):
                d = min(rh * distance, self.screen_height)
            elif direction in ("left", "right"):
                d = min(rw * distance, self.screen_width)
        elif isinstance(distance, int):
            d = distance

        while not element.visible:
            LOG.debug(f"{element.rect}")
            if direction == "down":
                # 内容向下加载，即从下向上滑动
                action.slide(int(self.screen_width * 0.5), int(self.screen_height * 0.75), int(self.screen_width * 0.5), int(self.screen_height * 0.75 - d), 300)
            elif direction == "up":
                action.slide(int(self.screen_width * 0.5), int(self.screen_height * 0.25), int(self.screen_width * 0.5), int(self.screen_height * 0.25 + d), 300)
            elif direction == "left":
                action.slide(int(self.screen_width * 0.25), int(self.screen_height * 0.5), int(self.screen_width * 0.25 + d), int(self.screen_height * 0.5), 300)
            elif direction == "right":
                action.slide(int(self.screen_width * 0.75), int(self.screen_height * 0.5), int(self.screen_width * 0.75 - d), int(self.screen_height * 0.5), 300)
            time.sleep(0.3)
        # 元素居中
        if element.visible:
            rx, ry, rw, rh = element.rect
            LOG.debug(f"Final {element.rect}")
            # 垂直方向
            dy = (ry + int(rh * 0.5)) - int(self.screen_height * 0.5)
            if dy > 0:
                action.slide(int(self.screen_width * 0.5), int(self.screen_height * 0.75), int(self.screen_width * 0.5), int(self.screen_height * 0.75 - dy), 500)
            elif dy < 0:
                action.slide(int(self.screen_width * 0.5), int(self.screen_height * 0.25), int(self.screen_width * 0.5), int(self.screen_height * 0.25 + dy), 500)
            time.sleep(0.5)
            LOG.debug(f"Vertical Centered {element.rect}")
            return True
        return False

    # def click_element(self, element: Element) -> None:
    #     """
    #     点击元素
    #     """

    def select_current_product(self) -> bool:
        """
        选择当前商品

        - 起始位置：买家评价-页面
        """
        # 多款式商品
        try:
            product_style_ele = WaitForSelector().get("product_style_dropdown_list")
            if product_style_ele:
                # 点击 “款式”
                product_style_ele.click()
                # 点击 “查看当前商品”
                WaitForSelector().get("current_product_checkbox_2").click()
                # product_name_label = WaitForSelector().get("product_name_label")
                # if product_name_label.text:
                #     self.current_task.product_name = product_name_label.text
                # selected_product_style_label = WaitForSelector().get("selected_product_style_label")
                # if selected_product_style_label.text:
                #     self.current_task.product_style = selected_product_style_label.text
                # 点击 “确定”
                WaitForSelector().get("confirm_current_product").click()
                return True
        except ElementNotFoundError:
            pass
        # 单品
        try:
            current_product_checkbox_1 = WaitForSelector().get("current_product_checkbox_1")
            if current_product_checkbox_1:
                current_product_checkbox_1.click()
                return True
        except ElementNotFoundError:
            pass
        return False

    def analyze_cell(self) -> tuple[list[tuple[int, str]], list[list[tuple[int, str]]]]:
        """
        分析包含评价信息的列表 cell 元素，分析：文本内容，图片组

        - 起始位置：买家评价-页面

        Returns:
             tuple[list[tuple[int, str]], list[list[tuple[int, str]]]]:
             ( [(cell_index, 文案内容), ...], [ [(cell索引, [第一组第1张图]), ...], ...] )
        """
        LOG.info("正在分析已有评价内容...")
        progress_bar(0, 1, 10)  # 初始化进度条
        cell_eles = WaitForSelector().get("evaluation_cells")  # 获取当前页面加载出的所有评价 cell
        # 筛出文案内容，图片数量符合要求的 cell
        evaluation_texts = []
        image_groups = []
        for index, cell_ele in enumerate(cell_eles, start=1):
            # 获取单个 cell 下的文案内容
            if not self.current_task.input_text:
                try:
                    reply_ele = WaitForSelector().get("reply_to_evaluation", cell_index=index)
                    if reply_ele:
                        text = WaitForSelector().get("evaluation_inner_text", cell_index=index).text
                        evaluation_texts.append((index, text))  # index: 第x个cell元素，text：文案内容
                        # LOG.debug(f"cell_index: {index}, text: {text}")
                except ElementNotFoundError:
                    # 广告，评价提问的 cell 中没有 “回复评价”
                    pass
            if not self.current_task.input_image:
                # 获取单个 cell 下全部的 XCUIElementTypeImage
                try:
                    img_eles = WaitForSelector().get("evaluation_inner_images", cell_index=index)
                    if img_eles:
                        image_groups.append([(index, img_ele) for img_ele in img_eles])
                except ElementNotFoundError:
                    # 研究发现，cell中有视频元素时，不会加载出 XCUIElementTypeImage，
                    pass
            progress_bar(index, len(cell_eles), 10)
        LOG.debug(f"evaluation_texts:{len(evaluation_texts)}, image_groups:{len(image_groups)}")
        return evaluation_texts, image_groups

    @sync_retry(max_retries=3, retry_delay=2, backoff_factor=2, exceptions=(ValueError,))
    def get_text_from_cell(self, evaluation_texts: list[tuple[int, str]]) -> str | None:
        """
        获取已有评论内容: 定位到cell并文本内容

        - 起始位置：买家评价-页面

        Returns:
             str: 一条评价文案
        """
        inner_text = ""
        # 筛出并获取符合要求的文案内容
        legal_text_cell = self.select_one_legal_text(evaluation_texts)
        if not legal_text_cell:
            LOG.warning("没有符合要求的文案内容！")
            return None
        cell_index = legal_text_cell[0]
        LOG.info(f"样本数【{len(evaluation_texts)}】获取索引为【{cell_index}】的文案")
        inner_text = legal_text_cell[1]
        # 评价文本过长，显示不全，进入单条评论的详情页面获取完整文案
        if inner_text.endswith("...展开"):
            LOG.info("正在定位目标cell...")
            cell_ele = WaitForSelector().get("evaluation_cell", cell_index=cell_index)
            self.scroll_to_visible(cell_ele, "visible", 0.5)
            # 点击文案区域
            inner_text_ele = WaitForSelector().get("evaluation_inner_text", cell_index=cell_index)
            inner_text_ele.scroll("visible", 0.8)
            time.sleep(5)
            LOG.debug(f"visible:{inner_text_ele.visible}, {inner_text_ele.rect}")
            inner_text_ele.click()
            evaluation_details_ele = WaitForSelector().get("evaluation_details")
            if evaluation_details_ele:
                # 单条评价详情-页面
                fragment = inner_text[:9] # 使用文案片段定位包含完整文案的元素
                full_inner_text_ele = WaitForSelector().get("full_evaluation_inner_text", fragment=fragment)
                inner_text = full_inner_text_ele.text
                self.back_to_previous_page(msg="返回-买家评价-页面")
        # 检测文案是否符合需求
        if len(inner_text) < self.MIN_DESCRIPTION_CHAR_COUNT:
            raise ValueError(f"文案字数【{len(inner_text)}】小于设置【{self.MIN_DESCRIPTION_CHAR_COUNT}】")
        LOG.debug(f"【inner_text】{inner_text}")
        return inner_text

    @sync_retry(max_retries=3, retry_delay=2, backoff_factor=2, exceptions=(ValueError,))
    def get_image_from_cell(self,  image_groups: list[list[tuple[int, str]]]) -> list | None:
        """
        获取已有评论内容：定位到cell并获取图片组

        - 起始位置：买家评价-页面

        Returns:
            list[str]: 图片路径的列表
        """
        inner_img = []
        legal_image_group = self.select_one_legal_image_group(image_groups)
        if not legal_image_group:
            LOG.warning("没有符合要求的图片组！")
            return None
        cell_index = legal_image_group[0][0]
        LOG.info(f"样本数【{len(image_groups)}】获取索引为【{cell_index}】的图片组")
        cell_ele = WaitForSelector().get("evaluation_cell", cell_index=cell_index)
        LOG.info("正在定位目标cell...")
        self.scroll_to_visible(cell_ele, "visible", distance=0.5)
        # 借助文案元素进入-单条评价详情-页面
        inner_text_ele = WaitForSelector().get("evaluation_inner_text", cell_index=cell_index)
        inner_text_ele.scroll("visible", 0.3)
        time.sleep(5)
        LOG.debug(f"visible:{inner_text_ele.visible}, {inner_text_ele.rect}")
        inner_text_ele.click()  # 点击文案元素
        # 单条评价详情-页面
        first_img_ele = WaitForSelector().get("evaluation_first_img")
        first_img_ele.scroll("visible", 0.5)
        first_img_ele.click()
        # 截屏纵坐标范围
        y1 = int((self.screen_height / 2) - (self.screen_width / 2))
        y2 = int((self.screen_height / 2) + (self.screen_width / 2))
        for index in range(1, len(legal_image_group) + 1):
            time.sleep(0.2)  # 等待图片加载
            # 区域截屏
            image = screen.capture([0, y1, self.screen_width, y2])
            # 保存图片
            img_file_path = R.img(f"img_{index}.png")
            screen.image_save(image, img_file_path)
            inner_img.append(img_file_path)
            # 从右向左滑动切图
            action.slide(600, int(self.screen_height / 2), 200, int(self.screen_height / 2), duration=200)
        self.back_to_previous_page(msg="返回-买家评价-页面")
        LOG.debug(f"【inner_img】{inner_img}")
        return inner_img

    def select_one_legal_text(self, text_list: list[tuple[int, str],]) -> bool | str:
        """
        检验文案内容是否符合规定，并选出合规的任意一组
        """
        if not text_list or len(text_list) == 0:
            return False
        legal_texts = []
        for index, inner_text in text_list:
            if inner_text.endswith("...展开"):
                legal_texts.append((index, inner_text))
            if len(inner_text) < self.MIN_DESCRIPTION_CHAR_COUNT:
                continue
            legal_texts.append((index, inner_text))
        legal_texts = legal_texts[1:-1] # 掐头去尾
        if len(legal_texts) == 0:
            return False
        return random.choice(legal_texts)

    def select_one_legal_image_group(self, image_groups: list[list[tuple[int, str],],]) -> bool | list:
        """
        检验图片组是否符合规定，并选出合规的任意一组
        """
        if not image_groups or len(image_groups) == 0:
            return False
        image_count = sum([len(image_group) for image_group in image_groups])
        if image_count <= self.MIN_EXISTING_PRODUCT_IMAGES:
            LOG.info(f"已有图片张数【{image_count}】小于设置【{self.MIN_EXISTING_PRODUCT_IMAGES}】")
            return False
        legal_groups = [image_group for image_group in image_groups if len(image_group) >= self.MIN_IMAGES_PER_REVIEW]
        legal_groups = legal_groups[1:-1]   # 掐头去尾
        if len(legal_groups) == 0:
            return False
        return random.choice(legal_groups)

    def auto_fill(self, task: EvaluationTask) -> None:
        """
        自动填充评价

        - 起始位置：订单评价-页面
        """
        # 获取文本框焦点
        text_input_ele = WaitForSelector().get("evaluation_text_input")
        ry = text_input_ele.rect[1]
        text_input_ele.click()
        action.input(task.input_text)   # 输入评价内容
        action.slide(int(self.screen_width / 2), ry, int(self.screen_width / 2), ry - 100) # 收起键盘
        time.sleep(0.2)
        image_input_ele = WaitForSelector().get("evaluation_image_input")
        if not image_input_ele:
            LOG.warning("没有图片输入元素")
        else:
            # 将图片存入相册
            for img in task.input_image:
                if media.save_pic2photo(img):
                    LOG.debug(f"{img}成功存入相册")
                else:
                    LOG.critical(f"{img}存入相册失败")
            # 模拟填充图片
            image_input_ele.click()  # 进入-相册总览-页面
            select_picture_ele = WaitForSelector().get("select_picture")
            select_picture_ele.click()
            WaitForSelector().get("picture_view_first_img").click()
            # 进入-相册单图展示-页面
            img_select_ele = WaitForSelector().get("img_checkbox")
            if img_select_ele:
                rx, ry, rw, rh = img_select_ele.rect
                x = int(rx + rw / 2)
                y = int(ry + rh / 2)
                for i in range(min(9, len(task.input_image))):  # 一次最多选 9 张图
                    action.click(x, y)
                    time.sleep(0.2)
                    # 从右向左滑动切图
                    action.slide(600, 500, 400, 500, duration=20)
                    time.sleep(1) # 等待图片稳定
                WaitForSelector().get("img_select_complete").click()
            LOG.success("评价内容填充完成")
            if self.AUTO_COMMIT:
                WaitForSelector().get("evaluation_commit_btn").click()
                LOG.success("当前评价自动提交成功")
            else:
                LOG.warning(f"【AUTO_COMMIT】:{self.AUTO_COMMIT}，等待手动提交评价......")
                

    def run(self):
        # 打开 JD App
        system.app_start(bundle_id="com.360buy.jdmobile")
        # 点击 “我的”，切换页面并刷新
        WaitForSelector().get("self_page").click()
        # 点击 “待评价”
        WaitForSelector().get("order_evaluated").click()

        # 任务循环--起点
        task_index = 1
        while True:
            goto_evaluate_ele = WaitForSelector().get("goto_evaluate")
            if not goto_evaluate_ele:
                LOG.success("没有待评价订单-程序退出！")
                sys.exit(0)
            self.current_task = EvaluationTask()  # 初始化任务
            self.current_task.id = f"{task_index}"
            # 通过 “去评价” 按钮元素计算大致的商品展示图片的 y 坐标
            rx, ry, rw, rh = goto_evaluate_ele.rect
            # 计算商品展示图片的大致坐标，并点击进入商详页
            x = int(self.screen_width * 0.15)  # 估算值，可点击的 x
            y = int(ry - rh * 1.2)  # 估算值，可点击的 y
            action.click(x, y, duration=20)  # 进入-商品详情-页面
            LOG.debug("进入-商品详情-页面")

            # 无货弹窗检测
            if WaitForSelector().get("out_of_stock_sign"):
                WaitForSelector().get("gift_close_btn").click()  # 关闭弹窗
                LOG.debug("关闭无货弹窗")

            # 将 “买家评价” 滑入视图
            time.sleep(1) # 页面加载较慢
            action.slide(500, 600, 500, 500, duration=20)  # 必须先扒拉一下才能加载出评价数据
            buyer_evaluation_ele = WaitForSelector().get("buyer_evaluation")
            while buyer_evaluation_ele.visible is False:
                jd_main_body = WaitForSelector().get("jd_main_body")
                jd_main_body.scroll("down", 0.3)
            buyer_evaluation_ele.click()  # 进入-买家评价-页面
            LOG.debug("进入-买家评价-页面")
            if self.SELECT_CURRENT_PRODUCT:
                if not self.select_current_product():
                    LOG.warning("选择当前商品失败！")
            # 下滑加载更多评价内容
            for _ in range(6):
                action.slide(random.randint(int(self.screen_width * 0.4), int(self.screen_width * 0.6)),
                             random.randint(int(self.screen_height * 0.6), int(self.screen_height * 0.8)),
                             random.randint(int(self.screen_width * 0.4), int(self.screen_width * 0.6)),
                             random.randint(int(self.screen_height * 0.2), int(self.screen_height * 0.4)),
                             500)
                time.sleep(0.2)
            inner_texts, inner_image_groups = self.analyze_cell()
            self.current_task.input_text = self.get_text_from_cell(inner_texts)
            self.current_task.input_image = self.get_image_from_cell(inner_image_groups)

            self.back_to_previous_page("返回-商品详情-页面")
            self.back_to_previous_page("返回-评价中心-页面")
            goto_evaluate_ele = WaitForSelector().get("goto_evaluate").click()  # 进入-订单评价-页面
            LOG.info(f"Task:{self.current_task}")
            self.auto_fill(self.current_task)

            task_index += 1
            break