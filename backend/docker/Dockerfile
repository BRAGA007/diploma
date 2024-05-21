FROM python:3.11

WORKDIR /portal
ENV PYTHONPATH=/portal

COPY ./requirements.txt /portal/
RUN pip install --no-cache-dir -r requirements.txt

COPY ./docker/scripts /portal/scripts
RUN chmod -R +x /portal/scripts/*.sh
COPY ./alembic.ini ./pyproject.toml ./setup.cfg /portal/

COPY ./app /portal/app
