import mysql.connector
from datetime import datetime as dt
from datetime import timedelta as td

from const import *

conn = mysql.connector.connect(
    host=DB_HOST,
    user=DB_USER,
    password = DB_PASS,
    database=DB_NAME
)

cur = conn.cursor()

try:
    now = dt.now()
    yesterday = now - td(days=1)
    # query = f"DELETE FROM bluesummers$ffxiinv.inventories WHERE expire_time < DATEADD(day, -2, GETDATE());"
    query = "DELETE FROM inventories WHERE expire_time < %s"
    cur.execute(query, (yesterday,))
except Exception as E:
    print(E)
else:
    print("24Hr DELETE ran with no errors")
finally:
    conn.commit()
    cur.close()
    conn.close()
