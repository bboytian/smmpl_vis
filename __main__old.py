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
    # _fps = REALTIMEFPS  # slow enough for animation to load
    # _equivtime = None
    _interval = 0
else:
    _starttime = pd.Timestamp(FAKETIMESTARTTIME)
    _deltatime = pd.Timedelta(FAKEDELTATIME, 'm')
    # _fps = FAKETIMEFPS  # defines temporal resolution of animation
    # _equivtime = pd.Timedelta(FAKETIMEEQUIVTIME, 's')  # duration of animation
    _interval = FAKETIMEINTERVAL  # [s] define interval between frames
_endtime = _starttime + pd.Timedelta(VISDURATION, 'h')


# main func
def main(
        starttime=_starttime,
        endtime=_endtime,
        deltatime=_deltatime,
        # fps=_fps,
        # equivtime=_equivtime,
        interval=_interval,
):
    '''
    Future
        - enable indefinte simulation
        - define func for visualisation such that it does not run indefinitely
         if the time has been set to indefinite

    '''
    # queue objs
    qscanpat = mp.Queue()
    qscanevent = mp.Queue()  # yet to implement

    # Process args
    scanpat_kwargs = {
        'write_boo': False,
        'queue': qscanpat,
        'verb_boo': True,
        'starttime': starttime,
        'endtime': endtime,
        # 'deltatime': deltatime,
        # 'fps': fps,
        # 'equivtime': equivtime,
    }

    # starting processes
    pscanpat = mp.Process(target=spc.scanpat_calc, kwargs=scanpat_kwargs)
    pscanpat.start()

    # vis objects under main thread
    to = spc.timeobj(
        starttime,
        endtime,
        smmplop.globalimports.UTCINFO,
        None,
        # pd.Timedelta(smmplop.globalimports.FINEDELTATIME, 'm'),
        pd.Timedelta(smmplop.globalimports.SEGDELTA, 'm'),
        deltatime,
        # fps=fps,
        # equivtime=equivtime,
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
    )


# execution
if __name__ == '__main__':
    main()
