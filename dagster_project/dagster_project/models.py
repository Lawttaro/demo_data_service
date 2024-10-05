from sqlalchemy import Column, String, Integer, Float, Date, JSON, PrimaryKeyConstraint
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class CoinData(Base):
    __tablename__ = 'coin_data'
    
    coin = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    price = Column(Float)
    json = Column(JSON)
    
    __table_args__ = (
        PrimaryKeyConstraint('coin', 'date', name='coin_data_pkey'),
    )


class CoinMonthData(Base):
    __tablename__ = 'coin_month_data'
    
    coin = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    min_price = Column(Float)
    max_price = Column(Float)
    
    __table_args__ = (
        PrimaryKeyConstraint('coin', 'year', 'month', name='coin_month_data_pkey'),
    )
