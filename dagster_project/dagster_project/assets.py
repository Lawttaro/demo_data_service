from dagster import asset, Output
from datetime import timedelta
import pandas as pd

from .resources import get_coin_data, parse_coin_data, save_coin_data_to_db, get_coin_data_from_db
from .feautres import FeaturesManager

@asset(
        io_manager_key="fs_io_manager")
def get_raw_data():
    data, date = get_coin_data("bitcoin", 1)
    result = {
        "data": data,
        "date": date
    }
    return result
    # Return date as a separate output

@asset(io_manager_key="fs_io_manager")
def procces_data(get_raw_data):
    data = get_raw_data.get('data')
    date = get_raw_data.get('date')
    data_parsed, date = parse_coin_data(data, date)
    result = {
        "data": data_parsed,
        "date": date,
    }
    return result

@asset(io_manager_key="fs_io_manager")
def save_data_to_db(procces_data):
    res_db = save_coin_data_to_db(procces_data)


@asset(io_manager_key="fs_io_manager")
def get_data_from_db():
    data = get_coin_data_from_db()
    return data


@asset(io_manager_key="fs_io_manager")
def get_model(get_data_from_db):
    df = get_data_from_db
    features_manager = FeaturesManager(df)
    features_manager.reshape_df_for_prediction()
    features_manager.add_feature_scaling()
    df = features_manager.add_time_features()
    df = df.dropna()
    X = df[[f'price_t-{i}' for i in range(1, 8)]]
    y = df['target']
    model = features_manager.lineal_regression(X, y)
    return Output(model)



@asset(io_manager_key="fs_io_manager")
def predict_next_weekend(get_model, get_data_from_db):
    # Step 1: Load the trained model from the 'get_model' asset
    model = get_model

    # Step 2: Load the data and prepare the features for prediction
    df = get_data_from_db
    features_manager = FeaturesManager(df)
    features_manager.reshape_df_for_prediction()  # Ensure dataframe is prepared

    # Step 3: Get the latest data for prediction
    # Assuming you want to predict the next weekend based on the last 7 days of price data for each coin
    latest_data = df.sort_values(by=['coin', 'date']).groupby('coin').tail(7)

    # Ensure we have the correct columns for prediction (price_t-1, price_t-2, ..., price_t-7)
    X_pred = latest_data[[f'price_t-{i}' for i in range(1, 8)]]

    # Step 4: Predict the next price (for the weekend)
    next_weekend_predictions = model.predict(X_pred)

    # Step 5: Prepare the dates for next weekend (Saturday and Sunday)
    today = pd.Timestamp.today()
    next_saturday = today + timedelta((5 - today.weekday()) % 7)
    next_sunday = next_saturday + timedelta(1)

    # Step 6: Combine predictions with coin and date
    predictions_df = latest_data[['coin']].copy()
    predictions_df['predicted_price_saturday'] = next_weekend_predictions[::2]  # Even indices for Saturday
    predictions_df['predicted_price_sunday'] = next_weekend_predictions[1::2]   # Odd indices for Sunday
    predictions_df['predicted_date_saturday'] = next_saturday
    predictions_df['predicted_date_sunday'] = next_sunday

    # Step 7: Return the prediction dataframe (or store it, depending on your pipeline)
    return Output(predictions_df, metadata={"predicted_saturday": next_saturday, "predicted_sunday": next_sunday})
