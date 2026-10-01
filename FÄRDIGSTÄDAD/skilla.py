from get_restconf import send_restconf, hostname
from hostname import check_hostname, EXPECTED_HOSTNAMES

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

if __name__ == "__main__":
    configure_hostname("HOME")
    result, actual = check_hostname("HOME")
    
    if result:
        print(f"✓ Hostname korrekt: {actual}")
    else:
        print(f"✗ Fel hostname: {actual}")