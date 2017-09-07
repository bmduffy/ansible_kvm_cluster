# Only need 4 playbooks to manage your cluster

provision:
	ansible-playbook ../../plays/provision.yml

startup:
	ansible-playbook ../../plays/startup.yml

shutdown:
	ansible-playbook ../../plays/shutdown.yml

teardown:
	ansible-playbook ../../plays/shutdown.yml
	ansible-playbook ../../plays/teardown.yml
