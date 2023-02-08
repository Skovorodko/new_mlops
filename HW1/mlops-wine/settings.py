import os
from pathlib import Path

from dotenv import dotenv_values
from helpers import str2bool

config = {
    **dotenv_values(".env.shared"),  # load shared development variables
    **dotenv_values(".env.secret"),  # load sensitive variables
    **os.environ,  # override loaded values with environment variables
}

env = config.get

BASE_DIR = Path(__file__).resolve().parent
STORAGE_PATH = BASE_DIR / "storage"
DATASET_PATH = BASE_DIR / env("DATASET_PATH", "storage/datasets/dataset.csv")

DEBUG = str2bool(env("DEBUG", False))
APP_HOST = env("APP_HOST", "127.0.0.1")
APP_PORT = int(env("APP_PORT", 5000))

MAX_MODELS = int(env("MAX_MODELS", 10))
