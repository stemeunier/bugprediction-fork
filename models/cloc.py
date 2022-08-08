from sqlalchemy import Column, Integer, String, ForeignKey, Table, DateTime, Float
from sqlalchemy.orm import relationship, backref
from models.database import Base

class Cloc(Base):
    """ Cloc stores the language table"""
    __tablename__ = "cloc"
    cloc_id = Column(Integer, primary_key=True)
    version_id = Column(Integer, ForeignKey("version.version_id"))
    # cloc metrics (filtered on the language)
    language = Column(String)
    files = Column(Integer)
    blank = Column(Integer)
    comment = Column(Integer)
    code = Column(Integer)
