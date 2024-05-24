'''
Author: HDJ
StartDate: 2024-05-15 00:00:00
LastEditTime: 2024-05-24 13:06:15
FilePath: \pythond:\LocalUsers\Goodnameisfordoggy-Gitee\jd-pers-data-exporter\src\dataStorageToExcel.py
Description: 

                *       写字楼里写字间，写字间里程序员；
                *       程序人员写程序，又拿程序换酒钱。
                *       酒醒只在网上坐，酒醉还来网下眠；
                *       酒醉酒醒日复日，网上网下年复年。
                *       但愿老死电脑间，不愿鞠躬老板前；
                *       奔驰宝马贵者趣，公交自行程序员。
                *       别人笑我忒疯癫，我笑自己命太贱；
                *       不见满街漂亮妹，哪个归得程序员？    
Copyright (c) 2024 by HDJ, All Rights Reserved. 
'''
import string
import pandas as pd
from openpyxl import load_workbook

try:
    from .dataPortector import ConfigManager
except ImportError:
    from dataPortector import ConfigManager


class ExcelStorage:
    def __init__(self, data: list[dict], header: list):
        self.data = data  # 需python3.7及以上，利用字典键值对的插入顺序。
        self.header = header  # 用户选择的表头字段列表
        # 获取配置文件
        self.configManager = ConfigManager()
        self.config = self.configManager.get_config()
        # 设置生成文件的文件名
        self.file_name = f'{self.config.get('user_name', '')}_JD_order.xlsx'
    
    def save_to_excel(self):
        """ 
        数据储存 
        """
        df = pd.DataFrame(self.data, columns=self.header)
        df.to_excel(self.file_name, index=False)
        self.adjust_column_width()

    def adjust_column_width(self):
        """ 调整 Excel 表头宽度 """
        workbook = load_workbook(self.file_name)
        worksheet = workbook.active

        uppercase_letters = [letter for letter in string.ascii_uppercase]  # 大写字母A~Z，用于表头设置
        index = 0
        default_width = 16
        for header in self.config['header']:  # 获取用户选择的表头名称
            for header_item in self.config['header_items']:  # 获取该表头的信息
                if header_item['name'] == header:
                    # 设置表头宽度
                    worksheet.column_dimensions[uppercase_letters[index]].width = float(header_item.get('width', default_width))
                    index += 1  # 下一个表头字母的索引
                    break

        # 保存修改后的 Excel 文件
        workbook.save(self.file_name)


if __name__ == "__main__":
    # 示例用法
    data = [{'order_id': '123', 'product_name': 'item1', 'amount': '10.0'}, {'order_id': '124', 'product_name': 'item2', 'amount': '20.0'}]
    header = ['order_id', 'product_name', 'amount']
    excel_storage = ExcelStorage(data, header)
    excel_storage.save_to_excel()
