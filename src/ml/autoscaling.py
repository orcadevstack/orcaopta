from sklearn.ensemble import RandomForestClassifier
import joblib
from .preprocess import clean, normalize, train_test_split
from .config import AUTOSCALE_MODEL

def train_autoscaler(df, target="scale"):
    df = normalize(clean(df))

    X = df.drop(columns=[target])
    y = df[target]

    train_X, test_X = train_test_split(X)
    train_y, test_y = train_test_split(y)

    model = RandomForestClassifier()
    model.fit(train_X, train_y)

    joblib.dump(model, AUTOSCALE_MODEL)
    return model

def autoscale_decision(model, df):
    df = normalize(clean(df))
    return model.predict(df)
