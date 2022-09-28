from sqlalchemy import Column, Integer, String, ForeignKey, Table, DateTime, Float
from sqlalchemy.orm import relationship, backref
from models.database import Base

class Version(Base):
    """
    Versions end when they are published
    """
    __tablename__ = "version"
    version_id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("project.project_id"))
    name = Column(String)
    tag = Column(String)
    # Deducted from the end date of the following release
    start_date = Column(DateTime)
    # the release date
    end_date = Column(DateTime)
    bugs = Column(Integer)
    # Rough estimate of the volume of changes
    changes = Column(Integer)
    avg_team_xp = Column(Float)
    bug_velocity = Column(Float)
    # codemetrics = Column(Float)
