import csv
import datetime
import os
import matplotlib.pyplot as plt
import pandas as pd
from pandas.plotting import scatter_matrix
from sklearn import linear_model

def get_new_csv_filename(from_date, to_date):
    from_date_str = from_date.strftime('%Y-%m-%d_%H_%M_%S')
    to_date_str   = to_date.strftime('%Y-%m-%d_%H_%M_%S')
    return "./data/stickdata_{0}_{1}_add_column.csv".format(from_date_str, to_date_str)


if __name__ == "__main__":
    print("start main")
    from_date = datetime.datetime(2019, 10, 4, 4, 20, 0)
    to_date = datetime.datetime(2019, 10, 5, 3, 50, 0)
    new_csv_file_name = get_new_csv_filename(from_date, to_date)

    if not os.path.exists(new_csv_file_name):
        print("couldn't find csv file")
    else:
        data = pd.read_csv(new_csv_file_name)
        data.describe()
        x = data['ofidiff'].values
        y = data['pl'].values
        plt.scatter(x, y, alpha = 0.3)
        plt.ylabel('pl')
        plt.xlabel('ofidiff')

        x2 = [[xs] for xs in x]
        clf = linear_model.LinearRegression()
        clf.fit(x2, y)
        plt.plot(x2, clf.predict(x2))
        plt.annotate("y=" + str(clf.coef_) + "*x + " + str(clf.intercept_), xy = (0, 100), size = 10)
        plt.annotate("R2=" + str(clf.score(x2, y)), xy = (0, 0), size = 10)
        mng = plt.get_current_fig_manager()
        mng.window.showMaximized()
        plt.show()
