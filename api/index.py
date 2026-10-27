import os
import sys

# Ensure root directory is in Python path so all modules (models, config, etc.) import cleanly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
