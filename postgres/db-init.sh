#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 -U postgres <<-EOSQL
    CREATE USER app WITH PASSWORD '$DB_PASSWORD';
    CREATE DATABASE app OWNER app;
EOSQL
