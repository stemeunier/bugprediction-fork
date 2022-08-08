from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

def setup_database(engine):
    """Create the database schema from models"""
    Base.metadata.create_all(bind=engine)
