from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
import pandas as pd

from ml.ml import ml
from models.metric import Metric
from models.version import Version
from utils.timeit import timeit
from xgboost import XGBRegressor


class PredictBug(ml):
    def __init__(self, session, project_id):
        ml.__init__(self, session, project_id)
        self.name = "predictbug"

    @timeit
    def train(self):
        """Train the model"""
        releases_statement = self.session.query(Version).order_by(Version.version_id.asc()).filter(Version.project_id == self.project_id).filter(Version.name != "Next Release").statement
        df = pd.read_sql(releases_statement, self.session.get_bind())
        X=df.drop(['bugs', 'metrics_id'], axis=1)
        y=df[['bugs']].values.ravel()

        # Model: XGBRegressor
        self.model = XGBRegressor(objective='reg:squarederror',
                                  n_estimators=200,
                                  learning_rate=0.1,
                                  tree_method='exact',
                                  random_state=1043)

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
        self.model.fit(X_train, y_train)
        y_pred = self.model.predict(X_test)
        xgbRegressor_predictions = [round(value) for value in y_pred]
        self.mse = mean_squared_error(y_test, xgbRegressor_predictions)
        self.store()


    @timeit
    def predict(self)->int:
        """Predict the next value"""
        self.restore()  # unpickle the model
        next_release = self.session.query(Version).filter(Version.project_id == self.project_id).filter(Version.name == "Next Release").first()
        last_release = self.session.query(Version).order_by(Version.end_date.desc()).filter(Version.project_id == self.project_id).limit(2)[1]
        # metrics = self.session.query(Metric).filter(Metric.version_id == next_release.version_id).first()
        d = {'predict_bug': [last_release.predict_bug]}
        X_test = pd.DataFrame(data=d)
        prediction_df = self.model.predict(X_test)
        value = round(prediction_df[0])
        return value
