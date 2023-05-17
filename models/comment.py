import logging
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import validates
from models.database import Base
from models.project import Project


class Comment(Base):
    """
    Comment
    """
    __tablename__ = "comment"
    comment_id = Column(Integer, primary_key=True)
    project_name = Column(Integer, ForeignKey("project.name"))
    user_id = Column(String)
    timestamp = Column(String)
    feature_url = Column(String)
    rating = Column(Integer)
    comment = Column(String)

    @property
    def valid_project_name(self):
        if self.project_name not in self.session.query(Project.name).all():
            logging.warning(f"Invalid project name: {self.project_name}")
            return False
        return True
