'''
Author: HDJ
StartDate: please fill in
LastEditTime: 2024-05-27 23:44:37
FilePath: \pythond:\LocalUsers\Goodnameisfordoggy-Gitee\jd-pers-data-exporter\src\DatabaseManager.py
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
import configparser
import mysql.connector
from mysql.connector import Error


class DatabaseManager:
    def __init__(self):
        # 获取配置文件
        self.__uer = self.get_user()
        self.connection = None
    
    @staticmethod
    def get_user():
        config = configparser.ConfigParser()
        config.read('config/mysql_user.ini')
        return {
            'host': config['mysql']['host'],
            'user': config['mysql']['user'],
            'password': config['mysql']['password'],
            'database': config['mysql']['database']
        }

    def connect_database(self):
        """连接到MySQL数据库"""
        try:
            self.connection = mysql.connector.connect(
            host=self.__uer.get('host', ''),
            user=self.__uer.get('user', ''),
            password=self.__uer.get('password', ''),
            database=self.__uer.get('database', '')
            )
            if self.connection.is_connected():
                print("连接成功")
        except mysql.connector.Error as err:
            print(f"连接失败: {err}")

    def __enter__(self):
        """进入上下文管理器时调用"""
        self.connect_database()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """退出上下文管理器时调用"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("连接已关闭")


if __name__ == "__main__":
    with DatabaseManager() as db_manager:
        if db_manager.connection:
            try:
                cursor = db_manager.connection.cursor()
                table_name = 'Goodnameisfordoggy_JD_order'
                cursor.execute(f"SELECT * FROM {table_name}")
                results = cursor.fetchall()
                for row in results:
                    print(row)
            except Error as err:
                print(f"查询失败: {err}")
            finally:
                cursor.close()
                print("游标已关闭")
