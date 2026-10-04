from hostname import check_hostname
from interfaces import check_interfaces
from eigrp import check_eigrp, check_eigrp_neighbors


DEVICES = [
    "HOME",
    "ISP",
    "INTERNET"
]


def main():

    print("\n========================================")
    print("          CCNA SKILL CHECK")
    print("==========================================")

    results = {}

    for device in DEVICES:

        print(f"\n\n=== {device} ===")

        # Hostname
        hostname_result, actual_hostname = check_hostname(device)

        # Interfaces
        interfaces_result = check_interfaces(device)

        # EIGRP
        eigrp_result = check_eigrp(device)

        # EIGRP neighbors
        neighbors_result = check_eigrp_neighbors(device)

        results[device] = (
            hostname_result
            and interfaces_result
            and eigrp_result
            and neighbors_result
        )

    print("\n\n========================================")
    print("              RESULTAT")
    print("========================================")

    for device, result in results.items():

        if result:
            print(f"{device:<10} ✓ GODKÄND")
        else:
            print(f"{device:<10} ✗ FEL")

    print("========================================")


if __name__ == "__main__":
    main()
