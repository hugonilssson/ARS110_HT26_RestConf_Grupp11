import requests

host = "192.168.0.247"
url = f"https://{host}/restconf/data/ietf-interfaces:interfaces"

headers = {
    "Accept": "application/yang-data+json"
}

response = requests.get(
    url,
    headers=headers,
    auth=("admin", "class"),
    verify=False
)

print(response.status_code)
print(response.json())


data = response.json()

interfaces = data["ietf-interfaces:interfaces"]["interface"]

for interface in interfaces:
    name = interface["name"]
    enabled = interface.get("enabled", False)

    status = "UP" if enabled else "DOWN"

    print(f"{name:<20} {status}")