# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"
VAGRANT_BOX = "ubuntu/trusty64"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = VAGRANT_BOX

  # Expose 4242 to our host
  config.vm.network :forwarded_port, guest: 4242, host: 4242

  # Install all the needed packages
  config.vm.provision "shell", inline: "apt-get update"
  config.vm.provision "shell", inline: "apt-get -y install python-pip python-dev"
  config.vm.provision "shell", inline: "wget -qO- https://get.docker.com/ | sh"
  config.vm.provision "shell", inline: "gpasswd -a vagrant docker"
  config.vm.provision "shell", inline: "pip install -r /vagrant/requirements.txt"

end
