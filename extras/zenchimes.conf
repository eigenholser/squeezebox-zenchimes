# zenchimes - Zen Chimes Logitech Media Server Client

description     "Zen Chimes Logitech Media Server Client"
author          "eigenholser <eigenholser@gmail.com>"

start on startup
stop on shutdown
respawn
respawn limit 3 12
setuid nobody
setgid nogroup

env PYTHON_HOME=__INSTALL_DIR__/env
exec $PYTHON_HOME/bin/python __PROJECT_ROOT__/server.py
