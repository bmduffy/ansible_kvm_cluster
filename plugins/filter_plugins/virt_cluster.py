#!/usr/bin/python

import os
import libvirt
import xml.dom.minidom

def merge_dicts(x, y):
    merged = x.copy()
    merged.update(y)
    return merged

def getElement(dom, tag):
    return dom.getElementsByTagName(tag)[0].firstChild.nodeValue


def getAttribute(dom, tag, attr):
    return dom.getElementsByTagName(tag)[0].getAttribute(attr)


class VirtualNetwork(object):

    def get_mappings(self):

        ipv4_to_hostname = {}
        hostname_to_ipv4 = {}

        for dns in self.data.getElementsByTagName('dns'):
            for host in dns.getElementsByTagName('host'):
                ipv4 = host.getAttribute('ip')
                hostname = getElement(host, 'hostname')
                hostname_to_ipv4[hostname] = ipv4
                ipv4_to_hostname[ipv4] = hostname

        dhcp = self.data.getElementsByTagName('dhcp')[0]

        for host in dhcp.getElementsByTagName('host'):
            macaddress = host.getAttribute('mac')
            ipv4 = host.getAttribute('ip')
            self.by_macaddress[macaddress] = {
                'ipv4': ipv4,
                'hostname': ipv4_to_hostname.get(ipv4)
            }
            self.by_ipv4[ipv4] = {
                'macaddress' : macaddress,
                'hostname': ipv4_to_hostname.get(ipv4),
            }
            self.by_hostname[ipv4_to_hostname.get(ipv4)] = {
                'ipv4': ipv4,
                'macaddress': macaddress,
            }

    def process_xml_data(self):

        self.name   = getElement(self.data, 'name')
        self.uuid   = getElement(self.data, 'uuid')
        self.mode   = getAttribute(self.data, 'forward', 'mode')
        self.bridge = getAttribute(self.data, 'bridge', 'name')
        self.domain = getAttribute(self.data, 'domain', 'name')
        self.macaddress = getAttribute(self.data, 'mac', 'address')

        self.by_ipv4        = {}
        self.by_hostname    = {}
        self.by_macaddress  = {}

        self.get_mappings()

    def __init__(self, network):
        self.data = xml.dom.minidom.parseString(network.XMLDesc(0))
        self.process_xml_data()

    def __str__(self):
        return """
        ----- VirtualNetwork ----
          name:       {}
          uuid:       {}
          mode:       {}
          bridge:     {}
          domain:     {}
          macaddress: {}
        """

    def get_ipv4s(self):
        return self.by_ipv4.keys()

    def get_hostnames(self):
        return self.by_hostname.keys()

    def get_macaddresses(self):
        return self.by_macaddress.keys()

    def get_by_ipv4(self, ipv4):
        return self.by_ipv4.get(ipv4)

    def get_by_hostname(self, hostname):
        return self.by_hostname.get(hostname)

    def get_by_macaddress(self, macaddress):
        return self.by_macaddress.get(macaddress)


class VirtualMachine(object):

    class Memory(object):
        def __init__(self, value, unit):
            self.value = value
            self.unit  = unit

    class Interface(object):
        def __init__(self, macaddress, network, model):
            self.macaddress = macaddress
            self.network = network
            self.model = model

        def get_dict(self):
            return {
                "macaddress": self.macaddress,
                "network": self.network,
                "model": self.model
            }

    def get_memory(self):
        return VirtualMachine.Memory(
            getElement(self.data, 'memory'),
            getAttribute(self.data, 'memory', 'unit'))

    def get_interfaces(self):
        interfaces = self.data.getElementsByTagName('interface')
        vm_interfaces = []
        for x in interfaces:
            if x.getAttribute('type') != 'network': continue
            vm_interfaces.append(
                VirtualMachine.Interface(
                    getAttribute(x, 'mac', 'address'),
                    getAttribute(x, 'source', 'network'),
                    getAttribute(x, 'model', 'type')
                )
            )
        return vm_interfaces

    def process_xml_data(self):

        self.name   = getElement(self.data, 'name')
        self.uuid   = getElement(self.data, 'uuid')
        self.memory = self.get_memory()
        self.cpus   = getElement(self.data, 'vcpu')
        self.nics   = self.get_interfaces()

    def __init__(self, domain):
        self.data = xml.dom.minidom.parseString(domain.XMLDesc(0))
        self.process_xml_data()

    def __str__(self):
        return """
        ----- Virutal Machine -----
          name:   {}
          uuid:   {}

          cpus:   {}
          memory: {}  {}
          nics:
            {}
        """.format(
            self.name, self.uuid, self.cpus,
            self.memory.value, self.memory.unit,
            "\n".join(["- {} {} {}".format(
                x.macaddress, x.network, x.model_type)
                for x in self.nics]))


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
    return '0' if (x == '1' and y == '1') \
               or (x == '0' and y == '0') else '1'


def bitwise_or(x, y):
    return ipv4("".join(
        [or_gate(i, j) for i, j in zip(bits(x), bits(y))]))


def bitwise_xor(x, y):
    return ipv4("".join(
        [xor_gate(i, j) for i, j in zip(bits(x), bits(y))]))


def bitwise_and(x, y):
    return ipv4("".join(
        [and_gate(i, j) for i, j in zip(bits(x), bits(y))]))


def complement(ip):
    return ipv4("".join(
        [str(int(x != '1')) for x in bits(ip)]))


def get_ipv4_netmask(length):
    return ipv4("".join(
        ['1' if x < int(length) else '0' for x in range(32)]))


def increment_ipv4(value):
    pass


def calculate_subnet(network):

    address, length = network.split("/")

    netmask   = get_ipv4_netmask(length)
    wildcard  = complement(netmask)
    broadcast = bitwise_or(address, wildcard)
    min_host  = bitwise_or(address, "0.0.0.1")
    max_host  = bitwise_xor(broadcast, "0.0.0.1")

    return {
        "network": network,
        "gateway": address,
        "netmask": netmask,
        "wildcard": wildcard,
        "broadcast": broadcast,
        "dhcp": {
            "range": {
                "start": min_host,
                "end":   max_host
            }
        }
    }


def get_vms():
    virt = libvirt.openReadOnly("qemu:///system")
    vms = [VirtualMachine(x) for x in virt.listAllDomains()]
    names = [x.name for x in vms]
    virt.close()
    return dict(zip(names, vms))


def get_vm(hostname):
    return get_vms().get(hostname)


def get_networks():
    virt = libvirt.openReadOnly("qemu:///system")
    networks = [VirtualNetwork(x) for x in virt.listAllNetworks()]
    names = [x.name for x in networks]
    virt.close()
    return dict(zip(names, networks))


def get_network(netname):
    return get_networks().get(netname)


def get_assigned_macaddresses():

    macs_assigned_to_vms = dict(
        [(n.macaddress, n.network)
         for v in get_vms().values() for n in v.nics])

    macs_assigned_to_net_bridges = dict(
        [(n.macaddress, n.name) for n in get_networks.values()])

    return merge_dicts(
        macs_assigned_to_vms,
        macs_assigned_to_net_bridges
    )


def generate_random_macaddress():
    digit = lambda: random.choice('0123456789ABCDEF')
    digits = [digit() for _ in xrange(6)]
    return "52:54:00:{}{}:{}{}:{}{}".format(*digits)


def get_random_macaddress():
    new_mac = generate_random_macaddress()
    assigned_macaddresses = get_assigned_macaddresses()
    while new_mac in assigned_macaddresses:
        new_mac = generate_random_macaddress()
    return new_mac


class FilterModule():

    def get_all_assigned_subnets(self):
        pass

    def get_all_assigned_ipv4_addresses(self):
        pass

    def get_subnet(self, network):
        return calculate_subnet(network)

    def get_subnets(self, networks):
        subnets = {}
        if networks:
            subnets = dict(
                [(name, self.get_subnet(network))
                  for name, network in networks.iteritems()])
        return subnets

    def get_nics(self, hostname, **kwargs):
        vm = get_vm(hostname)
        networks = get_networks()
        nics = []
        for nic in vm.nics:
            nic_data = nic.get_dict()
            netname = nic_data.get('network')
            macaddr = nic_data.get('macaddress')
            network = networks.get(netname)
            nic_data['ipv4'] = network.get_by_macaddress(macaddr).get('ipv4')
            nics.append(nic_data)
        return nics

    def expand(self, path):
        return os.path.expanduser(path)

    def filters(self):
        return {
            'expand'      : self.expand,
            'get_nics'    : self.get_nics,
            'get_subnet'  : self.get_subnet,
            'get_subnets' : self.get_subnets,
        }
