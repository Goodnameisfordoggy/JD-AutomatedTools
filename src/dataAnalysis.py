'''
Author: HDJ
StartDate: 2024-05-15 00:00:00
LastEditTime: 2024-05-24 21:20:51
FilePath: \pythond:\LocalUsers\Goodnameisfordoggy-Gitee\jd-pers-data-exporter\src\dataAnalysis.py
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

import re
import parsel

try:
    from .dataPortector import ConfigManager
except ImportError:
    from dataPortector import ConfigManager

class JDDataAnalysis:
    def __init__(self, page_html_src: str):
        self.configManager = ConfigManager()
        self.config = self.configManager.get_config() # 获取配置文件
        self.page_html_src = page_html_src
        self.result = parsel.Selector(page_html_src) 
        self.func_dict = {
            "order_id": self.get_order_id,
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
            list: 返回一个数据表，使用二维列表储存
        """
        # 找到合适的外层框架
        table = self.result.xpath('//table[@class="td-void order-tb"]')
        # 根据需求--筛掉合并订单，该类订单无具体商品信息
        tbodys = table.xpath('.//tbody[not(contains(@id, "parent"))]')
        form = []   # 表数据
        for tbody in tbodys:
            row = {}    # 行数据，一个字典存一个订单全部数据 
            for item in self.config['header']:
                try: 
                    row[item] = self.func_dict.get(item)(tbody)
                except TypeError:
                    row[item] = '暂无'
            form.append(row)
        return form

    def filter_data(self, form: list[dict[any]]):
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
            header_item = order.get(self.config.get('filter_config', {}).get('自定义筛选', {}).get('header_item'), '')
            keywords = self.config.get('filter_config', {}).get('自定义筛选', {}).get('keyword')
            if any(keyword in header_item for keyword in keywords):
                return True
            return False
        
        filters = []
        if self.config.get('filter_config', {}).get('去除券(包)类订单'):
            filters.append(is_coupon)
        if self.config.get('filter_config', {}).get('去除权益类订单'):
            filters.append(is_rights_interests)
        if self.config.get('filter_config', {}).get('筛选已完成订单'):
            filters.append(is_completed)        
        filters.append(custom_filtering)

        def apply_all_filters(order):
            """应用所有被选中的筛选器"""
            return all(f(order) for f in filters)
        
        return list(filter(apply_all_filters, form))
    
    def get_order_id(self, RP_element):
        """ 获取订单编号 """
        order_id = RP_element.xpath('.//tr/td/span[@class="number"]/a/text()').get('')
        return order_id

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
        amount = RP_element.xpath('.//tr/td/div[@class="amount"]/span[1]/text()').get('')
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
        consignee_name = RP_element.xpath('.//tr/td/div/div/div/strong/text()').get('')
        # 进行脱敏
        if len(consignee_name) == 2:
            return consignee_name[0] + "*"
        elif len(consignee_name) > 2:
            return consignee_name[0] + "*" * (len(consignee_name) - 2) + consignee_name[-1]
        return consignee_name

    def get_consignee_address(self, RP_element):
        """ 获取收货地址 """
        consignee_address = RP_element.xpath('.//tr/td/div/div/div/p[1]/text()').get('')
        # 进行脱敏
        return re.sub(r'\d+', '****', consignee_address)

    def get_consignee_phone_number(self, RP_element):
        """ 获取收件人联系方式 """
        consignee_phone_number = RP_element.xpath('.//tr/td/div/div/div/p[2]/text()').get('')
         # 进行脱敏
        if len(consignee_phone_number) == 11:
            return consignee_phone_number[:3] + "****" + consignee_phone_number[7:]
        return consignee_phone_number

if __name__ == "__main__":
    with open('1.html', 'r', encoding='utf-8') as f:
        html = f.read()
    extractor = JDDataAnalysis(html)
    data = extractor.extract_data()
    filtered_data = extractor.filter_data(data)
    print(filtered_data)
