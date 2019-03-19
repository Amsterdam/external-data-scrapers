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

RUN pip install --no-cache-dir -r /requirements.txt

USER datapunt

RUN export DJANGO_SETTINGS_MODULE=config.settings

CMD python manage.py kv6sub
