import virt_cluster

from virt_cluster import Subnet

if __name__ == "__main__":

    print "All assigned subnets"
    assigned_subnets = virt_cluster.get_all_assigned_subnets()
    for x in assigned_subnets.keys():
        print " >> {}".format(x)
        print Subnet(x)

    print "------\n{}".format(Subnet("20.0.0.100/24"))
    print "All assigned ipv4 addresses"
    assigned_ipv4s = virt_cluster.get_all_assigned_ipv4_addresses()
    for x in assigned_ipv4s.keys():
        print "> {}".format(x)
