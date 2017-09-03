#!/bin/bash

sed -i -E 's/PubkeyAuthentication no/PubkeyAuthentication yes/g' /etc/ssh/sshd_config
sed -i -E 's/PasswordAuthentication no/PasswordAuthentication yes/g' /etc/ssh/sshd_config
restorecon -F /root/.ssh /root/.ssh/authorized_keys
localectl set-x11-keymap {{ keymap }}
