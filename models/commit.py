from sqlalchemy import Column, Integer, String, ForeignKey, Table, DateTime, Float
from sqlalchemy.orm import relationship, backref
from models.database import Base


class Commit(Base):
    __tablename__ = "commit"
    commit_id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("project.project_id"))
    sha = Column(String)
    committer = Column(String)
    date = Column(DateTime)
    additions = Column(Integer)
    deletions = Column(Integer)
    total = Column(Integer)
