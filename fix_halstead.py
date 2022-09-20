import os
import logging

from dotenv import load_dotenv
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker
from models.metric import Metric
import math

if __name__ == '__main__':
    """
    ALTER TABLE metric ADD COLUMN halstead_length real;
    ALTER TABLE metric ADD COLUMN halstead_vocabulary integer;
    ALTER TABLE metric ADD COLUMN halstead_volume real;
    ALTER TABLE metric ADD COLUMN halstead_difficulty real;
    ALTER TABLE metric ADD COLUMN halstead_effort real;
    ALTER TABLE metric ADD COLUMN halstead_time real;
    ALTER TABLE metric ADD COLUMN halstead_bugs real;
    """
    load_dotenv()
    logging.basicConfig(level=logging.DEBUG)

    engine = db.create_engine(os.environ["OTTM_TARGET_DATABASE"])
    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()

    metrics = session.query(Metric).all()
    logging.info('Number of metrics to fix: ' + str(len(metrics)))
    for metric in metrics:
        mu1 = metric.lizard_unique_operators_count
        mu2 = metric.lizard_unique_operands_count
        N1 = metric.lizard_total_operators_count
        N2 = metric.lizard_total_operands_count
        #Vocabulary
        mu = mu1 + mu2
        #length
        N = N1 + N2
        if mu1 and mu2:
            metric.halstead_length = mu1 * math.log(mu1, 2) + mu2 * math.log(mu2, 2)
        else:
            metric.halstead_length = 0
        
        metric.halstead_vocabulary = mu
        metric.halstead_volume = N * math.log(mu, 2) if mu != 0 else 0 # the number of mental comparisons needed to write a program of length N
        metric.halstead_difficulty = (mu1 * N2) / float(2 * mu2) if mu2 != 0 else 0
        metric.halstead_effort = metric.halstead_difficulty * metric.halstead_volume
        metric.halstead_time = metric.halstead_effort / 18.0
        metric.halstead_bugs = metric.halstead_volume / 3000
        logging.info("Metrics ("+ str(metric.version_id) +"): " + str(metric.halstead_length) + " " + str(metric.halstead_vocabulary))
        session.commit()

