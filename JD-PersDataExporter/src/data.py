'''
Author: HDJ
StartDate: please fill in
LastEditTime: 2024-11-25 23:47:18
FilePath: \pythond:\LocalUsers\Goodnameisfordoggy-Gitee\JD-Automated-Tools\JD-PersDataExporter\src\data.py
Description: 以每个不可拆的订单为最小单元

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
import re
from typing import overload

class PerOrderInfoSlim():
    
    #####################################
    order_id: str = ""                  # 订单编号
    parent_order_id: str = ""           # 父订单编号(如果有)
    order_shop_name: str = ""           # 订单店铺名称
    product_id: str = ""                # 商品编号
    product_name: str = ""              # 商品名称
    goods_number: str = ""              # 商品数量
    actual_payment_amount: float = None # 实付金额
    jingdou_increment: int = None       # 订单返豆
    order_time: str = ""                # 下单时间
    order_status: str = ""              # 订单状态
    consignee_name: str = ""            # 收货人姓名
    consignee_address: str = ""         # 收货地址
    consignee_phone_number: str = ""    # 收货人电话(数据源已脱敏)
    #####################################
    order_url: str = ""                 # 订单详情页面地址

    

    def __str__(self):
        return (
            "=================================================================\n"
            f"订单编号: {self.order_id}\n"
            f"父订单编号: {self.parent_order_id}\n"
            f"店铺名称: {self.order_shop_name}\n"
            f"商品编号: {self.product_id}\n"
            f"商品名称: {self.product_name}\n"
            f"商品数量: {self.goods_number}\n"
            f"实付金额: {self.actual_payment_amount}元\n"
            f"订单返豆: {self.jingdou_increment}\n"
            f"下单时间: {self.order_time}\n"
            f"订单状态: {self.order_status}\n"
            f"收货人姓名: {self.consignee_name}\n"
            f"收货地址: {self.consignee_address}\n"
            f"收货人电话: {self.consignee_phone_number}\n"
            f"订单详情页面地址: {self.order_url}\n"
        )
    
    def to_dict(self):
        return {
            "订单编号": self.order_id,
            "父订单编号": self.parent_order_id,
            "店铺名称": self.order_shop_name,
            "商品编号": self.product_id,
            "商品名称": self.product_name,
            "商品数量": self.goods_number,
            "实付金额": self.actual_payment_amount,
            "订单返豆": self.jingdou_increment,
            "下单时间": self.order_time,
            "订单状态": self.order_status,
            "收货人姓名": self.consignee_name,
            "收货地址": self.consignee_address,
            "收货人电话": self.consignee_phone_number,
        }
    
    @staticmethod
    def mask_consignee_name(data, intensity: int = 2):
            """ 姓名覆盖脱敏 """
            if intensity == 0:
                return data
            elif intensity == 1:
                if len(data) == 2:
                    return data[0] + "*"
                elif len(data) > 2:
                    return data[0] + "*" * (len(data) - 2) + data[-1]
                else:
                    return data
            elif intensity == 2:
                return '*' * (len(data) - 1) + data[-1:]
    
    @staticmethod
    def mask_consignee_address(data, intensity: int = 2):
            """ 收货地址覆盖脱敏 """
            if intensity == 0:
                return data
            elif intensity == 1:
                return re.sub(r'\d+', '***', data)
            elif intensity == 2: # 只保留省，市，区级地址
                pattern = r'^([^省市区县]+?(?:省|市))?\s*([^市区县]+?(?:市|自治州|州|区))?\s*([^市区县]+?(?:区|县))?' # QWQ不会真有人地址直接填区级吧？
                match = re.match(pattern, data)
                if match:
                    return ''.join(filter(None, match.groups())) + "***"
                else:
                    return "******"
                
    @staticmethod
    def mask_consignee_phone_number(data, intensity: int = 2):
            """ 电话号码覆盖脱敏 """
            if intensity == 0:
                return data
            elif intensity == 1:
                return data[:3] + "****" + data[7:]
            elif intensity == 2:
                return '*' * 7 + data[7:]

class PerOrderInfoFull(PerOrderInfoSlim):
    
    #####################################
    courier_services_company: str = ""  # 物流公司
    courier_number: str = ""            # 快递单号
    product_total_price: float = None   # 商品总价  
    jingdou_decrement: int = None       # 订单用豆
    #####################################

    @overload
    def __init__(self) -> None:...
    @overload
    def __init__(self, slim_info: PerOrderInfoSlim) -> None:...
    
    def __init__(self, slim_info: PerOrderInfoSlim = None) -> None:
        if slim_info:
            self.__dict__.update(slim_info.__dict__) # 将 PerOrderInfoSlim 对象的属性复制到 self 中

    def __str__(self):
        return (
            super().__str__() +
            f"物流公司: {self.courier_services_company}\n"
            f"快递单号: {self.courier_number}\n"
            f"商品总价: {self.product_total_price}元\n"
            f"订单用豆: {self.jingdou_decrement}\n"
        )
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            "物流公司": self.courier_services_company,
            "快递单号": self.courier_number,
            "商品总价": self.product_total_price,
            "订单用豆": self.jingdou_decrement,
        })
        return data

DATE = {
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

STATUS = {
    "全部状态": 4096,
    "等待付款": 1,
    "等待收货": 128,
    "已完成": 1024,
    "已取消": -1,
}