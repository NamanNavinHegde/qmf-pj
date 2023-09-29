#!/usr/bin/python3.6
import test
from datetime import datetime
from time import sleep


def run(condition):
    while datetime.now().minute not in {0, 15, 30, 45}:  # Wait 1 second until we are synced up with the 'every 15 minutes' clock
        sleep(1)

    def task():
        test.writetxt()
    
    task()
    while (condition):
        sleep(60*15)  # Wait for 15 minutes
        task()


test.writetxt()
run(15)
