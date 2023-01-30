from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, UniqueConstraint
from models.database import Base

class Issue(Base):
    __tablename__ = "issue"
    issue_id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("project.project_id"))
    """External ID (Id in Github)"""
    number = Column(String)
    title = Column(String)
    source = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    __table_args__ = (
        UniqueConstraint("project_id", "number", "source"),
    )