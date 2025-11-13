import os
import sys

# BASE_DIR = carpeta 'backend'
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Aseguramos que 'backend' esté en sys.path
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
