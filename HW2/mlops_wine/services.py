import pickle
import settings
import pandas as pd
from db import DB

db = DB()


class Dataset:
    def __init__(self, file_path, sepparator=";", mode="csv"):
        match mode:
            case "csv":
                self.data_frame = pd.read_csv(file_path, sep=sepparator)

    def get_column_title(self, idx):
        return self.data_frame.columns[idx]

    @property
    def df(self):
        return self.data_frame


class ModelsStorage():
    def __init__(self):
        self.MODELS_PATH = settings.STORAGE_PATH / "models"

    def save_model(self, model_instance, model_name=None):
        model_name = model_name or model_instance.id_model
        pickle.dump(model_instance, open(
            self.MODELS_PATH / model_name, "wb"))

    def get_models(self):
        models_sql = pd.read_sql_query(
            """
                SELECT
                "Name" as "models", "type", "Params",
                "Trained", "train_acc", "test_acc",
                "Date"
                FROM public.models;
            """,
            db.engine
        )
        db.engine.dispose()
        models_dict = models_sql.to_dict(orient='index')
        return models_dict

    def load_model(self, model_name: str):
        model = pickle.load(open(self.MODELS_PATH / model_name, "rb"))
        return model

    def delete_model(self, model_name: str) -> bool | None:
        model_path = self.MODELS_PATH / model_name
        if not model_path.exists():
            return False

        model_path.unlink()

    def model_is_exists(self, model_name: str) -> bool:
        model_path = self.MODELS_PATH / model_name
        return model_path.exists()

    def models_count(self) -> int:
        return len(self.get_models())


def get_list_models():
    list_m = pd.read_sql_query(
        """
                SELECT DISTINCT "Name"
                FROM public.models;
                """,
        db.engine
    ).Name.tolist()
    db.engine.dispose()
    return list_m
