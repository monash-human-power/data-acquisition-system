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

# Make Python search for modules in the home directory as well
# This is because we cannot mount our `mhp` repository inside the mounted /boost folder as this
# would create a mhp folder on the host boost/ folder as well. So we mount it in home directory and make python search for modules in that directory as well.
RUN touch paths.pth
RUN echo "/root" > paths.pth

RUN eval 'cp ./paths.pth $(python -c "import sys; print(sys.path[-1])")'