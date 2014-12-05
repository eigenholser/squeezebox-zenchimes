#!/bin/bash
#
# install zen chimes
#
# This shell script installs the zen chimes app. The files are owned by
# nobody:nogroup which is also how the server runs. This shell script needs
# to run as root to set the ownership properly.

# Must run as root
if [ `id -u` != 0 ]; then
    echo "Please run as root: sudo ./install.sh"
    exit 1
fi

if [ -e /etc/redhat_release ]; then
    echo "Not tested at all on Redhat."
    exit 1
fi

# But if not sudo, compensate.
if [ -z $SUDO_USER ]; then
    SUDO_USER=root
fi

# Set override config settings via environment variables. Non-default settings
# changes should be made in `env.sh'.
sh env.sh

# Set sane default values.
[ ! -z $SERVER_HTTP_LISTEN_PORT ] && SERVER_HTTP_LISTEN_PORT=3031
[ ! -z $TCP_LOGGING_PORT ] && TCP_LOGGING_PORT=8020
[ ! -z $ZMQ_CONTROL_PORT ] && ZMQ_CONTROL_PORT=5000
[ ! -z $LOGGING_LEVEL ] && LOGGING_LEVEL="DEBUG"

# Want to install on recent Ubuntu only.
if [ -e /usr/bin/lsb_release ]; then
    # Ubuntu
    SERVER_STARTUP_SOURCE=extras/zenchimes_upstart.m4
    SERVER_STARTUP_FILE=/etc/init/zenchimes_server.conf
    SERVER_STARTUP_CMD="/sbin/start zenchimes_server"
    # Stop zenchimes if it is running.
    if [ -f $SERVER_STARTUP_FILE ]; then
        /sbin/status zenchimes_server | grep --silent running
        if [ $? == 0 ]; then
            stop zenchimes_server
            sleep 1
        fi
    fi

    SCHEDULER_STARTUP_SOURCE=extras/zenchimes_scheduler_upstart.m4
    SCHEDULER_STARTUP_FILE=/etc/init/zenchimes_scheduler.conf
    SCHEDULER_STARTUP_CMD="/sbin/start zenchimes_scheduler"
    # Stop zenchimes if it is running.
    if [ -f $SCHEDULER_STARTUP_FILE ]; then
        /sbin/status zenchimes_scheduler | grep --silent running
        if [ $? == 0 ]; then
            stop zenchimes_scheduler
            sleep 1
        fi
    fi
fi

#echo "Please specify installation prefix [/usr/local]: "
#read install_prefix
# TODO: This is hardwired for now. Need to do some reasonable validation to
# protect the innocent.
install_prefix=/usr/local
install_dir="${install_prefix}/zenchimes"

export PYTHON_HOME="${install_dir}/env"

# Create install directory
/usr/bin/install --group root --owner $SUDO_USER --directory $install_dir

# Install chimes sqlite3 database
[ -e $install_dir/zenchimes.db ] && rm $install_dir/zenchimes.db
/usr/bin/sqlite3 $install_dir/zenchimes.db < extras/chimes.sql
/usr/bin/sqlite3 $install_dir/zenchimes.db < extras/config.sql
# Service runs as user `nobody'. Database must be writable.
chown nobody:nogroup $install_dir/zenchimes.db

# Setup Python virtual environment and install requirements
if [ -e ${install_dir}/env ]; then
    chown -R $SUDO_USER $install_dir/env
else
    su $SUDO_USER -c "virtualenv ${install_dir}/env"
fi

# TODO: This is not permanent. Remove the existing package and make a new one.
# It's gonna break if we bump the __version__.
su $SUDO_USER -c "rm dist/zenchimes-0.1.tar.gz; python setup.py sdist"

su $SUDO_USER -c "source $install_dir/env/bin/activate; pip install -r requirements/install.txt"
su $SUDO_USER -c "source $install_dir/env/bin/activate; pip install dist/zenchimes-0.1.tar.gz"

export PROJECT_ROOT=`su $SUDO_USER -c "cd $install_dir; source env/bin/activate; python -c 'from zenchimes import settings; print settings.PROJECT_ROOT;'"`

# Install upstart files.
# Web server
/usr/bin/m4 \
    --define=__INSTALL_DIR__=$install_dir \
    --define=__PROJECT_ROOT__="${PROJECT_ROOT}" \
    --define=__SERVER_HTTP_LISTEN_PORT__=$SERVER_HTTP_LISTEN_PORT \
    --define=__TCP_LOGGING_PORT__=$TCP_LOGGING_PORT \
    --define=__ZMQ_CONTROL_PORT__=$ZMQ_CONTROL_PORT \
    --define=__LOGGING_LEVEL__="${LOGGING_LEVEL}" \
    $SERVER_STARTUP_SOURCE > $SERVER_STARTUP_FILE

# Scheduler daemon
/usr/bin/m4 \
    --define=__INSTALL_DIR__=$install_dir \
    --define=__PROJECT_ROOT__="${PROJECT_ROOT}" \
    --define=__TCP_LOGGING_PORT__=$TCP_LOGGING_PORT \
    --define=__ZMQ_CONTROL_PORT__=$ZMQ_CONTROL_PORT \
    --define=__LOGGING_LEVEL__="${LOGGING_LEVEL}" \
    $SCHEDULER_STARTUP_SOURCE > $SCHEDULER_STARTUP_FILE

chown root:root $SERVER_STARTUP_FILE
chown root:root $SCHEDULER_STARTUP_FILE

# Had to do this trick because I didn't want to run pip as root.
chown nobody:nogroup $install_dir
chown -R nobody:nogroup $install_dir/env

# Start the services
$SERVER_STARTUP_CMD
$SCHEDULER_STARTUP_CMD
