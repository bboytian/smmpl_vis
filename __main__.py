# imports
import multiprocessing as mp  # on unix this uses 'fork' program

import datetime as dt
import pandas as pd

from . import visualiser
from .globalimports import *
from .. import smmpl_opcodes as smmplop
from ..smmpl_opcodes import scanpat_calc as spc


# Params
if REALTIMEBOO:
    _starttime = pd.Timestamp(dt.datetime.now())  # local time
    _deltatime = pd.Timedelta(REALDELTATIME, 's')
    _interval = 0
else:
    _starttime = pd.Timestamp(FAKETIMESTARTTIME)
    _deltatime = pd.Timedelta(FAKEDELTATIME, 'm')
    _interval = FAKETIMEINTERVAL  # [s] define interval between frames
_endtime = _starttime + pd.Timedelta(VISDURATION, 'h')


# main func
def main(
        starttime=_starttime,
        endtime=_endtime,
        deltatime=_deltatime,
        interval=_interval,
):

    # vis protocol object

    ## scanpattern

    ## nrb data

    visprotobj_l = []

    # vis objects under main thread
    to = spc.timeobj(
        starttime,
        endtime,
        smmplop.globalimports.UTCINFO,
        None,
        pd.Timedelta(smmplop.globalimports.SEGDELTA, 'm'),
        deltatime,
    )
    sf = spc.sunforecaster(
        smmplop.globalimports.LATITUDE,
        smmplop.globalimports.LONGITUDE,
        smmplop.globalimports.ELEVATION
    )
    vis = visualiser(  # this runs the animation straight away
        to,
        sf,
        qscanpat,
        qscanevent,
        interval,
        *visprotobj_l
    )


# execution
if __name__ == '__main__':
    main()
