# imports
import multiprocessing as mp
import os
import os.path as osp
import pickle

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
_initreaddatatimes = 2


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

        self.iter_count = 0
        self.data_queue = mp.Queue()  # contains the filenames to be serialised
        self.serial_dir = DIRCONFN(
            osp.dirname(osp.dirname(osp.abspath(__file__))),
            TEMPSERIALDIR,
            SCANPATVISSERIAL
        )

        self.ps = None
        self.grid_lst_ps = None
        self.lidar_hem_ps = None
        self.sun_cone_ps = None
        self.targ_aimlines_ps = None
        self.targ_aimpath_ps = None

        self.suncone_l = []
        self.targaimlines_l = []
        self.targaimpath_l = []
        self.spaimlinescheck_l = []


        # init data read
        print('initialising scanpatvis data')
        self._queue_data(_initreaddatatimes)
        self._get_data()


    def init_vis(self, axl):
        self.ax3d_l = list(filter(lambda x: '3d' in x.name, axl))
        self.ax2d_l = list(filter(lambda x: '3d' not in x.name, axl))

        for ax in self.ax3d_l:
            self._create_plotshapes(ax, 'all')
        for i in range(len(self.grid_lst_ps)):
            self._create_plotshapes(self.ax2d_l[i], i)

    def _create_plotshapes(self, ax, gridind=None):
        ## static plot objects
        if type(gridind) == int:
            grid(
                ax,
                _grid_linewidth, _grid_linealpha,
                _grid_markersize, _grid_markeralpha,
                _grid_alpha, 'C{}'.format(_grid_colorstartind+gridind),

                self.grid_lst_ps[gridind]
            )
        elif gridind == 'all':
            for i, grid_ps in enumerate(self.grid_lst_ps):
                grid(
                    ax,
                    _grid_linewidth, _grid_linealpha,
                    _grid_markersize, _grid_markeralpha,
                    _grid_alpha, 'C{}'.format(_grid_colorstartind+i),

                    grid_ps
                )

        hemisphere(
            ax, gridind,
            _hem_alpha, 'C3',
            _hemints_linewidth,

            self.lidar_hem_ps
        )

        ## changing plot objects
        self.suncone_l.append(cone(
            ax, gridind,
            self.to, self.sf,
            _cone_height,
            True,               # swath_boo
            _cone_alpha, 'C1',
            _coneints_linewidth,

            self.sun_cone_ps
        ))

        self.targaimlines_l.append(aimlines(
            ax, gridind,
            _aimlines_linestyle, _aimlines_linewidth,
            _aimlines_markersize,
            _aimlines_alpha, _aimlines_color,
            _grid_colorstartind,

            self.targ_aimlines_ps
        ))

        self.targaimpath_l.append(aimpath(
            ax, gridind,
            _aimpath_linestyle, _aimpath_linewidth,
            _aimpath_alpha, _aimpath_color,

            self.targ_aimpath_ps
        ))

        ## other visualisation objects

        hemisphere(  # shows the blind range of the lidar
            ax, gridind,
            _hem_alpha, 'C2',
            _hemints_linewidth,

            r=0.3,
            grid_lst=self.grid_lst_ps
        )
        cone(
            ax, gridind,
            self.to, self.sf,
            _cone_height,
            False,              # swath_boo
            1, 'C2',
            _coneints_linewidth*2,

            thetas=0, phis=0,
            Thetas=0.005,
            grid_lst=self.grid_lst_ps,
        )
        if SHOWCHECKBOO:
            self.spaimlinescheck_l.append(aimlines_check(
                ax, gridind,
                _aimlinescheck_linestyle, _aimlinescheck_linewidth,
                _aimlinescheck_markersize,
                _aimlinescheck_alpha, _aimlinescheck_color,

                self.to.get_ts(),
                self.targ_aimlines_ps
            ))

    def _queue_data(self, n):
        for i in range(n):
            # serialising data and writing to file
            ps = scanpat_calc(
                write_boo=False,
                rettg_boo=True,
                starttime=self.starttime, endtime=self.endtime,
                verbboo=False
            )
            serial_dir = self.serial_dir.format(self.iter_count)
            with open(serial_dir, 'wb') as f:
                print(f'writing scanpatvis serial data to {serial_dir}')
                pickle.dump(ps, f)
            # message passing
            self.iter_count += 1
            self.data_queue.put(serial_dir)
            # iterating the next time range to consider
            self.starttime += _readduration
            self.endtime += _readduration

    def _get_data(self):
        '''
        Assumes that there is always serialised data in the queue, i.e. the
        serialisation process is faster than the animation and reading process
        '''
        # grabbing new data from queue
        serial_dir = self.data_queue.get()
        with open(serial_dir, 'rb') as f:
            _, self.ps = pickle.load(f)
        os.remove(serial_dir)   # deleting temp file

        # starting data queue if the data stock is low
        if self.data_queue.qsize() < _initreaddatatimes:
            # starting multiprocess
            print('starting scanpatvis background data retrieval')
            mp.Process(
                target=self._queue_data,
                args=(_initreaddatatimes, )
            ).start()

        # retrieving
        self.grid_lst_ps = self.ps.grid_lst
        self.lidar_hem_ps = self.ps.lidar_hem
        self.sun_cone_ps = self.ps.sun_cone
        self.targ_aimlines_ps = self.ps.targ_aimlines
        self.targ_aimpath_ps = self.ps.targ_aimpath


    # update methods

    def update_ts(self):
        for sun_cone in self.suncone_l:
            sun_cone.update_ts(*self.sf.get_angles(self.to.get_ts()))

    def update_toseg(self,):
        # retreive data
        self._get_data()

        # update objects
        for sun_cone in self.suncone_l:
            self.sun_cone.update_toseg(self.sun_cone_ps)
        for targ_aimlines in self.targaimlines_l:
            self.targ_aimlines.update_toseg(self.targ_aimlines_ps)
        for targ_aimpath in self.targaimpath_l:
            self.targ_aimpath.update_toseg(self.targ_aimpath_ps)
        if SHOWCHECKBOO:
            for sp_aimlinescheck in self.spaimlinescheck_l:
                self.sp_aimlinescheck.update_toseg(self.to.get_ts(),
                                                   self.targ_aimlines_ps)
