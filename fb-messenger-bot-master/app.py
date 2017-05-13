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

                            elif not pickedAsked:
                                pickedLat = lat
                                pickedLong = long
                                pickedAsked = True

        if not destAsked:
            query_location(sender_id, "Hi! Where would you like to go?")

        elif not pickedAsked:
            query_location(sender_id, "Where do you want to be picked up?")

        elif not routeCalculated:
            final = text(sender_id, "Calculating route...")
            send_message(sender_id, final)
            r = requests.get("http://ec2-204-236-212-212.compute-1.amazonaws.com:43001/")

            test = text(sender_id, r.json()["result"])
            send_message(sender_id, test)
            routeCalculated = True

    return "ok", 200


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
