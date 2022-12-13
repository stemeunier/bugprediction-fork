import logging
import pickle
from abc import abstractmethod, ABC
from datetime import datetime

from sqlalchemy import and_

from utils.timeit import timeit
from models.model import Model


class ml(ABC):
    """
    Model
    
    Attributes:
    -----------
     - session          Database connection managed by sqlachemy
     - project_id       Identifier of the project
     - configuration    Configuration
     - model            The current model
     - mse              Mean Square Error of the current model
    """
    
    def __init__(self, project_id, session, config):
        self.model = None
        self.name = None
        self.mse = None
        self.session = session
        self.project_id = project_id
        self.configuration = config

    @timeit
    def store(self):
        """Store a serialized trained model """
        logging.info('store model ' + self.name)
        model_in_db = self.session.query(Model).filter(and_(Model.name == self.name, Model.project_id == self.project_id)).first()
        if model_in_db is None:
            logging.info('insert the new model')
            model_in_db = Model(
                project_id = self.project_id,
                name = self.name,
                updated_at = datetime.now(),
                mean_squared_error = self.mse,
                data = pickle.dumps(self.model)
                )
            self.session.add(model_in_db)
            self.session.commit()
        else:
            logging.info('update the existing model')
            model_in_db.updated_at = datetime.now()
            model_in_db.mean_squared_error = self.mse
            model_in_db.data = pickle.dumps(self.model)
            self.session.commit()

    @timeit
    def restore(self):
        """Restore a pickled model"""
        logging.info('restore model ' + self.name)
        model_in_db = self.session.query(Model).filter(and_(Model.name == self.name, Model.project_id == self.project_id)).first()
        if model_in_db is None:
            logging.error('Cannot find model ' + self.name)
            self.model = None
        else:
            self.model = pickle.loads(model_in_db.data)

    @abstractmethod
    def train(self):
        raise NotImplementedError

    @abstractmethod
    def predict(self):
        raise NotImplementedError
