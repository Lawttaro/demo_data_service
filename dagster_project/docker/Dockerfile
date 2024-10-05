FROM python:3.10

# RUN apt-get update && apt-get install -y

WORKDIR /dagster_project

COPY setup.py .

RUN pip install scikit-learn

RUN pip install -e ".[dev]"
