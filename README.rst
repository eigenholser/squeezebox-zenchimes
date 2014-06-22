Squeezebox Zen Chimes
=====================
Zen Chimes is a server application that plays audio files by controlling the
Logitech Media Server through it's Command Line Interface plugin. The server-side
is implemented as a web server/REST API combination using Bottle. The client-side
uses Bootstrap, backbone.js and jQuery.

About The Chimes
----------------


Installation
------------
Clone the repository. Edit extras/zenchimes.cfg and set parameters as needed.
Then run the install.sh shell script. Everything will be installed. The
appication will be owned by nobody:nogroup and the server will also run as
nobody:nogroup. The install.sh shell script must be run with superuser
privileges to manage everything.

Logitech Media Server
---------------------
Install the chimes and cover art on your Logitech Media Server. See links
for that. TODO: add links. The chimes are located in public/media and the
cover art in lms.
http://wiki.slimdevices.com/index.php/Main_Page

Album Art
http://wiki.slimdevices.com/index.php/Album_Artwork

Chimes
------
There are some sample chimes inncluded but more can be added. Additional chimes
must be installed on the Logitech Media Server, added to the chimes sqlite3
database, and then copied into the static/media directory which is deeply
buried in the Zen Chimes Python virtual environment. Once that is complete,
the chimes will be selectable through the web user interface.

MP3 Tagging
-----------
Use easytag or similar.
sudo apt-get install easytag

Troubleshooting
---------------
Check /var/log/upstart/zenchimes.log
Check /usr/local/zenchimes/zenchimes.log
