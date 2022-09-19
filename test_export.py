import os
import logging

from dotenv import load_dotenv
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker
from exporters import flatfile

if __name__ == '__main__':
    load_dotenv()
    logging.basicConfig(level=logging.DEBUG)

    engine = db.create_engine(os.environ["OTTM_TARGET_DATABASE"])
    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()

    exporter = flatfile.FlatFileExporter(session, ".")
    exporter.export_to_csv("metrics.csv")
    exporter.export_to_parquet("metrics.parquet")
