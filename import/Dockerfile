FROM amsterdam/python
MAINTAINER datapunt@amsterdam.nl

ENV PYTHONUNBUFFERED 1

EXPOSE 8000

COPY requirements.txt /requirements.txt

ARG https_proxy=http://10.240.2.1:8080/
ENV https_proxy=$https_proxy

RUN pip install --cert /usr/local/share/ca-certificates/extras/adp_rootca.crt --no-cache-dir -r /requirements.txt

COPY . /app/

WORKDIR /app
