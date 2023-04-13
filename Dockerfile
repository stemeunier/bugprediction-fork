FROM python:3.10-slim

RUN useradd --create-home --shell /bin/bash optittm-user

WORKDIR /home/optittm-user

COPY requirements.txt ./

RUN apt-get -y update
# Install Git and Java executables
RUN apt-get install -y git openjdk-11-jre
# Install PHP executable and dependency for PDepend
RUN apt-get install -y php-cli php-xml

RUN python -m pip install -r requirements.txt

USER optittm-user

COPY --chown=optittm-user . .

ENTRYPOINT ["python", "main.py"]