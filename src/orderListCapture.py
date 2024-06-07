'''
Author: HDJ
StartDate: 2024-05-15 00:00:00
LastEditTime: 2024-06-07 23:32:03
FilePath: \pythond:\LocalUsers\Goodnameisfordoggy-Gitee\jd-pers-data-exporter\src\orderListCapture.py
Description: 
对订单列表页面源代码进行分析，并提取数据 / 
Analyze the source code of the order list page and extract the data
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

import re
import parsel
import logging

from .dataPortector import ConfigManager
from .data_type.Form import Form


class JDOrderListCapture:
    def __init__(self, page_html_src: str):
        # 日志记录器
        self.logger = logging.getLogger(__name__)

        self.__configManager = ConfigManager()
        self.__config = self.__configManager.get_config() # 获取配置文件
        self.__result = parsel.Selector(page_html_src) 
        self.__func_dict = {
            "order_id": self.get_order_id,
            "order_url": self.get_order_url,
            "product_name": self.get_product_name,
            "goods_number": self.get_goods_number,
            "amount": self.get_amount,
            "order_time": self.get_order_time, 
            "order_status": self.get_order_status,
            "consignee_name": self.get_consignee_name,
            "consignee_address": self.get_consignee_address,
            "consignee_phone_number": self.get_consignee_phone_number
        }

    def extract_data(self):
        """ 
        数据提取 

        Returns: 
            返回一个数据表 form (Form)
        """
        # 找到合适的外层框架
        table = self.__result.xpath('//table[@class="td-void order-tb"]')
        # 根据需求--筛掉合并订单，该类订单无具体商品信息
        tbodys = table.xpath('.//tbody[not(contains(@id, "parent"))]')
        form = Form()   # 表数据
        for tbody in tbodys:
            row = {}    # 行数据，一个字典存一个订单全部数据 
            for item in self.__config['header']:
                try: 
                    row[item] = self.__func_dict.get(item)(tbody)
                except TypeError:
                    row[item] = '暂无'
            form.append(row)
        return form

    def filter_data(self, form: Form):
        """ 数据筛选 """
        def is_coupon(order):
            """识别券(包)类订单, 返回Flase进行筛除"""
            if any(keyword in order['product_name'] for keyword in ['券包', '福利券', '优惠券', '兑换券']):
                return False
            return True
            
        def is_rights_interests(order):
            """识别权益类订单, 返回Flase进行筛除"""
            if any(keyword in order['product_name'] for keyword in ['权益', '特权']):
                return False
            return True
        
        def is_completed(order):
            """识别已完成订单, 返回Ture进行保留"""
            if order['order_status'] == '已完成':
                return True
            return False
        
        def custom_filtering(order):
            """自定义筛选"""
            header_item_choice = self.__config.get('filter_config', {}).get('自定义筛选', {}).get('header_item', '')
            header_item = order.get(header_item_choice, '')
            keywords = self.__config.get('filter_config', {}).get('自定义筛选', {}).get('keyword', '')
            if not header_item or not keywords:
                return True
            if any(keyword in header_item for keyword in keywords):
                return True
            return False
            
        filters = []
        if self.__config.get('filter_config', {}).get('去除券(包)类订单'):
            filters.append(is_coupon)
        if self.__config.get('filter_config', {}).get('去除权益类订单'):
            filters.append(is_rights_interests)
        if self.__config.get('filter_config', {}).get('筛选已完成订单'):
            filters.append(is_completed)        
        filters.append(custom_filtering)

        def apply_all_filters(order):
            """应用所有被选中的筛选器"""
            result = all(f(order) for f in filters)
            self.logger.debug(f"Order: {order}, Result: {result}")
            return result
        
        return list(filter(apply_all_filters, form))
    
    def get_order_id(self, RP_element):
        """ 获取订单编号 """

        def masking(data):
            """ 订单号覆盖脱敏 """
            masking_intensity = self.__config.get('masking_intensity').get('order_id', 2)
            try: 
                if masking_intensity == 0:
                    return data
                elif masking_intensity == 1:
                    return data[:4] + '****' + data[-4:]
                elif masking_intensity == 2:
                    return '*' * (len(data) - 4) + data[-4:]
                else:
                    raise ValueError
            except ValueError:
                self.logger.warning('请选择正确的覆盖脱敏强度！')

        order_id = RP_element.xpath('.//tr/td/span[@class="number"]/a/text()').get('')
        return masking(order_id)

    def get_product_name(self, RP_element):
        """ 获取商品名称 """
        tr_group = RP_element.xpath('.//tr[@class="tr-bd"]')
        if len(tr_group) == 1:
            product_name = RP_element.xpath('.//tr[@class="tr-bd"]/td/div/div/div/a/text()').get('').strip()
        else:  # 处理一个单号下多个商品的情况
            product_name = ''
            index = 1
            for tr in tr_group:
                item_name = tr.xpath('.//td/div/div/div/a/text()').get('').strip()
                product_name += f"({index}) {item_name}\n"
                index += 1
        return product_name

    def get_goods_number(self, RP_element):
        """ 获取商品数量 """
        tr_group = RP_element.xpath('.//tr[@class="tr-bd"]')
        if len(tr_group) == 1:
            goods_number = RP_element.xpath('.//tr/td/div[@class="goods-number"]/text()').get('').strip().strip('x')
        else:  # 处理一个单号下多个商品的情况
            goods_number = ''
            index = 1
            for tr in tr_group:
                item_number = tr.xpath('.//td/div[@class="goods-number"]/text()').get('').strip().strip('x')
                goods_number += f"({index}) {item_number}\n"
                index += 1
        return goods_number

    def get_amount(self, RP_element):
        """ 获取实付款金额 """
        amount = RP_element.xpath('.//tr/td/div[@class="amount"]/span[1]/text()').get('').strip('¥')
        return amount

    def get_order_time(self, RP_element):
        """ 获取下单时间 """
        order_time = RP_element.xpath('.//tr/td/span[@class="dealtime"]/text()').get('')
        return order_time

    def get_order_status(self, RP_element):
        """ 获取订单状态 """
        order_status = RP_element.xpath('.//tr/td/div[@class="status"]/span/text()').get('').strip()
        return order_status

    def get_consignee_name(self, RP_element):
        """ 获取收件人姓名 """

        def masking(data):
            """ 姓名覆盖脱敏 """
            masking_intensity = self.__config.get('masking_intensity').get('consignee_name', 2)
            try: 
                if masking_intensity == 0:
                    return data
                elif masking_intensity == 1:
                    if len(data) == 2:
                        return data[0] + "*"
                    elif len(data) > 2:
                        return data[0] + "*" * (len(data) - 2) + data[-1]
                    else:
                        return data
                elif masking_intensity == 2:
                    return '*' * (len(data) - 1) + data[-1:]
                else:
                    raise ValueError
            except ValueError:
                self.logger.warning('请选择正确的覆盖脱敏强度！')

        consignee_name = RP_element.xpath('.//tr/td/div/div/div/strong/text()').get('')
        # 进行脱敏
        return masking(consignee_name)

    def get_consignee_address(self, RP_element):
        """ 获取收货地址 """

        def masking(data):
            """ 收货地址覆盖脱敏 """
            masking_intensity = self.__config.get('masking_intensity').get('consignee_address', 2)
            try: 
                if masking_intensity == 0:
                    return data
                elif masking_intensity == 1:
                    return re.sub(r'\d+', '***', data)
                elif masking_intensity == 2: # 只保留省，市，区级地址
                    pattern = r'^([^省市区县]+?(?:省|市))?\s*([^市区县]+?(?:市|自治州|州|区))?\s*([^市区县]+?(?:区|县))?' # QWQ不会真有人地址直接填区级吧？
                    match = re.match(pattern, data)
                    if match:
                        return ''.join(filter(None, match.groups())) + "***"
                    else:
                        return "******"
                else:
                    raise ValueError
            except ValueError:
                self.logger.warning('请选择正确的覆盖脱敏强度！')
            
        consignee_address = RP_element.xpath('.//tr/td/div/div/div/p[1]/text()').get('')
        # 进行脱敏
        return masking(consignee_address)

    def get_consignee_phone_number(self, RP_element):
        """ 获取收件人联系方式 """

        def masking(data):
            """ 电话号码覆盖脱敏 """
            masking_intensity = self.__config.get('masking_intensity').get('consignee_phone_number', 2)
            try: 
                if masking_intensity == 0:
                    return data
                elif masking_intensity == 1:
                    return data[:3] + "****" + data[7:]
                elif masking_intensity == 2:
                    return '*' * 7 + data[7:]
                else:
                    raise ValueError
            except ValueError:
                self.logger.warning('请选择正确的覆盖脱敏强度！')
            
        consignee_phone_number = RP_element.xpath('.//tr/td/div/div/div/p[2]/text()').get('')
         # 进行脱敏
        if len(consignee_phone_number) == 11:
            masking(consignee_phone_number)
        return consignee_phone_number
    
    def get_order_url(self, RP_element):
        """ 获取订单url """
        order_url = RP_element.xpath('.//tr[@class="tr-bd"]/td/div[@class="status"]/a/@href').get('')
        whole_url = 'https:'+ order_url
        return whole_url
