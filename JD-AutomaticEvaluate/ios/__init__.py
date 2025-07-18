"""
Author: HDJ @https://github.com/Goodnameisfordoggy
Time@IDE: 2025-07-10 00:29:23 @PyCharm
Description: 

				|   早岁已知世事艰，仍许飞鸿荡云间；
				|   曾恋嘉肴香绕案，敲键弛张荡波澜。
				|
				|   功败未成身无畏，坚持未果心不悔；
				|   皮囊终作一抔土，独留屎山贯寰宇。

Copyright (c) 2024-2025 by HDJ, All Rights Reserved.
"""
from .src.automaticEvaluate import JDAppAutomaticEvaluate
from .src.logger import get_logger, init_logger
from .src.test import test_auto_func
LOG = init_logger("DEBUG")

# JDAppAutomaticEvaluate().run()
JDAppAutomaticEvaluate().get_text()

# test_auto_func.test_auto_fill()
# test_auto_func.test_scroll_to_visible()


print("运行结束！！！")