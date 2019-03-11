FROM amsterdam/python
MAINTAINER datapunt@amsterdam.nl

ENV PYTHONUNBUFFERED 1

EXPOSE 8000

RUN mkdir -p /app && chown datapunt /app
RUN mkdir -p /static && chown datapunt /static
RUN mkdir -p /deploy && chown datapunt /deploy

COPY src /app/
COPY deploy /deploy/
COPY requirements.txt /requirements.txt

WORKDIR /app

ARG https_proxy=http://10.240.2.1:8080/
ENV https_proxy=$https_proxy

RUN pip install --cert /usr/local/share/ca-certificates/extras/adp_rootca.crt --no-cache-dir -r /requirements.txt

USER datapunt

RUN export DJANGO_SETTINGS_MODULE=config.settings

RUN python manage.py collectstatic --no-input

CMD uwsgi
