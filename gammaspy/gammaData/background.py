"""!
@brief Module background
Contains background model def
"""
from __future__ import division


def bfactory(name, **kwargs):
    if name == "linear":
        return BgLinear(**kwargs)
    else:
        raise ValueError


class BgLinear(object):
    def __init__(self, **kwargs):
        pass
