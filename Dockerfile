FROM centos/postgresql-12-centos7

COPY ./database/dvdrental.tar /tmp/dvdrental.tar
COPY ./database/init-dvdrental-db.sh /usr/share/container-scripts/postgresql/start/init-dvdrental-db.sh
