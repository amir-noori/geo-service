

### for ansible connection setup

1- 

    ssh-keygen # with empty pass
    ssh-copy-id user@ip


2- create inventory:

    [apps]
    192.168.150.10
    192.168.160.10


### ansible commands:

ping:

    # ping apps with user vagrant
    ansible -i inventory apps -m ping -u vagrant

    # rm files
    ansible -i inventory apps -a "rm -rf /tmp/src/src" -u vagrant

    # run playbook
    ansible-playbook cicd/playbooks/deploy_apps.yaml -i cicd/inventory/dev.inv



### general commands:

    # add user to docker group:
    sudo usermod -a -G docker vagrant