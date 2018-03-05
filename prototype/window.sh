#!/bin/bash

# vagrant init peru/windows-10-enterprise-x64-eval \
#   --box-version 20180226.01
# vagrant up

Vagrant.configure("2") do |config|
  config.vm.box = "peru/windows-10-enterprise-x64-eval"
  config.vm.box_version = "20180226.01"
end
