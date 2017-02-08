FROM python:2.7-alpine

MAINTAINER Massimo Santini "santini@di.unimi.it"

RUN pip install gunicorn

EXPOSE 8000

ARG userid=1000
RUN adduser -HD -u $userid tmuser

RUN mkdir /app && chown tmuser /app

WORKDIR /app

ENV PYTHONPATH=/app/tm
ENV TM_SETTINGS=/app/conf.py

CMD [ "gunicorn", "--log-level", "INFO", "--error-logfile", "-", "-w", "4", "-b", "0.0.0.0:8000" ,"tm.web:app" ]

ADD https://github.com/scythe-suite/tristo-mietitore/releases/download/v0.2.3/tm /app

RUN chown tmuser /app/tm

USER tmuser
