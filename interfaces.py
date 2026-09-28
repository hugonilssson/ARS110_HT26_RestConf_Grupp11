import ipaddress

from get_restconf import get_restconf, interface

######################### FUNKTION FÖR PREFIX ###########################

def netmask_to_prefix(netmask):
    network = ipaddress.IPv4Network(f"0.0.0.0/{netmask}")
    return network.prefixlen

######################## FUNKTION FÖR IP-CHECK ##########################

def get_ipv4(interface):
    ipv4 = interface.get("ietf-ip:ipv4", {})
    addresses = ipv4.get("address", [])

    if not addresses:
        return None

    address = addresses[0]

    ip = address["ip"]
    prefix = netmask_to_prefix(address["netmask"])

    return f"{ip}/{prefix}"

##################### FÖRUTBESTÄMDA INTERFACES ##########################

EXPECTED_INTERFACES = {
    "HOME": {
        # RIKTIGT INTERFACE SKA VARA G0/0/0
        "GigabitEthernet0/0/0": {
            "ipv4": "10.10.10.1/24",
            "enabled": True,
            "description": True
        },
        # RIKTIGT INTERFACE SKA VARA S0/1/0
        "Serial0/1/0": {
            "ipv4": "172.16.16.1/24",
            "enabled": True,
            "description": True
        }
    },

    "ISP": {
        # RIKTIGT INTERFACE SKA VARA S0/1/0
        "Serial0/1/0": {
            "ipv4": "172.16.16.2/24",
            "enabled": True,
            "description": True
        },
        # RIKTIGT INTERFACE SKA VARA G0/0/0
        "GigabitEthernet0/0/0": {
            "ipv4": "10.11.12.2/24",
            "enabled": True,
            "description": True
        }
    },

    "INTERNET": {
        #RIKTIGT INTERFACE SKA VARA G0/0/0
        "GigabitEthernet0/0/0": {
            "ipv4": "10.11.12.3/24",
            "enabled": True,
            "description": True
        }
    }
}

##################### FUNKTION INTERFACES & DEVICE ########################

def check_interfaces(device):

    all_correct = True
    data = get_restconf(device, interface)
    interfaces = data["ietf-interfaces:interfaces"]["interface"]

    expected = EXPECTED_INTERFACES[device]

    actual_by_name = {
        item["name"]: item
        for item in interfaces
    }

    print(f"\n=== {device} INTERFACES ===")

    for interface_name, expected_config in expected.items():

        print(f"\n{interface_name}")

        ###################### FINNS RÄTT INTERFACE? #######################

        if interface_name not in actual_by_name:
            print("✗ Interface saknas")
            all_correct = False
            continue

        actual = actual_by_name[interface_name]

        ####################### ÄR INTERFACET PÅ? ##########################

        expected_enabled = expected_config["enabled"]
        actual_enabled = actual.get("enabled", False)

        if actual_enabled == expected_enabled:
            print("✓ Enabled korrekt")
        else:
            print(
                f"✗ Enabled fel "
                f"(förväntat: {expected_enabled}, "
                f"hittade: {actual_enabled})"
            )
            all_correct = False

        ######################### DESCRIPTION? #############################

        if expected_config["description"]:
            description = actual.get("description")

            if description:
                print(f"✓ Description finns: {description}")
            else:
                print("✗ Description saknas")
                all_correct = False

        ######################## RÄTT IP ADDRESS? ##########################

        expected_ipv4 = expected_config["ipv4"]
        actual_ipv4 = get_ipv4(actual)

        if actual_ipv4 == expected_ipv4:
            print("✓ IPv4 korrekt")
        else:
            print(
                f"✗ IPv4 fel "
                f"(förväntat: {expected_ipv4}, "
                f"hittade: {actual_ipv4})"
            )
            all_correct = False

    return all_correct


if __name__ == "__main__":
    result_isp = check_interfaces("ISP")
    result_internet = check_interfaces("INTERNET")
    result_home = check_interfaces("HOME")
    print(f"\nResultat: {result_isp}")
    print(f"\nResultat: {result_internet}")
    print(f"\nResultat: {result_home}")