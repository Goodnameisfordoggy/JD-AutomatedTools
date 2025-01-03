'''
Author: HDJ
StartDate: please fill in
LastEditTime: 2024-12-25 23:51:35
FilePath: \pythond:\LocalUsers\Goodnameisfordoggy-Gitee\JD-Automated-Tools\JD-PersDataExporter\src\logger.py
Description: 

				*		写字楼里写字间，写字间里程序员；
				*		程序人员写程序，又拿程序换酒钱。
				*		酒醒只在网上坐，酒醉还来网下眠；
				*		酒醉酒醒日复日，网上网下年复年。
				*		但愿老死电脑间，不愿鞠躬老板前；
				*		奔驰宝马贵者趣，公交自行程序员。
				*		别人笑我忒疯癫，我笑自己命太贱；
				*		不见满街漂亮妹，哪个归得程序员？    
Copyright (c) 2024 by HDJ, All Rights Reserved. 
'''
import os
import sys
from loguru import logger
from src import LOGS_DIR
logger.remove()

logger.add(os.path.join(LOGS_DIR, "log_{time:YYYY-MM-DD}.log"), level="INFO", rotation="00:00", retention="7 days")

if getattr(sys, 'frozen', False):
	logger.add(
		sink=sys.stdout,
		format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <level>{message}</level>",
		level="INFO"
	)
else:
    logger.add(sys.stdout, level="DEBUG")

def get_logger():
    return logger
