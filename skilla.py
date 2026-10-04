from get_restconf import send_restconf, get_restconf, hostname, interface, eigrp_conf, static_route
from hostname import check_hostname, EXPECTED_HOSTNAMES
from interfaces import check_interfaces
from eigrp import check_eigrp

######################################## SKICKA HOSTNAMN ##############################################

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

    print(f"Hostname skickat till {device}: {response.status_code}")

##################################### SKICKA INTERFACE-KONF ###########################################

def configure_interface(device, interface_type, name, ip, mask, description, method="PATCH"):

    payload = {
        f"Cisco-IOS-XE-native:{interface_type}": {
            "name": name,
            "description": description,
            "ip": {
                "address": {
                    "primary": {
                        "address": ip,
                        "mask": mask
                    }
                }
            }
        }
    }

    path = f"{interface}/{interface_type}={name.replace('/', '%2F')}"

    response = send_restconf(
        device,
        path,
        method,
        payload
    )

    print(f"Interface skickat till {device}: {response.status_code}")
    
##################### FUNKTION FÖR ATT STARTA EVENTUELLA INTERFACE FRÅN SHUTDOWN ######################

def enable_interface(device, interface_type, name):

    path = f"{interface}/{interface_type}={name.replace('/', '%2F')}"

    data = get_restconf(device, path)

    interface_data = data[f"Cisco-IOS-XE-native:{interface_type}"]

    if "shutdown" in interface_data:

        response = send_restconf(
            device,
            f"{path}/shutdown",
            "DELETE",
            None
        )

        print(f"Interface aktiverat på {device}: {response.status_code}")

    else:
        print(f"Interface saknar shutdown redan: {device} {interface_type}{name}")

##################################### KÖRNING AV SKRIPT 1/2 ############################################

if __name__ == "__main__":

    ########################## HOSTNAMN ###########################

    for device in ["HOME", "ISP", "INTERNET"]:
        configure_hostname(device)

        result, actual = check_hostname(device)

        if result:
            print(f"✓ Hostname korrekt: {actual}")
        else:
            print(f"✗ Fel hostname: {actual}")

    ########################## IP-KONF ############################

    configure_interface(
    "HOME",
    "GigabitEthernet",
    "0/0/0",
    "10.10.10.1",
    "255.255.255.0",
    "Link-to-Garderob"
)
    configure_interface(
    "HOME",
    "Serial",
    "0/1/0",
    "172.16.16.1",
    "255.255.255.0",
    "Link-to-ISP"
)
    configure_interface(
    "ISP",
    "Serial",
    "0/1/0",
    "172.16.16.2",
    "255.255.255.0",
    "Link-to-HEMMA"
)
    configure_interface(
    "ISP",
    "GigabitEthernet",
    "0/0/0",
    "10.11.12.2",
    "255.255.255.0",
    "Link-to-INTERNET"
)
    configure_interface(
    "INTERNET",
    "GigabitEthernet",
    "0/0/0",
    "10.11.12.3",
    "255.255.255.0",
    "Link-to-ISP"
)
    configure_interface(
    "INTERNET",
    "Loopback",
    "0",
    "10.255.255.1",
    "255.255.255.0",
    "Loopback-INTERNET",
    "PUT"
)

###################################### FUNKTION FÖR EIGRP KONF ########################################

def configure_eigrp(device, as_number, router_id, networks):

    network_list = []

    for network, wildcard in networks:
        network_list.append({
            "ipv4-address": network,
            "wildcard": wildcard
        })

    eigrp_settings = {
        "router-id": router_id
    }

    classic_mode = {
        "autonomous-system": as_number,
        "eigrp": eigrp_settings,
        "network": {
            "address-wildcard": network_list
        }
    }

    if device == "INTERNET":
        classic_mode["redistribute"] = {
            "static": {}
        }

    payload = {
        "Cisco-IOS-XE-eigrp:router-eigrp": {
            "eigrp": {
                "classic-mode": [
                    classic_mode
                ]
            }
        }
    }

    response = send_restconf(
        device,
        eigrp_conf,
        "PATCH",
        payload
    )

    print(f"EIGRP skickat till {device}: {response.status_code}")

############################ FUNKTION FÖR STATISK DEFAULT-ROUTE KONF ##################################

def configure_default_route():
    payload = {
        "Cisco-IOS-XE-native:route": {
            "ip-route-interface-forwarding-list": [
                {
                    "prefix": "0.0.0.0",
                    "mask": "0.0.0.0",
                    "fwd-list": [
                        {
                            "fwd": "Loopback0"
                        }
                    ]
                }
            ]
        }
    }

    response = send_restconf(
        "INTERNET",
        static_route,
        "PATCH",
        payload
    )

    print(f"Default route skickad till INTERNET: {response.status_code}")

##################################### KÖRNING AV SKRIPT 2/2 ###########################################

if __name__ == "__main__":
    configure_eigrp(
    "HOME",
    1,
    "3.3.3.3",
    [
        ("172.16.16.0", "0.0.0.255")
    ]
)
    configure_eigrp(
    "ISP",
    1,
    "2.2.2.2",
    [
        ("172.16.16.0", "0.0.0.255"),
        ("10.11.12.0", "0.0.0.255")
    ]
)
    configure_eigrp(
    "INTERNET",
    1,
    "1.1.1.1",
    [
        ("10.11.12.0", "0.0.0.255")
    ]
)
    configure_default_route()
    
    # HOME
    enable_interface("HOME", "GigabitEthernet", "0/0/0")
    enable_interface("HOME", "Serial", "0/1/0")

    # ISP
    enable_interface("ISP", "Serial", "0/1/0")
    enable_interface("ISP", "GigabitEthernet", "0/0/0")

    # INTERNET
    enable_interface("INTERNET", "GigabitEthernet", "0/0/0")

    for device in ["HOME", "ISP", "INTERNET"]:
        result = check_eigrp(device)

    if result:
        print(f"✓ {device} EIGRP korrekt")
    else:
        print(f"✗ {device} EIGRP har fel")
