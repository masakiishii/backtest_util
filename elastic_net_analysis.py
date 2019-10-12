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

import warnings

warnings.filterwarnings('ignore')

def get_new_csv_filename(from_date, to_date):
    from_date_str = from_date.strftime('%Y-%m-%d_%H_%M_%S')
    to_date_str   = to_date.strftime('%Y-%m-%d_%H_%M_%S')
    return "./data/stickdata_elasticnet_{0}_{1}_add_column.csv".format(from_date_str, to_date_str)

if __name__ == "__main__":
    print("start")
    from_date = datetime.datetime(2019, 10, 4, 4, 20, 0)
    to_date = datetime.datetime(2019, 10, 5, 3, 50, 0)
    new_csv_file_name = get_new_csv_filename(from_date, to_date)

    df_none = pd.read_csv(new_csv_file_name, usecols=lambda x: x not in ['timestamp', 'closeprice', 'sellvolume', 'buyvolume', 'askpressuredelta', 'bidpressuredelta', 'averagedelay', 'ofivolume', 'ofipressuredelta', 'emacloseprice', 'futurecloseprice'])

    X = df_none.drop('pl', axis=1)
    y = df_none.pl

    print('[X-header]')
    print(X.columns)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1)

    standardizer = StandardScaler()

    # elasticnet
    reg = ElasticNet()
    gscv = GridSearchCV(reg,
                        param_grid={'alpha': [1.0, 0.5, 0.1]},
                        cv=2)

    standardizer.fit(X_train)
    X_train_std = standardizer.transform(X_train)
    X_test_std = standardizer.transform(X_test)
    gscv.fit(X_train_std, y_train)
    y_test_pred = gscv.predict(X_test_std)

    best = gscv.best_estimator_
    print(best)
    print('[Model Evaluation]')
    print('  Intercept       :', best.intercept_)
    print('  Coefficient Std :', best.coef_)
    print('  Coefficient     :', best.coef_ * ((X_train.apply(lambda xt: y_train.values.var() / xt.var()))**(0.5)).values)
    print('  R^2 on train    : %.5f' % gscv.score(X_train_std, y_train))
    print('  R^2 on test     : %.5f' % gscv.score(X_test_std, y_test))

