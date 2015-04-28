FROM ubuntu

MAINTAINER Sapan 'Soup' Shah <soup@immuta.com>

RUN echo "deb http://archive.ubuntu.com/ubuntu/ $(lsb_release -sc) main universe" >> /etc/apt/sources.list

RUN apt-get update

RUN apt-get install -y tar git curl nano wget dialog net-tools build-essential

RUN apt-get install -y python python-dev python-distribute python-pip

RUN pip install flask

COPY my_application /usr/local/my_application

EXPOSE 80

WORKDIR /usr/local/my_application

CMD python server.py
