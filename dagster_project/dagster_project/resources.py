import logging
import pandas as pd
from datetime import datetime, timedelta
from pycoingecko import CoinGeckoAPI
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

from .models import CoinData, CoinMonthData

logger = logging.getLogger(__name__)

def init_session():
    engine = create_engine('postgresql+psycopg2://postgres:postgres@postgres:5432/postgres')
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

def get_coin_data(coin, offset_days):
    # Convert ISO8601 date to dd-mm-yyyy format required by the API
    date = datetime.now() - timedelta(days=offset_days)
    formatted_date = date.strftime("%d-%m-%Y")
    cg = CoinGeckoAPI()
    try:
        data = cg.get_coin_history_by_id(coin, date=formatted_date)
        return data, date
    except Exception as e:
        logging.error(f"Failed to fetch data: {e}")
        raise


def parse_coin_data(data, date):
    ## todo convert in df foramt and return
    df = pd.DataFrame(data)
    df['usd_price'] = df['market_data']['current_price']['usd']
    return df, date 


def save_coin_data_to_db(process_data):
    session = init_session()
    df_process_data = process_data.get('data')
    date = process_data.get('date')
    for index, row in df_process_data.iterrows():
        try:
            coin_data = CoinData(
                coin=row['id'],
                price=row['usd_price'],
                date=date,
                json=row
            )
            session.add(coin_data)
            session.commit()
            logger.info(f"Data for {row['coin']} on {date} saved to the database.")
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error saving data for {row['usd_price']} on {date}: {e}")
        finally:
            session.close()
    pass


def get_coin_data_from_db():
    session = init_session()
    query = "SELECT * FROM coin_data"
    result = session.execute(query)

    # Convert the result to a Pandas DataFrame
    df = pd.DataFrame(result.fetchall(), columns=result.keys())
    return df


def save_monthly_data_to_db(process_data):
    session = init_session()
    df_process_data = process_data.get('data')
    date = process_data.get('date')
    for index, row in df_process_data.iterrows():
        try:
            coin_month_data = CoinMonthData(
                coin=row['id'],
                year=date.year,
                month=date.month,
                min_price=row['min_price'],
                max_price=row['max_price']
            )
            session.add(coin_month_data)
            session.commit()
            logger.info(f"Monthly data for {row['coin']} on {date} saved to the database.")
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error saving monthly data for {row['usd_price']} on {date}: {e}")
        finally:
            session.close()
    pass