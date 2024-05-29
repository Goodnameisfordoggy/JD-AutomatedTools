import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.storage.dataStorageToExcel import ExcelStorage


if __name__ == "__main__":
    # 示例用法
    data = [{'order_id': '123', 'product_name': 'item1', 'amount': '10.0'}, {'order_id': '124', 'product_name': 'item2', 'amount': '20.0'}]
    header = ['order_id', 'product_name', 'amount']
    file_name = "测试.xlsx"
    excel_storage = ExcelStorage(data, header, file_name)
    excel_storage.save()