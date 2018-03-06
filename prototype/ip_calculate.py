def bits(ip):
    return "".join(["{0:08b}".format(int(x)) for x in ip.split(".")])

def ipv4(bits):
    bites = [bits[x: x + 8] for x in range(0, 32, 8)]
    bite = lambda x: str(int("".join(x), 2))
    return ".".join([bite(x) for x in bites])

def or_gate(x, y):
    return '0' if x == '0' and y == '0' else '1'

def and_gate(x, y):
    return '1' if x == '1' and y == '1' else '0'

def xor_gate(x, y):
    return (
        '0' if (x == '1' and y == '1') or
               (x == '0' and y == '0') else '1')

def bitwise_or(x, y):
    return ipv4(
        "".join([or_gate(i, j) for i, j in zip(bits(x), bits(y))]))

def bitwise_xor(x, y):
    return ipv4(
        "".join([xor_gate(i, j) for i, j in zip(bits(x), bits(y))]))

def bitwise_and(x, y):
    return ipv4(
        "".join([and_gate(i, j) for i, j in zip(bits(x), bits(y))]))

def complement(ip):
    return ipv4(
        "".join([str(int(x != '1')) for x in bits(ip)]))

def get_ipv4_netmask(length):
    return ipv4(
        "".join(['1' if x < int(length) else '0' for x in range(32)]))

def generate_network_data(subnet):

    address, length = subnet.split("/")

    netmask   = get_ipv4_netmask(length)
    wildcard  = complement(netmask)
    broadcast = bitwise_or(address, wildcard)
    min_host  = bitwise_or(address, "0.0.0.1")
    max_host  = bitwise_xor(broadcast, "0.0.0.1")

    return {
        "name": "test",
        "mode": "nat",
        "subnet": subnet,
        "gateway": address,
        "netmask": netmask,
        "wildcard": wildcard,
        "broadcast": broadcast,
        "dhcp": {
            "range": {
                "start": min_host,
                "end": max_host
            }
        }
    }

if __name__ == "__main__":

    print generate_network_data("172.30.0.0/16")
