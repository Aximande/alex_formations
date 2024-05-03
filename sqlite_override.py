# sqlite_override.py

import importlib
import sys

# Import pysqlite3 as sqlite3 and replace the sqlite3 in sys.modules
pysqlite3 = importlib.import_module('pysqlite3')
sys.modules['sqlite3'] = pysqlite3
