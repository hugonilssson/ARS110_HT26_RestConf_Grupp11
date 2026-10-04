import ipaddress
from get_restconf import get_restconf, interface


######################### FUNKTION FÖR PREFIX ###########################

def netmask_to_prefix(netmask):
    network = ipaddress.IPv4Network(f"0.0.0.0/{netmask}")
    return network.prefixlen

######################## FUNKTION FÖR IP-CHECK ##########################

def get_ipv4(interface_data):

    ### Hämtar IP-adress och omvandlar från nätmask till prefix ###

    ip_config = interface_data.get("ip", {})
    address_config = ip_config.get("address", {})
    primary_address = address_config.get("primary", {})

    ### Kontrollerar att en primär adress finns ###

    if not primary_address:
        return None
        
    ip = primary_address.get("address")
    net_mask = primary_address.get("mask")

    ### Kontrollerar att både IP-adress och nätmask finns ###

    if not ip or not net_mask:
        return None
        
    prefix = netmask_to_prefix(net_mask)

    return f"{ip}/{prefix}"

##################### FÖRUTBESTÄMDA INTERFACES ##########################

EXPECTED_INTERFACES = {
    "HOME": {
        "GigabitEthernet0/0/0": {
            "ipv4": "10.10.10.1/24",
            "enabled": True,
            "description": True
        },
        "Serial0/1/0": {
            "ipv4": "172.16.16.1/24",
            "enabled": True,
            "description": True
        }
    },

    "ISP": {
        "Serial0/1/0": {
            "ipv4": "172.16.16.2/24",
            "enabled": True,
            "description": True
        },
        "GigabitEthernet0/0/0": {
            "ipv4": "10.11.12.2/24",
            "enabled": True,
            "description": True
        }
    },

    "INTERNET": {
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
    
    ### Hämtar interface-info från routern (+ för Serial-länken) ###

    native_interfaces = data.get("Cisco-IOS-XE-native:interface", {})
    
    ### Samlar alla interfaces i en dict ###

    interfaces_by_name = {}
    
    ### Hämtar GigabitEthernet-interfaces ###

    gigabit_data = native_interfaces.get("GigabitEthernet", [])

    ### Hantering av ett och flera interfaces ###

    if isinstance(gigabit_data, dict):
        gigabit_data = [gigabit_data]

    ### Lägger till varje GigabitEthernet-interface i dicten ###

    for port in gigabit_data:
        interface_name = f"GigabitEthernet{port.get('name')}"
        interfaces_by_name[interface_name] = port
        
    ### Hämtar Serial-interfaces ###

    serial_data = native_interfaces.get("Serial", [])

    ### Hantering av ett och flera interfaces ###

    if isinstance(serial_data, dict):
        serial_data = [serial_data]

    ### Lägger till varje Serial-interface i dicten ###

    for port in serial_data:
        interface_name = f"Serial{port.get('name')}"
        interfaces_by_name[interface_name] = port

    expected = EXPECTED_INTERFACES[device]
    print(f"\n=== {device} INTERFACES ===")

    for interface_name, expected_config in expected.items():
        print(f"\n{interface_name}")

        ###################### FINNS RÄTT INTERFACE? #######################

        if interface_name not in interfaces_by_name:
            print("✗ Interface saknas")
            all_correct = False
            continue

        actual_config = interfaces_by_name[interface_name]

        ####################### ÄR INTERFACET PÅ? ##########################

        expected_enabled = expected_config["enabled"]

        ### I Cisco Native-modellen saknas keyword "shutdown" ---               ###
        ### --- om interfacet är aktivt, om keyword finns så är det i shutdown. ###

        is_shutdown = "shutdown" in actual_config
        actual_enabled = not is_shutdown

        if actual_enabled == expected_enabled:
            print("✓ Enabled korrekt")
        else:
            print(f"✗ Enabled fel (förväntat: {expected_enabled}, hittade: {actual_enabled})")
            all_correct = False

        ######################### DESCRIPTION? #############################

        if expected_config["description"]:
            description = actual_config.get("description")
            if description:
                print(f"✓ Description finns: {description}")
            else:
                print("✗ Description saknas")
                all_correct = False

        ######################## RÄTT IP ADDRESS? ##########################

        expected_ipv4 = expected_config["ipv4"]
        actual_ipv4 = get_ipv4(actual_config)

        if actual_ipv4 == expected_ipv4:
            print("✓ IPv4 korrekt")
        else:
            print(f"✗ IPv4 fel (förväntat: {expected_ipv4}, hittade: {actual_ipv4})")
            all_correct = False

    return all_correct
