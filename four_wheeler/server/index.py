from handGesture import hand
import cv2
import sys
import json
import pika


def send_data(channel, data):
    channel.basic_publish(exchange='',
                          routing_key='hand_gesture_data',
                          body=json.dumps(data))


credentials = pika.PlainCredentials('anish', 'dotmail123')
connection = pika.BlockingConnection(
    pika.ConnectionParameters('172.19.0.2',
                              5672,
                              '/',
                              credentials))
channel = connection.channel()

channel.queue_declare(queue='hand_gesture_data')

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
        if data["right"]:
            x0, x1 = data["right"][0][0], data["right"][12][0]
            y0, y1 = data["right"][0][1], data["right"][12][1]

            # circle shape x and y axis point
            cv2.circle(img, (x0, y0), 8, (0, 255, 0), cv2.FILLED)
            cv2.circle(img, (x1, y1), 8, (0, 255, 0), cv2.FILLED)

            # line between the two points
            cv2.line(img, (x0, y0), (x1, y1), (255, 255, 255), 2)
            # cv2.circle(img, (data["right"][4][0], data["right"][4][1]),
            #            8, (0, 255, 0), cv2.FILLED)
            # cv2.circle(img, (data["right"][8][0], data["right"][8][1]),
            #            8, (0, 255, 0), cv2.FILLED)
            # if data["right"][12][1] < data["right"][11][1]:
            #     # lines for the eache shape in rgb
            #     cv2.line(img, (data["right"][4][0], data["right"][4][1]),
            #              (data["right"][8][0], data["right"][8][1]), (0, 0, 0), 2)
            # else:
            #     # lines for the eache shape in rgb
            #     cv2.line(img, (data["right"][4][0], data["right"][4][1]),
            #              (data["right"][8][0], data["right"][8][1]), (255, 255, 255), 2)
                
        # if data["left"]:
        #     cv2.circle(img, (data["left"][4][0], data["left"][4][1]),
        #                    8, (0, 255, 0), cv2.FILLED)
        #     cv2.circle(img, (data["left"][8][0], data["left"][8][1]),
        #                    8, (0, 255, 0), cv2.FILLED)
        #     if data["left"][4][0] < data["left"][8][0]:
        #         # lines for the eache shape in rgb
        #         cv2.line(img, (data["left"][4][0], data["left"][4][1]),
        #                  (data["left"][8][0], data["left"][8][1]), (0, 0, 0), 2)
        #     elif data["left"][4][0] > data["left"][8][0]:
        #         # lines for the eache shape in rgb
        #         cv2.line(img, (data["left"][4][0], data["left"][4][1]),
        #                  (data["left"][8][0], data["left"][8][1]), (255, 255, 255), 2)
                
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
