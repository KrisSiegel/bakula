# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"
VAGRANT_BOX = "puppetlabs/centos-7.0-64-nocm"


Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = VAGRANT_BOX

  # Expose 5000 to our host
  config.vm.network :forwarded_port, guest: 5000, host: 5000

  # Bump up memory
  config.vm.provider :virtualbox do |vb|
    vb.customize ["modifyvm", :id, "--memory", "2048"]
  end
  #
  # Install Base Packages
  config.vm.provision "shell", inline: "yum -y update"
  config.vm.provision "shell", inline: "yum -y install http://download.fedoraproject.org/pub/epel/7/x86_64/e/epel-release-7-5.noarch.rpm"
  config.vm.provision "shell", inline: "rpm --import /etc/pki/rpm-gpg/RPM-GPG-KEY-EPEL-7"
  config.vm.provision "shell", inline: "yum -y install python-pip python-devel libffi-devel"

  # Get and start Docker
  config.vm.provision "shell", inline: "curl -sSL https://get.docker.com/ | sh"
  config.vm.provision "shell", inline: "service docker start"
  config.vm.provision "shell", inline: "usermod -a -G docker vagrant"

  # Clearing out the iptables rules so that the host machine can
  # access the services on the VM
  config.vm.provision "shell", inline: "iptables -F"

  # Install our application requireiments
  config.vm.provision "shell", inline: "pip install -r /vagrant/requirements.txt"
end
