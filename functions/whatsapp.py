from enum import Enum
import requests
import os
import json


class Button(Enum):
    AKTIFKAN = "enable"
    NONAKTIFKAN = "disable"
    STATUS = "status"
    AKTIFKAN_TTE = "enable_tte"
    AKTIFKAN_MAINTENANCE = "enable_maintenance"
    NONAKTIFKAN_TTE = "disable_tte"
    NONAKTIFKAN_MAINTENANCE = "disable_maintenance"


def _send_message(payload: dict) -> requests.Response:
    base_url = os.environ.get("WA_BASE_URL")
    access_token = os.environ.get("WA_ACCESS_TOKEN")

    # Create a dictionary to hold request headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }

    # Send a POST request including headers and payload data
    response = requests.post(base_url, data=payload, headers=headers)

    if response.status_code == 200:
        # If the request is successful, return the response
        return response
    else:
        # If the request is unsuccessful, print the error and return None
        print(f"Error whatsapp operation: {response.text}")
        return None


# Send messages including up to 3 options —each option is a button.
# This type of message offers a quicker way for users to make a selection from a menu when interacting
def send_interactive_message(
    phone_number: str,
    body: str,
    buttons: list,
) -> requests.Response:
    # Create a dictionary to hold payload for interactive message
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": phone_number,
        "type": "interactive",
        "interactive": json.dumps(
            {
                "type": "button",
                "header": {"type": "text", "text": "SIDEBAR Assist"},
                "body": {"text": body},
                "footer": {"text": "Pesan ini dikirim secara otomatis oleh sistem"},
                "action": {"buttons": buttons},
            }
        ),
    }

    return _send_message(data)


def send_text_message(
    phone_number: str,
    body: str,
) -> requests.Response:
    # Create a dictionary to hold payload for plain text message
    data = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "text",
        "text": json.dumps({"body": body}),
    }

    return _send_message(data)
