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
class EvaluationTask(object):
    product_name: str = ""  # 商品名称
    input_text: str = ""  # 评价填充文本
    input_image: list = []  # 评价填充图片

    def __str__(self):
        return ("\n"
                f"【product_name】 {self.product_name}\n"
                f"【input_text】 {self.input_text}\n"
                f"【input_image】 {self.input_image}")