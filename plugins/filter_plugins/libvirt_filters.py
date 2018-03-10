#!/usr/bin/python

import os
import random
import libvirt
import xml.dom.minidom

from ansible.errors import AnsibleError, AnsibleParserError


def merge_dicts(x, y):
    merged = x.copy()
    merged.update(y)
    return merged


def getElement(dom, tag):
    return dom.getElementsByTagName(tag)[0].firstChild.nodeValue


def getAttribute(dom, tag, attr):
    return dom.getElementsByTagName(tag)[0].getAttribute(attr)


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


def to_int_array(str_ipv4):
    return [int(x) for x in str_ipv4.split(".")]


def to_string(int_array):
    return ".".join([str(x) for x in int_array])


def increment_ipv4(str_ipv4):
    int_array = to_int_array(str_ipv4)
    if int_array[3] < 255:
        int_array[3] += 1
    else:
        int_array[3] = 0
        if int_array[2] < 255:
            int_array[2] += 1
        else:
            int_array[2] = 0
            if int_array[1] < 255:
                int_array[1] += 1
            else:
                int_array[1] = 0
                if int_array[0] < 255:
                    int_array[0] += 1
    return to_string(int_array)


class Subnet(object):

    def __init__(self, cidr):

        address, length = cidr.split("/")

        self.cidr      = cidr
        self.netmask   = get_ipv4_netmask(length)
        self.wildcard  = complement(self.netmask)
        self.gateway   = bitwise_and(address, self.netmask)
        self.broadcast = bitwise_or(self.gateway, self.wildcard)
        self.min_host  = bitwise_or(self.gateway, "0.0.0.1")
        self.max_host  = bitwise_xor(self.broadcast, "0.0.0.1")

    def to_dict(self):
        return {
            "cidr": self.cidr,
            "mode": "nat",
            "gateway": self.min_host,
            "netmask": self.netmask,
            "wildcard": self.wildcard,
            "broadcast": self.broadcast,
            "dhcp": {
                "range": {
                    "start": self.min_host,
                    "end":   self.max_host
                }
            }
        }

    def __str__(self):
        return """
        ---- Subnet ---
        cidr:      {}
        netmask:   {}
        gateway:   {}
        wildcard:  {}
        broadcast: {}
        min_host:  {}
        max_host:  {}
        """.format(
            self.cidr, self.netmask, self.gateway,
            self.wildcard, self.broadcast, self.min_host, self.max_host)


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

    def get_cidr_block(self):

        ip_block = self.data.getElementsByTagName('ip')[0]

        self.gateway = ip_block.getAttribute('address')
        self.netmask = ip_block.getAttribute('netmask')
        self.length = sum([int(b) for b in bits(self.netmask)])
        self.cidr_block = "{}/{}".format(self.gateway, self.length)

    def process_xml_data(self):

        self.name   = getElement(self.data, 'name')
        self.uuid   = getElement(self.data, 'uuid')
        self.mode   = getAttribute(self.data, 'forward', 'mode')
        self.bridge = getAttribute(self.data, 'bridge', 'name')
        self.domain = getAttribute(self.data, 'domain', 'name')
        self.macaddress = getAttribute(self.data, 'mac', 'address')

        self.get_cidr_block()

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
          cidr_block: {}
          netmask:    {}
          gateway:    {}
        """.format(
            self.name, self.uuid, self.mode, self.bridge,
            self.domain, self.macaddress, self.cidr_block,
            self.netmask, self.gateway)

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


class VirtualMachineSnapshot(object):

    def process_xml_data(self):
        values = self.data.getElementsByTagName("name")
        print values
        self.snapshot_name = values[0].firstChild.nodeValue
        self.virtual_machine_name = values[1].firstChild.nodeValue

    def __init__(self, snapshot):
        self.data = xml.dom.minidom.parseString(snapshot.getXMLDesc(0))
        self.process_xml_data()

    def __str__(self):
        return """
        ----- Virutal Machine Snapshot -----
          virutal machine :   {}
          snapshot        :   {}
        """.format(self.virutal_machine_name, self.snapshot_name)


def get_virtual_networks():
    virt = libvirt.openReadOnly("qemu:///system")
    networks = [VirtualNetwork(x) for x in virt.listAllNetworks()]
    names = [x.name for x in networks]
    virt.close()
    return dict(zip(names, networks))


def get_virtual_network(netname):
    return get_virtual_networks().get(netname)


def get_all_assigned_subnets():
    networks = get_virtual_networks()
    subnets = {}
    for network in networks.values():
        subnets[network.cidr_block] = network.name
    return subnets


def get_all_assigned_ipv4_addresses():
    networks = get_virtual_networks()
    assigned = {}
    if networks:
        for netname, virtual_network in networks.iteritems():
            assigned[netname] = virtual_network.get_ipv4s()
    return assigned


def get_virtual_machines():
    virt = libvirt.openReadOnly("qemu:///system")
    vms = [VirtualMachine(x) for x in virt.listAllDomains()]
    names = [x.name for x in vms]
    virt.close()
    return dict(zip(names, vms))


def get_virtual_machine(hostname):
    return get_virtual_machines().get(hostname)


def get_all_assigned_macaddresses():

    macs_assigned_to_vms = dict(
        [(n.macaddress, n.network)
         for v in get_virtual_machines().values() for n in v.nics])

    macs_assigned_to_net_bridges = dict(
        [(n.macaddress, n.name)
        for n in get_virtual_networks().values()])

    return merge_dicts(
        macs_assigned_to_vms,
        macs_assigned_to_net_bridges
    )


def generate_random_macaddress():
    digit = lambda: random.choice('0123456789ABCDEF')
    digits = [digit() for _ in xrange(6)]
    return "52:54:00:{}{}:{}{}:{}{}".format(*digits)


def get_network(cidr_block):
    return Subnet(cidr_block).to_dict()


def get_networks(domain, cidr_blocks):
    networks = []
    for block in cidr_blocks:
        data = get_network(block.get('cidr'))
        data['name'] = "{}.{}".format(block.get('name'), domain)
        networks.append(data)
    return networks


def get_instances(hostvars, domain, cidr_blocks):

    assigned_macaddresses = get_all_assigned_macaddresses()
    assigned_ip_addresses = get_all_assigned_ipv4_addresses()

    networks = get_networks(domain, cidr_blocks)
    instances = []

    def setup_host_nic(hostname, network):

        virtual_machine = get_virtual_machine(hostname)
        virtual_network = get_virtual_network(network.get('name'))

        macaddress = None
        ip_address = None

        if virtual_machine is not None and virtual_network is not None:
            data = virtual_network.get_by_hostname(hostname)
            if data is not None:
                macaddress = data.get('macaddress')
                ip_address = data.get('ipv4')
        else:

            macaddress = generate_random_macaddress()

            while macaddress in assigned_macaddresses:
                macaddress = generate_random_macaddress()

            assigned_macaddresses[macaddress] = hostname

            min_host = network.get("dhcp").get("range").get("start")
            max_host = network.get("dhcp").get("range").get("start")

            ip_address = increment_ipv4(min_host)
            while ip_address in assigned_ip_addresses:
                ip_address = increment_ipv4(ip_address)

            assigned_ip_addresses[ip_address] = hostname

        return macaddress, ip_address

    for hostname in hostvars.keys():

        data = hostvars[hostname]
        nics = []

        for network in networks:
            network_name = network.get('name')
            macaddress, ip_address = setup_host_nic(hostname, network)
            nics.append({
                "network"    : network_name,
                "macaddress" : macaddress,
                "model"      : "virtio",
                "ipv4"       : ip_address,
            })

        metadata = {
            "name"        : hostname,
            "cpus"        : data.get('cpus'),
            "memory"      : data.get('memory'),
            "nics"        : nics,
            "boot_disk"   : data.get('boot_disk')
        }

        if data.get('other_disks') is not None:
            metadata['other_disks'] = data.get('other_disks')

        instances.append(metadata)

    return instances


def list_snapshots(hosts):

    virt = libvirt.openReadOnly("qemu:///system")
    snapshots = [VirtualMachineSnapshot(snapshot)
                 for vm in virt.listAllDomains()
                 for snapshot in vm.listAllSnapshots()]
    virt.close()

    data = {}

    for x in snapshots:
        if x.virtual_machine_name not in data:
            data[x.virtual_machine_name] = []
        data[x.virtual_machine_name].append(x.snapshot_name)

    return [{"virutal_machine_name": vm, "snapshot_name": snap}
            for vm, snaps in data.iteritems()
for snap in snaps]


def list_vms_in_domain(domain):
    return [x for x in get_virtual_machines().keys() if domain in x]


def list_networks_in_domain(domain):
    return [x for x in get_virtual_networks().keys() if domain in x]


class FilterModule(object):

    def filters(self):
        return {
            'get_network'             : get_network,
            'get_networks'            : get_networks,
            'get_instances'           : get_instances,
            'list_snapshots'          : list_snapshots,
            'list_networks_in_domain' : list_networks_in_domain,
            'list_vms_in_domain'      : list_vms_in_domain,
        }
