#! /usr/bin/python3

import os, sys
from dotenv import load_dotenv
from time import sleep
import RPi.GPIO as GPIO
remote = os.path.abspath(os.path.dirname(__file__))
repo_dir = os.path.abspath(os.path.join(remote, '../'))

load_dotenv(os.path.join(repo_dir,'vars.env'))

try:
    arg = sys.argv[1].lower()
except:
    arg = None

safety_relay_no_pin = int(os.environ.get('RELAY_SAFETY_NO'))
safety_relay_nc_pin = int(os.environ.get('RELAY_SAFETY_NC'))

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(safety_relay_no_pin, GPIO.OUT)
GPIO.output(safety_relay_no_pin, 1)
GPIO.setup(safety_relay_nc_pin, GPIO.OUT)
GPIO.output(safety_relay_nc_pin, 0)

garage_doors = []
for garage_door in os.environ.get('GARAGE_ACTS').split(','):
    garage_doors.append(int(garage_door))

if arg == 'a':
    garage_pin = garage_doors[0]
    delay = .25
elif arg == 'b':
    garage_pin = garage_doors[1]
    delay = .25

GPIO.setup(garage_pin, GPIO.OUT)
GPIO.output(garage_pin, 1)
sleep(delay)
GPIO.output(garage_pin, 0)
