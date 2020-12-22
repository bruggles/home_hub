#! /usr/bin/python3

import os, sys, subprocess, time
from dotenv import load_dotenv
from time import sleep
import RPi.GPIO as GPIO
repo_dir = '/home/pi/repos/home_hub'
app_contents = os.path.abspath(os.path.join(repo_dir, 'flask_app/app_contents'))
sys.path.append(app_contents)
from functions import text_send

load_dotenv(os.path.join(repo_dir,'vars.env'))

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
pins = []
for pin in os.environ.get('GARAGE_SENSORS').split(','):
    pins.append(int(pin))
pin_map = {0:'A',1:'B'}
signal_times = [10,30,60] #send messages at these specific times 10,30,60
signal_mult = 120 #send messages at any multiple of this time 120
garage_nums_text = os.environ.get('GARAGE_NUMS')
garage_nums = []
for phone_num in garage_nums_text.split(','):
    garage_nums.append(phone_num)
    text_send(body='It looks like Home Hub was restarted', to=phone_num)
for pin in pins:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

change_time = [0,0]
pin_state = [0,0]
old_pin_state = [0,0]
last_message_sent = [0,0]
#0 = closed and 1 = open
while 1:
    state = ''
    for num, pin in enumerate(pins):
        open_time_mins = int(time.time()/60 - change_time[num]/60)
        pin_state[num] = GPIO.input(pin)
        state = state + str(pin_state[num]) + ','
        if pin_state[num] == 1 and pin_state[num] != old_pin_state[num]:
            change_time[num] = int(time.time())
            #print("opened at %s" % change_time[num])
        elif pin_state[num] == 0 and pin_state[num] != old_pin_state[num]:
            #print("closed at %s" % int(time.time()))
            change_time[num] = 0
            if last_message_sent[num] != 0:
            #send closed message
                message = 'Garage door %s is now closed :-)' %  pin_map[num].upper()
                for phone_num in garage_nums:
                    text_send(body=message,to=phone_num)
                last_message_sent[num] = 0
        elif change_time[num] != 0 and (open_time_mins in signal_times\
            or (open_time_mins%signal_mult == 0 and open_time_mins !=0)) and last_message_sent[num] != open_time_mins:
            #send open message
            message = 'Garage door %s has been open for %s minutes' % (pin_map[num].upper(), open_time_mins) 
            for phone_num in garage_nums:
                text_send(body=message,to=phone_num)
            last_message_sent[num] = open_time_mins
        old_pin_state[num] = pin_state[num]
        #print("state: %s change time: %s open time mins: %s last message sent: %s divided into: %s" % (pin_state[num],change_time[num], open_time_mins, last_message_sent[num],open_time_mins%signal_mult))
    sub_list = ['ssh',os.environ.get('MAIN_ADDR'), 'echo', state, '>', '/home/pi/repos/home_hub/remote/garage_state.txt']
    #print("state: %s change time: %s open time mins: %s last message sent: %s divided into: %s" % (state,change_time[num], open_time_mins, last_message_sent[num],open_time_mins%signal_mult))
    subprocess.run(sub_list)
    sleep(15)
