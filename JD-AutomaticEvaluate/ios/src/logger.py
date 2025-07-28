"""
Author: HDJ @https://github.com/Goodnameisfordoggy
Time@IDE: 2025-07-10 00:28:19 @PyCharm
Description: 

				|   早岁已知世事艰，仍许飞鸿荡云间；
				|   曾恋嘉肴香绕案，敲键弛张荡波澜。
				|
				|   功败未成身无畏，坚持未果心不悔；
				|   皮囊终作一抔土，独留屎山贯寰宇。

Copyright (c) 2024-2025 by HDJ, All Rights Reserved.
"""
import os
import sys
from ..res.loguru import logger

logger.remove()

def init_logger(level="INFO"):
	# # 日志记录到文件
	# logger.add(
	# 	"./logs/log_{time:YYYY-MM-DD}.log",
	# 	level=level,
	# 	rotation="00:00",
	# 	retention="7 days"
	# 	)

	# 日志输出到标准输出，根据不同的日志等级切换日志输出格式
	if level == "DEBUG" or "TRACE":
		log_format = "<level>{level.icon}</level> | <cyan>{file}:{function}:{line}</cyan> | <level>{message}</level>"
	else:
		log_format = "<level>{level.icon}</level> | <level>{message}</level>"

	logger.add(
		sink=sys.stdout,
		format=log_format,
		level=level
	)
	return logger

def get_logger():
	return logger
