from sqlalchemy import Column, Integer, String, ForeignKey, Table, DateTime, Float
from sqlalchemy.orm import relationship, backref
from models.database import Base

class Issue(Base):
    __tablename__ = "issue"
    issue_id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("project.project_id"))
    version_id = Column(Integer, ForeignKey("version.version_id"))
    """External ID (Id in Github"""
    number = Column(String)
    title = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
