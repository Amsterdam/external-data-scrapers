FROM amsterdam/python
MAINTAINER datapunt@amsterdam.nl

ENV PYTHONUNBUFFERED 1

EXPOSE 8000

COPY requirements.txt /requirements.txt

RUN pip install --no-cache-dir -r /requirements.txt

COPY . /app/

ENV REQUESTS_CA_BUNDLE /etc/ssl/certs/ca-certificates.crt

WORKDIR /app
