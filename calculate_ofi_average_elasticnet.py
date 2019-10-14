import csv
import datetime
import os

def get_csv_filename(from_date, to_date):
    from_date_str = from_date.strftime('%Y-%m-%d_%H_%M_%S')
    to_date_str   = to_date.strftime('%Y-%m-%d_%H_%M_%S')
    return "./data/stickdata_elasticnet_{0}_{1}.csv".format(from_date_str, to_date_str)

def get_new_csv_filename(from_date, to_date):
    from_date_str = from_date.strftime('%Y-%m-%d_%H_%M_%S')
    to_date_str   = to_date.strftime('%Y-%m-%d_%H_%M_%S')
    return "./data/stickdata_elasticnet_{0}_{1}_add_column.csv".format(from_date_str, to_date_str)

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

def filter_not_equal_zero(matrix, index):
    m = []
    row_length = len(matrix)
    for i in range(row_length):
        if i == 0:
            m.append(matrix[i])
        else:
            if float(matrix[i][index]) != 0:
                m.append(matrix[i])
    return m

def filter_under_one_second(matrix, index):
    m = []
    row_length = len(matrix)
    for i in range(row_length):
        if i == 0:
            m.append(matrix[i])
        else:
            if float(matrix[i][index]) < 1:
                m.append(matrix[i])
    return m

def calculate_subtraction(matrix, new_col_name, lhs_index, rhs_index):
    matrix[0].append(new_col_name)
    row_length = len(matrix)
    for i in range(row_length):
        if i == 0:
            continue
        m = matrix[i]
        m.append(float(m[lhs_index]) - float(m[rhs_index]))

def calculate_ema(org_matrix, new_col_name, window_length, ref_col_index):
    org_matrix[0].append(new_col_name)
    row_length = len(org_matrix)
    for i in range(row_length):
        if i == 0:
            continue
        j = i - window_length + 1
        if j <= 0:
            org_matrix[i].append(0)
            continue
        all_sum = 0
        for k in range(window_length):
            index_current = j + k
            all_sum = all_sum + float(org_matrix[index_current][ref_col_index])
        org_matrix[i].append((all_sum + float(org_matrix[i][ref_col_index])) / (window_length + 1))


if __name__ == "__main__":
    print("start main")
    from_date = datetime.datetime(2019, 10, 13, 4, 20, 0)
    to_date = datetime.datetime(2019, 10, 14, 3, 50, 0)
    csv_file_name = get_csv_filename(from_date, to_date)
    new_csv_file_name = get_new_csv_filename(from_date, to_date)

    if os.path.exists(new_csv_file_name):
        os.remove(new_csv_file_name)

    ## Parameter
    ofi_long_term = 30
    ofi_short_term = 2
    delay_term = 5
    future_close_price_term = 5
    close_price_ema_term = 3

    # ref index
# 0: timestamp
# 1: closeprice
# 2: sellvolume
# 3: buyvolume
# 4: askpressuredelta
# 5: bidpressuredelta
# 6: averagedelay
# 7: ofivolume
# 8: ofipressuredelta
    ref_closeprice = 1
    ref_delay = 6
    ref_ofi_volume = 7
    ref_ofi_pressure = 8

    ref_ofi_volume_short = 9
    ref_ofi_volume_long = 10
    ref_ofi_pressure_short = 11
    ref_ofi_pressure_long = 12
    ref_ema_closeprice = 13
    ref_ema_price_diff = 14
    ref_future_price = 15
    ##

    with open(csv_file_name) as f:
        reader = csv.reader(f)
        org_matrix = [row for row in reader]
        calculate_ema(org_matrix, "ofishortvolume" + str(ofi_short_term), ofi_short_term, ref_ofi_volume)
        calculate_ema(org_matrix, "ofilongvolume" + str(ofi_long_term), ofi_long_term, ref_ofi_volume)
        calculate_ema(org_matrix, "ofishortpressure" + str(ofi_short_term), ofi_short_term, ref_ofi_pressure)
        calculate_ema(org_matrix, "ofilongpressure" + str(ofi_long_term), ofi_long_term, ref_ofi_pressure)
        calculate_ema(org_matrix, "emacloseprice", close_price_ema_term, ref_closeprice)
        calculate_subtraction(org_matrix, "emapricediff", ref_ema_closeprice, ref_closeprice)
        calculate_future_data(org_matrix, "futurecloseprice", future_close_price_term, ref_closeprice)
        m = filter_not_equal_zero(org_matrix, ref_ofi_volume_long)
        m = filter_not_equal_zero(m, ref_ema_closeprice)
        m = filter_not_equal_zero(m, ref_future_price)
        filter_under_one_second(m, ref_delay)
        calculate_subtraction(m, "pl", ref_future_price, ref_closeprice)
        with open(new_csv_file_name, 'w') as wf:
            writer = csv.writer(wf)
            writer.writerows(m)
