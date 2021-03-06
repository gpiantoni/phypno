Installation
============
phypno is pure python, so it can be installed on every platform if you have the correct dependencies, just run:

``pip install phypno``

and to run it:

``scroll_data``

To install the correct dependencies, follow the platform-specific instructions below.

Linux / Mac OS X
----------------
Make sure that you're running the latest version of pip:

``pip install --upgrade pip``

Then you can install all the dependencies with:

``pip install numpy scipy``

If you want a GUI, also install:

``pip install pyqt5``

Windows
-------
Unfortunately scipy cannot be easily be installed on Windows at the moment.
There are two ways to get around it:

Wheels
^^^^^^
If you have the official python binaries, you can should make sure that you're running the latest version of pip:

``pip install --upgrade pip``

then download the wheels (precompiled packages) for `numpy <http://www.lfd.uci.edu/~gohlke/pythonlibs/#numpy>`_ and `scipy <http://www.lfd.uci.edu/~gohlke/pythonlibs/#scipy>`_.

If you want a GUI, also install:

``pip install pyqt5``

Anaconda
^^^^^^^^
You can download and install the 64-bit installer from `anaconda <http://conda.pydata.org/miniconda.html>`_.
Then make sure that you're using the latest version:

``conda update conda``

and install numpy and scipy:

``conda install numpy scipy``

If you want a GUI, also install:

``pip install pyqt5``
