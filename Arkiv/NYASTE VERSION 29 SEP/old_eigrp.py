from get_restconf import get_restconf, eigrp_conf, eigrp_operation, routing

################## FÖRVÄNTAD EIGRP-KONF #####################

EXPECTED_EIGRP = {
    "HOME": {
        "as": 1,
        "router_id": "3.3.3.3",
        "networks": [
            ("172.16.16.0", "0.0.0.255")
        ]
    },

    "ISP": {
        "as": 1,
        "router_id": "2.2.2.2",
        "networks": [
            ("172.16.16.0", "0.0.0.255"),
            ("10.11.12.0", "0.0.0.255")
        ]
    },

    "INTERNET": {
        "as": 1,
        "router_id": "1.1.1.1",
        "networks": [
            ("10.11.12.0", "0.0.0.255")
        ],
    }
}

################## FÖRVÄNTADE EIGRP GRANNAR ###################

EXPECTED_NEIGHBORS = {
    "HOME": [
        "172.16.16.2"
    ],

    "ISP": [
        "172.16.16.1",
        "10.11.12.3"
    ],

    "INTERNET": [
        "10.11.12.2"
    ]
}

##################### FUNKTION EIGRP ###########################

def check_eigrp(device):

    all_correct = True
    data = get_restconf(device, eigrp_conf)

    eigrp_data = data["Cisco-IOS-XE-eigrp:router-eigrp"]["eigrp"]
    eigrp_config = eigrp_data["classic-mode"][0]

    expected = EXPECTED_EIGRP[device]

    actual_as = eigrp_config["autonomous-system"]
    actual_router_id = eigrp_config["eigrp"]["router-id"]

    print(f"\n=== {device} EIGRP ===")

    ##################### AS-NUMMER? ###########################

    if actual_as == expected["as"]:
        print(f"✓ EIGRP AS korrekt: {actual_as}")
    else:
        print(
            f"✗ Fel EIGRP AS "
            f"(förväntat: {expected['as']}, "
            f"hittade: {actual_as})"
        )
        all_correct = False

    ##################### ROUTER-ID? ##########################

    if actual_router_id == expected["router_id"]:
        print(f"✓ Router-ID korrekt: {actual_router_id}")
    else:
        print(
            f"✗ Fel Router-ID "
            f"(förväntat: {expected['router_id']}, "
            f"hittade: {actual_router_id})"
        )
        all_correct = False

    ###################### NÄTVERK ###########################

    actual_networks = []

    for network in eigrp_config["network"]["address-wildcard"]:
        actual_networks.append(
            (
                network["ipv4-address"],
                network["wildcard"]
            )
        )

    ### Jämför innehållet oberoende av ordningen routern returnerar (set) ###
 
    expected_networks = expected["networks"]

    if set(actual_networks) == set(expected_networks):
        print("✓ EIGRP networks korrekta")
    else:
        print("✗ EIGRP networks fel")
        all_correct = False

        missing_networks = set(expected_networks) - set(actual_networks)
        extra_networks = set(actual_networks) - set(expected_networks)

        for network in missing_networks:
            print(f"  ✗ Saknas: {network[0]} {network[1]}")

        for network in extra_networks:
            print(f"  ✗ Extra: {network[0]} {network[1]}")

    #################### REDISTRIBUTE ##########################

    if device == "INTERNET":
        redistribute = eigrp_config.get("redistribute", {})

        if "static" in redistribute:
            print("✓ Static routes redistribueras via EIGRP")
        else:
            print("✗ Static routes redistribueras inte via EIGRP")
            all_correct = False

    ################### ROUTING-TABELLEN #######################

    ### Kontrollerar att INTERNET har en statisk default-route via en Loopback ###

    if device == "INTERNET":
        data = get_restconf(device, routing)

        routing_instance = data["ietf-routing:routing-instance"][0]
        routes = routing_instance["ribs"]["rib"][0]["routes"]["route"]

        default_route = None

        for route in routes:
            if route["destination-prefix"] == "0.0.0.0/0":
                default_route = route
                break

        if default_route is None:
            print("✗ Default route saknas")
            all_correct = False
        else:
            print("✓ Default route finns")

            if default_route["source-protocol"] == "ietf-routing:static":
                print("✓ Default route är statisk")
            else:
                print(
                    f"✗ Default route har fel source-protocol: "
                    f"{default_route['source-protocol']}"
                )
                all_correct = False

            next_hop = default_route.get("next-hop", {})
            outgoing_interface = next_hop.get("outgoing-interface", "")

            ### Checka att en Loopback finns, inget krav på vilken ###

            if outgoing_interface.startswith("Loopback"):
                print(
                    f"✓ Default route går via {outgoing_interface}"
                )
            else:
                print(
                    f"✗ Default route går inte via en Loopback "
                    f"({outgoing_interface})"
            )
                all_correct = False

    return all_correct

################ FUNKTION FÖR EIGRP-FUNKTIONALITET #################

def check_eigrp_neighbors(device):

    all_correct = True
    data = get_restconf(device, eigrp_operation)

    eigrp_instance = data[
        "Cisco-IOS-XE-eigrp-oper:eigrp-oper-data"
    ]["eigrp-instance"][0]

    ### Dict för insamling av grannar ###

    actual_neighbors = []

    ### Samlar IP-adresser för upptäckta grannar ###

    for interface_data in eigrp_instance.get("eigrp-interface", []):
        for neighbor_data in interface_data.get("eigrp-nbr", []):
            actual_neighbors.append(neighbor_data["nbr-address"])

    expected_neighbors = EXPECTED_NEIGHBORS[device]

    print(f"\n=== {device} EIGRP NEIGHBORS ===")

    ### Jämförelse mellan förväntade och faktiska grannar ###

    if set(actual_neighbors) == set(expected_neighbors):
        print("✓ EIGRP neighbors korrekta")
    else:
        print("✗ EIGRP neighbors fel")
        all_correct = False

        ### Ordningen på grannarna spelar ingen roll (set) ###
        
        missing = set(expected_neighbors) - set(actual_neighbors)
        extra = set(actual_neighbors) - set(expected_neighbors)

        for neighbor in missing:
            print(f"  ✗ Neighbor saknas: {neighbor}")

        for neighbor in extra:
            print(f"  ✗ Extra neighbor: {neighbor}")

    return all_correct


if __name__ == "__main__":

    result_home = check_eigrp("HOME")
    result_isp = check_eigrp("ISP")
    result_internet = check_eigrp("INTERNET")

    print("\n=== RESULTAT ===")
    print(f"HOME: {result_home}")
    print(f"ISP: {result_isp}")
    print(f"INTERNET: {result_internet}")
