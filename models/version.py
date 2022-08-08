from sqlalchemy import Column, Integer, String, ForeignKey, Table, DateTime, Float
from sqlalchemy.orm import relationship, backref
from models.database import Base

class Version(Base):
    __tablename__ = "version"
    version_id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("project.project_id"))
    tag = Column(String)
    date = Column(DateTime)
    # From repo if available
    bugs = Column(Integer)
    changes = Column(Integer)
    avg_team_xp = Column(Float)
    bug_velocity = Column(Float)

