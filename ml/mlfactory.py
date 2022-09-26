import logging
import sys

from ml.ml import ml
from ml.bugvelocity import BugVelocity
from ml.predictbug import PredictBug


class MlFactory:

    @staticmethod
    def create_ml_model(model_name: str, session, project_id) -> ml:
        if model_name == "bugvelocity":
            logging.info("Using BugVelocity Model")
            return BugVelocity(session, project_id)
        if model_name == "predictbug":
            logging.info("Using PredicBug Model")
            return PredictBug(session, project_id)
        else:
            logging.error(f"Unknown ml model: {model_name}")
            sys.exit('Unknown ml model')
