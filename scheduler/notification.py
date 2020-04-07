import atexit

import boto3
from apscheduler.schedulers.blocking import BlockingScheduler

import time

client = boto3.client('lambda')


def invoke_send_email():
    print("invoke")
    client.invoke(
        FunctionName='arn:aws:lambda:us-east-1:253735393254:function:sendemail-dev'
    )


scheduler = BlockingScheduler()


scheduler.add_job(func=invoke_send_email,
                  trigger='interval', seconds=60*60)

scheduler.start()

atexit.register(lambda: scheduler.shutdown())
