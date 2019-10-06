import numpy as np
import os
import psycopg2
import csv
import json
import matplotlib.pyplot as plt

from sshtunnel import SSHTunnelForwarder

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
cur.execute("""select markettime, openprice, closeprice, ofilong, ofishort, volentry, volclear, delay, action, limitorderprice, limitorderpos, positionprice, position, pnl from public.simulation order by markettime;""")

# Get the result
r = cur.fetchall()

# 0:markettime
# 1:openprice
# 2:closeprice
# 3:ofilong
# 4:ofishort
# 5:volentry
# 6:volclear
# 7:delay
# 8:action
# 9:limitorderprice
#10:limitorderpos
#11:positionprice
#12:position
#13:pnl

x = list(map(lambda d: d[0], r))

y_closeprice = list(map(lambda d: d[2], r))
y_ofi_long = list(map(lambda d: d[3], r))
y_ofi_short = list(map(lambda d: d[4], r))
y_vol_entry = list(map(lambda d: d[5], r))
y_vol_clear = list(map(lambda d: d[6], r))
y_delay = list(map(lambda d: d[7], r))
y_position = list(map(lambda d: d[12], r))
y_pnl = list(map(lambda d: d[13], r))

ax1 = plt.subplot(6, 1, 1)
ax1.grid(which='major', axis='x', color='blue', alpha=0.3, linestyle='--')
ax1.grid(which='major', axis='y', color='blue', alpha=0.3, linestyle='--')
plt.plot(x, y_closeprice, label="closeprice", linewidth=0.5)
plt.legend()

ax2 = plt.subplot(6, 1, 2, sharex=ax1)
ax2.grid(which='major', axis='x', color='blue', alpha=0.3, linestyle='--')
ax2.grid(which='major', axis='y', color='blue', alpha=0.3, linestyle='--')
plt.plot(x, y_ofi_long, label="ofi-long", linewidth=0.5)
plt.plot(x, y_ofi_short, label="ofi-short", linewidth=0.5)
plt.legend()
ax2.fill_between(x, y_ofi_long, 0, facecolor='skyblue', alpha = 0.3)
ax2.fill_between(x, y_ofi_short, 0, facecolor='springgreen', alpha = 0.3)

ax3 = plt.subplot(6, 1, 3, sharex=ax1)
ax3.grid(which='major', axis='x', color='blue', alpha=0.3, linestyle='--')
ax3.grid(which='major', axis='y', color='blue', alpha=0.3, linestyle='--')
plt.plot(x, y_vol_entry, label="vol-entry", linewidth=0.5)
plt.plot(x, y_vol_clear, label="vol-clear", linewidth=0.5)
plt.legend()
ax3.fill_between(x, y_vol_entry, 0, facecolor='skyblue', alpha = 0.3)
ax3.fill_between(x, y_vol_clear, 0, facecolor='springgreen', alpha = 0.3)

ax4 = plt.subplot(6, 1, 4, sharex=ax1)
ax4.grid(which='major', axis='x', color='blue', alpha=0.3, linestyle='--')
ax4.grid(which='major', axis='y', color='blue', alpha=0.3, linestyle='--')
plt.plot(x, y_delay, label="delay", linewidth=0.5)
plt.legend()
ax4.fill_between(x, y_delay, 0, facecolor='skyblue', alpha = 0.3)

ax5 = plt.subplot(6, 1, 5, sharex=ax1)
ax5.grid(which='major', axis='x', color='blue', alpha=0.3, linestyle='--')
ax5.grid(which='major', axis='y', color='blue', alpha=0.3, linestyle='--')
plt.plot(x, y_position, label="position", linewidth=0.5)
plt.legend()
ax5.fill_between(x, y_position, 0, facecolor='skyblue', alpha = 0.3)

ax6 = plt.subplot(6, 1, 6,sharex=ax1)
ax6.grid(which='major', axis='x', color='blue', alpha=0.3, linestyle='--')
ax6.grid(which='major', axis='y', color='blue', alpha=0.3, linestyle='--')
plt.plot(x, y_pnl, label="pnl", color='black', linewidth=0.5)
plt.legend()
ax6.fill_between(x, y_pnl, 0, facecolor='skyblue', alpha = 0.3)


mng = plt.get_current_fig_manager()
mng.window.showMaximized()
plt.show()

colnames = [col.name for col in cur.description]

# f = open('simulation_20190908.csv', 'w')
# writer = csv.writer(f, lineterminator='\n')

print("")
#for row in r:
#    print(row[0].strftime("%Y-%m-%d %H:%M:%S.%f"), row[1], row[2], row[3], row[4], row[5])

# writer.writerow(colnames)
# writer.writerows(r)

# f.close()

# Close connections
conn.close()

# Stop the tunnel
tunnel.stop()

