=======
libambx
=======

by Kyle Machulis <kyle@nonpolynomial.com>
Nonpolynomial Labs - http://www.nonpolynomial.com

Hardware Diagrams by Electrosthetics
http://electrosthetics.blogspot.com/

===========
Description
===========

libambx is an implementation of the control protocol for amBX ambient environment hardware. More information on ambx can be found at

http://www.ambx.com

Currently, the library is written in python while the protocol is being fleshed out. This will be turned into a C library once things are more stable.

============
Requirements
============

------
Python
------

Version 2.5 or greater
http://www.python.org

-----
PyUSB
-----

http://sourceforge.net/apps/mediawiki/pyusb/index.php?title=Main_Page

==================
Platform Specifics
==================

-------
Windows
-------

libambx will not work on windows unless the stock amBX driver is uninstalled and a libusb filter driver is installed. This will probably be the case permanently, as the windows drivers come with their own API and SDK. If you want to work with windows, get the amBX SDK. It's free, and I'll try to make a shim layer for it in libambx once we get things a little more stable
