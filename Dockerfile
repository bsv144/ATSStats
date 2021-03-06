FROM tiangolo/uwsgi-nginx-flask:python3.7

RUN apt-get update && apt-get install -y  unixodbc-dev nano

ENV STATIC_PATH /app/app/static

COPY requirements.txt /app/
RUN pip install -r /app/requirements.txt

