#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 -U postgres <<-EOSQL
    CREATE USER app WITH PASSWORD '$POSTGRES_APP_PASSWORD';
    CREATE DATABASE app OWNER app;
EOSQL
