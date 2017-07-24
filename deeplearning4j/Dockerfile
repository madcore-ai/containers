FROM nvidia/cuda:8.0-cudnn6-devel-centos7
MAINTAINER Skymind Inc <help@skymind.io>


RUN  yum-config-manager --enable rhel-server-rhscl-7-rpms
RUN yum -y install wget epel-release pciutils kernel-devel-"$(uname -r)" kernel-headers-"$(uname -r)" dkms perl
RUN yum -y install centos-release-scl git
RUN yum -y install devtoolset-4-toolchain 
RUN scl enable devtoolset-4 bash


ENV LD_PRELOAD /lib64/libgomp.so.1
RUN echo 'export LD_PRELOAD=/lib64/libgomp.so.1' >> /etc/profile.d/mkl.sh

RUN echo 'source /opt/rh/devtoolset-4/enable' >> /etc/profile.d/softwarecollections.sh && chmod +x /etc/profile.d/softwarecollections.sh

RUN yum -y groupinstall "Development Tools"
COPY install_openblas.sh /opt/install_openblas.sh
RUN chmod +x /opt/install_openblas.sh
RUN /opt/install_openblas.sh

ADD https://s3-us-west-2.amazonaws.com/skil-distro/apache-maven-3.3.9-bin.tar.gz /apache-maven-3.3.9-bin.tar.gz
RUN mv /apache-maven-*/apache-maven-* /opt/mvn
#ADD https://s3-us-west-2.amazonaws.com/skil-distro/cmake-3.5.2-Linux-x86_64.tar.gz cmake-3.5.2-Linux-x86_64.tar.gz
#RUN mv cmake-3.5.2-Linux-x86_64.tar.gz/cmake-* /opt/cmake


RUN wget --no-cookies \
    --no-check-certificate \
    --header "Cookie: oraclelicense=accept-securebackup-cookie" \
    "http://download.oracle.com/otn-pub/java/jdk/8u131-b11/d54c1d3a095b4ff2b6607d096fa80163/jdk-8u131-linux-x64.tar.gz" \
    -O jdk-8u131-linux-x64.tar.gz
RUN tar xzvf jdk-8u131-linux-x64.tar.gz
RUN mv jdk1.8.0_131 /opt
ENV JAVA_HOME /opt/jdk1.8.0_131/
RUN echo "SETTING UP MAVEN"

RUN ln -s /opt/mvn/bin/mvn /usr/bin/mvn
#Ensure that the right gcc/g++ is being used for centos
ENV CC /opt/rh/devtoolset-4/root/usr/bin/gcc
ENV CXX /opt/rh/devtoolset-4/root/usr/bin/g++
RUN rm /usr/bin/g++ && ln -s  /opt/rh/devtoolset-4/root/usr/bin/g++ /usr/bin/g++
RUN rm /usr/bin/gcc && ln -s  /opt/rh/devtoolset-4/root/usr/bin/gcc  /usr/bin/gcc

ENV PATH $PATH:/opt/cmake/bin:$JAVA_HOME/bin:/opt/mvn/bin

RUN git clone --depth 1 https://github.com/bytedeco/javacpp /opt/javacpp
RUN ls -alh /opt/mvn
RUN cd /opt/javacpp && mvn clean install -DskipTests

#ENV TRICK_NVCC "YES"
#ENV LD_LIBRARY_PATH /usr/local/nvidia/lib:/usr/local/nvidia/lib64:$LD_LIBRARY_PATH:/usr/local/mkl/lib/intel64:/usr/local/mkl/lib/intel64_lin:/usr/local/mkl/lib/intel64_lin_mic
#RUN ldconfig
#ENV PATH $PATH:/usr/local/cuda-8.0/bin
#RUN apt install -y nvidia-cuda-dev nvidia-cuda-toolkit nvidia-361
RUN yum install -y centos-release-scl-rh epel-release
RUN yum install -y devtoolset-3-toolchain maven30 cmake3 git
RUN scl enable devtoolset-3 maven30 bash
RUN export TRICK_NVCC=YES
RUN git clone https://github.com/deeplearning4j/libnd4j /opt/libnd4j
RUN /opt/libnd4j/buildnativeoperations.sh
RUN /opt/libnd4j/buildnativeoperations.sh -c cuda -сс 37

#RUN /opt/libnd4j/buildnativeoperations.sh -c cuda
#RUN /opt/libnd4j/buildnativeoperations.sh
#ENV LIBND4J_HOME /opt/libnd4j/


RUN rm -rf /opt/nd4j && git clone --depth 1 https://github.com/deeplearning4j/nd4j /opt/nd4j
RUN /opt/nd4j/buildmultiplescalaversions.sh clean install -DskipTests -Dmaven.javadoc.skip=true

RUN rm -rf /opt/DataVec && git clone https://github.com/deeplearning4j/DataVec /opt/DataVec
RUN cd /opt/DataVec  && chmod +x ./change-scala-versions.sh && ./buildmultiplescalaversions.sh  clean install -DskipTests

RUN rm -rf /opt/deeplearning4j && git clone  https://github.com/deeplearning4j/deeplearning4j /opt/deeplearning4j
RUN cd /opt/deeplearning4j && chmod +x ./change-scala-versions.sh && cd /opt/deeplearning4j && ./buildmultiplescalaversions.sh -P !testresources clean install -DskipTests

RUN rm -rf /opt/Arbiter && git clone https://github.com/deeplearning4j/Arbiter /opt/Arbiter
RUN cd /opt/Arbiter  && chmod +x ./change-scala-versions.sh && ./buildmultiplescalaversions.sh  clean install -DskipTests


