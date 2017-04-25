About
=====

GammaSpy is a gamma ray spectroscopy peak visualization, finding, and
fitting application.

Todo
-------------
- Energy efficiency
- Compute activity of a sample.
- Automatically determine the source of a gamma peak.

Installation
============

Depends:

- numpy
- scipy
- h5py
- pyqt4.8+
- numdifftools
- pyqtgraph (https://github.com/pyqtgraph/pyqtgraph)
- xylib-py (https://github.com/wojdyr/xylib)


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

Dev Install GammaSpy
--------------------
    
    git clone https://github.com/wgurecky/GammaSpy.git
    cd GammaSpy
    python3 setup.py develop --user

Filetype Compatibility
=======================

Thanks to xylib (ref.) GammaSpy can import energy spectra in the following data formats:

- CNF
- csv
- hdf5

License
=======

MIT
