About
=====

GammaSpy is a gamma ray spectroscopy peak visualization, finding, and
fitting application.

Energy calibration curve fitting is also provided.

Experimental
-------------

- Automatically determine the source of a gamma peak.
- Compute activity of a sample.

Installation
============

Depends:

- numpy
- pyqt4.8+
- pyqtgraph (https://github.com/pyqtgraph/pyqtgraph)
- xylibi-py (https://github.com/wojdyr/xylib)


Installing xylib-py
-------------------

via pip:

    sudo pip3 install xylib-py

Installing pyqtgraph
--------------------

from github:

    git clone https://github.com/pyqtgraph/pyqtgraph.git
    cd pyqtgraph
    python3 setup.py install --user

Filetype Compatibility
=======================

Thanks to xylib (ref.) GammaSpy can import energy spectra in the following data formats:

- .CNF
- .csv

License
=======

MIT
