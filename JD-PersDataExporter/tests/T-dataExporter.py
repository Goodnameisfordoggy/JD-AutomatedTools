import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.dataExporter import JDDataExporter


if __name__ == "__main__":
    exporter = JDDataExporter()
    exporter.run()