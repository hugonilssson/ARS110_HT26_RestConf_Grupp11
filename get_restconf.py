import os
import requests
from dotenv import load_dotenv

############################# VRF-ADDRESSER ###################################

HOSTS = {
    "HOME": "192.168.0.113",
    "ISP": "192.168.0.112",
    "INTERNET": "192.168.0.111"
}


load_dotenv()

USERNAME = os.getenv("RESTCONF_USERNAME")
PASSWORD = os.getenv("RESTCONF_PASSWORD")

############################# RESTCONF PATHS ##################################

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

####################### FUNKTION FÖR ENSKILD ENHET ############################

def get_restconf(device, path):

    host = HOSTS[device]

    url = f"https://{host}/restconf/data/{path}"

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


