FROM python:3

COPY requirements.txt /app/requirements.txt

RUN apt update && apt install -y cron

RUN python -m pip install -r /app/requirements.txt

COPY . /app

WORKDIR /app

RUN chmod 755 *

CMD [ "/bin/bash", "entrypoint.sh" ]