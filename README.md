wintools
========

Some tools I wrote when I was on Windows. This repository is more of a nostalgia tour than anything else. If you're looking for a full suite of POSIX tools, try cygwin. If you're looking for a one-off script, please feel free :-)



My Google-fu used to be apalling. Back when I was at uni, and before I truly started exploring Linux/GNU and its rich command set, I found that I was lacking a few tools for day-to-day work. Using the tools I had at the time, I came up with what you see in this directory.

All of them seem to have equivalents in standard utilities, so are kinda worthless on Linux, BSD and OS X, except for the corner cases they were written for...

Tools
=====

chop
----

Written in Python 2

Before I found out that you could use the *nix `split` command, I had to come up with my own way of splitting long text files.

`chop` is the result of this, though to achieve the same results would probably need to combine `split`, `grep` and `sed`...

It doesn't process by size, and cannot take binary files as it works by doing line matching; but you can define a regular expression that will serve to identify the start of a new section, causing the file to be split according to content. It also allows defining regex patterns to ignore certain lines (was useful to me at the time to strip combined files where headers would be erroneously repeated...)

copier
------

Written in Java 5

Copying files using a GUI (Finder, Explorer, Thunar, Nautilus, etc...) is all fine and dandy - unless copying from old CDs, over the network, or from one file system to another (where idiosyncratic naming allowances clash). If there's an error on one file, the entire copy task is interrupted.

Not cool.

On *nix systems you can simply use the `rsync` command. On Windows... I've since found Roadkill's unstoppable copier and Microsoft's own robocopy to exist; but before I found these (quite a few years ago!), I was despairing at the task of restoring my music collection from a bunch of CDs... I found it necessary to write this copier, that would not only soldier on if it encountered an error, but would also inform me how much of my files (in terms of file count) was lost.... never more than 3% lost per CD thankfully!

Reviewing some of the code today, I found my unsafe use of an Iterator, and some dodgy variable incrementation... It's dirty, but it does the trick...! That it was written in Java indicates that I was probably still at university, before the days I was confident in using python for the task...

Serial Downloader
-----------------

Written in Python 2

In the documentation, I wrote that it was useful for downloading reports like report001.txt, report002.txt etc.... Indeed. Frankly I was downloading webcomics for offline reading.

On *nix you can use globbing to achieve this simply with wget, but on Windows you're still at the mercy of the basic DOS prompt and no CLI downloading tool.

So the serial downloader allows you to specify a prefix, a suffix, and a number range, as well as the desired zero-padding. The latter is a feature you don't get with globbing ;-)

StaleNet
--------

Written in Java 5

On *nix systems you use the `ssh` command; on Windows you're better served with putty.

This is basically just a basic application of the TCP sockets 101 lesson which nonetheless allows you to have a telnet-like tool for testing your SecureSocket implementation. Nothing more. Again, written in Java. Again, re-inventing the wheel.