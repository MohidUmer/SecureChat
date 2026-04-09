import os
import sys

# Add parent directory to path to allow importing app.py
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app import app

