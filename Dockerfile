FROM python:3.9

RUN apt update && apt install -y cron

RUN python -m pip install requests Telegram python-telegram-bot

COPY . /app

WORKDIR /app

RUN chmod 755 *

CMD [ "/bin/bash", "entrypoint.sh" ]