import logging
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
import pandas as pd

from ml.ml import ml
from models.metric import Metric
from models.version import Version
from utils.database import get_included_and_current_versions_filter
from utils.timeit import timeit


class BugVelocity(ml):
    """
    BugVelocity is a simple Machine Learning model (a bit naive) based on the history of
    bug velocity values. It demonstrate how you can integrate your own model into the tool.
    """
    
    def __init__(self, project_id, session, config):
        ml.__init__(self, project_id, session, config)
        self.name = "bugvelocity"

    @timeit
    def train(self):
        """Train the model"""
        logging.info("BugVelocity:train")

        included_versions = self.configuration.include_versions
        excluded_versions = self.configuration.exclude_versions

        releases_statement = self.session.query(Version). \
            order_by(Version.start_date.asc()) \
            .filter(Version.project_id == self.project_id) \
            .filter(Version.include_filter(included_versions)) \
            .filter(Version.exclude_filter(excluded_versions)) \
            .filter(Version.name != self.configuration.next_version_name).statement
        df = pd.read_sql(releases_statement, self.session.get_bind())
        X=df[['bug_velocity']]
        y=df[['bugs']].values.ravel()

        # Model: RandomForestRegressor
        self.model = RandomForestRegressor(n_estimators=200, random_state=1043)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=5)
        self.model.fit(X_train, y_train)
        y_pred = self.model.predict(X_test)
        rdmForest_predictions = [round(value) for value in y_pred]
        self.mse = mean_squared_error(y_test, rdmForest_predictions)
        logging.info("BugVelocity: Mean Square Error : " + str(self.mse))
        self.store()


    @timeit
    def predict(self)->int:
        """Predict the next value"""
        logging.info("BugVelocity::predict")
        self.restore()  # unpickle the model
        bug_velocity = self.session.query(Version.bug_velocity). \
            filter(Version.project_id == self.project_id). \
            filter(Version.name == self.configuration.next_version_name).scalar()
        d = {'bug_velocity': [bug_velocity]}
        X_test = pd.DataFrame(data=d)
        if self.model is None :
            logging.warning("No trained model found for the given project.")
            return None
        else : 
            prediction_df = self.model.predict(X_test)
            value = round(prediction_df[0])
            return value
