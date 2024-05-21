FROM python:3.11-slim

WORKDIR /portal
ENV PYTHONPATH=/portal

COPY ./requirements.txt /portal/
RUN pip install --no-cache-dir -r requirements.txt


COPY ./docker/scripts /portal/scripts
RUN chmod -R +x /portal/scripts/*.sh
COPY ./alembic.ini /portal/alembic.ini

COPY ./app /portal/app