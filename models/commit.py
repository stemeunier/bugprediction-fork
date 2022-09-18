from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship, backref
from models.database import Base


class Commit(Base):
    __tablename__ = "commit"
    commit_id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("project.project_id"))
    """hash of the commit"""
    hash = Column(String, unique=True, nullable=False)
    """commit committer (name, email)"""
    committer = Column(String)
    """commit date"""
    date = Column(DateTime)
    """number of added lines in the commit (as shown from –shortstat)"""
    insertions = Column(Integer)
    """number of deleted lines in the commit (as shown from –shortstat)"""
    deletions = Column(Integer)
    """total number of added + deleted lines in the commit (as shown from –shortstat)"""
    lines = Column(Integer)
    """number of files changed in the commit (as shown from –shortstat)"""
    files = Column(Integer)
    """DMM metric value for the unit size property"""
    dmm_unit_size = Column(Float)
    """DMM metric value for the unit complexity property"""
    dmm_unit_complexity = Column(Float)
    """DMM metric value for the unit interfacing property"""
    dmm_unit_interfacing = Column(Float)
