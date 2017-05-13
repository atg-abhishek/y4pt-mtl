import os
import sys
import json

import requests
from flask import Flask, request

app = Flask(__name__)


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

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent us a message

                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    message_text = messaging_event["message"]["text"]  # the message's text

                    atext = text(sender_id, "Hi! Where would you like to go?")
                    aQuery = ask_location(sender_id)
                    send_message(sender_id, atext)
                    send_message(sender_id, aQuery)

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass

                if messaging_event.get("attachements"):
                    pass  # send_message(sender_id, "yoyoyo")


    return "ok", 200


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


def ask_location(user_id):
    return json.dumps({
        "recipient": {
            "id": user_id
        },
        "message": {
            "text": "Please share your location:",
            "quick_replies": [{
                "content_type": "location",
            }]
        }
    })


def log(message):  # simple wrapper for logging to stdout on heroku
    print str(message)
    sys.stdout.flush()


if __name__ == '__main__':
    app.run(debug=True)
