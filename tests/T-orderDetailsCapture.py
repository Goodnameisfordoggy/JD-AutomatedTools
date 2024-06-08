import os 
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.orderDetailsCapture import JDOrderDetailsCapture

if __name__ == '__main__':
    orderDetailsCapture = JDOrderDetailsCapture()
    # orderDetailsCapture.get()
    orderDetailsCapture.extract_data()
    # print(orderDetailsCapture.get_courier_services_company())