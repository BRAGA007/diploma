#! /usr/bin/env bash

# Let the DB start
python /portal/app/backend_pre_start.py

# Run migrations
alembic upgrade head
