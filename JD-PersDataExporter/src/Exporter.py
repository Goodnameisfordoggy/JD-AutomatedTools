'''
Author: HDJ
StartDate: please fill in
LastEditTime: 2024-12-23 21:57:53
FilePath: \pythond:\LocalUsers\Goodnameisfordoggy-Gitee\JD-Automated-Tools\JD-PersDataExporter\src\Exporter.py
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
import re
import time
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError, Page

from src.LoginManager import LoginManager
from src.data import PerOrderInfoSlim, PerOrderInfoFull, DATE, STATUS
from src.dataPortector import OrderExportConfig
from src.logger import get_logger

LOG = get_logger()

class JDOrderDataExporter():
    """
    JDOrderDataExporter 导出京东订单数据。

    Usage:
    ```
    exporter = JDOrderDataExporter()
    exporter.exec_()
    # 获取导出的数据
    orderInfo_list: list(dict) = exporter.get_order_info_list()
    ```
    """
    DATA_RETRIEVAL_MODE = "详细"        # slim(精简) | full(详细)
    HIGH_SEARCH = "全部类型"            # 全部类型 | 实物商品
    DATE_SEARCH = "近三个月订单"          # 日期筛选
    STATUS_SEARCH = "已完成"            # 订单状态筛选
    
    def __init__(self, config: OrderExportConfig, page: Page) -> None:
        self.__config = config
        self.__page = page
        self.__orderInfo_list = []
        self.__start_time = time.time()
    
    def get_order_info_list(self) -> list[dict]:
        return [orderInfo.to_dict() for orderInfo in self.__orderInfo_list]
    
    def exec_(self):
        """ 终端运行 """
        mode = self.__config.data_retrieval_mode or self.DATA_RETRIEVAL_MODE
        try:
            match mode:
                case "精简":
                    self.__slim_step_1()
                case "详细":
                    self.__full_step_1()
            LOG.success(f"脚本运行结束--耗时:{int(time.time()-self.__start_time)}秒")
        except Exception as err:
            raise err
        finally:
            self.__page.close()

    def __slim_step_1(self):
        """
        根据筛选条件导航到订单列表，获取精简信息
        """
        date_search = self.__config.date_search or self.DATE_SEARCH
        status_search = self.__config.status_search or self.STATUS_SEARCH
        page = 1
        while True:
            url_1 = f"https://order.jd.com/center/list.action?d={DATE.get(date_search)}&s={STATUS.get(status_search, 4096)}&page={page}"
            self.__page.goto(url_1)
            # 结束标志
            try:
                if self.__page.wait_for_selector(".empty-box", timeout=5000):
                    LOG.info(f"识别到结束标志，时间跨度: {date_search} 的订单获取完毕。")
                    break
            except PlaywrightTimeoutError:
                LOG.info(f"==========date-{date_search}=====page-{page}==========")
            tbody_elements = self.__page.query_selector_all("tbody")
            for tbody_element in tbody_elements:
                orderInfo = PerOrderInfoSlim()
                tbody_id: str = tbody_element.get_attribute('id')
                if "parent" in tbody_id:
                    continue # 父订单的 tbody 没有具体信息，直接跳过
                
                # 订单编号
                order_id_element = tbody_element.query_selector('[name="orderIdLinks"]')
                orderInfo.order_id = order_id_element.inner_text()
                
                # 父订单编号(如果有)
                parent_order_id_text = tbody_element.get_attribute("data-parentid")
                if parent_order_id_text:
                    orderInfo.parent_order_id = parent_order_id_text.strip()
                
                # 订单店铺名称
                order_shop_name_element = tbody_element.query_selector(".shop-txt")
                orderInfo.order_shop_name = order_shop_name_element.inner_text().strip()

                # 商品编号
                porduct_id_element = tbody_element.query_selector(".p-name a.a-link")
                product_id_text = porduct_id_element.get_attribute("href")
                match = re.search(r"\d{3,}", product_id_text) # 长度下限，筛除 javascript:void(0); 占位符
                if match:
                    orderInfo.product_id = match.group(0) 

                # 商品名称 && 商品数量
                goods_item_elements = tbody_element.query_selector_all(".goods-item") # 订单中的子商品
                item_num = len(goods_item_elements)
                if item_num == 1:
                    product_name_element = tbody_element.query_selector("div.p-name a.a-link")
                    orderInfo.product_name = product_name_element.inner_text().strip()
                    
                    goods_number_element = tbody_element.query_selector("div.goods-number")
                    orderInfo.goods_number = goods_number_element.inner_text().strip()
                elif item_num > 1:
                    for index, goods_item_element in enumerate(goods_item_elements, start=1):                    
                        product_name_element = goods_item_element.query_selector(".p-name a.a-link")
                        product_name: str = product_name_element.inner_text().strip()
                        orderInfo.product_name += f"({index}) {product_name}\n"

                        goods_number_elements = tbody_element.query_selector_all(f".goods-number")
                        goods_number: str = goods_number_elements[index-1].inner_text().strip()
                        orderInfo.goods_number += f"({index}) {goods_number}\n"
                else:
                    LOG.critical(f"没有找到 goods_item_elements")

                # 实付金额
                actual_payment_amount_element = tbody_element.query_selector(".amount span")
                orderInfo.actual_payment_amount = float(re.search(r"¥(\d+(\.\d+)?)", actual_payment_amount_element.inner_text()).group(1))

                # 订单返豆
                jingdou_increment_element = tbody_element.query_selector('a[href*="myJingBean/list"]')
                if jingdou_increment_element:
                    jingdou_increment_text: str = jingdou_increment_element.inner_text()
                    orderInfo.jingdou_increment = int(re.search(r"\d+", jingdou_increment_text).group(0))

                # 下单时间
                order_time_element = tbody_element.query_selector(".dealtime")
                orderInfo.order_time = order_time_element.inner_text().strip()

                # 订单状态
                order_status_element = tbody_element.query_selector(".status span")
                orderInfo.order_status = order_status_element.inner_text().strip()
                
                # 收货人姓名 && 收货地址 && 收货人电话(数据源已脱敏)
                pc_element = tbody_element.query_selector(".pc")
                if pc_element:
                    orderInfo.consignee_name = pc_element.query_selector("strong").inner_text().strip()

                    orderInfo.consignee_address = pc_element.query_selector("p:nth-of-type(1)").inner_text().strip()

                    orderInfo.consignee_phone_number = pc_element.query_selector("p:nth-of-type(2)").inner_text().strip()
                
                # 订单详情页面地址
                order_url_element = tbody_element.query_selector('a[name="orderIdLinks"]')
                order_url_text = order_url_element.get_attribute("href")
                if "jd" in order_url_text:
                    if "http" not in order_url_text:
                        orderInfo.order_url = "https:" + order_url_text
                self.__orderInfo_list.append(orderInfo)
            # break
            page += 1
    
    def __full_step_1(self):
        self.__slim_step_1()
        # 获取 slim 对象进行信息增添
        for index, slim_info in enumerate(self.__orderInfo_list):
            orderInfo = PerOrderInfoFull(slim_info)
            if "jd" not in orderInfo.order_url:
                LOG.warning(f"无法查看单号为{orderInfo.order_id}订单的详细信息。")
                continue
            self.__page.goto(orderInfo.order_url, wait_until="load")
            self.__page.wait_for_timeout(500)
            body_element = self.__page.wait_for_selector("body")
            page_text = body_element.inner_text()

            # 物流公司
            courier_services_company = None
            priority_patterns = [
                r"承运人：(.*?)(快递咨询|包裹|\n|$)", 
                r"国内物流承运方：(.*?)\.*?货运单号", 
                r"交付([\u4e00-\u9fa5]+)，"
            ]
            for pattern in priority_patterns:
                courier_services_company_match = re.search(pattern, page_text)
                if courier_services_company_match:
                    courier_services_company = courier_services_company_match.group(1).strip()
                    break
            orderInfo.courier_services_company = courier_services_company
            # courier_services_company_match = re.search(r'国际物流承运方：(.*?)\.*?货运单号：(.*?)(\n|$)', page_text)
            
            # 快递单号
            courier_number = None
            priority_patterns = [
                r"货运单号：([A-Za-z0-9]+)",
                r"国内物流承运方：.*?货运单号：(.*?)(点击查询|\n|$)", 
                r"运单号为([a-zA-Z0-9]+)"
            ]
            for pattern in priority_patterns:
                courier_number_match = re.search(pattern, page_text)
                if courier_number_match:
                    courier_number = courier_number_match.group(1).strip()
                    break
            orderInfo.courier_number = courier_number

            
            # 商品总价 
            product_total_price_match = re.search(r"商品总(价|额)：\s*?¥(\d+\.\d{2,})", page_text)
            if product_total_price_match:
                orderInfo.product_total_price = float(product_total_price_match.group(2))
            
            # 订单用豆
            jingdou_decrement_match = re.search(r"京豆：\s*[-+]?\s?¥(\d+\.\d{2,})", page_text)
            if jingdou_decrement_match:
                orderInfo.jingdou_decrement = int(float(jingdou_decrement_match.group(1)) * 100)
            
            # print(orderInfo)
            self.__orderInfo_list[index] = orderInfo
