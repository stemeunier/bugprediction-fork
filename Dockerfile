FROM python:3.10-slim

RUN useradd --create-home --shell /bin/bash optittm-user

WORKDIR /home/optittm-user

COPY requirements.txt ./

# Install Git, Java executables, PHP executable and dependency for PDepend
RUN apt-get -y update && apt-get install -y wget git openjdk-17-jre php-cli php-xml

RUN python -m pip install -r requirements.txt

USER optittm-user

COPY --chown=optittm-user . .

ENTRYPOINT ["python", "main.py"]