'''
Author: HDJ
StartDate: please fill in
LastEditTime: 2024-07-21 23:28:24
FilePath: \pythond:\LocalUsers\Goodnameisfordoggy-Gitee\JD-Automated-Tools\JD-PersDataExporter\src\data_type\Form.py
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
import typing
import logging

from ..storage.dataStorageToExcel import ExcelStorage
from ..storage.dataStorageToMySQL import MySQLStorange


class Form(list):
    """ 表格 """
    def __init__(self, *args):
        # 日志记录器
        self.logger = logging.getLogger(__name__)

        if args:
            raise ValueError("暂不支持传参构造")
        # 使用提供的参数初始化父列表
        super().__init__()
    
    @typing.override
    def append(self, item):
        if not isinstance(item, dict):
            raise TypeError("Only dictionary items are allowed")
        super().append(item)
    
    def get_by_key(self, key):
        """返回所有字典中特定键的值。"""
        return [d.get(key, "NULL") for d in self if key in d]

    def save_to_excel(self, header_needed: list, file_name: str):
        excelStorage = ExcelStorage(self, header_needed, file_name)
        excelStorage.save()
        self.logger.info('Excel文件已生成, 请于项目目录内查看')

    def save_to_mysql(self, fields_needed: list, table_name: str, config_file_path: str, **kwargs):
        mysqlStorage = MySQLStorange(self, fields_needed, table_name)
        mysqlStorage.save(config_file_path, **kwargs)
        self.logger.info('数据已存入MySQL服务器, 请查看')
