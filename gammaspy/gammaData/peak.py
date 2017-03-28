"""!
@brief Module peak
Contains peak model def
"""
from __future__ import division


def pfactory(name, **kwargs):
    if name == "gauss":
        return PeakGauss(**kwargs)
    else:
        raise ValueError


class PeakGauss(name):
    def __init__(self, **kwargs):
        pass
