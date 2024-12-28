'''
Author: HDJ
StartDate: please fill in
LastEditTime: 2024-12-29 00:49:32
FilePath: \pythond:\LocalUsers\Goodnameisfordoggy-Gitee\JD-Automated-Tools\JD-PersDataExporter\main.py
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

from src.Exporter import JDOrderDataExporter
from src.LoginManager import LoginManager
from src.dataPortector import OrderExportConfig
from src.storage.dataStorageToExcel import ExcelStorage

if __name__ == "__main__":
	config = OrderExportConfig().load_from_json()
	if not config.jd_accounts_info:
		loginManager = LoginManager(headless=False)
		account_info = loginManager.login_new_account()
		config.add_account_info(account_info)
	loginManager = LoginManager(
		headless=False, 
		cookie_file=config.jd_accounts_info[0]["cookies_path"] # 选择账号列表中第一个账号
	).login_with_cookies()
	
	exporter = JDOrderDataExporter(config, loginManager.page)
	exporter.exec_()
	orderInfo_list = exporter.get_order_info_list()
	ExcelStorage(
		data=orderInfo_list, 
		header_needed=["订单编号", "父订单编号", "店铺名称", "商品名称", "商品数量", "实付金额", "订单返豆", "订单用豆", "下单时间", "订单状态", "收货人姓名", "收货地址", "收货人电话", "物流公司", "快递单号", "商品总价"], 
		file_name="订单信息.xlsx",
		sheet_name=config.jd_accounts_info[config.jd_account_last_used]["sheet_name"]
	).save()
	os.startfile("订单信息.xlsx")
