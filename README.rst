Squeezebox Zen Chimes
=====================
Zen Chimes is a server application that plays audio files by controlling the
Logitech Media Server through it's Command Line Interface plugin. The server-side
is implemented as a web server/REST API combination using Bottle. The client-side
uses Bootstrap, backbone.js and jQuery.

About The Chimes
----------------
Mindfulness and meditation are centuries-old practices for connecting an
individual to the person’s inner self and for establishing a consciousness of
love and harmony.

A gentle sound, often a bell or gong, is a wonderful reminder either to pause
for such contemplation or to sustain the individual’s uplifted awareness.


Installation
------------
Clone the repository. Edit ``extras/zenchimes.cfg`` and set parameters as
needed. Then run the ``install.sh`` shell script. Everything will be installed.
The appication will be owned by ``root:root`` and the server will run as
``nobody:nogroup``. The ``install.sh`` shell script must be run with superuser
privileges to manage everything.::

    $ git clone https://github.com/eigenholser/squeezebox-zenchimes.git
    $ cd squeezebox-zenchimes
    # add chimes and cover art to Logitech Media Server
    # edit extras/zenchimes.cfg
    $ sudo ./install.sh

Dependencies
------------
Ubuntu is ready for installation. On Raspian, install these dependencies
first::

    sudo apt-get install python-pip
    sudo apt-get install python-virtualenv
    sudo apt-get install m4
    sudo apt-get install sqlite3

Logitech Media Server
---------------------
Install the chimes and cover art on your Logitech Media Server. See links
for that. The chimes are located in ``static/mp3`` and the
cover art in ``static/images``.

See the `Logitech Media Server wiki <http://wiki.slimdevices.com/index.php/Main_Page>`_
for more information on installing audio files on the server.

Album Art
---------
Follow the `Album artwork instructions <http://wiki.slimdevices.com/index.php/Album_Artwork>`_
to add the album artwork to the Logitech Media Server. The cover and thumbs are
located in ``static/images``.

Chimes
------
There are some sample chimes inncluded but more can be added. Additional chimes
must be installed on the Logitech Media Server, added to the chimes sqlite3
database, and then copied into the ``static/mp3`` directory which is
buried in the Zen Chimes Python virtual environment. Once that is complete,
the chimes will be selectable through the web user interface.

MP3 Tagging
-----------
Use easytag or similar to add ID3 tags to custom chimes.::

    sudo apt-get install easytag

Troubleshooting
---------------
Check the logfiles for clues about misbehavior.

*  ``/var/log/upstart/zenchimes.log``
*  ``/usr/local/zenchimes/zenchimes.log``
