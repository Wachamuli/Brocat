from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base


engine = create_engine(
    name_or_url='sqlite:///brocat/database/db_brocat.db', 
    connect_args={'check_same_thread': False}
)
db_session = scoped_session(sessionmaker(bind=engine, autocommit=False, autoflush=False))
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    import brocat.models
    Base.metadata.create_all(bind=engine)
    