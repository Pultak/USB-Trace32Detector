from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker



# used mainly for testing purposes. Creates local sqllite data file
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
'''

# Defining connection url with postgresql database
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@10.5.0.5:5432/usb_api_db"

# Creating engine for database communication
engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
'''
# Session maker for data transmissions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()