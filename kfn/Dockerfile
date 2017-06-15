FROM ubuntu:16.04

RUN apt-get update
RUN apt-get install kafkacat

#ENV WORK_DIR /var/offlineimap
#ENV REMOTE_USER ''
#ENV OAUTH2_CLIENT_ID ''
#ENV OAUTH2_CLIENT_SECRET ''
#ENV OAUTH2_REFRESH_TOKEN ''
#
#
#RUN apt-get update
#RUN apt-get install -y git
#RUN pip install Jinja2
#RUN pip install jinja2-cli
#
#ADD offlineimap_config.j2 /tmp/offlineimap_config.j2
#
#RUN mkdir ${WORK_DIR}
#
#RUN mkdir /opt/offlineimap
#RUN git clone -b docker https://github.com/styk-tv/offlineimap.git /opt/offlineimap
#RUN cd /opt/offlineimap && python setup.py install
#
#CMD echo "{\"remote_user\":\"$REMOTE_USER\",\"volume_mount_path\":\"$WORK_DIR\",\"oauth2_client_id\":\"$OAUTH2_CLIENT_ID\",\"oauth2_client_secret\":\"$OAUTH2_CLIENT_SECRET\",\"oauth2_refresh_token\":\"$OAUTH2_REFRESH_TOKEN\"}" | jinja2 /tmp/offlineimap_config.j2 --format=json >/root/.offlineimaprc & /usr/bin/python2.7 /opt/offlineimap/offlineimap.py
#
