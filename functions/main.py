from dotenv import load_dotenv
from firebase_functions import https_fn
import os
import reply
import remote_config
from whatsapp import Button

# Take environment variables from .env
load_dotenv()


@https_fn.on_request()
def whatsapp_webhook(req: https_fn.Request) -> https_fn.Response:
    # Get the verify_token value from environment variables
    verify_token = os.environ.get("VERIFY_TOKEN")

    # List of allowed phone numbers
    allowed_numbers = os.environ.get("ALLOWED_NUMBERS")

    # To handle verification request
    if req.method == "GET":
        # Parse the query params
        mode = req.args.get("hub.mode")
        token = req.args.get("hub.verify_token")
        challenge = req.args.get("hub.challenge")

        # Check if a token and mode is in the query string of the request
        if mode and token:
            # Check the mode and token sent is correct
            if mode == "subscribe" and token == verify_token and challenge:
                # Respond with the challenge token from the request
                print("WEBHOOK_VERIFIED")
                return challenge
            else:
                # Respond with '403 Forbidden' if verify tokens do not match
                # return https_fn.Response('403 Forbidden', 403) is same with code below
                print("403_FORBIDDEN")
                return "403 Forbidden", 403
        else:
            return "OKE"

    # To handle incoming messages
    elif req.method == "POST" and req.get_json():
        # Get the request data
        json_req = req.get_json()
        print(json_req)

        try:
            # Check if this json data is response send message to user
            if "entry" not in json_req and "messages" in json_req:
                return "OK"

            value = json_req.get("entry")[0]["changes"][0]["value"]

            if "messages" not in value and "statuses" in value:
                return "OK"

            # Get json data from user message
            message = value["messages"][0]
            sender_number = message["from"]
            type = message["type"]

            # Check if any of the allowed numbers are in the incoming phone numbers
            if sender_number in allowed_numbers:
                if type == "text" and message["text"]["body"] == "SIDEBAR":
                    reply.welcome(sender_number)
                    return "OK"

                if type == "interactive" and message["interactive"]:
                    reply.button(
                        sender_number, message["interactive"]["button_reply"]["id"]
                    )
                    return "OK"

            else:
                # Respond with '422 Unprocessable Content'
                print("401 UNAUTHORIZED")
                return "401 Unauthorized", 401

        except:
            # Respond with '422 Unprocessable Content'
            print("422_UNPROCESSABLE", json_req)
            return "422 Unprocessable Content", 422

    else:
        # Respond with '403 Forbidden' if the request method does not match
        print("403_FORBIDDEN")
        return "403 Forbidden", 403
