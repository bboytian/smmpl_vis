# imports
import datetime as dt
import multiprocessing as mp  # on unix this uses 'fork' program
import os

import pandas as pd

from . import visualiser
from .global_imports.smmpl_vis import *
from .productvis import productvis
from .scanpatvis import scanpatvis

from .smmpl_opcodes.global_imports.params_smmpl_opcodes import SEGDELTA
from .smmpl_opcodes import scanpat_calc as spc
from .solaris_opcodes.file_readwrite.mpl_reader import smmpl_reader


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
    # clearing all temporary serial files
    for f in FINDFILESFN(SCANPATVISSERIAL, TEMPSERIALDIR) \
        + FINDFILESFN(PRODUCTVISSERIAL, TEMPSERIALDIR):
        os.remove(f)

    # vis objects under main thread
    to = spc.timeobj(
        starttime,
        endtime,
        UTCINFO,
        None,
        pd.Timedelta(SEGDELTA, 'm'),
        deltatime,
    )

    # vis protocol object

    ## product_calc
    productcalc_vis = productvis(
        to,

        'smmpl_E2', smmpl_reader,
        angularoffset=ANGOFFSET,

        datakey_l=[
            'SNR2_tra'
        ],
        productkey_d={
            # 'cloud': 'cloud_mask'
        }
    )

    ## scanpat_calc
    scanpatcalc_vis = scanpatvis(to)


    # begin animation
    vis = visualiser(  # this runs the animation straight away
        to,
        interval,
        scanpatcalc_vis,
        productcalc_vis
    )


# execution
if __name__ == '__main__':
    main()
