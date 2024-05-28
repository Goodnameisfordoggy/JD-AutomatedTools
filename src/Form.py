'''
Author: HDJ
StartDate: please fill in
LastEditTime: 2024-05-29 00:15:01
FilePath: \pythond:\LocalUsers\Goodnameisfordoggy-Gitee\jd-pers-data-exporter\src\Form.py
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

try:
    from .dataStorageToExcel import ExcelStorage
    from .dataStorageToMySQL import MySQLStorange
except ImportError:
    from dataStorageToExcel import ExcelStorage
    from dataStorageToMySQL import MySQLStorange


class Form(list):
    """ 表格 """
    def __init__(self, *args):
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
        print('Excel文件已生成, 请于项目目录内查看')

    def save_to_mysql(self, fields_needed: list, table_name: str):
        mysqlStorage = MySQLStorange(self, fields_needed, table_name)
        mysqlStorage.save()
        print('数据已存入MySQL服务器, 请查看')


if __name__ == "__main__":
    
    # 示例使用
    data = Form()
    # data = Form(
    #     {'name': 'Alice', 'age': 30},
    #     {'name': 'Bob', 'age': 25},
    # )

    data.append({'name': 'Charlie', 'age': 35})

    try:
        data.append(['Not a dict'])  # 这将会引发一个TypeError
    except TypeError as e:
        print(e)

    print(data.get_by_key('name'))  # 输出 ['Alice', 'Bob', 'Charlie']
