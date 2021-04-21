#!/bin/sh

BENCHMARK=$1
[ ! -z "$BENCHMARK" ] && shift;

case $BENCHMARK in
init)
  cd pg/init
  exec python ./main.py $@;
user)
  cd pg/user
  exec python ./main.py $@;
  ;;
app)
  cd pg/app
  exec python ./main.py $@;
  ;;
*)
  echo "$BENCHMARK is not a valid benchmark. Please select a supported benchmark to run: [pg/user|pg/app]";
  ;;
esac