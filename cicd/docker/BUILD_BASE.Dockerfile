FROM ubuntu:latest
SHELL ["/bin/bash", "-c"]

RUN date

RUN apt update

# Oracle client libaio1t64
RUN apt install curl net-tools unzip wget vim -y 

# Python and dependencies
RUN apt install -y python3
RUN apt install python3-pip -y
RUN apt install python3-venv -y

# install ansible
RUN UBUNTU_CODENAME=jammy && \
 wget -O- "https://keyserver.ubuntu.com/pks/lookup?fingerprint=on&op=get&search=0x6125E2A8C77F2818FB7BD15B93C4A3FD7BB9C367" | gpg --dearmour -o /usr/share/keyrings/ansible-archive-keyring.gpg && \
 echo "deb [signed-by=/usr/share/keyrings/ansible-archive-keyring.gpg] http://ppa.launchpad.net/ansible/ansible/ubuntu $UBUNTU_CODENAME main" | tee /etc/apt/sources.list.d/ansible.list && \
  apt update && apt install ansible -y

RUN mkdir /opt/director; cd /opt/director
WORKDIR /opt/director
RUN cd /opt/director && python3 -m venv .
RUN cd /opt/director && source bin/activate && \
pip install paramiko && \
pip install requests && \
deactivate
