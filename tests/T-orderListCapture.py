import os 
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.orderListCapture import JDOrderListCapture


if __name__ == "__main__":
    with open('1.html', 'r', encoding='utf-8') as f:
        html = f.read()
    extractor = JDOrderListCapture(html)
    data = extractor.extract_data()
    filtered_data = extractor.filter_data(data)
    print()
    print(filtered_data)
    print(data.get_by_key('order_url'))