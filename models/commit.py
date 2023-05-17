from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float
from models.database import Base


class Commit(Base):
    """
    Commit to a git-based SCM system

    Attributes
    ----------
    commit_id : int
        Unique Idendtifier of the commit
    project_id : int
        Identifier of the project
    hash : str
        hash of the commit
    committer : str
        commit committer (name, email)
    date : datetime
        commit date
    message : str
        commit message
    insertions : int
        number of added lines in the commit (as shown from –shortstat)
    deletions : int
        number of deleted lines in the commit (as shown from –shortstat)
    lines : int
        total number of added + deleted lines in the commit (as shown from –shortstat)
    files : int
        number of files changed in the commit (as shown from –shortstat)
    dmm_unit_size : float
        DMM metric value for the unit size property
    dmm_unit_complexity : float
        DMM metric value for the unit complexity property
    dmm_unit_interfacing : float
        DMM metric value for the unit interfacing property
    """
    __tablename__ = "commit"
    commit_id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("project.project_id"))
    hash = Column(String)
    committer = Column(String)
    date = Column(DateTime)
    message = Column(String)
    insertions = Column(Integer)
    
    deletions = Column(Integer)
    lines = Column(Integer)
    files = Column(Integer)
    dmm_unit_size = Column(Float)
    dmm_unit_complexity = Column(Float)
    dmm_unit_interfacing = Column(Float)
    