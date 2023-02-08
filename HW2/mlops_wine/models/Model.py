import pickle

import pandas as pd
from sklearn.linear_model import LinearRegression, Ridge


class Model():
    def __init__(self, id_model, type_model, x_cols, y_col):
        self.id_model = id_model
        self.type_model = type_model
        self.models = self._get_model(type_model)
        self.x_cols = x_cols
        self.y_col = y_col

    def data_preprocessing(self, path, target_variable):
        df = pd.read_csv(path)
        x = df.drop(columns=[target_variable])
        y = df[target_variable]
        return x, y

    def fit(self, data, params_model):
        if params_model is not None:
            self.models.set_params(**params_model)
        dx = data[self.y_col]
        dy = data[data.columns.difference([self.y_col])]

        self.models.fit(X=dy, y=dx)

    def predict(self, df):
        # Use dy for prediction
        dy = df[df.columns.difference(self.y_col)]
        y_pred = self.model.predict(dy)
        return y_pred

    def load(self, path):
        with open(path, 'rb') as f:
            self.model, self.y_col = pickle.load(f)
        self.fit_status = True

    def model_saving(self, path):
        with open(path, 'wb') as f:
            pickle.dump((self.model, self.y_col), f)

    def _get_model(model_type: str):
        match model_type:
            case 'Ridge':
                return Ridge()
            case 'LinearRegression':
                return LinearRegression()
            case _:
                raise ValueError(f'Unknown model type: {model_type}')
