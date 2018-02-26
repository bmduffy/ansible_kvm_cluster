
import libvirt
import xml.dom.minidom

# >> sudo virsh dumpxml node1.test.cluster.local
# <domain type='kvm'>
#   <name>node1.test.cluster.local</name>
#   <uuid>a8705aac-5a71-4dda-ad9b-ce5fa718c592</uuid>
#   <memory unit='KiB'>1048576</memory>
#   <currentMemory unit='KiB'>1048576</currentMemory>
#   <vcpu placement='static'>1</vcpu>
#   <os>
#     <type arch='x86_64' machine='pc-i440fx-rhel7.0.0'>hvm</type>
#     <boot dev='hd'/>
#   </os>
#   <features>
#     <acpi/>
#     <apic/>
#   </features>
#   <cpu mode='custom' match='exact' check='partial'>
#     <model fallback='allow'>Broadwell</model>
#   </cpu>
#   <clock offset='utc'>
#     <timer name='rtc' tickpolicy='catchup'/>
#     <timer name='pit' tickpolicy='delay'/>
#     <timer name='hpet' present='no'/>
#   </clock>
#   <on_poweroff>destroy</on_poweroff>
#   <on_reboot>restart</on_reboot>
#   <on_crash>destroy</on_crash>
#   <pm>
#     <suspend-to-mem enabled='no'/>
#     <suspend-to-disk enabled='no'/>
#   </pm>
#   <devices>
#     <emulator>/usr/libexec/qemu-kvm</emulator>
#     <disk type='file' device='disk'>
#       <driver name='qemu' type='qcow2'/>
#       <source file='/home/brian.duffy/libvirt/images/node1.test.cluster.local.test.cluster.local.disk.1'/>
#       <target dev='vda' bus='virtio'/>
#       <address type='pci' domain='0x0000' bus='0x00' slot='0x06' function='0x0'/>
#     </disk>
#     <controller type='usb' index='0' model='ich9-ehci1'>
#       <address type='pci' domain='0x0000' bus='0x00' slot='0x04' function='0x7'/>
#     </controller>
#     <controller type='usb' index='0' model='ich9-uhci1'>
#       <master startport='0'/>
#       <address type='pci' domain='0x0000' bus='0x00' slot='0x04' function='0x0' multifunction='on'/>
#     </controller>
#     <controller type='usb' index='0' model='ich9-uhci2'>
#       <master startport='2'/>
#       <address type='pci' domain='0x0000' bus='0x00' slot='0x04' function='0x1'/>
#     </controller>
#     <controller type='usb' index='0' model='ich9-uhci3'>
#       <master startport='4'/>
#       <address type='pci' domain='0x0000' bus='0x00' slot='0x04' function='0x2'/>
#     </controller>
#     <controller type='pci' index='0' model='pci-root'/>
#     <controller type='virtio-serial' index='0'>
#       <address type='pci' domain='0x0000' bus='0x00' slot='0x05' function='0x0'/>
#     </controller>
#     <interface type='network'>
#       <mac address='52:54:00:00:00:20'/>
#       <source network='test.eth0'/>
#       <model type='virtio'/>
#       <address type='pci' domain='0x0000' bus='0x00' slot='0x03' function='0x0'/>
#     </interface>
#     <serial type='pty'>
#       <target port='0'/>
#     </serial>
#     <console type='pty'>
#       <target type='serial' port='0'/>
#     </console>
#     <channel type='unix'>
#       <target type='virtio' name='org.qemu.guest_agent.0'/>
#       <address type='virtio-serial' controller='0' bus='0' port='1'/>
#     </channel>
#     <input type='tablet' bus='usb'>
#       <address type='usb' bus='0' port='1'/>
#     </input>
#     <input type='mouse' bus='ps2'/>
#     <input type='keyboard' bus='ps2'/>
#     <memballoon model='virtio'>
#       <address type='pci' domain='0x0000' bus='0x00' slot='0x07' function='0x0'/>
#     </memballoon>
#   </devices>
# </domain>

class VirtualMachine(object):

    class Memory(object):
        def __init__(self, value, unit):
            self.value = value
            self.unit  = unit

    class NIC(object):
        def __init__(self, macaddress, network, model_type):
            self.macaddress = macaddress
            self.network = network
            self.model_type = model_type

    def get_element_value(self, dom, tag):
        return dom.getElementsByTagName(tag)[0].firstChild.nodeValue

    def get_attribute_value(self, dom, tag, attr):
        return dom.getElementsByTagName(tag)[0].getAttribute(attr)

    def get_memory(self):
        return VirtualMachine.Memory(
            self.get_element_value(self.data, 'memory'),
            self.get_attribute_value(self.data, 'memory', 'unit')
        )

    def get_interfaces(self):
        interfaces = self.data.getElementsByTagName('interface')
        nics = []
        for x in interfaces:
            if x.getAttribute('type') != 'network': continue
            nics.append(
                VirtualMachine.NIC(
                    self.get_attribute_value(x, 'mac', 'address'),
                    self.get_attribute_value(x, 'source', 'network'),
                    self.get_attribute_value(x, 'model', 'type')
                )
            )
        return nics

    def process_xml_data(self):

        self.name   = self.get_element_value(self.data, 'name')
        self.uuid   = self.get_element_value(self.data, 'uuid')
        self.memory = self.get_memory()
        self.cpus   = self.get_element_value(self.data, 'vcpu')
        self.nics   = self.get_interfaces()

    def __init__(self, libvirt_domain):
        self.data = xml.dom.minidom.parseString(
            libvirt_domain.XMLDesc(0))
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

def get_vms():
    virt = libvirt.openReadOnly("qemu:///system")
    vms = [VirtualMachine(x) for x in virt.listAllDomains()]
    names = [x.name for x in vms]
    virt.close()
    return dict(zip(names, vms))

def get_networks():
    virt = libvirt.openReadOnly("qemu:///system")
    networks = virt.listAllNetworks()
    virt.close()
    return networks

def get_assigned_macaddresses():
    return dict([(n.macaddress, n.network)
                 for v in get_vms().values() for n in v.nics])

def is_macaddress_assigned(macaddress):
    return macaddress in get_assigned_macaddresses()

if __name__ == "__main__":
    vms = get_vms()
    for vm in vms.values():
        print vm
    print get_assigned_macaddresses()
