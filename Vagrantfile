# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure(2) do |config|

  config.vm.box = "debian/jessie64"

  # The private network is 192.168.10.0/24
  # The host will get IP 192.168.10.1
  config.vm.network "private_network", ip: "192.168.10.10"

  config.vm.provision "file", source: "bootstrap.sh", destination: "bootstrap.sh"

end
