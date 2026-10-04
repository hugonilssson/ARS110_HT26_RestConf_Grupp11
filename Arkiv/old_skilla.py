from get_restconf import send_restconf, hostname, interface
from hostname import check_hostname, EXPECTED_HOSTNAMES
from interfaces import check_interfaces

#################### SÄTTER HOSTNAME-KONF ##########################

def configure_hostname(device):

    expected_hostname = EXPECTED_HOSTNAMES[device]

    payload = {
        "Cisco-IOS-XE-native:hostname": expected_hostname
    }

    response = send_restconf(
        device,
        hostname,
        "PATCH",
        payload
    )

#################### SÄTTER INTERFACE-KONF ##########################

def configure_interface(device):

    payload = {
        "Cisco-IOS-XE-native:GigabitEthernet": {
            "name": "0/0/0",
            "description": "LAN HOME",
            "ip": {
                "address": {
                    "primary": {
                        "address": "10.10.10.1",
                        "mask": "255.255.255.0"
                    }
                }
            }
        }
    }

    response = send_restconf(
        device,
        interface + "/GigabitEthernet=0%2F0%2F0",
        "PATCH",
        payload
    )

    print(f"Interface skickat till {device}: {response.status_code}")
    print(f"Hostname skickat till {device}: {response.status_code}")

if __name__ == "__main__":
    configure_hostname("HOME")
    result, actual = check_hostname("HOME")
    
    if result:
        print(f"✓ Hostname korrekt: {actual}")
    else:
        print(f"✗ Fel hostname: {actual}")
