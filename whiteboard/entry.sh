#!/bin/sh
set -e

orig=$*
cmd=$1
shift
  if[$cmd == 'web-local']; then
    #alembic revision --autogenerate -m 'operator base model'
    #alembic upgrade head
    python -m bin.start_api
  fi

exec $orig