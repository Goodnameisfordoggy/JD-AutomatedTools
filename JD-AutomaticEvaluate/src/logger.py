'''
Author: HDJ
StartDate: please fill in
LastEditTime: 2024-11-08 00:05:35
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
Copyright (c) 2024 by HDJ, All Rights Reserved. 
'''
import os
import sys
from loguru import logger

logger.remove()

logger.add(sys.stdout, level="INFO")

logger.add("logs/log_{time:YYYY-MM-DD}.log", level="INFO", rotation="00:00", retention="7 days")

def get_logger():
    return logger
