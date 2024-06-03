'''
Author: HDJ
StartDate: please fill in
LastEditTime: 2024-06-01 23:54:59
FilePath: \pythond:\LocalUsers\Goodnameisfordoggy-Gitee\jd-pers-data-exporter\src\storage\dataStorageToMySQL.py
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

from ..dataPortector import ConfigManager
from ..databaseManager import DatabaseManager


class MySQLStorange():
    
    def __init__(self, data: list[dict], fields_needed: list, table_name: str) -> None:
        self.__data = data  # 数据(含全部字段)
        self.__fields_needed = fields_needed  # 用户需要的字段
        # 获取配置文件
        self.__configManager = ConfigManager()
        self.__config = self.__configManager.get_mysql_config()
        # 设置生成表的表名
        self.__table_name = table_name 
        self.__existent_order_id = None

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
    
    def get_order_id(self, cursor):
        """ 获取表中order_id字段下全部值 """
        order_id_list = []
        try:
            cursor.execute(f"SELECT order_id FROM {self.__table_name}")
            results = cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"order_id获取失败: {err}")
        for result in results:
            order_id_list.append(result[0])
        return order_id_list
    
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
            # 检测所选表是否存在，否则创建新表        
            if not self.table_exists(cursor):
                self.creat_table(cursor)
            # 获取表中存在的order_id
            self.__existent_order_id = self.get_order_id(cursor)
            for order in self.__data:
                if order.get('order_id', 0) not in self.__existent_order_id:
                    self.insert_data(cursor, order)
            db_m.connection.commit()
                