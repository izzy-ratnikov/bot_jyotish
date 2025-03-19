from sqlalchemy import create_engine, Column, Integer, String, Date, Time, BigInteger, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class UserData(Base):
    __tablename__ = 'user_data'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    telegram_id = Column(Integer, nullable=False)
    username = Column(String, nullable=True)
    location = Column(String, nullable=False)
    birth_date = Column(Date, nullable=False)
    birth_time = Column(Time, nullable=False)
    chart_interpretation = Column(Text, nullable=True)
    zodiac_info = Column(Text, nullable=True)
    houses_info = Column(Text, nullable=True)


DATABASE_URL = "postgresql://jyotish:P6SSw0RdJyot1_sh@109.205.180.137:5432/jyotish"

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()
