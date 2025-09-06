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
from typing import Callable, Optional
from ascript.ios.node import Selector, Element
from .utils import sync_retry, sync_retry_class
from .data import ElementNotFoundError


class WaitForSelector(object):
    """
    元素选择器集中调度

    元素获取:
    ```
    # 直接调用
    ele = WaitForSelector.jd_main_body()
    ele = WaitForSelector().get("jd_main_body")
    # 添加额外参数
    ele = WaitForSelector.jd_main_body(name="京东")
    ele = WaitForSelector().get("jd_main_body", name="京东")
    ```python
    """

    # 以下标注均为页面，以最终到达页面为准
    # JD APP
    jd_main_body = lambda *args: Selector().name("京东").find()
    self_page = lambda *args: Selector().name("我的").type("XCUIElementTypeButton").find()
    # APP>>我的
    order_evaluated = lambda *args: Selector().name("待评价", 1).find()
    # APP>>我的>>评价中心>>待评价
    goto_evaluate = lambda *args: Selector().name("去评价").type("XCUIElementTypeButton").find()
    goto_evaluates = lambda *args: Selector().name("去评价").type("XCUIElementTypeButton").find_all()
    wait_evaluate_table = lambda *args: Selector().type("XCUIElementTypeTable").find()
    # APP>>我的>>评价中心>>待评价>>商品详情
    buyer_evaluation = lambda *args: Selector().name("买家评价", 1).find()
    out_of_stock_sign = lambda *args: Selector().name("无货", 1).find()
    gift_close_btn = lambda *args: Selector().name("pd mainImage gfit colse").find()
    # APP>>我的>>评价中心>>待评价>>商品详情>>买家评价
    product_style_dropdown_list = lambda *args: Selector().name("款式").find()
    current_product_checkbox_1 = lambda *args: Selector().name("当前商品").type("XCUIElementTypeButton").find()
    evaluation_cell = lambda *args, **kwargs: Selector().xpath(f"//XCUIElementTypeTable//XCUIElementTypeCell[{kwargs.get('cell_index')}]").find()
    evaluation_cells = lambda *args: Selector().xpath("//XCUIElementTypeTable//XCUIElementTypeCell").find_all()
    evaluation_inner_text = lambda *args, **kwargs: Selector().xpath(f"//XCUIElementTypeTable//XCUIElementTypeCell[{kwargs.get('cell_index')}]//XCUIElementTypeButton[1]").find()
    evaluation_inner_images = lambda *args, **kwargs: Selector().xpath(f"//XCUIElementTypeTable//XCUIElementTypeCell[{kwargs.get('cell_index')}]//XCUIElementTypeOther[1]//XCUIElementTypeImage").find_all()
    reply_to_evaluation = lambda *args, **kwargs: Selector().xpath(f"//XCUIElementTypeTable//XCUIElementTypeCell[{kwargs.get('cell_index')}]//XCUIElementTypeButton[contains(@name, '回复')]").find_all()
    image_and_video_tab = lambda *args: Selector().name("图/视频", 1).find()
    image_set_tab = lambda *args: Selector().name("图集").find()
    # APP>>我的>>评价中心>>待评价>>商品详情>>买家评价>>晒图相册
    shareorder_video_mute_btn = lambda *args: Selector().name("shareorder video mute",1).find()
    image_progress_bar = lambda *args: Selector().name("/",1).find()
    # APP>>我的>>评价中心>>待评价>>商品详情>>买家评价>>款式选择
    product_name_label = lambda *args: Selector().name("查看当前商品").parent(1).child(2).find()
    selected_product_style_label = lambda *args:Selector().name("查看当前商品").parent(1).child(4).find()
    current_product_checkbox_2 = lambda *args: Selector().name("查看当前商品").find()
    confirm_current_product = lambda *args: Selector().name("确定").find()
    # APP>>我的>>评价中心>>待评价>>商品详情>>买家评价>>单条评价详情
    evaluation_details = lambda *args: Selector().type("XCUIElementTypeNavigationBar").name("评价详情").find()
    evaluation_first_img = lambda *args: Selector().xpath("//XCUIElementTypeTable//XCUIElementTypeCell[2]//XCUIElementTypeImage").find()
    full_evaluation_inner_text = lambda *args, **kwargs: Selector().xpath(f"//XCUIElementTypeTable//XCUIElementTypeCell[1]//XCUIElementTypeStaticText[contains(@label, '{kwargs.get('fragment')}')]").find()
    # APP>>我的>>评价中心>>待评价>>订单评价
    evaluation_text_input = lambda *args: Selector().type("XCUIElementTypeTextView").find()
    evaluation_text_inputs = lambda *args: Selector().type("XCUIElementTypeTextView").find_all()
    evaluation_image_input = lambda *args: Selector().name("添加视频/图").find()
    evaluation_image_inputs = lambda *args: Selector().name("添加视频/图").find_all()
    express_evaluation_commit_btn = lambda *args: Selector().name("发布").type("XCUIElementTypeButton").find()
    takeaway_evaluation_commit_btn = lambda *args: Selector().name("提交").type("XCUIElementTypeButton").find()
    takeaway_order_sign = lambda *args: Selector().name("骑手",1).find()
    exit_evaluation = lambda *args: Selector().name("返回").find()
    confirm_exit_evaluation = lambda *args: Selector().name("退出评价").type("XCUIElementTypeButton").find()
    product_evaluate_labels = lambda *args: Selector().name("商品评价").find_all()
    first_star = lambda *args: Selector().name("已选中 1星").find()
    first_stars = lambda *args: Selector().name("已选中 1星").find_all()
    fifth_star = lambda *args: Selector().name("已选中 5星").find()
    # APP>>我的>>评价中心>>待评价>>订单评价>>系统相册预览
    select_picture = lambda *args: Selector().name("选照片").find()
    picture_view_first_img = lambda *args: Selector().xpath("//XCUIElementTypeScrollView//XCUIElementTypeCollectionView//XCUIElementTypeCell[1]").find()
    img_select_complete = lambda *args: Selector().name("完成").type("XCUIElementTypeButton").find()
    # APP>>我的>>评价中心>>待评价>>订单评价>>系统相册预览>>选照片预览>>大图显示
    img_checkbox = lambda *args: Selector().name("照片未选中").find()

    @sync_retry(max_retries=3, retry_delay=1, backoff_factor=2, exceptions=(ElementNotFoundError,))
    def get(self, selector_name: str, **kwargs) -> Element | list[Element,]:
        """更安全的获取元素"""
        selector_func = getattr(self, selector_name, None)
        if selector_func is None:
            raise NameError(f"Selector name【{selector_name}】not found")

        # # 检查函数是否接受任意关键字参数(**kwargs)
        # sig = inspect.signature(selector_func)
        # accepts_kwargs = any(param.kind == param.VAR_KEYWORD for param in sig.parameters.values())

        # 根据函数是否接受关键字参数决定是否传递kwargs
        if len(kwargs) > 0:
            try:
                element: Element | None = selector_func(**kwargs)
            except TypeError as e:
                raise ValueError(f"Selector【{selector_name}】does not accept arguments【{e}】") from e
        else:
            element: Element | None = selector_func()
        if not element:
            raise ElementNotFoundError(message="<UNK>", selector=f"{selector_name}")
        return element