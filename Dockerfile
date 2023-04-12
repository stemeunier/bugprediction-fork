FROM python:3.10-slim

RUN useradd --create-home --shell /bin/bash optittm-user

WORKDIR /home/optittm-user

COPY requirements.txt ./

RUN apt-get -y update && apt-get install -y git openjdk-11-jre php-cli

RUN python -m pip install -r requirements.txt

USER optittm-user

COPY --chown=optittm-user . .

ENTRYPOINT ["python", "main.py"]