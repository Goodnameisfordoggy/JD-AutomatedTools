'''
Author: HDJ
StartDate: please fill in
LastEditTime: 2024-11-08 16:17:10
FilePath: \pythond:\LocalUsers\Goodnameisfordoggy-Gitee\JD-Automated-Tools\JD-AutomaticEvaluate\src\data.py
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
import copy


class EvaluationTask:
    order_id: str = ""  # 订单编号(商品归属单号)
    orderVoucher_url: str = ""  # 评价页面url
    productHtml_url: str = ""  # 商品详情页面url
    product_name: str = ""	# 商品名称
	
    input_text: str = ""  # 评价填充文本
    input_image: list = []  # 评价填充图片
    
    def __str__(self):
        return ("\n"
                f"order_id: '{self.order_id}'\n"
                f"orderVoucher_url: '{self.orderVoucher_url}'\n"
                f"productHtml_url: '{self.productHtml_url}'\n"
                f"product_name: '{self.product_name}'\n"
                f"input_text: '{self.input_text}'\n"
                f"input_image: {self.input_image}")
    
    def copy(self):
        # 创建一个浅拷贝
        return copy.copy(self)