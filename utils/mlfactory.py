import logging

from dependency_injector import providers
from dependency_injector.wiring import Provide, inject

from ml.bugvelocity import BugVelocity
from ml.codemetrics import CodeMetrics
from models.model import Model
from utils.container import Container


class MlFactory:

    @staticmethod
    @inject
    def create_training_ml_model(model_name: str,
                        session = Provide[Container.session], 
                        config = Provide[Container.configuration],
                        ml_factory_provider = Provide[Container.ml_factory_provider.provider]) -> None:
        if model_name == "bugvelocity":
            logging.info("Using BugVelocity Model")
            ml_factory_provider.override(
                providers.Factory(
                    BugVelocity,
                    session = session,
                    config = config
                )
            )
        elif model_name == "codemetrics":
            logging.info("Using CodeMetrics Model")
            ml_factory_provider.override(
                providers.Factory(
                    CodeMetrics,
                    session = session,
                    config = config
                )
            )
        else:
            logging.error(f"Unknown ml model: {model_name}")
            raise Exception('Unknown ml model')

    @staticmethod
    @inject
    def create_predicting_ml_model(project_id,
                                   session = Provide[Container.session],
                                   config = Provide[Container.configuration],
                                   ml_factory_provider = Provide[Container.ml_factory_provider.provider]) -> None:
        
        trained_models = session.query(Model.name).filter(Model.project_id == project_id).all()
        trained_models = [r for r, in trained_models]

        if 'bugvelocity' in trained_models:
            logging.info("Using BugVelocity Model")
            ml_factory_provider.override(
                providers.Factory(
                    BugVelocity,
                    session = session,
                    config = config,
                    project_id=project_id
                )
            )
        elif 'codemetrics' in trained_models:
            logging.info("Using CodeMetrics Model")
            ml_factory_provider.override(
                providers.Factory(
                    CodeMetrics,
                    session = session,
                    config = config,
                    project_id=project_id
                )
            )
        else:
            raise Exception("No trained model found.")