'''
Author: HDJ
StartDate: please fill in
LastEditTime: 2025-03-26 23:19:51
FilePath: \pythond:\LocalUsers\Goodnameisfordoggy-Gitee\JD-Automated-Tools\JD-AutomaticEvaluate\src\logger.py
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
import sys
from loguru import logger

logger.remove()

def init(level):
	# 日志记录到文件	
	logger.add(
		"./logs/log_{time:YYYY-MM-DD}.log", 
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
