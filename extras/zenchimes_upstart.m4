# zenchimes - Zen Chimes Logitech Media Server Client

description     "Zen Chimes Logitech Media Server Client"
author          "eigenholser <eigenholser@gmail.com>"

start on startup
stop on shutdown
respawn
respawn limit 3 12
setuid nobody
setgid nogroup

env SERVER_HTTP_LISTEN_PORT=__SERVER_HTTP_LISTEN_PORT__
env TCP_LOGGING_PORT=__TCP_LOGGING_PORT__
env ZMQ_CONTROL_PORT=__ZMQ_CONTROL_PORT__
env LOGGING_LEVEL=__LOGGING_LEVEL__
env PYTHON_HOME=__INSTALL_DIR__/env

exec $PYTHON_HOME/bin/python __PROJECT_ROOT__/server.py
