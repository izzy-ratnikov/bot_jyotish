from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    Time,
    BigInteger,
    Text,
)
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class UserData(Base):
    __tablename__ = "user_data"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    telegram_id = Column(String, nullable=False)
    username = Column(String, nullable=True)
    location = Column(String, nullable=False)
    birth_date = Column(Date, nullable=False)
    birth_time = Column(Time, nullable=False)
    chart_interpretation = Column(Text, nullable=True)
    zodiac_info = Column(Text, nullable=True)
    houses_info = Column(Text, nullable=True)
    vimshottari_dasha = Column(String, nullable=False)
