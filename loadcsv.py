import numpy as np
import os
import psycopg2
import csv
import json
import matplotlib.pyplot as plt
import datetime

from sshtunnel import SSHTunnelForwarder

from_date     = datetime.datetime(2019, 10, 19, 4, 20, 0)
to_date       = datetime.datetime(2019, 10, 19, 23, 59, 0)
from_date_str = from_date.strftime('%Y-%m-%d_%H_%M_%S')
to_date_str   = to_date.strftime('%Y-%m-%d_%H_%M_%S')

with open('./configuration.json', 'r') as f:
    df = json.load(f)

# Create an SSH tunnel
tunnel = SSHTunnelForwarder(
    (df['ssh']['ip'], 22),
    ssh_username=df['ssh']['username'],
    ssh_password=df['ssh']['password'],
    remote_bind_address=(df['ssh']['remote_bind_address'], 5432),
    local_bind_address=(df['ssh']['local_bind_address'],6432), # could be any available port
)
# Start the tunnel
tunnel.start()
print("start tunnel")

# Create a database connection
conn = psycopg2.connect(
    database=df['db']['dbname'],
    user=df['db']['user'],
    password=df['db']['password'],
    host=tunnel.local_bind_host,
    port=tunnel.local_bind_port,
)

# Get a database cursor
cur = conn.cursor()
print("start cursor")


# Execute SQL
sql_stmt = """select "timestamp", health, closeprice, sellvolume, buyvolume, askpressuredelta, bidpressuredelta, averagedelay, (buyvolume + bidpressuredelta - sellvolume - askpressuredelta) as ofi from public.stickdata where '{0}' <= timestamp and timestamp <= '{1}' order by timestamp;""".format(from_date, to_date)

# 0: timestamp
# 1: health
# 2: closeprice
# 3: sellvolume
# 4: buyvolume
# 5: askpressuredelta
# 6: bidpressuredelta
# 7: averagedelay
# 8: oif

cur.execute(sql_stmt)

# Get the result
r = cur.fetchall()
colnames = [col.name for col in cur.description]

file_name = './data/stickdata_{0}_{1}.csv'.format(from_date_str, to_date_str)
f = open(file_name, 'w')
writer = csv.writer(f, lineterminator='\n')
writer.writerow(colnames)
writer.writerows(r)

f.close()
conn.close()
tunnel.stop()
