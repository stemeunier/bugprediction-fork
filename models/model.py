from sqlalchemy import Column, Integer, String, ForeignKey, LargeBinary, DateTime, Float
from sqlalchemy.orm import relationship, backref
from models.database import Base

class Model(Base):
    __tablename__ = "model"
    model_id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("project.project_id"))
    name = Column(String)
    updated_at = Column(DateTime)
    mean_squared_error = Column(Float)
    data = Column(LargeBinary)

