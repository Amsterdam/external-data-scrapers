FROM amsterdam/python
MAINTAINER datapunt@amsterdam.nl

ENV PG_VERSION 11

RUN apt-get install -y \
        lsb-release \
        curl \
    && curl --insecure https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - \
    && echo "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -sc)-pgdg main $PG_VERSION" > /etc/apt/sources.list.d/pgdg.list \
    && apt-get update

RUN apt-get remove postgresql-client-9.6 -y \
    && apt-get install -y \
        postgresql-client-$PG_VERSION \
        gdal-bin

ENV PYTHONUNBUFFERED 1
EXPOSE 8000

RUN mkdir -p /app && chown datapunt /app
RUN mkdir -p /static && chown datapunt /static
RUN mkdir -p /deploy && chown datapunt /deploy

COPY requirements.txt /requirements.txt
COPY requirements-django.txt /requirements-django.txt
RUN pip install --no-cache-dir -r /requirements.txt -r /requirements-django.txt

COPY src /app/
COPY deploy /deploy/

WORKDIR /app

USER datapunt

ENV DJANGO_SETTINGS_MODULE config.settings
ENV REQUESTS_CA_BUNDLE /etc/ssl/certs/ca-certificates.crt

RUN python manage.py collectstatic --no-input

CMD uwsgi
