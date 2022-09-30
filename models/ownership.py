from sqlalchemy import Column, Integer, ForeignKey
from models.database import Base

class Ownership(Base):
    __tablename__ = "ownership"
    ownership_id = Column(Integer, primary_key=True)
    version_id = Column(Integer, ForeignKey("version.version_id"))
    file_id = Column(Integer, ForeignKey("file.file_id"))
    author_id = Column(Integer, ForeignKey("author.author_id"))
    added = Column(Integer)
    deleted = Column(Integer)
    author_revs = Column(Integer)
    total_revs = Column(Integer)
