#!/usr/bin/env python
import asyncio
import sys
import RPi.GPIO as GPIO
from time import sleep
import pika
import json
import threading
import math

channel = [16,20,21]

# for board setting
GPIO.setmode(GPIO.BCM)

# setup to pin mode
for i in channel:
    GPIO.setup(i, GPIO.OUT)


#rgb in pwm mode in a list
rgbcolor= [GPIO.PWM(c,100) for c in channel]

# start the birghtness with 100
for i in range(len(rgbcolor)):
    rgbcolor[i].start(100)

def findPercents(inp, mi, ma, v):
    va = (inp - mi) * 100 / (ma - mi)
    if v == 100:
        va = v - va
    if va > 100:
        return 100
    elif va < 0:
        return 0
    else:
        return int(va)


def AccelerationOperation(rightHand):
    try:
        if len(rightHand) > 0:
            x0, x1 = rightHand[0][0], rightHand[12][0]
            y0, y1 = rightHand[0][1], rightHand[12][1]
            x3, x4 = rightHand[3][0], rightHand[4][0]
            acc = findPercents(
                math.hypot(x0-x1, y0-y1), 50, 140, 0)
            # accleration speed start
            motorDriver1_1.start(acc)
            motorDriver1_2.start(acc)
            motorDriver2_1.start(acc)
            motorDriver2_2.start(acc)
            # neutral Acceleration
            if acc > 0:
                angle = abs(math.atan2(y1 - y0, x1 - x0) * 180 / math.pi)
                print(angle)
                if angle < 60:
                    GPIO.output(13, 0)
                    GPIO.output(19, 0)
                    GPIO.output(5, 1)
                    GPIO.output(6, 0)
                    GPIO.output(27, 1)
                    GPIO.output(22, 0)
                    GPIO.output(10, 0)
                    GPIO.output(9, 0)
                elif angle > 120:
                    GPIO.output(13, 1)
                    GPIO.output(19, 0)
                    GPIO.output(5, 0)
                    GPIO.output(6, 0)
                    GPIO.output(27, 0)
                    GPIO.output(22, 0)
                    GPIO.output(10, 1)
                    GPIO.output(9, 0)
                else:
                    if x3 > x4:
                        print("direction back")
                        GPIO.output(13, 0)
                        GPIO.output(19, 1)
                        GPIO.output(5, 0)
                        GPIO.output(6, 1)
                        GPIO.output(27, 0)
                        GPIO.output(22, 1)
                        GPIO.output(10, 0)
                        GPIO.output(9, 1)
                    else:  # forward Acceleration
                        print("direction front")
                        GPIO.output(13, 1)
                        GPIO.output(19, 0)
                        GPIO.output(5, 1)
                        GPIO.output(6, 0)
                        GPIO.output(27, 1)
                        GPIO.output(22, 0)
                        GPIO.output(10, 1)
                        GPIO.output(9, 0)

            else:
                GPIO.output(13, 0)
                GPIO.output(19, 0)
                GPIO.output(5, 0)
                GPIO.output(6, 0)
                GPIO.output(27, 0)
                GPIO.output(22, 0)
                GPIO.output(10, 0)
                GPIO.output(9, 0)
            print("Acceleration:", acc)
        else:
            motorDriver1_1.start(0)
            motorDriver1_2.start(0)
            motorDriver2_1.start(0)
            motorDriver2_2.start(0)
            GPIO.output(13, 0)
            GPIO.output(19, 0)
            GPIO.output(5, 0)
            GPIO.output(6, 0)
            GPIO.output(27, 0)
            GPIO.output(22, 0)
            GPIO.output(10, 0)
            GPIO.output(9, 0)
    except KeyboardInterrupt:
        print("Force exit operation")
        motorDriver1_1.start(0)
        motorDriver1_2.start(0)
        motorDriver2_1.start(0)
        motorDriver2_2.start(0)
        GPIO.output(13, 0)
        GPIO.output(19, 0)
        GPIO.output(5, 0)
        GPIO.output(6, 0)
        GPIO.output(27, 0)
        GPIO.output(22, 0)
        GPIO.output(10, 0)
        GPIO.output(9, 0)
        sys.exit()


def AccessingTheGPIO(handData):
    # print(handData, width, height)
    rightHand = handData["right"]

    # Acceleration threading
    if len(rightHand) > 0:
        rightThread = threading.Thread(
            target=AccelerationOperation, args=(rightHand,)
        )
        # after defineing the thread model we need to start the thread
        rightThread.start()
    else:
        motorDriver1_1.start(0)
        motorDriver1_2.start(0)
        motorDriver2_1.start(0)
        motorDriver2_2.start(0)
        GPIO.output(13, 0)
        GPIO.output(19, 0)
        GPIO.output(5, 0)
        GPIO.output(6, 0)
        GPIO.output(27, 0)
        GPIO.output(22, 0)
        GPIO.output(10, 0)
        GPIO.output(9, 0)
# RabbitMQ receiveing data


def callback(ch, method, properties, body):
    data = json.loads(body)
    landmarks = data
    # print(landmarks)  # Replace this with your own processing code
    GPIOthread = threading.Thread(
        target=AccessingTheGPIO, args=(landmarks,))
    GPIOthread.start()


if __name__ == "__main__":
    cred = pika.PlainCredentials('anish', 'dotmail123')
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='172.19.0.2', port=5672, virtual_host='/', credentials=cred))
    channel = connection.channel()

    channel.queue_declare(queue='hand_gesture_data')

    channel.basic_consume(queue='hand_gesture_data',
                          on_message_callback=callback, auto_ack=True)

    print('Waiting for hand gesture data. To exit press CTRL+C')
    channel.start_consuming()
