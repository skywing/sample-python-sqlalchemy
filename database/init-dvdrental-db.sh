#!/bin/sh

db_exists=`echo "select count(*) from pg_database where datname = 'dvdrental';" | psql -qAt -d postgres`
if [ $db_exists -eq 0 ]
then
    echo "creating DVD rental database..."
    set -e
    psql -v ON_ERROR_STOP=1 --username "postgres" <<-EOSQL
      CREATE DATABASE dvdrental;
EOSQL
  echo "DVD rental database created."
  echo "Restoring DVD rental data from dvdrental.tar..."
  pg_restore -U postgres -d dvdrental /tmp/dvdrental.tar
  echo "DVD rental database restore completed."
else
  echo "dvd rental database exists!!!! Skip creating."
fi
