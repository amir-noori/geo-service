FROM geoubuntu:latest
SHELL ["/bin/bash", "-c"]
ARG mode

RUN if [ "$app_level"="dev" ] ; then \
    echo "dev mode"; \
    apt install net-tools -y; \
    apt install vim -y; \
    apt install telnet -y; \
    apt install curl -y; \
fi

# symlink for libaio cause oracledb looks for libaio.so.1 instead of 64 version
RUN ln -s /lib/x86_64-linux-gnu/libaio.so.1t64.0.2 /lib/x86_64-linux-gnu/libaio.so.1

WORKDIR /opt/app
ENV LD_LIBRARY_PATH=/opt/oracle

COPY ./ /opt/app 
# ENTRYPOINT ["/opt/app/startup.sh"]


