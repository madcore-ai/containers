FROM ubuntu:16.04

ENV PATH_BASE /var/xlswriter
ENV PATH_DATA /opt/xlswriter

RUN mkdir -p $PATH_BASE
RUN mkdir -p $PATH_DATA

COPY . $PATH_BASE

RUN apt-get update
RUN apt-get install librdkafka-dev libyajl-dev kafkacat python-pip dnsutils nano -y

RUN pip install -r $PATH_BASE/requirements.txt

