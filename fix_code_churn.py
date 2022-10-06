import os
import logging
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
from pydriller.metrics.process.code_churn import CodeChurn

from models.project import Project
from models.version import Version
from models.commit import Commit
import utils.math as mt

if __name__ == '__main__':
    load_dotenv()
    logging.basicConfig(level=logging.INFO)

    """
    ALTER TABLE version ADD COLUMN code_churn_count int;
    ALTER TABLE version ADD COLUMN code_churn_max real;
    ALTER TABLE version ADD COLUMN code_churn_avg int;
    """

    # Setup database
    engine = db.create_engine(os.environ["OTTM_TARGET_DATABASE"])
    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()

    project = session.query(Project).filter(Project.name == os.environ["OTTM_SOURCE_PROJECT"]).first()
    if not project:
        project = Project(name=os.environ["OTTM_SOURCE_PROJECT"],
                        repo=os.environ["OTTM_SOURCE_REPO"],
                        language=os.environ["OTTM_LANGUAGE"])
        session.add(project)
        session.commit()

    versions = session.query(Version).filter(Version.project_id == project.project_id).order_by(Version.start_date.asc()).all()
    from_commit = session.query(Commit.hash).filter(Commit.project_id == project.project_id).order_by(Commit.date.asc()).first()[0]
    for version in versions:
        logging.info("Counting churn between " + from_commit + " and " + version.tag)
        metric = CodeChurn(path_to_repo='/tmp/tmp0jvcoiku/dbeaver/',
                        from_commit=from_commit,
                        to_commit=version.tag)
        files_count = metric.count()
        files_avg = metric.avg()
        files_max = metric.max()
        churn_count = 0
        for file_count in files_count.values():
            churn_count += abs(file_count)
        churn_avg = mt.Math.get_rounded_mean(list(files_avg.values()))
        # for file_avg in files_avg.values():
        #     churn_avg += abs(file_avg)
        churn_max = max(list(files_max.values()))
        # for file_max in files_max.values():
        #     churn_max += abs(file_max)

        logging.info('Chrun count: ' + str(churn_count) + ' / Chrun avg: ' + str(files_avg) + ' / Chrun max: ' + str(files_max))
        from_commit = version.tag
        version.code_churn_count = churn_count
        version.code_churn_avg = churn_avg
        version.code_churn_max = churn_max
        session.commit()

    
    # print('Total code churn for each file: {}'.format(files_count))
    # print('Maximum code churn for each file: {}'.format(files_max))
    # print('Average code churn for each file: {}'.format(files_avg))
