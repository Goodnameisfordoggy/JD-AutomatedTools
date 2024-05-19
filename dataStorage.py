'''
Author: HDJ
StartDate: 2024-05-15 00:00:00
LastEditTime: 2024-05-19 16:59:30
FilePath: \pythond:\LocalUsers\Goodnameisfordoggy-Gitee\jd-data-exporter\dataStorage.py
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
import string
import pandas as pd
from openpyxl import load_workbook
from dataPortector import config


def data_storage_to_Excel(data: list, header: list):
	""" 
	数据储存 
	
	Args:
		data (ListLikeU | DataFrame | dict[Any, Any] | Iterable[ListLikeU | tuple[Hashable, ListLikeU] | dict[Any, Any]] | None)
		header (list): 用户选择的表头字段列表
	"""
    
	df = pd.DataFrame(data, columns=header)
	# 将 DataFrame 导出为 Excel 文件
	file_name = 'my_JD_order.xlsx'
	df.to_excel(file_name, index=False)

	# 使用 openpyxl 加载刚刚创建的 Excel 文件
	workbook = load_workbook(file_name)
	worksheet = workbook.active

	uppercase_letters = [letter for letter in string.ascii_uppercase] # 大写字母A~Z，用于表头设置
	index = 0
	default_width = 16
	for header in config['header']:	# 获取用户选择的表头名称
		for header_item in config['header_items']:	# 获取该表头的信息
			if header_item['name'] == header:
				# 设置表头宽度
				worksheet.column_dimensions[uppercase_letters[index]].width = float(header_item.get('width', default_width))
				index += 1  # 下一个表头字母的索引
				break

	# 保存修改后的 Excel 文件
	workbook.save(file_name)



if __name__ == "__main__":
	pass