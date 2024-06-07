import os 
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.dataPortector import ConfigManager


if __name__ == "__main__":
    config_manager = ConfigManager()
    config = config_manager.get_config()
    print(config)
    config = config_manager.get_excel_config()
    print(config)
    config = config_manager.get_mysql_config()
    print(config)
    # date_range_dict = config_manager.get_date_range_dict()
    # print(date_range_dict)