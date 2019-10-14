import csv
import datetime
import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import ElasticNet
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn import linear_model

import warnings
import seaborn as sns
import matplotlib.pyplot as plt

warnings.filterwarnings('ignore')

def get_new_csv_filename(from_date, to_date):
    from_date_str = from_date.strftime('%Y-%m-%d_%H_%M_%S')
    to_date_str   = to_date.strftime('%Y-%m-%d_%H_%M_%S')
    return "./data/stickdata_elasticnet_{0}_{1}_add_column.csv".format(from_date_str, to_date_str)

def get_output_csv_filename(from_date, to_date):
    from_date_str = from_date.strftime('%Y-%m-%d_%H_%M_%S')
    to_date_str   = to_date.strftime('%Y-%m-%d_%H_%M_%S')
    return "./data/stickdata_elasticnet_targetdata_{0}_{1}.csv".format(from_date_str, to_date_str)

if __name__ == "__main__":
    print("start")
    from_date = datetime.datetime(2019, 10, 4, 4, 20, 0)
    to_date = datetime.datetime(2019, 10, 5, 3, 50, 0)
    new_csv_file_name = get_new_csv_filename(from_date, to_date)

    df_none = pd.read_csv(new_csv_file_name, usecols=lambda x: x not in ['timestamp', 'closeprice', 'sellvolume', 'buyvolume', 'askpressuredelta', 'bidpressuredelta', 'averagedelay', 'ofivolume', 'ofipressuredelta', 'emacloseprice', 'futurecloseprice'])

    output_filepath = get_output_csv_filename(from_date, to_date)
    if os.path.exists(output_filepath):
        os.remove(output_filepath)
    df_none.to_csv(output_filepath)

    X = df_none.drop('pl', axis=1)
    y = df_none.pl

    print('[X-header]')
    print(X.columns)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.5)

    #standardizer = StandardScaler()

    # elasticnet
    #reg = ElasticNet(fit_intercept=False)
    reg = ElasticNet()
    gscv = GridSearchCV(reg,
                        param_grid={'alpha': [0.00001, 0.0001, 0.001, 0.01, 0.1, 1], 'l1_ratio' : [0.001, 0.01, 0.1, 1]},
                        cv=10)

    # standardizer.fit(X_train)
    # X_train_std = standardizer.transform(X_train)
    # X_test_std = standardizer.transform(X_test)
    #gscv.fit(X_train_std, y_train)
    # y_test_pred = gscv.predict(X_test_std)
    gscv.fit(X_train, y_train)
    y_test_pred = gscv.predict(X_test)

    best = gscv.best_estimator_
    print(best)
    print('[Model Evaluation]')
    print('  Intercept       :', best.intercept_)
    print('  Coefficient     :', best.coef_)
    # print('  R^2 on train    : %.5f' % gscv.score(X_train_std, y_train))
    # print('  R^2 on test     : %.5f' % gscv.score(X_test_std, y_test))
    print('  R^2 on train    : %.5f' % gscv.score(X_train, y_train))
    print('  R^2 on test     : %.5f' % gscv.score(X_test, y_test))


    isStd = False

    if isStd:
        y_test_pred_std = (y_test_pred - y_test_pred.mean()) / y_test_pred.std()
        y_test_std = (y_test - y_test.mean()) / y_test.std()
        plt.scatter(y_test_pred_std, y_test_std, alpha = 0.3)
        plt.xlabel('y_test_pred_std')
        plt.ylabel('y_test_std')
        plt.grid(which='major', axis='x', color='blue', alpha=0.3, linestyle='--')
        plt.grid(which='major', axis='y', color='blue', alpha=0.3, linestyle='--')
        x2 = [[xs] for xs in y_test_pred_std]
        clf = linear_model.LinearRegression()
        clf.fit(x2, y_test_std)
        y2 = clf.coef_ * x2 + clf.intercept_
        plt.plot(x2, y2, color='black', alpha=0.3)
        plt.annotate("y=" + str(clf.coef_) + "*x + " + str(clf.intercept_), xy = (0, 1.0), size = 10)
        plt.annotate("R2=" + str(clf.score(x2, y_test_std)), xy = (0, 0), size = 10)
        mng = plt.get_current_fig_manager()
        mng.window.showMaximized()
        plt.show()
    else:
        plt.scatter(y_test_pred, y_test, alpha = 0.3)
        plt.xlabel('y_test_pred')
        plt.ylabel('y_test')
        plt.grid(which='major', axis='x', color='blue', alpha=0.3, linestyle='--')
        plt.grid(which='major', axis='y', color='blue', alpha=0.3, linestyle='--')
        x2 = [[xs] for xs in y_test_pred]
        clf = linear_model.LinearRegression()
        clf.fit(x2, y_test)
        y2 = clf.coef_ * x2 + clf.intercept_
        plt.plot(x2, y2, color='black', alpha=0.3)
        plt.annotate("y=" + str(clf.coef_) + "*x + " + str(clf.intercept_), xy = (0, 100), size = 10)
        plt.annotate("R2=" + str(clf.score(x2, y_test)), xy = (0, 0), size = 10)
        mng = plt.get_current_fig_manager()
        mng.window.showMaximized()
        plt.show()
