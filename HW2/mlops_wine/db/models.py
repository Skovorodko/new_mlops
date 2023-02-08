from sqlalchemy import Column, Float
from sqlalchemy.ext.declarative import declarative_base

DeclarativeBase = declarative_base()


class DatasetValuesModel(DeclarativeBase):
    __tablename__ = 'dataset'

    fixed_acidity = Column(Float)
    volatile_acidity = Column(Float)
    citric_acid = Column(Float)
    residual_sugar = Column(Float)
    chlorides = Column(Float)
    free_sulfur_dioxide = Column(Float)
    total_sulfur_dioxide = Column(Float)
    density = Column(Float)
    pH = Column(Float)
    sulphates = Column(Float)
    alcohol = Column(Float)
    quality = Column(Float)

