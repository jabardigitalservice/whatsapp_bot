from google.oauth2 import service_account
from google.auth.transport import requests as auth_request
import requests
import os
import json
import base64
from whatsapp import Button


# Retrieve a valid access token that can be used to authorize requests
def _get_access_token():
    service_cred = os.environ.get("SERVICE_CRED")
    decoded_bytes = base64.b64decode(service_cred)
    service_json = json.loads(decoded_bytes.decode("utf-8"))

    credentials = service_account.Credentials.from_service_account_info(service_json)

    scoped = credentials.with_scopes(
        ["https://www.googleapis.com/auth/firebase.remoteconfig"]
    )

    # Generate the access token
    auth_req = auth_request.Request()
    scoped.refresh(auth_req)
    access_token = scoped.token
    print(access_token)
    return access_token


# Retrieve the current Firebase Remote Config template from server
def _get_config() -> requests.Response:
    base_url = os.environ.get("CONFIG_BASE_URL")

    # Create a dictionary to hold request headers
    headers = {
        "Authorization": "Bearer " + _get_access_token(),
        "Accept-Encoding": "gzip",
    }

    # Make a GET request including headers
    response = requests.get(base_url, headers=headers)
    return response


# Publish updated template to Firebase server
# etag: ETag for safe (avoid race conditions) template updates.
def _publish(etag: str, data):
    base_url = os.environ.get("CONFIG_BASE_URL")

    headers = {
        "Authorization": "Bearer " + _get_access_token(),
        "Content-Type": "application/json; UTF-8",
        "If-Match": etag,
    }

    json_data = json.dumps(data)

    response = requests.put(base_url, data=json_data.encode("utf-8"), headers=headers)

    if response.status_code == 200:
        print("Template has been published.")
        print("ETag from server: {}".format(response.headers["ETag"]))
    else:
        print("Unable to publish template.")
        print(response.text)

    return response


def update_template(type: Button):
    data = _get_config()

    if data.status_code == 200:
        # If the request is successful, get the json configuration
        json_respone = data.json()
        value_tte = json_respone["parameterGroups"]["Feature Config"]["parameters"][
            "feature_tte"
        ]["defaultValue"]["value"]
        value_maintenance = json_respone["parameterGroups"]["Feature Config"][
            "parameters"
        ]["maintenance_mode"]["defaultValue"]["value"]
        result = None

        if type == Button.AKTIFKAN_TTE:
            json_respone["parameterGroups"]["Feature Config"]["parameters"][
                "feature_tte"
            ]["defaultValue"]["value"] = value_tte.replace(
                '"enabled":false', '"enabled":true', 1
            )
            result = "[TTE AKTIF]"
        elif type == Button.NONAKTIFKAN_TTE:
            json_respone["parameterGroups"]["Feature Config"]["parameters"][
                "feature_tte"
            ]["defaultValue"]["value"] = value_tte.replace(
                '"enabled":true', '"enabled":false', 1
            )
            result = "[TTE NONAKTIF]"
        elif type == Button.AKTIFKAN_MAINTENANCE:
            json_respone["parameterGroups"]["Feature Config"]["parameters"][
                "maintenance_mode"
            ]["defaultValue"]["value"] = value_maintenance.replace(
                '"active_mode":false', '"active_mode":true', 1
            )
            result = "[MAINTENANCE AKTIF]"
        elif type == Button.NONAKTIFKAN_MAINTENANCE:
            json_respone["parameterGroups"]["Feature Config"]["parameters"][
                "maintenance_mode"
            ]["defaultValue"]["value"] = value_maintenance.replace(
                '"active_mode":true', '"active_mode":false', 1
            )
            result = "[MAINTENANCE NONAKTIF]"

        response = _publish(data.headers["ETag"], json_respone)

        if response.status_code == 200:
            return result
        else:
            return None

    else:
        # If the request is unsuccessful, print the error and return text response
        print(f"Error getting remote config")
        return None


# Parsing the status tte and maintenance from template
def get_status():
    response = _get_config()

    if response.status_code == 200:
        # If the request is successful, get the json configuration
        json_respone = response.json()

        # Parse the JSON object into a Python dictionary
        json_tte = json.loads(
            json_respone["parameterGroups"]["Feature Config"]["parameters"][
                "feature_tte"
            ]["defaultValue"]["value"]
        )
        json_maintenance = json.loads(
            json_respone["parameterGroups"]["Feature Config"]["parameters"][
                "maintenance_mode"
            ]["defaultValue"]["value"]
        )

        # Define the data to be returned
        status = {
            "status_tte": "Aktif 🟢" if json_tte["enabled"] else "Nonaktif 🔴",
            "status_maintenance": "Aktif 🟢"
            if json_maintenance["active_mode"]
            else "Nonaktif 🔴",
        }

        return status
    else:
        # If the request is unsuccessful, print the error and return text response
        print(f"Error getting remote config")
        return None
