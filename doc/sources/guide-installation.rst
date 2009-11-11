.. _guide_installation:

Instalation
===========

This document has been drafted to help developers install and run PyMT.


Install Python
--------------

PyMT is a `Python`_ module, and therefore requires Python. Currently we only
support Python 2.6. If you are running Linux or Mac OS X, you probably already
have it installed.

.. _Python: http://www.python.org


Windows Installer
-----------------

The PyMT Crew provides a PyMT Installer which is bundled with the latest stable
version of PyMT and all of its dependencies. You can download them from the
following links:

`PyMT Core 0.3.1 Installer`_
`PyMT Examples 0.3.1`_

To install PyMT, double click on executable once it finishes downloading, and
follow the on-screen instructions. Once it finishes installing, unzip the
examples bundle and double click on any file with a ``.py`` extension to play
with our collection of small applications. Have fun!

.. _PyMT Core 0.3.1 Installer: http://pymt.googlecode.com/files/pymt-0.3.1-win32-full-py26.exe
.. _PyMT Examples 0.3.1: http://pymt.googlecode.com/files/pymt-examples-0.3.1.zip


Install PyMT
------------

The PyMT Crew does not provide an automated installer for any other operating
systems. Installation instructions are slightly different depending on whether
you decide to install using a distribution-specific package, download the
latest official release, or checkout the latest development version.


Installing a distribution-specific package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

PyMT is currently not supported by any distributions.


Installing an official release
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    1. Download the latest release from our `download page`_.

    2. Untar the downloaded file:: 

        tar xzvf pymt-XXX.tar.gz

    In the above example, ``XXX`` represents the version number of the latest
    release. If you are using Windows, you can download the command-line tool
    `bsdtar`_ to do this or use a GUI-based tool such as `7-zip`_.

    3. Change into the directory created in step 2::
        
        cd pymt-XXX

    4. If you are using Mac OS X, Linux or any other flavor of Unix, run the
    following command at the shell prompt::

        sudo python setup.py install

    If you are using Windows, start up a command shell with administrator
    privileges and run the command::

        setup.py install

These commands will install PyMT in your Python installation's
``site-packages`` directory.

.. _7-zip: http://www.7-zip.org/
.. _bsdtar: http://gnuwin32.sourceforge.net/packages/bsdtar.htm
.. _download page: http://pymt.txzone.net/pages/Downloads


Installing the development version
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you would like to try the bleeding edge version of PyMT, follow these
instructions:

    1. Make sure you have `Git`_ installed and are familiar with it.

    2. Check out PyMT's main development branch from `GitHub`_::

        git clone git://github.com/tito/pymt.git

    3. Make sure that the Python interpreter can load PyMT's code. You can
    either put the downloaded source directly into the ``site-packages``
    directory, or create a symbolic link if you are using Mac OS X or Linux::

        ln -s `pwd`/pymt SITE-PACKAGES-DIR/pymt

    Substitute ``SITE-PACKAGES-DIR`` to match the location of your system's
    ``site-packages`` directory.

    Alternatively, you can define your ``PYTHONPATH`` environment variable to
    include the ``pymt`` directory. This is the most convenient solution on
    system with Windows, which does not support symbolic links.

*Do not* run ``python setup.py install``. You have already carried out the
equivalent actions in the previous step.

When you want to update your copy of the PyMT source code, run the following
command from the ``pymt`` directory::

    git pull origin master

When you do this, `Git`_ will automatically download any changes.

.. _Git: http://git-scm.com/
.. _GitHub: https://github.com/
