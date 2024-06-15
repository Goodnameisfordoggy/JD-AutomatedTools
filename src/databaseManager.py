'''
Author: HDJ
StartDate: please fill in
LastEditTime: 2024-06-15 22:52:45
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
import os
import logging
import configparser
import mysql.connector

WORKING_DIRECTORY_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class DatabaseManager:
    def __init__(self, **kwargs):
        # 日志记录器
        self.logger = logging.getLogger(__name__)
        
        # 获取配置文件
        self.__user_info = self.get_user_info()

        # 使用kwargs中的参数覆盖配置文件中的配置信息
        if kwargs:
            if 'host' in kwargs:
                self.__user_info.update(host=kwargs['host'])
            if 'user' in kwargs:
                self.__user_info.update(user=kwargs['user'])
            if 'password' in kwargs:
                self.__user_info.update(password=kwargs['password'])
            if 'database' in kwargs:
                self.__user_info.update(database=kwargs['database'])
        self.connection = None
    
    @staticmethod
    def get_user_info():
        config = configparser.ConfigParser()
        config.read(os.path.join(WORKING_DIRECTORY_PATH, 'config/mysql_user.ini'))
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
            host=self.__user_info.get('host', ''),
            user=self.__user_info.get('user', ''),
            password=self.__user_info.get('password', ''),
            database=self.__user_info.get('database', '')
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

