"""
Author: HDJ @https://github.com/Goodnameisfordoggy
Time@IDE: 2025-07-10 00:27:42 @PyCharm
Description: 

				|   早岁已知世事艰，仍许飞鸿荡云间；
				|   曾恋嘉肴香绕案，敲键弛张荡波澜。
				|
				|   功败未成身无畏，坚持未果心不悔；
				|   皮囊终作一抔土，独留屎山贯寰宇。

Copyright (c) 2024-2025 by HDJ, All Rights Reserved.
"""
import random


class EvaluationTask(object):
    id: str = ""                # 任务编号
    order_type: str = ""        # 订单类型
    product_name: str = ""      # 商品名称
    product_style: str = ""     # 商品款式
    input_text: str = ""        # 评价填充文本
    input_image: list = []      # 评价填充图片

    def __str__(self):
        return ("\n"
                f"【id】 {self.id}\n"
                f"【product_name】 {self.product_name}\n"
                f"【product_style】 {self.product_style}\n"
                f"【input_text】 {self.input_text}\n"
                f"【input_image】 {self.input_image}")

    def guaranteed_add_text(self):
        """使用默认文案池，生成保底文案"""
        self.input_text = random.choice(DEFAULT_COMMENT_TEXT_LIST)

    # def guaranteed_add_image(self, img_num: int = 0):
    #     """使用默认图片池，生成保底图片组"""
    #     image_default_pool = ""
    #     pass


class ElementNotFoundError(Exception):
    """没有捕获到元素时抛出的异常"""

    def __init__(self, message="ElementNotFound", selector="", details=None):
        self.message = message
        self.selector = selector
        self.details = details
        super().__init__(self.message)

    def __str__(self):
        parts = []
        if self.message:
            parts.append(f"message: {self.message}")
        if self.selector:
            parts.append(f"selector: {self.selector}")
        if self.details:
            parts.append(f"details: {self.details}")
        return f"ElementNotFoundError({', '.join(parts)})"


DEFAULT_COMMENT_TEXT_LIST = [
    "非常满意这次购物体验，商品质量非常好，物超所值。朋友们看到后也纷纷称赞。客服服务热情周到，物流也非常给力，发货迅速，收到货物时包装完好。商品设计也符合我的预期，非常愉快的购物经历，强烈推荐！",
    "不得不夸赞这家店，商品价格美丽，质量绝佳。物流迅速，商家服务周到，售后放心。买之前还担心价格低质量不行，结果收到货后惊讶得不行，质量好得没话说，太满意了！不得不说，这商品太值了，物美价廉，质量出色。物流快，商家服务周到，售后有保障",
    "看着不错，性价比很高，比超市划算太多，而且品牌好，现在习惯在京东购物，服务也好，快递也方便，购买PLUS会员很划算，会继续回购。相信京东，会继续支持京东，多年的老粉了。",
    "我真的非常喜欢它，质量非常好，和卖家描述的一模一样，我非常满意。我真的很喜欢它，它完全超出了预期的价值，交货速度非常快，包装非常仔细和紧凑，交货速度非常快，我非常满意购物。下次有机会再找你，店家人蛮好的，东东很不错,淘到心意的宝贝是一件让人很开心的事，比心。",
    "商品的质量：产品总体上是好的，包装很紧。商家服务：可以打五星。快递交付：非常快。另一个是感谢京东赠送优惠券。毕竟，廉价商品更真实。质量非常好，完全符合卖方的描述。我真的很喜欢。这完全超出了预期。交货速度非常快。包装非常仔细和紧密。物流公司有良好的服务态度，交货速度非常快。",
    "这个价格仍然很划算。经济、便宜、质量非常好，与卖方描述的完全一样。非常满意，完全出乎意料，超划算，购物比实体店便宜多了。我希望京东的生意会越来越红火，物流会越来越快，包装会越来越结实。六星表扬，多一星不怕你骄傲，犹豫不决的朋友会很快下单，这是良心的推荐。",
    "我终于得到了我需要的东西，东西很好，而且价格又漂亮又便宜。谢谢！老实说，这是我在京东购物时最满意的一次购物。我对京东的态度和商品都很满意。物流比较想象中要快太多，没想到下单第二天下午就收到快递小哥哥的电话了、以后会继续关注！",
    "我个人来评价下这个宝贝，这是一个不错的选择，尤其送女生，价格不错，质量不错，快递不错，店铺卖家也不错。东西收到了，很满意的，是我想要的那种。每次买东西我都会根据价格，质量和评价进行参考，最后选择我满意的一家，是性价比最高的，很符合我的标准我觉得很满意。东西便宜，质量好，物美价廉,买的放心又开心，品类多，而且齐全，划算，方便，快捷，实惠，包装又好，没有任何破损。",
    "商品相当满意，质量过关，送人或自用都是不错的选择。物流也及时，无需长时间等待。包装也完好，没有破损的现象。购买前咨询店家，店家很热情，解释很到位，还会给予相关建议，很人性化。家人和朋友都说挺好的，还让我分享了商品。下次有需要还会回购的。",
    "东西很喜欢，质量也很好的，这个价格能买到是真的很划算真的很喜欢，完全超出期望值，发货速度非常快，包装非常仔细、严实，运送速度很快，很满意的一次购物特别特别棒，货比三家才买的，店主人很好，回答问题很有耐心，也很详细，有需要还会再来的",
]