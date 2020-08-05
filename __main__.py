# imports
import multiprocessing as mp  # on unix this uses 'fork' program

import datetime as dt
import pandas as pd

from . import visualiser
from .globalimports import *
from .productvis import productvis
from .. import smmpl_opcodes as smmplop
from ..smmpl_opcodes import scanpat_calc as spc
from ..solaris_opcodes.file_readwrite.mpl_reader import smmpl_reader


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
    # vis objects under main thread
    to = spc.timeobj(
        starttime,
        endtime,
        UTCINFO,
        None,
        pd.Timedelta(smmplop.globalimports.SEGDELTA, 'm'),
        deltatime,
    )

    # vis protocol object
    ## product_calc
    productcalc_vis = productvis('SNR2_tra', to, 'smmpl_E2', smmpl_reader)

    # begin animation
    vis = visualiser(  # this runs the animation straight away
        to,
        interval,
        productcalc_vis
    )


# execution
if __name__ == '__main__':
    main()
