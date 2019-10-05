import csv
import datetime
import os

def get_csv_filename(from_date, to_date):
    from_date_str = from_date.strftime('%Y-%m-%d_%H_%M_%S')
    to_date_str   = to_date.strftime('%Y-%m-%d_%H_%M_%S')
    return "./data/stickdata_{0}_{1}.csv".format(from_date_str, to_date_str)

def get_new_csv_filename(from_date, to_date):
    from_date_str = from_date.strftime('%Y-%m-%d_%H_%M_%S')
    to_date_str   = to_date.strftime('%Y-%m-%d_%H_%M_%S')
    return "./data/stickdata_{0}_{1}_add_column.csv".format(from_date_str, to_date_str)

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

def calculate_future_data(org_matrix, new_col_name, future_length, ref_col_index):
    org_matrix[0].append(new_col_name)
    row_length = len(org_matrix)
    for i in range(row_length):
        if i == 0: # header
            continue
        j = i + future_length
        if row_length > j:
            org_matrix[i].append(org_matrix[j][ref_col_index])
        else:
            org_matrix[i].append(0)

def calculate_weighted_average(org_matrix, new_col_name, window_length, ref_col_index):
    org_matrix[0].append(new_col_name)
    row_length = len(org_matrix)
    for i in range(row_length):
        if i == 0: # header
            continue
        j = i - window_length + 1
        if j <= 0: # not enough market data
            org_matrix[i].append(0)
            continue
        just_sum = 0
        all_sum = 0
        for k in range(window_length):
            index_current = j + k
            just_sum = just_sum + (k + 1)
            all_sum = all_sum + float(org_matrix[index_current][ref_col_index]) * (k + 1)
        org_matrix[i].append(all_sum / just_sum)

def calculate_simple_average(org_matrix, new_col_name, window_length, ref_col_index):
    org_matrix[0].append(new_col_name)
    row_length = len(org_matrix)
    for i in range(row_length):
        if i == 0: # header
            continue
        j = i - window_length + 1
        if j <= 0: # not enough market data
            org_matrix[i].append(0)
            continue
        all_sum = 0
        for k in range(window_length):
            index_current = j + k
            all_sum = all_sum + float(org_matrix[index_current][ref_col_index])
        org_matrix[i].append(all_sum / window_length)


def filter_data(matrix, ofi_long_index, delay_index, future_price_index):
    m = []
    row_length = len(matrix)
    for i in range(row_length):
        if i == 0:
            m.append(matrix[i])
        else:
            if float(matrix[i][ofi_long_index]) != 0 and float(matrix[i][delay_index]) < 1 and float(matrix[i][future_price_index]) != 0:
                m.append(matrix[i])
    return m

if __name__ == "__main__":
    print("start main")
    from_date = datetime.datetime(2019, 10, 4, 4, 20, 0)
    to_date = datetime.datetime(2019, 10, 5, 3, 50, 0)
    csv_file_name = get_csv_filename(from_date, to_date)
    new_csv_file_name = get_new_csv_filename(from_date, to_date)

    if os.path.exists(new_csv_file_name):
        os.remove(new_csv_file_name)

    with open(csv_file_name) as f:
        reader = csv.reader(f)
        org_matrix = [row for row in reader]
        calculate_simple_average(org_matrix, "ofilong50", 50, 8)
        calculate_simple_average(org_matrix, "ofishort5", 5, 8)
        calculate_weighted_average(org_matrix, "delayweighted5", 5, 7)
        calculate_future_data(org_matrix, "futurecloseprice5sec", 5, 2)

        m = filter_data(org_matrix, 9, 11, 12)
        with open(new_csv_file_name, 'w') as wf:
            writer = csv.writer(wf)
            writer.writerows(m)
