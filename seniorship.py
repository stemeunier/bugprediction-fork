
from models.issue import Issue
from models.project import Project
from models.version import Version
from models.issue import Issue
from models.commit import Commit
from datetime import datetime, date
from sqlalchemy.sql import func
import os
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from models.database import setup_database
from dotenv import load_dotenv

load_dotenv()

engine = db.create_engine(os.environ["OTTM_TARGET_DATABASE"])
Session = sessionmaker()
Session.configure(bind=engine)
session = Session()
setup_database(engine)

start_date = datetime(2017, 12, 29)
end_date = datetime(2020, 10, 11)

team_members = session.query(Commit.committer).filter(Commit.date.between(start_date, end_date)).group_by(Commit.committer).all()

print(team_members)

seniorship = []
seniority_total = 0

for member in team_members:
    first_commit = session.query(
        func.min(Commit.date).label("date")
        ).filter(Commit.committer == member[0]).scalar()
    delta = end_date - first_commit
    seniority = delta.days
    seniority_total += seniority
    print(member[0], first_commit, seniority)

seniority_avg = seniority_total / len(team_members)
print(seniority_avg)
