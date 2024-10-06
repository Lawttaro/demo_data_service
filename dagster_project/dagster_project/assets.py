from dagster import asset, Output
from datetime import timedelta
import pandas as pd

from .resources import get_coin_data, parse_coin_data, save_coin_data_to_db, get_coin_data_from_db, save_prediction_in_db
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
def train_model(get_data_from_db):
    df = get_data_from_db
    features_manager = FeaturesManager(df)
    
    # Step 1: Reshape the data for prediction
    features_manager.reshape_df_for_prediction()
    
    # Step 2: Apply feature scaling
    features_manager.add_feature_scaling()
    
    # Step 3: Add time-based features
    df = features_manager.add_time_features()
    
    # Drop rows with missing data
    df = df.dropna()
    
    # Prepare the feature set X and target variable y
    X = df[[f'price_t-{i}' for i in range(1, 8)]]
    y = df['target']
    
    # Step 4: Train the model
    model = features_manager.lineal_regression(X, y)
    
    # Return the trained model
    return Output(model)


@asset(io_manager_key="fs_io_manager")
def generate_predictions(train_model, get_data_from_db):
    # Step 1: Load the trained model from the previous asset
    model = train_model
    
    # Step 2: Load the most recent data for prediction
    df = get_data_from_db
    features_manager = FeaturesManager(df)
    
    features_manager.reshape_df_for_prediction()
    df = features_manager.df
    
    # Get the last 7 days of data to make predictions
    latest_data = df.sort_values(by=['coin', 'date']).groupby('coin').tail(7)
    
    X_pred = latest_data[[f'price_t-{i}' for i in range(1, 8)]]
    
    # Step 3: Generate predictions using the model
    predictions = model.predict(X_pred)
    
    # Add predictions to the DataFrame
    latest_data['predictions'] = predictions
    
    return Output(latest_data, metadata={"predicted_rows": len(latest_data)})


@asset(io_manager_key="fs_io_manager")
def save_predictions(generate_predictions):
    # Step 1: Load the predicted data from the previous asset
    predicted_df = generate_predictions
    
    save_prediction_in_db(predicted_df) 
    # Step 2: Save the predictions (this could be to a database, CSV, etc.)
    # For example, saving to a CSV:
#    predicted_df.to_csv("predicted_prices.csv", index=False)
    
    return Output(None, metadata={"data_saved": "predictions_table"})
