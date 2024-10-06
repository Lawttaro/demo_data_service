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


class predictions(Base):
    __tablename__ = 'predictions'
    
    coin = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    day_pred_1 = Column(Float)
    day_pred_2 = Column(Float)
    day_pred_3 = Column(Float)
    day_pred_4 = Column(Float)
    day_pred_5 = Column(Float)
    day_pred_6 = Column(Float)
    day_pred_7 = Column(Float)
    
    __table_args__ = (
        PrimaryKeyConstraint('coin', 'date', name='predictions_pkey'),
    )