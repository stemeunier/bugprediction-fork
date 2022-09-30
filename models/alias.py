from sqlalchemy import Column, Integer, String, ForeignKey
from models.database import Base

class Alias(Base):
    """Author alias"""
    __tablename__ = "alias"
    alias_id = Column(Integer, primary_key=True)
    author_id = Column(Integer, ForeignKey("author.author_id"))
    name = Column(String)
