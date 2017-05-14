import os
import sys
import json

import requests
from flask import Flask, request

app = Flask(__name__)

destAsked = False
pickedAsked = False
routeCalculated = False

destLat = 0
destLong = 0
pickedLat = 0
pickedLong = 0

@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world", 200


@app.route('/', methods=['POST'])
def webhook():

    # endpoint for processing incoming messaging events

    data = request.get_json()
    log(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":

        global destAsked
        global pickedAsked
        global destLat
        global destLong
        global pickedLat
        global pickedLong
        global routeCalculated

        if 'message' in data['entry'][0]['messaging'][0]:
            entry = data["entry"][0]["messaging"][0]
            sender_id = entry["sender"]["id"] # the facebook ID of the person sending you the message

            if entry.get("message"):  # someone sent us a message

                message = entry["message"]

                if message.get("attachments"):
                    if "payload" in message["attachments"][0]:
                        if "coordinates" in message["attachments"][0]["payload"]:
                            location = message["attachments"][0]["payload"]["coordinates"]

                            lat = location["lat"]
                            long = location["long"]

                            if not destAsked:
                                destLat = lat
                                destLong = long
                                destAsked = True

                                test1 = text(sender_id, "Got it!")
                                send_message(sender_id, test1)

                            elif not pickedAsked:
                                pickedLat = lat
                                pickedLong = long
                                pickedAsked = True

                                test2 = text(sender_id, "Thanks! Calculating Route...")
                                send_message(sender_id, test2)

        if routeCalculated:
                    final1 = text(sender_id, "You're all set! See you soon and thanks for using Find My Taxi :)")
                    send_message(sender_id, final1)

        if not destAsked:
            query_location(sender_id, "Hi! Where would you like to go?")

        elif not pickedAsked:
            query_location(sender_id, "Where do you want to be picked up?")

        elif not routeCalculated:
            final = text(sender_id, "We found a transport available for you in 12 minutes. Would you like to reserve it?")
            send_message(sender_id, final)

            headers = {"Content-type": "application/json"}
            # trajectory_info = build_route_json()
            # r = requests.post("http://ec2-204-236-212-212.compute-1.amazonaws.com:43001/start_booking", data=trajectory_info, headers=headers)

            # answer = r.json()["result"]

            # final = text(sender_id, answer)
            # send_message(sender_id, final)

            routeCalculated = True
            # hasRoute = False
#
            # if hasRoute:
            #    prompt_yesno(sender_id,
            #                 "Would you like to book the transport?",
            #                 "Your transport is reserved. Thank you for using Find My Taxi.",
            #                 "Thank you for using Find my Taxi :)")
            # else:
            #    prompt_yesno(sender_id,
            #                 "No Transport was found. Do you want to receive a notification when a transport becomes available for your route?",
            #                 "Noted! We'll notify you as soon as we have something for you",
            #                 "Thank you for using Find My Taxi :)")

    return "ok", 200


def prompt_yesno(user_id, message, ansy, ansn):
    return json.dumps({
        "recipient": {
            "id": user_id
        },
        "message": {
            "text": message,
            "quick_replies": [{
                "content_type": "text",
                "title": "Yes",
                "payload": ansy,
            },
            {
                "content_type": "text",
                "title": "No",
                "payload": ansn,
            }]
        }
    })


def build_route_json():
    # return json.dumps({
    #    "pickup": {
    #        "lat": pickedLat,
    #        "lng": pickedLong
    #    },
    #    "dropoff": {
    #        "lat": destLat,
    #        "lng": destLong
    #    }
    # })

    return json.dumps({
        "pickup": {
            "lat": 18.52184,
            "lng": -33.9464
        },
        "dropoff": {
            "lat": 18.42842,
            "lng": -33.92264
        }
    })

def query_location(user_id, question):
    aQuery = location(user_id, question)
    send_message(user_id, aQuery)


def send_message(user_id, data):
    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }

    aData = data
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=aData)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def text(user_id, message):
    return json.dumps({
        "recipient": {
            "id": user_id
        },
        "message": {
            "text": message
        }
    })


def location(user_id, question):
    return json.dumps({
        "recipient": {
            "id": user_id
        },
        "message": {
            "text": question,
            "quick_replies": [{
                "content_type": "location",
            }]
        }
    })


def log(message):  # simple wrapper for logging to stdout on heroku
    print str(message)
    sys.stdout.flush()


if __name__ == '__main__':

    global pickedAsked
    global destAsked

    pickedAsked = False
    destAsked = False

    app.run(debug=True)
