# imports
import datetime as dt
import os
import os.path as osp

import pandas as pd

from . import visualiser
from .global_imports.smmpl_vis import *
from .productvis import productvis
from .scanpatvis import scanpatvis
from .staticvis import staticvis

from .smmpl_opcodes import scanpat_calc as spc
from .smmpl_opcodes.global_imports.params_smmpl_opcodes import SEGDELTA, \
    LIDARNAME, ANGOFFSET, LATITUDE, LONGITUDE, ELEVATION
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
    tempdir = DIRCONFN(osp.dirname(osp.abspath(__file__)), TEMPSERIALDIR)
    for f in FINDFILESFN(SCANPATVISSERIAL, tempdir) \
        + FINDFILESFN(PRODUCTVISSERIAL, tempdir):
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

        LIDARNAME, smmpl_reader,
        TIMESTEP, RANGESTEP,
        ANGOFFSET,
        COMBPOLBOO,

        PIXELSIZE, GRIDLEN, MAXHEIGHT,
        LATITUDE, LONGITUDE, ELEVATION,

        datakey_l=[
            # 'SNR2_tra'
        ],
        productkey_d={
            'cloud': 'mask',
        },
        pixelavgkey_d={
            'cloud': 'pixel_bottom',
        },
    )

    ## scanpat_calc
    scanpatcalc_vis = scanpatvis(to)

    ## static shapes for visualisation
    static_vis = staticvis(
        PIXELSIZE, GRIDLEN,
        plotbot_boo=True
    )


    # begin animation
    visualiser(  # this runs the animation straight away
        to,
        interval,
        # scanpatvis=scanpatcalc_vis,
        productvis=productcalc_vis,
        staticvis=static_vis,
    )


# execution
if __name__ == '__main__':
    main()
