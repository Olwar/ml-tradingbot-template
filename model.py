import sqlite3
import pandas as pd
from sklearn.preprocessing import StandardScaler
from pickle import load

def train_model():
    # Connecting to the sqlite database
    conn = sqlite3.connect('crypto_database.sqlite')
    cur = conn.cursor()
    df = pd.read_sql_query("SELECT * from prices", conn)

    # Making lagged features
    def make_lags(name, feature, lags):
        return pd.concat(
        {
            f'{name}_lag_{i}': feature.shift(i)
            for i in range(1, lags + 1)
        },
        axis = 1)

    df = df.join(make_lags("macd", df.macd, lags=10))
    df = df.join(make_lags("macdsig", df.macdsig, lags=10))
    df = df.join(make_lags("macdhis", df.macdhis, lags=10))
    df = df.join(make_lags("rsi", df.rsi, lags=10))
    df = df.join(make_lags("slowd", df.slowd, lags=10))
    df = df.join(make_lags("slowk", df.slowk, lags=10))

    # Dropping missing values
    df.dropna()
    X = df.drop(["target", "date", "id", "close", "low", "high"], axis=1)
    
    # Loading the pretrained Machine Learning models and scalers
    short_model = load(open('model_short.pkl', 'rb'))
    short_scaler = load(open('scaler_short.pkl', 'rb'))

    short_X_scaled = short_scaler.transform(X)
    short_y_pred = short_model.predict(short_X_scaled) > 0.5
    short_target = short_y_pred[-1][0]

    long_model = load(open('model_long.pkl', 'rb'))
    long_scaler = load(open('scaler_long.pkl', 'rb'))

    # Predicting whether to long, short or do nothing
    long_X_scaled = long_scaler.transform(X)
    long_y_pred = long_model.predict(long_X_scaled) > 0.5
    long_target = long_y_pred[-1][0]

    # Returning 1 for shorting, 1 for longing and 0 for doing nothing
    return (short_target, long_target)

train_model()
