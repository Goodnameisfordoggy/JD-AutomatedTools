'''
Author: HDJ
StartDate: please fill in
LastEditTime: 2024-07-21 22:57:09
FilePath: \pythond:\LocalUsers\Goodnameisfordoggy-Gitee\JD-Automated-Tools\JD-PersDataExporter\src\databaseManager.py
Description: 

				*		写字楼里写字间，写字间里程序员；
				*		程序人员写程序，又拿程序换酒钱。
				*		酒醒只在网上坐，酒醉还来网下眠；
				*		酒醉酒醒日复日，网上网下年复年。
				*		但愿老死电脑间，不愿鞠躬老板前；
				*		奔驰宝马贵者趣，公交自行程序员。
				*		别人笑我忒疯癫，我笑自己命太贱；
				*		不见满街漂亮妹，哪个归得程序员？    
Copyright (c) 2024-2025 by HDJ, All Rights Reserved. 
'''
import os
import logging
import configparser
import mysql.connector

class DatabaseManager:
    def __init__(self, config_file_path = None, **kwargs):
        # 日志记录器
        self.logger = logging.getLogger(__name__)
        self.__user_info = {}
        if config_file_path:
                # 获取配置文件
                self.__user_info = self.get_config_info(config_file_path)
        if kwargs:
            # 使用kwargs中的参数覆盖配置文件中的配置信息, 用于无配置文件的连接或在位置参数固定某一信息。
            if 'host' in kwargs:
                self.__user_info.update(host=kwargs['host'])
            if 'port' in kwargs:
                self.__user_info.update(host=kwargs['port'])
            if 'user' in kwargs:
                self.__user_info.update(user=kwargs['user'])
            if 'password' in kwargs:
                self.__user_info.update(password=kwargs['password'])
            if 'database' in kwargs:
                self.__user_info.update(database=kwargs['database'])
        self.connection = None
    
    @staticmethod
    def get_config_info(config_file_path: str = None):
        """ 从配置文件中获取连接信息 """
        config = configparser.ConfigParser()
        if os.path.splitext(config_file_path)[1] == '.ini':
            config.read(os.path.join(config_file_path))
        return {
            'host': config['mysql'].get('host', ''),
            'port': config['mysql'].get('port', ''),
            'user': config['mysql'].get('user', ''),
            'password': config['mysql'].get('password', ''),
            'database': config['mysql'].get('database', '')
        }

    def __connect_database(self):
        """ 连接到MySQL数据库 """
        try:
            self.logger.debug(self.__user_info)
            self.connection = mysql.connector.connect(
            host=self.__user_info.get('host', 'localhost') or 'localhost',
            port=self.__user_info.get('port', 3306) or 3306,
            user=self.__user_info.get('user', 'root') or 'root',
            password=self.__user_info.get('password', ''),
            database=self.__user_info.get('database', '')
            )
            if self.connection.is_connected():
                self.logger.info("数据库连接成功!")
        except mysql.connector.Error as err:
            self.logger.info(f"数据库连接失败: {err}")

    def __enter__(self):
        """ 进入上下文管理器时 """
        self.__connect_database()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """ 退出上下文管理器时 """
        if self.connection and self.connection.is_connected():
            self.connection.close()
            self.logger.info("数据库连接已关闭!")

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    with DatabaseManager(password='root', database='hdj') as dbm:
        pass