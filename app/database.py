from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# In a real app, use environment variables. Hardcoded for local docker setup as requested.
SQLALCHEMY_DATABASE_URL = "postgresql://user:password@db/dr_soler_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
