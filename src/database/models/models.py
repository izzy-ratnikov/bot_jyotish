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


DATABASE_URL = "postgresql://jyotish:P6SSw0RdJyot1_sh@109.205.180.137:5432/jyotish"

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()
