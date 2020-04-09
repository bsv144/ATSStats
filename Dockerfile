FROM tiangolo/uwsgi-nginx-flask:python3.7

ENV STATIC_INDEX 1

COPY requirements.txt /app/
RUN pip install -r /app/requirements.txt


COPY ./app /app