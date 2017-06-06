FROM python:2.7

RUN apt-get update

# Install wkhtmltopdf
RUN curl -L#o wk.tar.xz https://downloads.wkhtmltopdf.org/0.12/0.12.4/wkhtmltox-0.12.4_linux-generic-amd64.tar.xz \
    && tar xf wk.tar.xz \
    && cp wkhtmltox/bin/wkhtmltopdf /usr/bin \
    && cp wkhtmltox/bin/wkhtmltoimage /usr/bin \
    && rm wk.tar.xz \
    && rm -r wkhtmltox

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
 
CMD [ "python", "./render_template.py" ]
