import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error


class FeaturesManager:

    def __init__(self, df):
        self.df = df

    def reshape_df_for_prediction(self):

        self.df = self.df.sort_values(by=['coin', 'date'])
        self.df['target'] = self.df.groupby('coin')['price'].shift(-1)

        for i in range(1, 8):
            self.df[f'price_t-{i}'] = self.df.groupby('coin')['price'].shift(i)

        self.df = self.df.dropna(subset=[f'price_t-{i}' for i in range(1, 8)] + ['target'])

    def add_feature_scaling(self):
        scaler = StandardScaler()
        columns_to_scale = [f'price_t-{i}' for i in range(1, 8)] + ['target']
        scaled_features = scaler.fit_transform(self.df[columns_to_scale])
        self.df[columns_to_scale] = scaled_features

    def add_time_features(self):
        self.df['date'] = pd.to_datetime(self.df['date'], errors='coerce')
        self.df['day_of_week'] = self.df['date'].dt.dayofweek
        self.df['is_weekend'] = self.df['day_of_week'].isin([5, 6]).astype(int)
        self.df['week_of_year'] = self.df['date'].dt.isocalendar().week
        self.df['month'] = self.df['date'].dt.month
        return self.df

    def lineal_regression(self, X, y):
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        model = LinearRegression()
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)

        mse = mean_squared_error(y_test, y_pred)
        return model
        print(f"Mean Squared Error: {mse}")
