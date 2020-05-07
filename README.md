# PyPlayMusic
Python3-based player for music in a Google Play Music account.

Dependencies
------------------------------------------------------------
Tkinter, gmusicapi, urllib2, pillow, eyed3<br />
Python 3.5+ is also required.<br />
python-vlc is an optional dependency if you want to use VLC as the backend.


Ubuntu:<br />
`sudo apt install python3-pil python3-pil.imagetk python3-pip python3-gi`<br />
`sudo pip3 install gmusicapi eyed3`

Note About Player Backends
--------------------------
The default backend uses GStreamer 1.0 and should be available on
most current Gnome/GTK systems. There is a backup backend that uses
VLC. VLC needs to be installed to use it. Also, python-vlc needs to
be installed.<br />
Using pip on Ubuntu:<br />
`sudo pip3 install python-vlc`<br />
On Windows(Assuming python is on the path):<br />
`python3 -m pip install python-vlc`
