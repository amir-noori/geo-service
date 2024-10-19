FROM ubuntu:latest
SHELL ["/bin/bash", "-c"]

RUN apt update

# Oracle client libaio1t64
RUN apt install libaio1t64 unzip wget -y 
ENV LD_LIBRARY_PATH=/opt/oracle
RUN mkdir -p /opt/oracle
COPY ./lib/instantclient_21_4_ /opt/oracle

# Python and dependencies
RUN apt install -y python3
RUN apt install python3-pip -y
RUN apt install python3-venv -y
RUN apt install pipx -y
RUN cd /opt
RUN mkdir /opt/app; cd /opt/app
WORKDIR /opt/app
RUN cd /opt/app && python3 -m venv .
RUN pwd
RUN ls -l
RUN cd /opt/app && source bin/activate && \
    pip install oracledb && \
    pip install "fastapi[standard]" && \
    pip install shapely && \
    pip install requests && \
    deactivate
