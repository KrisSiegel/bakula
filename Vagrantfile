# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"
VAGRANT_BOX = "ubuntu/trusty64"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = VAGRANT_BOX

  # Expose 5000 to our host
  config.vm.network :forwarded_port, guest: 5000, host: 5000

  # Install all the needed packages
  config.vm.provision "shell", inline: "apt-get update"
  config.vm.provision "shell", inline: "apt-get -y install python-pip python-dev libffi-dev"
  config.vm.provision "shell", inline: "wget -qO- https://get.docker.com/ | sh"
  config.vm.provision "shell", inline: "gpasswd -a vagrant docker"
  config.vm.provision "shell", inline: "pip install -r /vagrant/requirements.txt"
  config.vm.provision "shell", inline: "apt-get -y install nodejs npm"
  config.vm.provision "shell", inline: "update-alternatives --install /usr/bin/node node /usr/bin/nodejs 10"
  config.vm.provision "shell", inline: "npm -g install bower"
  config.vm.provision "shell", inline: "cd /vagrant/ui; bower install --allow-root --config.interactive=false;"

end
