'''
Author: HDJ
StartDate: please fill in
LastEditTime: 2024-05-27 23:28:57
FilePath: \pythond:\LocalUsers\Goodnameisfordoggy-Gitee\jd-pers-data-exporter\src\dataStorageToMySQL.py
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
import mysql.connector

try:
    from .dataPortector import ConfigManager
    from .databaseManager import DatabaseManager
except ImportError:
    from dataPortector import ConfigManager
    from databaseManager import DatabaseManager


class MySQLStorange():
    
    def __init__(self, data: list[dict], fields_needed: list, table_name: str) -> None:
        self.__data = data  # 数据(含全部字段)
        self.__fields_needed = fields_needed  # 用户需要的字段
        # 获取配置文件
        self.__configManager = ConfigManager()
        self.__config = self.__configManager.get_mysql_config()
        # 设置生成表的表名
        self.__table_name = table_name 

    def table_exists(self, cursor):
        """检查表是否存在"""
        try:
            cursor.execute("""
                SELECT COUNT(*)
                FROM information_schema.tables 
                WHERE table_schema = %s 
                AND table_name = %s
                """, (DatabaseManager.get_user().get('database'), self.__table_name))
            result = cursor.fetchone()
            return result[0] > 0
        except mysql.connector.Error as err:
            print(f"检查表存在失败: {err}")
            return False

    def creat_table(self, cursor):
        """ 创建表,包含全部字段 """
        field_items = self.__config.get('field_items', '')
        field_definitions = []
        for item in field_items:
            field_name = item['name']
            field_type = item['type']
            if field_type == "varchar":
                field_length = item['length']
                field_definitions.append(f"{field_name} {field_type}({field_length})")
            elif field_type == "decimal":
                field_length = item['length']
                decimal_places = item['decimal_places']
                field_definitions.append(f"{field_name} {field_type}({field_length}, {decimal_places})")
            else: # 普通类型
                field_definitions.append(f"{field_name} {field_type}")

        fields = ", ".join(field_definitions) # sql字段创建部分
        try:
            cursor.execute(f"""
                CREATE TABLE {self.__table_name} (
                    {fields}
                );
                """)
        except mysql.connector.Error as err:
            print(f"创建表失败: {err}")
        
    def get_table_fields(self, cursor):
        """ 获取表中全部字段 """
        cursor.execute(f"SHOW COLUMNS FROM {self.__table_name}")
        fields = [row[0] for row in cursor.fetchall()]
        return fields
    
    def insert_data(self, cursor, order: dict):
        """ 插入数据,逐条"""
        table_fields = self.get_table_fields(cursor)  # 当前表拥有的全部字段
        # 用户需要的字段,需与表中字段比较,筛去未拥有字段
        field_items = [item for item in self.__fields_needed if item in table_fields] 
        field_names = ", ".join(field_items)  # sql字段名部分
        placeholders = ", ".join(["%s"] * len(field_items))  # sql占位符部分
        values = tuple(order.get(field, None) for field in field_items)  # sql插入值部分
        # print(values)
        # print("字段数量:", len(field_items))
        # print("参数数量:", len(values))
        try:
            cursor.execute(f"""
                INSERT INTO {self.__table_name} 
                ({field_names})
                VALUES ({placeholders})
            """, values)
        except mysql.connector.Error as err:
            print(f"数据插入失败: {err}")

    def save(self):
        """ 
        数据储存 
        """
        with DatabaseManager() as db_m:
            cursor =db_m.connection.cursor()
            if not self.table_exists(cursor):
                self.creat_table(cursor)
            for order in self.__data:
                self.insert_data(cursor, order)
            db_m.connection.commit()
                
        
if __name__ == "__main__":
    data = [{'order_id': '293190326521', 'product_name': '冈本 避孕套 安全套 001超薄标准 12只（3片*4盒） 0.01 套套 成人用品 计生用品', 'goods_number': '10', 'amount': '880.70', 'order_time': '2024-05-20 22:04:08', 'order_status': '已完成', 'consignee_name': '霍* 君', 'consignee_address': '河北邯郸市邯山区罗城头街道光明南大街****号 科信学院 广才楼 ****楼', 'consignee_phone_number': '131****6978'}, {'order_id': '293197422650', 'product_name': '(1) 小米（MI）手环8 NFC版 150种运动模式 血氧心率睡眠监测 支持龙年表盘 电子门禁 智能手环 运动手环 亮黑色\n(2) 小米（MI）手环8Pro 夜跃黑 150+种运动模式 双通道血氧心率监测 独立五星定位 小米手环 智能手环 运动手环\n(3) 小米（MI）手环8 150种运动模式 血氧心率睡眠监测 支持龙年表盘 小米手环 智能手环 运动手环 亮黑色\n', 'goods_number': '(1) 1\n(2) 1\n(3) 1\n', 'amount': '746.55', 'order_time': '2024-05-20 21:34:28', 'order_status': '已完成', 'consignee_name': '霍*君', 'consignee_address': '河北邯郸市邯山区罗城头街道金威写字楼****号楼', 'consignee_phone_number': '131****6978'}, {'order_id': '293111369850', 'product_name': '伊利安慕希希腊风味早餐酸奶原味205g*16盒牛奶整箱多35%乳蛋白礼盒装', 'goods_number': '5', 'amount': '188.65', 'order_time': '2024-05-18 10:38:41', 'order_status': '已完成', 'consignee_name': '霍*君', 'consignee_address': '广东深圳市宝安区福海街道龙岗区龙城街道彩云路****栋****楼', 'consignee_phone_number': '131****6978'}, {'order_id': '293113747128', 'product_name': '兰蔻塑颜紧致尝鲜礼【校园专享】', 'goods_number': '1', 'amount': '6.04', 'order_time': '2024-05-18 10:16:55', 'order_status': '已完成', 'consignee_name': '霍*君', 'consignee_address': '河北邯郸市邯山区罗城头街道光明南大街****号 科信学院 广才楼 ****楼', 'consignee_phone_number': '131****6978'}, {'order_id': '293749423277', 'product_name': '安热沙（Anessa）小金瓶防晒乳90ml安耐晒防晒霜SPF50+ 520情人节礼物', 'goods_number': '1', 'amount': '109.05', 'order_time': '2024-05-14 14:42:12', 'order_status': '已完成', 'consignee_name': '霍*君', 'consignee_address': '河北邯郸市邯山区罗城头街道金威写字楼****号楼', 'consignee_phone_number': '131****6978'}, {'order_id': '293794276777', 'product_name': '兰蔻（LANCOME）小白管防晒霜 50ml清透水漾隔离面部清爽型护肤品  520情人节礼物', 'goods_number': '1', 'amount': '259.87', 'order_time': '2024-05-14 00:53:32', 'order_status': '已完成', 'consignee_name': '霍*君', 'consignee_address': '河北邯郸市邯山区罗城头街道光明南大街****号 科 信学院 广才楼 ****楼', 'consignee_phone_number': '131****6978'}, {'order_id': '292776382868', 'product_name': '兰蔻极光尝鲜盒 （极光水10ml+极光精华1ml+小白管1ml+柔光粉底液1ml）', 'goods_number': '1', 'amount': '9.90', 'order_time': '2024-05-12 00:07:09', 'order_status': '已完成', 'consignee_name': '霍*君', 'consignee_address': '河北邯郸市邯山区罗城头街道光明南大街****号 科信 学院 广才楼 ****楼', 'consignee_phone_number': '131****6978'}, {'order_id': '293449653572', 'product_name': '(1) 美宝莲眼唇卸 妆液套装330ml(70ml*3+40ml*3)温和深层清洁 生日礼物女\n(2) 美宝莲净透焕颜卸妆液 40ml\n', 'goods_number': '(1) 16\n(2) 16\n', 'amount': '826.00', 'order_time': '2024-05-09 11:31:29', 'order_status': '已完成', 'consignee_name': '霍*君', 'consignee_address': '河北石家庄市桥西区休门街道邮电园****-****-****', 'consignee_phone_number': '131****6978'}, {'order_id': '293441732139', 'product_name': '美的（Midea）千万负离子电吹风 大功率 家用速干柔顺护发吹风筒 可折叠电吹风机 节日礼物 FZ1-深海蓝', 'goods_number': '1', 'amount': '0.00', 'order_time': '2024-05-09 11:31:29', 'order_status': '已完成', 'consignee_name': '霍*君', 'consignee_address': '河北石家庄市桥西区休门街道邮电园****-****-****', 'consignee_phone_number': '131****6978'}, {'order_id': '293415285158', 'product_name': '兰芝（LANEIGE）水衡凝肌水乳护肤品套盒套装礼盒385ml 滋润型 水+乳液+面膜', 'goods_number': '1', 'amount': '109.92', 'order_time': '2024-05-08 14:23:26', 'order_status': '已完成', 'consignee_name': '霍*君', 'consignee_address': '河北 邯郸市邯山区罗城头街道光明南大街****号 科信学院 广才楼 ****楼', 'consignee_phone_number': '131****6978'}, {'order_id': '292158458455', 'product_name': '资生堂（SHISEIDO）悦薇智感塑颜抗皱霜2ml', 'goods_number': '1', 'amount': '9.90', 'order_time': '2024-05-08 10:15:29', 'order_status': '已完成', 'consignee_name': '霍*君', 'consignee_address': '河北邯郸市邯山区罗城头街道光明南 大街****号 科信学院 广才楼 ****楼', 'consignee_phone_number': '131****6978'}, {'order_id': '292293859827', 'product_name': '(1) 可口可乐（Coca-Cola）美汁源 Minute Maid 果粒橙 果汁饮料 1.25L*12 新老包装随机发货\n(2) 可口可乐（Coca-Cola）碳酸汽水摩登罐饮料330ml*24罐新老包装随机发货\n', 'goods_number': '(1) 5\n(2) 4\n', 'amount': '365.57', 'order_time': '2024-05-08 00:14:53', 'order_status': '已完成', 'consignee_name': '霍*君', 'consignee_address': '上海普陀区真如镇街道真如古镇-南门', 'consignee_phone_number': '131****6978'}, {'order_id': '293397173801', 'product_name': '兰蔻【返30元券】明星修护尝鲜礼', 'goods_number': '1', 'amount': '9.90', 'order_time': '2024-05-08 00:01:37', 'order_status': '已完成', 'consignee_name': '霍*君', 'consignee_address': '河北邯郸市邯山区罗城头街道光明南大街****号 科信学院 广才楼 ****楼', 'consignee_phone_number': '131****6978'}, {'order_id': '292241542140', 'product_name': '(1) 可口可乐（Coca-Cola）美汁源 Minute Maid 果粒橙 果汁饮料 1.25L*12 新老包装随机发货\n(2) 可口可乐（Coca-Cola）碳酸汽水摩登罐饮料330ml*24罐新老包装随机发货\n', 'goods_number': '(1) 5\n(2) 4\n', 'amount': '393.24', 'order_time': '2024-05-07 23:58:16', 'order_status': '已完成', 'consignee_name': '霍*君', 'consignee_address': '上海普陀区真如镇街道真如古镇-南门', 'consignee_phone_number': '131****6978'}, {'order_id': '293396861513', 'product_name': '兰蔻塑颜紧致尝鲜礼【校园专享】', 'goods_number': '1', 'amount': '6.86', 'order_time': '2024-05-07 23:51:42', 'order_status': '已完成', 'consignee_name': '霍*君', 'consignee_address': '河北邯郸市邯山区罗城头街道光明南大街****号 科信学院 广才楼 ****楼', 'consignee_phone_number': '131****6978'}]
    mysql_storange = MySQLStorange(
        data, 
        ["order_id", "product_name", "goods_number", "amount", "order_time", "order_status", "consignee_name", "consignee_address", "consignee_phone_number"], 
        'Goodnameisfordoggy_JD_order'
    )
    mysql_storange.save()