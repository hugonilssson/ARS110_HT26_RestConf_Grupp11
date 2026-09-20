from get_restconf import get_restconf, eigrp_conf

data = get_restconf(eigrp_conf)

print(data)