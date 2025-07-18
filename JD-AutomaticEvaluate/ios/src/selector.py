"""
Author: HDJ @https://github.com/Goodnameisfordoggy
Time@IDE: 2025-07-15 16:44:46 @PyCharm
Description: 不同页面下的控件选择器

				|   早岁已知世事艰，仍许飞鸿荡云间；
				|   曾恋嘉肴香绕案，敲键弛张荡波澜。
				|
				|   功败未成身无畏，坚持未果心不悔；
				|   皮囊终作一抔土，独留屎山贯寰宇。

Copyright (c) 2024-2025 by HDJ, All Rights Reserved.
"""
import inspect
from ascript.ios.node import Selector, Element
from .utils import sync_retry, sync_retry_class


@sync_retry_class(max_retries=3, retry_delay=1, backoff_factor=2, exceptions=(ValueError,))
class WaitForSelector(object):
    """元素获取操作类"""

    SELECTORS = {
        # 以下标注均为页面
        # JD APP
        "jd_main_body": lambda : Selector().name("京东").find(),
        "self_page": lambda : Selector().name("我的").type("XCUIElementTypeButton").find(),
        # APP>>我的
        "order_evaluated": lambda : Selector().name("待评价", 1).find(),
        # APP>>我的>>评价中心>>待评价
        "goto_evaluate": lambda : Selector().name("去评价").type("XCUIElementTypeButton").find(),
        # APP>>我的>>评价中心>>待评价>>商品详情
        "buyer_evaluation": lambda : Selector().name("买家评价", 1).find(),
        # APP>>我的>>评价中心>>待评价>>商品详情>>买家评价
        "product_style": lambda : Selector().name("款式").find(),
        "evaluation_cell": lambda **kwargs: Selector().xpath(f"//XCUIElementTypeTable//XCUIElementTypeCell[{kwargs.get('cell_index')}]").find(),
        "evaluation_cells": lambda: Selector().xpath("//XCUIElementTypeTable//XCUIElementTypeCell").find_all(),
        "evaluation_inner_text": lambda **kwargs: Selector().xpath(f"//XCUIElementTypeTable//XCUIElementTypeCell[{kwargs.get('cell_index')}]//XCUIElementTypeButton[1]").find(),
        "evaluation_inner_images": lambda **kwargs: Selector().xpath(f"//XCUIElementTypeTable//XCUIElementTypeCell[{kwargs.get('cell_index')}]//XCUIElementTypeOther[1]//XCUIElementTypeImage").find_all(),
        "reply_to_evaluation": lambda **kwargs: Selector().xpath(f"//XCUIElementTypeTable//XCUIElementTypeCell[{kwargs.get('cell_index')}]//XCUIElementTypeButton[contains(@name, '回复')]").find_all(),
        # APP>>我的>>评价中心>>待评价>>商品详情>>买家评价>>款式选择
        "current_product": lambda: Selector().name("查看当前商品").find(),
        "confirm_current_product": lambda: Selector().name("确定").find(),
        # APP>>我的>>评价中心>>待评价>>商品详情>>买家评价>>单条评价详情
        "evaluation_details": lambda : Selector().type("XCUIElementTypeNavigationBar").name("评价详情").find(),
        "evaluation_first_img": lambda: Selector().xpath("//XCUIElementTypeTable//XCUIElementTypeCell[2]//XCUIElementTypeImage").find(),
        "full_evaluation_inner_text": lambda **kwargs: Selector().xpath(f"//XCUIElementTypeTable//XCUIElementTypeCell[1]//XCUIElementTypeStaticText[contains(@label, '{kwargs.get('fragment')}')]").find(),
        # APP>>我的>>评价中心>>待评价>>订单评价
        "text_input": lambda: Selector().name("呼起键盘", 1).parent(1).parent(1).child(2).find(),
        "image_input": lambda: Selector().name("添加视频/图").find(),
        # APP>>我的>>评价中心>>待评价>>订单评价>>系统相册预览
        "select_picture": lambda: Selector().name("选照片").find(),
        "picture_view_first_img": lambda: Selector().xpath("//XCUIElementTypeScrollView//XCUIElementTypeCollectionView//XCUIElementTypeCell[1]").find(),
        "img_select_complete": lambda: Selector().name("完成").type("XCUIElementTypeButton").find(),
        # APP>>我的>>评价中心>>待评价>>订单评价>>系统相册预览>>选照片预览>>大图显示
        "img_checkbox": lambda: Selector().name("照片未选中").find(),
    }

    def get(self, selector_name: str, **kwargs) -> Element | list[Element,]:
        selector_func = self.SELECTORS.get(selector_name)
        if selector_func is None:
            raise NameError(f"Selector name【{selector_name}】not found")

        # 检查函数是否接受任意关键字参数(**kwargs)
        sig = inspect.signature(selector_func)
        accepts_kwargs = any(param.kind == param.VAR_KEYWORD for param in sig.parameters.values())

        # 根据函数是否接受关键字参数决定是否传递kwargs
        if accepts_kwargs:
            element: Element | None = selector_func(**kwargs)
        else:
            element: Element | None = selector_func()
        if not element:
            raise ValueError(f"Selector【{selector_name}】<UNK>")
        return element


    # @staticmethod
    # def self_page():
    #     ele: Element | None =
    #     if not ele:
    #         raise ValueError("self_page_ele <UNK>")
    #     return ele

    @staticmethod
    def product_style_ele():
        ele: Element | None = Selector().name("款式").find()