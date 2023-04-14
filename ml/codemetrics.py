import logging

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sqlalchemy.orm import defer

from ml.ml import ml
from utils.timeit import timeit
from xgboost import XGBRegressor

from utils.metricfactory import MetricFactory


class CodeMetrics(ml):
    def __init__(self, project_id, session, config):
        ml.__init__(self, project_id, session, config)
        self.name = "codemetrics"

    @timeit
    def train(self):
        """Train the model"""

        versions_metrics_statement = MetricFactory.get_metrics_query(self.project_id, "train").statement

        dataframe = pd.read_sql(versions_metrics_statement, self.session.get_bind())
        dataframe = dataframe.dropna(axis=1, how='any')
        X = dataframe.drop('bugs', axis=1)
        y = dataframe[['bugs']].values.ravel()
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

        stand = StandardScaler()

        X_train = stand.fit_transform(X_train)
        X_test = stand.transform(X_test)

        # Model: XGBRegressor
        self.model = XGBRegressor(objective='reg:squarederror',
                                  n_estimators=200,
                                  learning_rate=0.1,
                                  tree_method='exact',
                                  random_state=1043)
        self.model.fit(X_train, y_train)
        y_pred = self.model.predict(X_test)
        xgbRegressor_predictions = [round(value) for value in y_pred]
        self.mse = mean_squared_error(y_test, xgbRegressor_predictions)
        logging.info("BugVelocity: Mean Square Error : " + str(self.mse))
        self.store()

    @timeit
    def predict(self) -> int:
        """Predict the next value"""
        logging.info("CodeMetrics::predict")
        self.restore()  # unpickle the model
        versions_metrics_statement = MetricFactory.get_metrics_query(self.project_id, "predict").statement

        dataframe = pd.read_sql(versions_metrics_statement, self.session.get_bind())
        dataframe = dataframe.iloc[0]

        prediction_dataframe = self.model.predict(dataframe)
        value = round(prediction_dataframe[0])
        return value
