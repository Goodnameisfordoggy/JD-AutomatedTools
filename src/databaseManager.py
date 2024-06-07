'''
Author: HDJ
StartDate: please fill in
LastEditTime: 2024-06-07 11:14:17
FilePath: \pythond:\LocalUsers\Goodnameisfordoggy-Gitee\jd-pers-data-exporter\src\databaseManager.py
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
import logging
import configparser
import mysql.connector


class DatabaseManager:
    def __init__(self):
        # 日志记录器
        self.logger = logging.getLogger(__name__)
        
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
                self.logger.info("数据库连接成功")
        except mysql.connector.Error as err:
            self.logger.info(f"数据库连接失败: {err}")

    def __enter__(self):
        """进入上下文管理器时调用"""
        self.connect_database()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """退出上下文管理器时调用"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            self.logger.info("数据库连接已关闭")

