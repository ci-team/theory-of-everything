---
slug: 7/how-to-use-vagrant-with-sshfs-for-saltstack-tests
title: How to use Vagrant with sshfs for saltstack tests
author: bookwar
date: 2017-06-06 15:23:07
tags: how-to,saltstack,vagrant
categories: Knowledge Base
link: https://quantum-integration.org/topic/7/how-to-use-vagrant-with-sshfs-for-saltstack-tests
---

I often find myself writing salt configurations and therefore need an easy way to test, debug and write particular salt states. Here is how I manage that.

## Salt structure

I use a very simple layout for the saltstack repository with two main folders: *states* and *pillars* at the root level. Secrets are [gpg-encrypted](https://docs.saltstack.com/en/latest/ref/renderers/all/salt.renderers.gpg.html) and stay in the same repository in the *pillars/_secret* subfolder.
There is also a _secret_mock folder which mirrors the *_secret*  but contains unencrypted dummy values.

```txt
.
├── pillars
│   ├── ...
│   └── _secret
├── _secret_mock
├── states
├── minion.config
└── Vagrantfile

```

## Test environment
To test salt states you need salt minions. One can of course use docker, but I prefer to avoid the unnecessary complications and don't want to dig into kernel and system-level differences, so I use **Vagrant** with proper virtualization instead.

Since I use Fedora Linux workstation, I also prefer to use native Linux tools (nicely packaged and working out of the box) over the cross-platform toolchains provided by some third-parties. Thus I use Vagrant with **libvirt** vm provider.

Now, to test something we need a way to deliver the test data into the test environment. While Vagrant by default uses NFS to mount external volumes, I don't like it, as it required NFS server setup on the host machine, asks for root password,.. and generally I don't like NFS.

Fortunately, there is a [**vagrant-sshfs** plugin](https://fedoramagazine.org/vagrant-sharing-folders-vagrant-sshfs/). It is easy to setup, it doesn't require specific configuration on the host and/or client, it (as opposed to rsync) allows you to edit files on the fly from both host and guest command line without need to reload the vagrant box.

## Code snippets

To install requirements:
```bash
$ sudo dnf install vagrant vagrant-libvirt vagrant-sshfs
```
Here  is the *./Vagrantfile*:
```ruby

Vagrant.configure(2) do |config|

  config.vm.box = "debian/jessie64"
  config.vm.network "private_network", ip: "192.168.222.111"

  config.vm.synced_folder "./states", "/srv/salt/states", type: "sshfs"
  config.vm.synced_folder "./pillars", "/srv/salt/pillars", type: "sshfs"
  config.vm.synced_folder "./_secret_mock", "/srv/salt/pillars/_secret",
                          type: "sshfs",
                          # mock secrets are mounted on top of existing _secret folder
                          sshfs_opts_append: "-o nonempty" 

  # ca-certificates required for salt botstrap script to work
  config.vm.provision "shell",
                      inline: "apt-get update; apt-get -qq install ca-certificates curl"

  config.vm.provision :salt do |salt|
      salt.minion_config = "minion.config"
      salt.masterless = true

  end
end
```
and *./minion.config*:
```
file_client: local
file_roots:
  base:
    - /srv/salt/states
pillar_roots:
  base:
    - /srv/salt/pillars
```

