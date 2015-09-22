# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"
VAGRANT_BOX = "puppetlabs/centos-7.0-64-nocm"


Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = VAGRANT_BOX

  # Expose 5000 to our host
  config.vm.network :forwarded_port, guest: 5000, host: 5000
  #
  # Install Base Packages
  config.vm.provision "shell", inline: "yum -y update"
  config.vm.provision "shell", inline: "yum -y install http://mirror.cs.pitt.edu/epel/7/x86_64/e/epel-release-7-5.noarch.rpm"
  config.vm.provision "shell", inline: "rpm --import /etc/pki/rpm-gpg/RPM-GPG-KEY-EPEL-7"
  config.vm.provision "shell", inline: "yum -y install python-pip python-devel libffi-devel"

  # Get Docker
  # Setup the docker repo file, this is a cheap hack since the 'ssh' user is vagrant which doesn't have
  # rights to write to /etc/yum.repos.d/docker.repo but the shell provision commands are run as root
  # so they can
  config.vm.provision "file",  source: "./docker_centos_7.repo", destination: "/tmp/docker.repo"
  config.vm.provision "shell", inline: "mv /tmp/docker.repo /etc/yum.repos.d/docker.repo"
  config.vm.provision "shell", inline: "yum -y install docker-engine"
  config.vm.provision "shell", inline: "service docker start"
  config.vm.provision "shell", inline: "usermod -a -G docker vagrant"

  # Install our application requireiments
  config.vm.provision "shell", inline: "pip install -r /vagrant/requirements.txt"
end
