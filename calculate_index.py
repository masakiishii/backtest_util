import csv
import datetime
import os

def get_csv_filename(from_date, to_date):
    from_date_str = from_date.strftime('%Y-%m-%d_%H_%M_%S')
    to_date_str   = to_date.strftime('%Y-%m-%d_%H_%M_%S')
    return "stickdata_{0}_{1}.csv".format(from_date_str, to_date_str)

def get_new_csv_filename(from_date, to_date):
    from_date_str = from_date.strftime('%Y-%m-%d_%H_%M_%S')
    to_date_str   = to_date.strftime('%Y-%m-%d_%H_%M_%S')
    return "stickdata_{0}_{1}_add_column.csv".format(from_date_str, to_date_str)

def add_vol_column(f):
    reader = csv.reader(f)
    l = [row for row in reader]
    l[0].append('vol_5sec')
    row_length = len(l)
    for i in range(row_length):
        if i == 0:
            continue
        j = i + 5
        if row_length > j:
            current_price = int(l[i][2])
            next_price = int(l[j][2])
            l[i].append(abs(current_price - next_price))
        else:
            l[i].append(0)
    return l

def calculate_vol_weighted_average(l, window_time, vol_time):
    l[0].append('vol_5sec_ave')
    row_length = len(l)
    for i in range(row_length):
        if i == 0:
            continue
        j = i - window_time
        if j <= 0:
            l[i].append(0)
            continue
        just_sum = 0
        all_sum = 0
        for k in range(window_time - vol_time):
           index_current = j + k
           just_sum = just_sum + (k + 1)
           all_sum = all_sum + int(l[index_current][12]) * (k + 1)

        l[i].append(all_sum/just_sum)

if __name__ == "__main__":
    print("start main")
    from_date = datetime.datetime(2019, 9, 15, 21, 0, 0)
    to_date = datetime.datetime(2019, 9, 15, 23, 59, 0)
    csv_file_name = get_csv_filename(from_date, to_date)
    new_csv_file_name = get_new_csv_filename(from_date, to_date)
    if os.path.exists(new_csv_file_name):
        os.remove(new_csv_file_name)

    with open(csv_file_name) as f:
        l = add_vol_column(f)
        calculate_vol_weighted_average(l, 60, 5)
        with open(new_csv_file_name, 'w') as wf:
            writer = csv.writer(wf)
            writer.writerows(l)
