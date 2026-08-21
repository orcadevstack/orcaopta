from sklearn.tree import DecisionTreeRegressor
import joblib
from .preprocess import clean, normalize, train_test_split
from .config import RESOURCE_MODEL

def train_resource_optimizer(df, target):
    df = normalize(clean(df))

    X = df.drop(columns=[target])
    y = df[target]

    train_X, test_X = train_test_split(X)
    train_y, test_y = train_test_split(y)

    model = DecisionTreeRegressor()
    model.fit(train_X, train_y)

    joblib.dump(model, RESOURCE_MODEL)
    return model

def optimize_resources(model, df):
    df = normalize(clean(df))
    return model.predict(df)
