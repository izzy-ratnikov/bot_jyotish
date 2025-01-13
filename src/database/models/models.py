from sqlalchemy import create_engine, Column, Integer, String, Date, Time
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class UserData(Base):
    __tablename__ = 'user_data'

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(Integer, nullable=False)
    location = Column(String, nullable=False)
    birth_date = Column(Date, nullable=False)
    birth_time = Column(Time, nullable=False)


engine = create_engine('sqlite:///userdata.db')
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()
