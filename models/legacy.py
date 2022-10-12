from sqlalchemy import Column, Integer, ForeignKey
from models.database import Base

class Legacy(Base):
    """
    Versions end when they are published
    """
    __tablename__ = "legacy"
    legacy_id = Column(Integer, primary_key=True)
    version_id = Column(Integer, ForeignKey("version.version_id"))
    file_id = Column(Integer, ForeignKey("file.file_id"))
    
