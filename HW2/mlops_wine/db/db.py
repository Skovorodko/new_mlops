import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class DB:
    session = None

    def __init__(self):
        self.session = self.get_session()

    @property
    def engine(self):
        return create_engine(self.URL)

    def get_session(self):
        if self.session is not None:
            return self.session

        self.session = sessionmaker(self.engine)()
        return self.session

    @property
    def URL(self) -> str:
        return "postgresql+psycopg2://{}:{}@{}:5432/{}".format(
            settings.POSTGRES_USER,
            settings.POSTGRES_PASSWORD,
            settings.POSTGRES_HOST,
            settings.POSTGRES_DB
        )
