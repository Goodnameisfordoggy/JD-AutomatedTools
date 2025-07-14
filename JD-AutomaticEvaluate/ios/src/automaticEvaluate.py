"""
Author: HDJ @https://github.com/Goodnameisfordoggy
Time@IDE: 2025-07-10 00:20:25 @PyCharm
Description: 使用到的页面结构
JD-APP
    - 我的-页面
        - 评价中心-页面（待评价-图标）
            - 商品详情详-页面（待评价-列表 > 商品展示图）
                - 买家评价-页面（买家评价-字样）
                    - 单条评价详情-页面（买家评价-列表 > 子项主体文案）
                        - 评价大图展示-页面（首张评价预览图）
            - 订单评价-页面（待评价-列表 > 子项主体非商品展示图部分/去评价按钮）
                - 系统相册预览-页面（添加图片-字样）
                    - 仅照片预览-页面（仅照片选项）
                        - 照片大图显示-页面（仅照片预览区域 > 图片元素）

				|   早岁已知世事艰，仍许飞鸿荡云间；
				|   曾恋嘉肴香绕案，敲键弛张荡波澜。
				|
				|   功败未成身无畏，坚持未果心不悔；
				|   皮囊终作一抔土，独留屎山贯寰宇。

Copyright (c) 2024-2025 by HDJ, All Rights Reserved.
"""
import asyncio
import time
import random
import hashlib
from PIL import Image

from ascript.ios import action, system, screen, media
from ascript.ios.system import R, device
from ascript.ios.node import Selector, Element
from .data import EvaluationTask
from .utils import sync_retry, progress_bar


class JDAppAutomaticEvaluate(object):
    """JD APP 端自动评价逻辑封装"""

    MIN_EXISTING_PRODUCT_DESCRIPTIONS: int = 15  # 商品已有文案的最少条数 | 真实评论文案多余这个数脚本才会正常获取已有文案。
    MIN_EXISTING_PRODUCT_IMAGES: int = 15  # 商品已有图片的最少张数 | 真实评论图片多余这个数脚本才会正常获取已有图片。
    MIN_DESCRIPTION_CHAR_COUNT: int = 60  # 每条评论文案的最少字数 | 在已有评论中随机筛选文案的限制条件，JD:优质评价要求60字以上。
    MIN_IMAGES_PER_REVIEW: int = 2  # 每条评论包含的图片张数 | 在已有评论中随机筛选图片组的限制条件
    CLOSE_SELECT_CURRENT_PRODUCT: bool = None  # 关闭仅查看当前商品 | True：在获取已有评论文案与图片时将查看商品所有商品评论信息，关闭可能会导致评论准确性降低
    CLOSE_AUTO_COMMIT: bool = None  # 关闭自动提交 | True：在自动填充完评价页面后将不会自动点击提交按钮
    GUARANTEE_COMMIT: bool = None  # 保底评价 | True：在获取不到已有信息时仅使用默认文本评价（无图片）并提交

    def __init__(self):
        self.screen_width, self.screen_height = screen.size()

    def back_to_previous_page(self, msg: str = "") -> None:
        """退回到上一页"""
        # 从屏幕左边缘向右滑动
        action.slide(0, 800, 300, 800)
        if msg:
            print(msg)
        time.sleep(1)  # 等待页面加载

    def select_current_product(self) -> None:
        """
        选择当前商品

        - 起始位置：返回买家评价列表-页面
        """
        # 选择当前商品--点击 “款式”
        product_style_ele: Element | None = Selector().name("款式").find(timeout=10000)
        if not product_style_ele:
            raise ValueError("product_style_ele <UNK>")
        else:
            product_style_ele.click()
            time.sleep(1)
            print("点击:选择当前商品--点击 “款式”")

        # 选择当前商品--点击 “查看当前商品”
        current_product_ele: Element | None = Selector().name("查看当前商品").find(timeout=10000)
        if not current_product_ele:
            raise ValueError("current_product_ele <UNK>")
        else:
            current_product_ele.click()
            print("点击:选择当前商品--点击 “查看当前商品”")
            time.sleep(1)
        # 选择当前商品--点击 “确定”
        confirm_current_product_ele: Element | None = Selector().name("确定").find(timeout=10000)
        if not confirm_current_product_ele:
            raise ValueError("confirm_current_product_ele <UNK>")
        else:
            confirm_current_product_ele.click()
            print("点击:选择当前商品--点击 “确定”")
            time.sleep(1)

    @sync_retry(max_retries=3, retry_delay=2, backoff_factor=2, exceptions=(ValueError,))
    def get_text(self) -> str | None:
        """
        获取已有评论内容--文本

        - 起始位置：返回买家评价列表-页面
        Returns:
             str: 一条评价文案
        """
        inner_text = ""
        print("正在分析已有评价文案...")
        cell_eles: list[Element] = Selector().xpath(
            "//XCUIElementTypeTable//XCUIElementTypeCell").find_all()  # 获取当前页面加载出的所有评价 cell
        if not cell_eles:
            raise ValueError("cell_eles <UNK>")
        else:
            cell_index = random.randint(1, len(cell_eles))
            print(f"样本数【{len(cell_eles)}】获取索引为【{cell_index}】的文案")
            inner_text_xpath = f"//XCUIElementTypeTable//XCUIElementTypeCell[{cell_index}]//XCUIElementTypeButton[1]"
            inner_text_ele: Element | None = Selector().xpath(inner_text_xpath).find(timeout=10000)
            if not inner_text_ele:
                raise ValueError("inner_text_ele <UNK>")
            else:
                inner_text = inner_text_ele.text
                # 评价文本过长，显示不全，进入单条评论的详情页面获取完整文案
                if inner_text.endswith("...展开"):
                    inner_text_ele.scroll("visible", 3.0)
                    # 更新元素状态
                    inner_text_ele: Element | None = Selector().xpath(inner_text_xpath).find(timeout=10000)
                    if not inner_text_ele:
                        raise ValueError("inner_text_ele <UNK> 2")
                    else:
                        inner_text_ele.click()  # 进入-单条评价详情-页面
                        time.sleep(1)
                        complete_inner_text_xpath = "//XCUIElementTypeTable//XCUIElementTypeCell[1]//XCUIElementTypeStaticText[1]"
                        complete_inner_text_ele: Element | None = Selector().xpath(complete_inner_text_xpath).find(timeout=10000)
                        if not complete_inner_text_ele:
                            self.back_to_previous_page(msg="返回-买家评价-页面")
                            raise ValueError("complete_inner_text_ele <UNK>")
                        else:
                            inner_text = complete_inner_text_ele.text
                            self.back_to_previous_page(msg="返回-买家评价-页面")
        # 检测文案是否符合需求
        if len(inner_text) < self.MIN_DESCRIPTION_CHAR_COUNT:
            raise ValueError(f"文案字数【{len(inner_text)}】小于设置【{self.MIN_DESCRIPTION_CHAR_COUNT}】")
        return inner_text

    @sync_retry(max_retries=3, retry_delay=2, backoff_factor=2, exceptions=(ValueError,))
    def get_image(self) -> list | None:
        """
        获取已有评论内容--图片

        - 起始位置：返回买家评价列表-页面

        Returns:
            list[str]: 图片路径的列表
        """
        inner_img = []
        print("正在分析已有评价图片...")
        progress_bar(0, 1, 10)
        cell_eles: list[Element] = Selector().xpath(
            "//XCUIElementTypeTable//XCUIElementTypeCell").find_all()  # 获取当前页面加载出的所有评价 cell
        if not cell_eles:
            raise ValueError("cell_eles <UNK>")
        else:
            # 筛出图片数量符合要求的 cell
            image_groups = []
            for index, cell_ele in enumerate(cell_eles, start=1):
                # 获取单个 cell 下全部的 XCUIElementTypeImage
                # 研究发现，cell中有视频元素时，不会加载出 XCUIElementTypeImage
                img_xpath = f"//XCUIElementTypeTable//XCUIElementTypeCell[{index}]//XCUIElementTypeOther[1]//XCUIElementTypeImage"
                img_eles: list[Element] | None = Selector().xpath(img_xpath).find_all()
                image_groups.append([(index, img_ele) for img_ele in img_eles])
                progress_bar(index, len(cell_eles), 10)

            legal_image_group = self.select_one_legal_image_group(image_groups)
            if not legal_image_group:
                raise ValueError("未选出合适的图片组！")
            else:
                cell_index = legal_image_group[0][0]
                print(f"样本数【{len(cell_eles)}】获取索引为【{cell_index}】的图片组")
                cell_ele: Element | None = Selector().xpath(
                    f"//XCUIElementTypeTable//XCUIElementTypeCell[{cell_index}]").find(timeout=10000)
                if not cell_ele:
                    raise ValueError("cell_eles <UNK>")
                else:
                    cell_ele.scroll("visible", 1.8)  # distance 不宜过大，否则在目标为首、尾元素时会有意想不到的异常；
                    # 借助文案元素进入-单条评价详情-页面
                    inner_text_xpath = f"//XCUIElementTypeTable//XCUIElementTypeCell[{cell_index}]//XCUIElementTypeButton[1]"
                    inner_text_ele: Element | None = Selector().xpath(inner_text_xpath).find(timeout=10000)
                    if not inner_text_ele:
                        raise ValueError("inner_text_ele <UNK>")
                    else:
                        inner_text_ele.click()  # 点击文案元素
                        time.sleep(1)
                        # 单条评价详情-页面
                        first_img_xpath = "//XCUIElementTypeTable//XCUIElementTypeCell[2]//XCUIElementTypeImage"
                        first_img_ele: Element | None = Selector().xpath(first_img_xpath).scroll("visible", 0.5).click().find(timeout=10000)
                        time.sleep(1)
                        y1 = int((self.screen_height / 2) - (self.screen_width / 2))
                        y2 = int((self.screen_height / 2) + (self.screen_width / 2))
                        for index in range(1, len(legal_image_group) + 1):
                            time.sleep(0.1)  # 等待图片加载
                            # 区域截屏
                            image = screen.capture([0, y1, self.screen_width, y2])
                            # 保存图片
                            img_file_path = R.img(f"img_{index}.png")
                            screen.image_save(image, img_file_path)
                            inner_img.append(img_file_path)
                            # 从右向左滑动切图
                            action.slide(600, int(self.screen_height / 2), 200, int(self.screen_height / 2),
                                         duration=200)
                        self.back_to_previous_page(msg="返回-买家评价-页面")
        return inner_img

    def select_one_legal_image_group(self, image_groups: list[list]) -> bool | list:
        """
        检验图片组是否符合规定，并选出合规的任意一组
        """
        if not image_groups or len(image_groups) == 0:
            return False
        image_count = sum([len(image_group) for image_group in image_groups])
        if image_count <= self.MIN_EXISTING_PRODUCT_IMAGES:
            print(f"已有图片张数【{image_count}】小于设置【{self.MIN_EXISTING_PRODUCT_IMAGES}】")
            return False
        legal_groups = [image_group for image_group in image_groups if len(image_group) >= self.MIN_IMAGES_PER_REVIEW]
        if len(legal_groups) == 0:
            return False
        return random.choice(legal_groups)

    def auto_fill(self, task: EvaluationTask) -> None:
        """
        自动填充评价

        - 起始位置：订单评价-页面
        """
        # 获取文本框焦点
        text_input_ele: Element | None = Selector().name("呼起键盘", 1).parent(1).parent(1).child(2).click(0).find(timeout=10000)
        if not text_input_ele:
            print("text_input_ele <UNK>")
        else:
            action.input(task.input_text)
            text_input_ele.scroll("up", 0.1)
            time.sleep(2)
        image_input_ele: Element | None = Selector().name("添加视频/图").find(timeout=10000)
        if not image_input_ele:
            print("image_input_ele <UNK>")
            print("没有图片输入元素")
        else:
            # 将图片存入相册
            for img in task.input_image:
                if media.save_pic2photo(img):
                    print(f"{img}成功存入相册")
                else:
                    print(f"{img}存入相册失败")
            # 模拟填充图片
            image_input_ele.click()  # 进入-相册总览-页面
            time.sleep(1)
            Selector().name("选照片").click(0).find(timeout=10000)
            time.sleep(1)
            first_img_xpath = "//XCUIElementTypeScrollView//XCUIElementTypeCollectionView//XCUIElementTypeCell[1]"
            first_img_ele: Element | None = Selector().xpath(first_img_xpath).find(timeout=10000)
            if not first_img_ele:
                ValueError("相册中没有图片")
            else:
                first_img_ele.click()  # 进入-相册单图展示-页面
                time.sleep(1)
                img_select_ele: Element | None = Selector().name("照片未选中").find(timeout=10000)
                if img_select_ele:
                    rx, ry, rw, rh = img_select_ele.rect
                    x = int(rx + rw / 2)
                    y = int(ry + rh / 2)
                    for i in range(min(9, len(task.input_image))):  # 一次最多选 9 张图
                        action.click(x, y)
                        time.sleep(0.2)
                        # 从右向左滑动切图
                        action.slide(600, 500, 400, 500, duration=20)
                        time.sleep(1)
                    Selector().name("完成").type("XCUIElementTypeButton").click(0).find(timeout=10000)

    def run(self):
        # 打开 JD App
        system.app_start(bundle_id="com.360buy.jdmobile")
        # 点击 “我的”，切换页面并刷新
        self_page_ele: Element | None = Selector().name("我的").type("XCUIElementTypeButton").find(timeout=10000)
        if not self_page_ele:
            print("self_page_ele <UNK>")
        else:
            self_page_ele.click()
            time.sleep(2)
        # 点击 “待评价”
        order_evaluated_ele: Element | None = Selector().name("待评价", 1).find(timeout=10000)
        if not order_evaluated_ele:
            print("order_evaluated_ele <UNK>")
        else:
            order_evaluated_ele.click()
            time.sleep(2)
        # 任务循环--起点
        task = EvaluationTask()

        goto_evaluate_ele: Element | None = Selector().name("去评价").type("XCUIElementTypeButton").find(timeout=10000)
        if not goto_evaluate_ele:
            print("goto_evaluate_ele <UNK>")
            print("没有待评价订单!")
        else:
            time.sleep(5)
            # 通过 “去评价” 按钮元素计算大致的商品展示图片的 y 坐标
            rx, ry, rw, rh = goto_evaluate_ele.rect
            # 计算商品展示图片的大致坐标，并点击进入商详页
            x = int(self.screen_width * 0.15)  # 估算值，可点击的 x
            y = int(ry - rh * 1.2)  # 估算值，可点击的 y
            time.sleep(2)
            action.click(x, y, duration=20)  # 进入-商品详情-页面
            print("进入-商品详情-页面")
            time.sleep(2)
            # 将 “买家评价” 滑入视图
            action.slide(500, 600, 500, 500, duration=20)  # 必须先扒拉一下才能加载出评价数据
            buyer_evaluation_ele: Element | None = Selector().name("买家评价", 1).find(timeout=10000)
            if not buyer_evaluation_ele:
                raise ValueError("buyer_evaluation_ele <UNK>")
            else:
                while buyer_evaluation_ele.visible is False:
                    Selector().name("京东").scroll("down", 0.3).find(timeout=10000)
                buyer_evaluation_ele.click()  # 进入-买家评价-页面
                print("进入-买家评价-页面")
                time.sleep(1)
                self.select_current_product()
                # 下滑加载更多评价内容
                for _ in range(10):
                    action.slide(random.randint(450, 550), random.randint(1450, 1550), random.randint(450, 550),
                                 random.randint(450, 550), 300)
                    time.sleep(0.2)
                task.input_text = self.get_text()
                task.input_image = self.get_image()
                print(f"【input_text】{task.input_text}")
                print(f"【input_image】{task.input_image}")
                self.back_to_previous_page("返回-商品详情-页面")
                self.back_to_previous_page("返回-评价中心-页面")
                self.auto_fill(task)
