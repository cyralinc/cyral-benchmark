#!/bin/sh

SUBCOMMAND=$1
[ ! -z "$SUBCOMMAND" ] && shift;

case $SUBCOMMAND in
init)
  cd pg/init
  exec python ./main.py $@;
  ;;
user)
  cd pg/user
  exec python ./main.py $@;
  ;;
app)
  cd pg/app
  exec python ./main.py $@;
  ;;
*)
  echo "$SUBCOMMAND is not a valid subcommand. Please select a supported subcommand to run: [init|user|app]";
  ;;
esac