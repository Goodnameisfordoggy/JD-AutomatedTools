import os 
import sys
import mysql.connector

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.databaseManager import DatabaseManager


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
            except mysql.connector.Error as err:
                print(f"查询失败: {err}")
            finally:
                cursor.close()
                print("游标已关闭")