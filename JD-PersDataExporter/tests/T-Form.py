import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.data_type.Form import Form


if __name__ == "__main__":
    
    # 示例使用
    data = Form()
    # data = Form(
    #     {'name': 'Alice', 'age': 30},
    #     {'name': 'Bob', 'age': 25},
    # )

    data.append({'name': 'Charlie', 'age': 35})

    try:
        data.append(['Not a dict'])  # 这将会引发一个TypeError
    except TypeError as e:
        print(e)

    print(data.get_by_key('name'))  # 输出 ['Alice', 'Bob', 'Charlie']
