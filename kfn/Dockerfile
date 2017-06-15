FROM ubuntu:16.04

ENV PATH_BASE /var/kfn
ENV PATH_DATA /opt/kfn

RUN mkdir -p $PATH_BASE
RUN mkdir -p $PATH_DATA

RUN apt-get update
RUN apt-get install librdkafka-dev libyajl-dev -y
RUN apt-get install kafkacat -y
RUN apt-get install python-pip -y
RUN pip install kafka-python
RUN pip install neo4j-driver

ADD examples/consumer.py $PATH_BASE/examples/consumer.py
ADD examples/producer.py $PATH_BASE/examples/producer.py
