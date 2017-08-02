
FROM ubuntu:xenial

RUN apt update -y
RUN apt install -y git maven wget


RUN wget --no-cookies \
    --no-check-certificate \
    --header "Cookie: oraclelicense=accept-securebackup-cookie" \
    "http://download.oracle.com/otn-pub/java/jdk/8u131-b11/d54c1d3a095b4ff2b6607d096fa80163/jdk-8u131-linux-x64.tar.gz" \
    -O jdk-8u131-linux-x64.tar.gz
RUN tar xzvf jdk-8u131-linux-x64.tar.gz
RUN mv jdk1.8.0_131 /opt
ENV JAVA_HOME /opt/jdk1.8.0_131/

RUN  git clone https://github.com/deeplearning4j/dl4j-examples.git /opt/dl4j-examples
RUN cd /opt/dl4j-examples && mvn clean package
WORKDIR /opt/dl4j-examples
CMD exec /bin/bash -c "trap : TERM INT; sleep infinity & wait"
