FROM python:3.9

WORKDIR /DAS

COPY requirements.txt .

COPY poetry.lock .

COPY pyproject.toml .

RUN pip install poetry

# RUN poetry remove mhp

# RUN poetry install

RUN pip install -r requirements.txt