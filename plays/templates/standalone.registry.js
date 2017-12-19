[OSEv3:children]
masters
nodes

[OSEv3:vars]
ansible_ssh_user=root

openshift_master_default_subdomain=ocp.cluster
openshift_use_dnsmasq=false
deployment_type=openshift-enterprise
deployment_subtype=registry

openshift_master_identity_providers=[{'name': 'htpasswd_auth', 'login': 'true', 'challenge': 'true', 'kind': 'HTPasswdPasswordIdentityProvider', 'filename': '/etc/origin/master/htpasswd'}]
openshift_master_htpasswd_users={'admin': 'passw0rd'}

[masters]
registry.ocp.cluster

[nodes]
registry.ocp.cluster openshift_node_labels="{'region': 'infra', 'zone': 'default'}" openshift_schedulable=true
