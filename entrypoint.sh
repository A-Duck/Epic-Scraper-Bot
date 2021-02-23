#! /bin/bash -x

echo "Starting Cron Service"
service cron start

echo "Starting Epic Scraper Bot"
python Startup.py