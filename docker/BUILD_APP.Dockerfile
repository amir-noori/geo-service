FROM geoubuntu:latest
SHELL ["/bin/bash", "-c"]
ARG mode

RUN if [ "$mode"="dev" ] ; then \
    echo "dev mode"; \
    apt install net-tools -y; \
    apt install vim -y; \
    apt install telnet -y; \
    apt install curl -y; \
fi

WORKDIR /opt/app
ENV LD_LIBRARY_PATH=/opt/oracle/instantclient_21_4

COPY ./ /opt/app 
# ENTRYPOINT ["/opt/app/startup.sh"]


