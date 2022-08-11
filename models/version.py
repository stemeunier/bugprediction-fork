from sqlalchemy import Column, Integer, String, ForeignKey, Table, DateTime, Float
from sqlalchemy.orm import relationship, backref
from models.database import Base

class Version(Base):
    __tablename__ = "version"
    version_id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("project.project_id"))
    name = Column(String)
    tag = Column(String)
    start_date = Column(DateTime)
    # Deducted from the start date of the following release
    end_date = Column(DateTime)
    bugs = Column(Integer)
    # Rough estimate of the volume of changes
    changes = Column(Integer)
    avg_team_xp = Column(Float)
    bug_velocity = Column(Float)

