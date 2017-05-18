FROM python:2.7

RUN apt-get update
RUN apt-get -y upgrade

# Add requirements.txt
RUN mkdir /opt/pdfkit
ADD requirements.txt /opt/requirements.txt

# Install app requirements
RUN pip install -r /opt/requirements.txt

# Create app directory
ADD . /opt/pdfkit
 
# Set the default directory for our environment
ENV HOME /opt/pdfkit
WORKDIR /opt/pdfkit
 
CMD [ "python", "./render.py" ]
