import os
import requests
from dotenv import load_dotenv

############################# VRF-ADDRESSER ###################################

HOSTS = {
    ### 192.168.0.113 ###
    "HOME": "HEMMA.lab",
    ### 192.168.0.112 ###
    "ISP": "ISP.lab",
    ### 192.168.0.111 ###
    "INTERNET": "INTERNET.lab"
}

### CERTIFIKAT FÖR SÄKER HTTPS ###
CERTIFICATES = {
    "HOME": "HEMMA.crt",
    "ISP": "ISP.crt",
    "INTERNET": "INTERNET.crt"
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

static_route = (
    "Cisco-IOS-XE-native:native/ip/route"
)

####################### FUNKTION FÖR ENSKILD ENHET ############################

def get_restconf(device, path):

    host = HOSTS[device]
    certificate = CERTIFICATES[device]

    url = f"https://{host}/restconf/data/{path}"

    headers = {
        "Accept": "application/yang-data+json"
    }

    response = requests.get(
        url,
        headers=headers,
        auth=(USERNAME, PASSWORD),
        verify=certificate,
        timeout=10
    )

    response.raise_for_status()
    if response.status_code == 204 or not response.text.strip():
        return {}
    return response.json()

####################### FUNKTION FÖR ATT SKICKA KONF ###########################

def send_restconf(device, path, method, payload):

    host = HOSTS[device]
    certificate = CERTIFICATES[device]

    url = f"https://{host}/restconf/data/{path}"

    headers = {
        "Accept": "application/yang-data+json",
        "Content-Type": "application/yang-data+json"
    }

    response = requests.request(
        method,
        url,
        headers=headers,
        auth=(USERNAME, PASSWORD),
        verify=certificate,
        timeout=10,
        json=payload
    )

    if not response.ok:
        print("RESTCONF FEL:", response.status_code)
        print("FELMEDDELANDE:", response.text)
    
    response.raise_for_status()

    return response
