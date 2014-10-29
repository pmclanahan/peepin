======
Peepin
======

This tool makes it easier to update your strict peep-ready
requirements.txt file.

If you want to add a package or edit the version of one you're currently
using you have to do the following steps:

    1. Go to pypi for that package
    2. Download the .tgz file
    3. Possibly download the .whl file
    4. Run `peep hash downloadedpackage-1.2.3.tgz`
    5. Run `peep hash downloadedpackage-1.2.3.whl`
    6. Edit requirements.txt

This script does all those things.
Hackishly wonderfully so.

Installation
============

This is something you only do or ever need in a development
environment. Ie. your laptop.

    pip install peepin

How to use it
=============

Suppose you want to install ``futures``. You can either do this::

    peepin futures

Which will download the latest version tarball (and wheel) and
calculate their peep hash and edit your ``requirements.txt`` file.

Or you can be specific about exactly which version you want::

    peepin "futures==2.1.3"

Suppose you don't have a ``requirements.txt`` right there in the same
directory you can do this::

    peepin "futures==2.1.3" stuff/requirementst/prod.txt

If there's not output. It worked. Check how it edited your
requirements files.

Ode to Erik Rose
================

Just in case you didn't know;
`peep <https://github.com/erikrose/peep>`_ is awesome.
It makes it possible to confidently leave
third-party packages to be installed on the server without needing to
be checked into some sort of "vendor" directory.

Having said that, if you don't care about security or repeatability.
Then Erik is just a dude with a goatee.

Version History
===============

0.1
  * Works