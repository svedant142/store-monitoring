from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

#used MySQL
DATABASE_URL = "mysql+pymysql://{username}:{password}@localhost:3306/{database_name}"

Engine = create_engine(
    DATABASE_URL
)

SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=Engine
)

def get_db_connection():
    db = scoped_session(SessionLocal)
    try:
        yield db
    finally:
        db.close()