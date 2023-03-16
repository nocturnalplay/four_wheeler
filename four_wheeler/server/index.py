from handGesture import hand
import cv2
import sys
import json
import pika
from data import serverdata as env
import math

# banner for our tool


def Banner():
    print("""                                                            
 (                                 )            (             
 )\ )         (   (     (  (    ( /(    (    (  )\   (   (    
(()/(   (    ))\  )(    )\))(   )\())  ))\  ))\((_) ))\  )(   
 /(_))  )\  /((_)(()\  ((_)()\ ((_)\  /((_)/((_)_  /((_)(()\  
(_) _| ((_)(_))(  ((_) _(()((_)| |(_)(_)) (_)) | |(_))   ((_) 
 |  _|/ _ \| || || '_| \ V  V /| ' \ / -_)/ -_)| |/ -_) | '_| 
 |_|  \___/ \_,_||_|    \_/\_/ |_||_|\___|\___||_|\___| |_|    """)

# send's the message to the RabbitMQ server


def send_data(channel, data):
    channel.basic_publish(exchange='',
                          routing_key='hand_gesture_data',
                          body=json.dumps(data))

# car controle function


def Ailoop(inp):
    try:
        hands = hand.Hand(max_hands=1)
        cap = cv2.VideoCapture(0)

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("Can't receive frame (stream end?). Exiting ...")
                break
            res = hand.DetectHands(frame, hands)
            if not res['status']:
                break

            img = res["image"]
            data = res["data"]
            print(data)
            send_data(channel, res["data"])
            # Display the resulting image
            # circle shape x and y axis point
            right = data["right"]
            if right:
                if inp == 1:
                    Car(right, img)
                elif inp == 2:
                    RGB(right, img)

            cv2.imshow('Hand Gestures', img)
            if cv2.waitKey(1) == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
        sys.exit()
    except KeyboardInterrupt:
        print("Force exit operation")
        cap.release()
        cv2.destroyAllWindows()
        sys.exit()
    except Exception as e:
        print(e)
        cap.release()
        cv2.destroyAllWindows()
        sys.exit()

# car control


def Car(right, img):
    print("Car control using Hand Gesture")
    x0, x1 = right[0][0], right[12][0]
    y0, y1 = right[0][1], right[12][1]
    x3, x4 = right[3][0], right[4][0]
    angle = abs(math.atan2(y1 - y0, x1 - x0) * 180 / math.pi)
    if angle < 60:
        cv2.putText(img, "left direction", (30, 40),
                    cv2.FONT_HERSHEY_PLAIN, 2, (50, 255, 0), 2)
    elif angle > 120:
        cv2.putText(img, "right direction", (30, 40),
                    cv2.FONT_HERSHEY_PLAIN, 2, (50, 255, 0), 2)
    else:
        if x3 > x4:
            cv2.putText(img, "forward direction", (30, 40),
                        cv2.FONT_HERSHEY_PLAIN, 2, (50, 255, 0), 2)
        else:
            cv2.putText(img, "backward direction", (30, 40),
                        cv2.FONT_HERSHEY_PLAIN, 2, (50, 255, 0), 2)
    # circle shape x and y axis point
    cv2.circle(img, (x0, y0), 8, (0, 255, 0), cv2.FILLED)
    cv2.circle(img, (x1, y1), 8, (0, 255, 0), cv2.FILLED)
    # line between the two points
    cv2.line(img, (x0, y0), (x1, y1), (255, 255, 255), 2)

# rgb light control


def RGB(right,img):
    print("RGB Effect like Doctor Strange")
    # rgb x and y axis point
    x0, y0 = right[0][0], right[0][1]
    rx, ry = right[4][0], right[4][1]
    gx, gy = right[8][0], right[8][1]
    bx, by = right[12][0], right[12][1]

    # circle shape x and y axis point
    cv2.circle(img, (rx, ry), 8, (0, 0, 255), cv2.FILLED)
    cv2.circle(img, (gx, gy), 8, (0, 255, 0), cv2.FILLED)
    cv2.circle(img, (bx, by), 8, (255, 0, 0), cv2.FILLED)

     # lines for the eache shape in rgb
    cv2.line(img, (x0, y0), (rx, ry), (0, 0, 255), 2)
    cv2.line(img, (x0, y0), (gx, gy), (0, 255, 0), 2)
    cv2.line(img, (x0, y0), (bx, by), (255, 0, 0), 2)
    # connect in bellow bottom point of index 0
    cv2.circle(img, (x0, y0), 8, (255, 255, 255), cv2.FILLED)


if __name__ == "__main__":
    # build the connection to the RabbitMQ server
    credentials = pika.PlainCredentials(env.username, env.password)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(env.ipaddress,
                                  env.port,
                                  '/',
                                  credentials))
    channel = connection.channel()
    channel.queue_declare(queue='hand_gesture_data')

    # show the banner of out tool
    Banner()
    print("""
[1] Car control
[2] RGB light control
[0] Quit
    """)
    inp = int(input(">"))

    if inp == 0:
        sys.exit(0)
    else:
        Ailoop(inp)
