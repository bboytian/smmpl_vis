# imports
import multiprocessing as mp

import pandas as pd

from .aimlines import aimlines
from .aimlines_check import aimlines_check
from .aimpath import aimpath
from .cone import cone
from .grid import grid
from .hemisphere import hemisphere

from ..global_imports.smmpl_vis import *
from ..smmpl_opcodes.scanpat_calc import main as scanpat_calc
from ..smmpl_opcodes.scanpat_calc.sunforecaster import sunforecaster
from ..smmpl_opcodes.global_imports.params_smmpl_opcodes import\
    LATITUDE, LONGITUDE, ELEVATION

# params

## plot params
_hem_alpha = 0.2
_hemints_linewidth = 2

_cone_alpha = 0.2
_coneints_linewidth = _hemints_linewidth

_grid_markersize = 5
_grid_markeralpha = 0.2
_grid_linewidth = 0.5
_grid_linealpha = 0.6
_grid_alpha = 0.4
_grid_colorstartind = 6

_aimlines_linewidth = 1
_aimlines_alpha = 0.2
_aimlines_linestyle = '-'
_aimlines_color = 'k'
_aimlines_markersize = _grid_markersize

_aimlinescheck_linestyle, _aimlinescheck_linewidth = '-', 3
_aimlinescheck_markersize = _grid_markersize
_aimlinescheck_alpha, _aimlinescheck_color = 1, 'orange'

_aimpath_linewidth = 1.5
_aimpath_alpha = 0.3
_aimpath_linestyle = '-'
_aimpath_color = 'b'

## other plot values
_cone_height = 20        # [km]

## other params
_readduration = pd.Timedelta(1, 'd')
_initreaddatatimes = 1
_inittimeout = 2                # [s]


# main class
class scanpatvis:

    def __init__(
            self,
            timeobj,
    ):
        self.to = timeobj
        self.starttime = self.to.get_ts()
        self.endtime = self.starttime + _readduration

        self.sf = sunforecaster(LATITUDE, LONGITUDE, ELEVATION)

        self.data_queue = mp.Queue()

        self.tg = None
        self.grid_lst_tg = None
        self.lidar_hem_tg = None
        self.sun_cone_tg = None
        self.targ_aimlines_tg = None
        self.targ_aimpath_tg = None


        # init data read
        self._queue_data(_initreaddatatimes)
        self._get_data()


    def init_vis(self, axl):
        self.ax3d_l = list(filter(lambda x: '3d' in x.name, axl))
        self.ax2d_l = list(filter(lambda x: '3d' not in x.name, axl))

        for ax in self.ax3d_l:
            self._create_plotshapes(ax)
        for i, ax in enumerate(self.ax2d_l):
            self._create_plotshapes(ax, i)

    def _create_plotshapes(self, ax, gridind=None):
        ## static plot objects
        if gridind:
            grid_obj = grid(
                ax,
                _grid_linewidth, _grid_linealpha,
                _grid_markersize, _grid_markeralpha,
                _grid_alpha, 'C{}'.format(_grid_colorstartind+gridind),

                self.grid_lst_tg[gridind]
            )
        else:
            grid_lst = [
                grid(
                    ax,
                    _grid_linewidth, _grid_linealpha,
                    _grid_markersize, _grid_markeralpha,
                    _grid_alpha, 'C{}'.format(_grid_colorstartind+i),

                    grid_tg
                ) for i, grid_tg in enumerate(self.grid_lst_tg)
            ]


        lidar_hem = hemisphere(
            ax, gridind,
            _hem_alpha, 'C3',
            _hemints_linewidth,

            self.lidar_hem_tg
        )

        ## changing plot objects
        self.sun_cone = cone(
            ax, gridind,
            self.to, self.sf,
            _cone_height,
            True,               # swath_boo
            _cone_alpha, 'C1',
            _coneints_linewidth,

            self.sun_cone_tg
        )
        self.targ_aimlines = aimlines(
            ax, gridind,
            _aimlines_linestyle, _aimlines_linewidth,
            _aimlines_markersize,
            _aimlines_alpha, _aimlines_color,
            _grid_colorstartind,

            self.targ_aimlines_tg
        )
        self.targ_aimpath = aimpath(
            ax, gridind,
            _aimpath_linestyle, _aimpath_linewidth,
            _aimpath_alpha, _aimpath_color,

            self.targ_aimpath_tg
        )

        ## other visualisation objects

        unit_hem = hemisphere(  # shows the blind range of the lidar
            ax, gridind,
            _hem_alpha, 'C2',
            _hemints_linewidth,

            r=0.3,
            grid_lst=self.grid_lst_tg
        )
        self.lidar_cone = cone(
            ax, gridind,
            self.to, self.sf,
            _cone_height,
            False,              # swath_boo
            1, 'C2',
            _coneints_linewidth*2,

            thetas=0, phis=0,
            Thetas=0.005,
            grid_lst=self.grid_lst_tg,
        )
        if SHOWCHECKBOO:
            self.sp_aimlinescheck = aimlines_check(
                ax, gridind,
                _aimlinescheck_linestyle, _aimlinescheck_linewidth,
                _aimlinescheck_markersize,
                _aimlinescheck_alpha, _aimlinescheck_color,

                self.to.get_ts(),
                self.targ_aimlines_tg
            )

    def _queue_data(self, n):
        for i in range(n):
            # scanpat_calc puts in a targetgenerator object for each time segment
            scanpat_calc(
                queue=self.data_queue,
                starttime=self.starttime, endtime=self.endtime,
                verbboo=False
            )
            # iterating the next time range to consider
            self.starttime += _readduration
            self.endtime += _readduration

    def _get_data(self):
        # grabbing new data from queue
        self.tg = self.data_queue.get()

        ## starting data queue if the data stock is low
        if self.data_queue.qsize() < _initreaddatatimes:
            self._queue_data(_initreaddatatimes)

        # retrieving
        self.grid_lst_tg = self.tg.ps.grid_lst
        self.lidar_hem_tg = self.tg.ps.lidar_hem
        self.sun_cone_tg = self.tg.ps.sun_cone
        self.targ_aimlines_tg = self.tg.ps.targ_aimlines
        self.targ_aimpath_tg = self.tg.ps.targ_aimpath


    # update methods

    def update_ts(self):
        self.sun_cone.update_ts(*self.sf.get_angles(self.to.get_ts()))

    def update_toseg(self,):
        self.sun_cone.update_toseg(self.sun_cone_tg)
        self.targ_aimlines.update_toseg(self.targ_aimlines_tg)
        self.targ_aimpath.update_toseg(self.targ_aimpath_tg)
        if SHOWCHECKBOO:
            self.sp_aimlinescheck.update_toseg(self.to.get_ts(),
                                               self.targ_aimlines_tg)
