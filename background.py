from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler


def print_message():
    print("dont sleep")


app = Flask(__name__)
scheduler = BackgroundScheduler()
scheduler.add_job(print_message, 'interval', minutes=1)
scheduler.start()
