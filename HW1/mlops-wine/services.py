import pickle
import settings
import pandas as pd


class Dataset:
    def __init__(self, file_path, sepparator=";"):
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

    def get_models(self) -> list[str]:
        ignore = [".gitkeep"]

        models = [model.name for model in self.MODELS_PATH.iterdir()]
        filtered_models = list(filter(lambda x: x not in ignore, models))

        return filtered_models

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


def read_models_list():
    storage = ModelsStorage()
    models = {}

    for model_name in storage.get_models():
        model = storage.load_model(model_name)
        models[model_name] = {
            "type_model": model.type_m,
            "fitted": model.fit_status,
            "accur_train": model.score_train if model.fit_status else None,
            "accur_test": model.score_test if model.test_score else None,
        }

    return models
