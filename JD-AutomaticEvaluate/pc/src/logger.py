'''
Author: HDJ @https://github.com/Goodnameisfordoggy
LastEditTime: 2025-07-12 23:47:22
FilePath: \pythond:\LocalUsers\Goodnameisfordoggy-Gitee\JD-Automated-Tools\JD-AutomaticEvaluate\pc\src\logger.py
Description: @VSCode

				|	早岁已知世事艰，仍许飞鸿荡云间；
				|	曾恋嘉肴香绕案，敲键弛张荡波澜。
				|					 
				|	功败未成身无畏，坚持未果心不悔；
				|	皮囊终作一抔土，独留屎山贯寰宇。

Copyright (c) 2024-2025 by HDJ, All Rights Reserved. 
'''
import os
import sys
from loguru import logger

from pc.src import LOGS_DIR

logger.remove()

def init_logger(level="INFO"):
	# 日志记录到文件	
	logger.add(
		os.path.join(LOGS_DIR, "log_{time:YYYY-MM-DD}.log"), 
		level=level, 
		rotation="00:00", 
		retention="7 days"
		)

	# 日志输出到标准输出，根据不同的日志等级切换日志输出格式
	if level == "DEBUG": 
		# DEBUG时，为了在高级的编辑器中可以直接跳转到源代码行，添加了详细的文件路径。
		log_format = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{file.path}:{line}</cyan> | <level>{message}</level>"
	else:
		# 正常使用时，简化日志输出
		log_format = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>"

	# 程序运行在冻结的环境时，及 exe 等可执行文件
	logger.add(
		sink=sys.stdout,
		format=log_format,
		level=level
	)

def get_logger():
	return logger
