import os
import requests
from dotenv import load_dotenv
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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
    "Cisco-IOS-XE-native:native/interface"
)

eigrp_conf = (
    "Cisco-IOS-XE-native:native/router/Cisco-IOS-XE-eigrp:router-eigrp"
)

eigrp_operation = (
    "Cisco-IOS-XE-eigrp-oper:eigrp-oper-data"
)

routing = (
    "ietf-routing:routing-state/routing-instance"
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
        timeout=10
    )

    response.raise_for_status()
    return response.json()


