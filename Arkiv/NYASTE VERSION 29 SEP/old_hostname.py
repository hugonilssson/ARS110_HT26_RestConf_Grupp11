from get_restconf import get_restconf, hostname

EXPECTED_HOSTNAMES = {
    "HOME": "HEMMA",
    "ISP": "ISP",
    "INTERNET": "INTERNET"
}

def check_hostname(device):
    data = get_restconf(device, hostname)

    actual_hostname = data["Cisco-IOS-XE-native:hostname"]
    expected_hostname = EXPECTED_HOSTNAMES[device]

    if actual_hostname == expected_hostname:
        return True, actual_hostname

    return False, actual_hostname

if __name__ == '__main__':
    for device in EXPECTED_HOSTNAMES:
        result, actual = check_hostname(device)

        if result:
            print(f'✓ Hostname Korrekt: {actual}')

        else:
            print(f'✗ Fel Hostname. Förväntat: {EXPECTED_HOSTNAMES[device]}, hittade: {actual}')
