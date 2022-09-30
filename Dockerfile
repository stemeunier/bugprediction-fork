FROM python:3.10-slim

RUN useradd --create-home --shell /bin/bash optittm-user

WORKDIR /home/optittm-user

COPY requirements.txt ./

RUN apt-get -y update && apt-get install -y git openjdk-11-jre

RUN python -m pip install -r requirements.txt

USER optittm-user

COPY . .

ENTRYPOINT ["python", "main.py"]