FROM python:3.9

WORKDIR /root/DAS

COPY poetry.lock .

COPY pyproject.toml .

# Convert poetry dependencies to requirements.txt so pip can use it
RUN pip install poetry
RUN poetry export -f requirements.txt --output requirements.txt

# Remove dependency on our mhp (common reposiotry) from requirements.txt as pip cannot install repositories
RUN sed -i '/mhp/d' requirements.txt

RUN pip install -r requirements.txt