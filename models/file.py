from sqlalchemy import Column, Integer, String, ForeignKey, Table, DateTime, Float
from sqlalchemy.orm import relationship, backref
from models.database import Base

class File(Base):
    """File in the repository"""
    __tablename__ = "file"
    file_id = Column(String, primary_key=True)
    path = Column(String)
    language = Column(String)
