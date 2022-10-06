from sqlalchemy import Column, Integer, String, ForeignKey, Table, DateTime, Float
from sqlalchemy.orm import relationship, backref
from models.database import Base

class Version(Base):
    """
    Versions end when they are published
    """
    __tablename__ = "version"
    version_id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("project.project_id"))
    # By convention, the next version is nammed "Next Release"
    name = Column(String)
    # Might be the same as tag, except for the next release
    tag = Column(String)
    # Deducted from the end date of the following release
    start_date = Column(DateTime)
    # the release date
    end_date = Column(DateTime)
    # Number of bugs in the version
    bugs = Column(Integer)
    # Rough estimate of the volume of changes
    changes = Column(Integer)
    # Average experience of the dev team
    avg_team_xp = Column(Float)
    # Bug velocity (avg new bug opened daily in the version)
    bug_velocity = Column(Float)
    # Code churn, or code that is rewritten or deleted shortly after being written
    code_churn_count = Column(Integer)
    # Maximun code chrun on a file
    code_churn_max = Column(Integer)
    # Average code churn per file
    code_churn_avg = Column(Float)
