FROM geoubuntu:latest
SHELL ["/bin/bash", "-c"]



# symlink for libaio cause oracledb looks for libaio.so.1 instead of 64 version
RUN ln -s /lib/x86_64-linux-gnu/libaio.so.1t64.0.2 /lib/x86_64-linux-gnu/libaio.so.1


RUN useradd -ms /bin/bash foo
RUN chmod 777 -R /opt

USER foo

ENV LD_LIBRARY_PATH=/opt/oracle

COPY ./ /opt/app 
WORKDIR /opt/app


ENTRYPOINT ["geoservice/startup.sh"]


