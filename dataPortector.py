'''
Author: HDJ
StartDate: 2024-05-15 00:00:00
LastEditTime: 2024-05-19 15:43:44
FilePath: \pythond:\LocalUsers\Goodnameisfordoggy-Gitee\jd-data-exporter\dataPortector.py
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
import json


with open('config.json', 'r', encoding='utf-8') as jsf:
    config = json.load(jsf)
    
date_range_dict = {
    "ALL": -1,
    "近三个月订单": 1,
    "今年内订单": 2,
    "2023年订单": 2023,
    "2022年订单": 2022,
    "2021年订单": 2021,
    "2020年订单": 2020,
    "2019年订单": 2019,
    "2018年订单": 2018,
    "2017年订单": 2017,
    "2016年订单": 2016,
    "2015年订单": 2015,
    "2014年订单": 2014,
    "2014年以前订单": 3,
} 