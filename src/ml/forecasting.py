from sklearn.linear_model import LinearRegression
import joblib
from .preprocess import clean, normalize, train_test_split
from .config import FORECAST_MODEL

def train_forecast(df, target):
    df = normalize(clean(df))

    X = df.drop(columns=[target])
    y = df[target]

    train_X, test_X = train_test_split(X)
    train_y, test_y = train_test_split(y)

    model = LinearRegression()
    model.fit(train_X, train_y)

    joblib.dump(model, FORECAST_MODEL)
    return model

def predict_future(model, df):
    df = normalize(clean(df))
    return model.predict(df)
