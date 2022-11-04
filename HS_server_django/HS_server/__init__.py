import os
import sys
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__),"modules"))
sys.path.append(os.path.join(os.path.dirname(__file__),"tools"))
import pymysql
pymysql.install_as_MySQLdb()
