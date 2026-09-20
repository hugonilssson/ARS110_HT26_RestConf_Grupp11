import os
import requests
from dotenv import load_dotenv

HOST = "192.168.0.247"
BASE_URL = f"https://{HOST}/restconf/data"

load_dotenv()

USERNAME = os.getenv("RESTCONF_USERNAME")
PASSWORD = os.getenv("RESTCONF_PASSWORD")

# Restconf PATHs

hostname = (
    "Cisco-IOS-XE-native:native/hostname/"
)

interface = (
    "ietf-interfaces:interfaces"
)

eigrp_conf = (
    "Cisco-IOS-XE-native:native/router/Cisco-IOS-XE-eigrp:router-eigrp"
)

eigrp_operation = (
    "Cisco-IOS-XE-eigrp-oper:eigrp-oper-data"
)


def get_restconf(path):
    url = f"{BASE_URL}/{path}"

    headers = {
        "Accept": "application/yang-data+json"

    }

    response = requests.get(
        url,
        headers=headers,
        auth=(USERNAME, PASSWORD),
        verify=False
    )

    response.raise_for_status()
    return response.json()


