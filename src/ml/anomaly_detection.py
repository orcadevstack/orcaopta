from sklearn.ensemble import IsolationForest
import joblib
from .preprocess import clean, normalize, train_test_split
from .config import ANOMALY_MODEL

def train_anomaly(df):
    df = normalize(clean(df))
    train, test = train_test_split(df)

    model = IsolationForest(contamination=0.05)
    model.fit(train)

    joblib.dump(model, ANOMALY_MODEL)
    return model

def predict_anomaly(model, df):
    df = normalize(clean(df))
    return model.predict(df)
