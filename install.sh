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

# But if not sudo, compensate.
if [ -z $SUDO_USER ]; then
    SUDO_USER=root
fi

# Stop zenchimes if it is running.
status zenchimes | grep --silent running
if [ $? == 0 ]; then
    stop zenchimes
    sleep 1
fi

echo "Please specify installation prefix [/usr/local]: "

read install_prefix
# TODO: This is hardwired for now. Need to do some reasonable validation to
# protect the innocent.
install_prefix=/usr/local
install_dir="${install_prefix}/zenchimes"

export PYTHON_HOME="${install_dir}/env"

# Create install directory
/usr/bin/install --group root --owner $SUDO_USER --directory $install_dir

# Install zenchimes program files
if [ ! -e "${install_dir}/zenchimes.cfg" ]; then
    # Service runs as user `nobody'. Configuration file must be writable.
    /usr/bin/install --group nogroup --owner nobody --target-directory \
        $install_dir extras/zenchimes.cfg
fi

# Install chimes sqlite3 database
[ -e $install_dir/chimes.db ] && rm $install_dir/chimes.db
/usr/bin/sqlite3 $install_dir/chimes.db < extras/chimes.sql
# Service runs as user `nobody'. Database must be writable.
chown nobody:nogroup $install_dir/chimes.db

# Create logfile
[ -e $install_dir/zenchimes.log ] && rm $install_dir/zenchimes.log
touch $install_dir/zenchimes.log
chown nobody:nogroup $install_dir/zenchimes.log

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

# Install upstart file
/usr/bin/m4 \
    --define=__INSTALL_DIR__=$install_dir \
    --define=__PROJECT_ROOT__="${PROJECT_ROOT}" \
    extras/zenchimes.conf > /etc/init/zenchimes.conf
chown root:root /etc/init/zenchimes.conf

# Had to do this trick because I didn't want to run pip as root.
chown root:root $install_dir
chown -R root:root $install_dir/env

# Start the service
/sbin/start zenchimes
