import os
import sys

# Add the directory containing 'ballistic_range' to sys.path
# This allows running 'python ballistic_range/main.py' or 'python -m ballistic_range'
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from ballistic_range.main import main

if __name__ == "__main__":
    main()
