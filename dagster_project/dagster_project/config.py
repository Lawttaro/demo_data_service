from dagster import Config

class CoinFilter(Config):
    coin_id: str = 'bitcoin'
    start_date: str = '2022-09-01'
    end_date: str = ''