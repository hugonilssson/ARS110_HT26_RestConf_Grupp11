from get_restconf import get_restconf, hostname

EXPECTED_HOSTNAME = "INTERNET"

def check_hostname():
    data = get_restconf(hostname)

    actual_hostname = data["Cisco-IOS-XE-native:hostname"]

    if actual_hostname == EXPECTED_HOSTNAME:
        return True, actual_hostname

    return False, actual_hostname

result, actual = check_hostname()

if result:
    print(f'✓ Hostname Korrekt: {actual}')

else:
    print(f'✗ Fel Hostname. Förväntat: {EXPECTED_HOSTNAME}, hittade: {actual}')