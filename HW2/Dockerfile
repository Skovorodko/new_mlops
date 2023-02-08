FROM python:3.11

WORKDIR /usr/src/app

COPY poetry.lock pyproject.toml .env.shared run.sh .
RUN pip3 install poetry && poetry install

COPY mlops_wine /usr/src/app/mlops_wine
RUN chmod -R 777 /usr/src/app/


ENV RUNTIME_DOCKER 1

EXPOSE 5000

CMD poetry run python3 ./mlops_wine/app.py
