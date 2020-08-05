# imports
import multiprocessing as mp

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as pcm
import numpy as np

from ..globalimports import *
from ...solaris_opcodes.product_calc.nrb_calc import nrb_calc
from ...solaris_opcodes.file_readwrite.mpl_reader import smmpl_reader


# params
_dataf = nrb_calc
_readduration = pd.Timedelta(1, 'h')
_initreaddatatimes = 5
_inittimeout = 2                # [s]

_colormap = 'Blues'
_nrbmaxthres = np.log(500 + 1)
# _nrbmaxthres = 20
_alphascale = 0.5
_scatterpointsize = 150

# class
class productvis():

    def __init__(
            self,
            datakey, timeobj,
            lidarname, mplreader
    ):
        self.datakey = datakey
        self.to = timeobj
        self.lidarname = lidarname

        self.starttime = self.to.get_ts()
        self.endtime = self.starttime + _readduration

        self.data_queue = mp.Queue()
        self.queuedata_proc = None  # ensures we are only running one at one time
        self.data_d = None
        self.dataplotts = None
        self.dataplotind = None

        self.ts_ta = None
        self.x_tra = None
        self.y_tra = None
        self.z_tra = None
        self.r_trm = None
        self.dirtup_ta = None      # [(phi, theta), ...] [rad], 2 d.p
        self.cmap_trca = None      # (timestamp, maxNbin, RGBA)
        self.datalen = None

        self.x_ta = None
        self.y_ta = None
        self.z_ta = None
        self.r_rm = None
        self.dir_tup = None     # (phi, theta) [rad], 2 d.p
        self.cmap_rca = None

        self.ax_l = None        # list for axes to plot on
        self.cmap_sm = pcm.ScalarMappable(cmap=_colormap)
        self.plot_d = {}        # holds plots, keys are the direction tuples
                                # (phi, theta) [rad]

        # initial data read
        self._queue_data(_initreaddatatimes)
        self._get_data()

    def init_vis(self, axl):
        # only performing plots on 3d axis
        self.ax_l = list(filter(lambda x: '3d' in x.name, axl))

    def _queue_data(self, n):
        for i in range(n):
            data_d = _dataf(
                self.lidarname, smmpl_reader,
                starttime=self.starttime, endtime=self.endtime,
                verbboo=False
            )
            if data_d:
                self.data_queue.put(data_d)
            # iterating the next time range to consider
            self.starttime += _readduration
            self.endtime += _readduration

    def _get_data(self):
        '''
        gets the data from data_queue and initiates a _queue_data if the queue
        size is less than _initreaddatatimes,
        will throw an error if nothing is in the queue
        '''
        # grabbing new data from queue
        self.data_d = self.data_queue.get()

        ## starting data queue if the data stock is low
        if self.data_queue.qsize() < _initreaddatatimes:
            try:                # runnning one data queue at each time
                self.queuedata_proc.join()
            except AttributeError:  # first process to be called
                self.queuedata_proc = mp.Process(target=self._queue_data,
                                                 args=(_initreaddatatimes,))
                self.queuedata_proc.start()

        # storing new values
        self.ts_ta = self.data_d['Timestamp']
        self.r_trm = self.data_d['r_trm']

        data_trca = self.data_d[self.datakey]
        data_trca[data_trca < 0] = 0  # baseline negative values
        data_trca += 1
        data_trca = np.log(data_trca)  # log scaling for vis
        data_trca /= _nrbmaxthres  # setting upper limit
        data_trca[data_trca > 1] = 1
        self.cmap_trca = self.cmap_sm.to_rgba(data_trca)
        self.cmap_trca = self.cmap_trca[..., :3]
        ## setting variable alpha
        self.cmap_trca = np.append(self.cmap_trca, data_trca[..., None], axis=-1)
        ## adjusting alpha for visibility
        self.cmap_trca[..., 3] *= _alphascale

        r_tra = self.data_d['r_tra']
        theta_ta = self.data_d['theta_ta']
        phi_ta = self.data_d['phi_ta']
        self.x_tra = r_tra * np.sin(theta_ta)[:, None] * np.cos(phi_ta)[:, None]
        self.y_tra = r_tra * np.sin(theta_ta)[:, None] * np.sin(phi_ta)[:, None]
        self.z_tra = r_tra * np.cos(theta_ta)[:, None]
        self.dirtup_ta = [tuple(dir_l) for dir_l in
                          np.stack([phi_ta, theta_ta], axis=1)]

        # resetting the indices
        self.dataplotind = 0
        self.dataplotts = self.ts_ta[0]
        self.datalen = len(self.ts_ta)

    def update_ts(self):
        while self.to.get_ts() >= self.dataplotts:
            # indexing storage
            self.r_rm = self.r_trm[self.dataplotind]
            self.x_ra = self.x_tra[self.dataplotind][self.r_rm]
            self.y_ra = self.y_tra[self.dataplotind][self.r_rm]
            self.z_ra = self.z_tra[self.dataplotind][self.r_rm]
            self.cmap_rca = self.cmap_trca[self.dataplotind][self.r_rm]
            self.dir_tup = self.dirtup_ta[self.dataplotind]

            # plotting
            self._plot_data()

            # update the next timestamp
            self.dataplotind += 1
            self.dataplotts = self.ts_ta[self.dataplotind]
            if self.dataplotind >= self.datalen:
                self._get_data()

    def update_toseg(self):
        pass

    def _plot_data(self):
        for ax in self.ax_l:
            # remove previous plots
            try:
                self.plot_d[self.dir_tup].remove()
            except KeyError:
                pass

            # plot new plot
            self.plot_d[self.dir_tup] = ax.scatter(
                self.x_ra, self.y_ra, self.z_ra,
                c=self.cmap_rca,
                s=_scatterpointsize,
            )


if __name__ == '__main__':
    from mpl_toolkits.mplot3d import Axes3D

    from ...smmpl_opcodes.scanpat_calc.timeobj import timeobj


    to = timeobj(
        pd.Timestamp('202008040800'),
        pd.Timestamp('202008051100'),
        8,
        pd.Timedelta(1, 'm'),
        pd.Timedelta(30, 'm'),
        None
    )
    pv = productvis(
        'SNR_tra', to, 'smmpl_E2', smmpl_reader
    )

    # figure creation
    _scale = 1.3
    _curlyl = 30
    fig3d = plt.figure(figsize=(10, 10), constrained_layout=True)
    ax3d = fig3d.add_subplot(111, projection='3d')
    ax3d.pbaspect = [_scale, _scale, _scale]
    ax3d.set_xlabel('South -- North')
    ax3d.set_ylabel('East -- West')
    ax3d.set_xlim([-_curlyl/2, _curlyl/2])
    ax3d.set_ylim([-_curlyl/2, _curlyl/2])
    ax3d.set_zlim([0, _curlyl])

    pv.init_vis([ax3d])

    to.ts = LOCTIMEFN(pd.Timestamp('202008040830'), 8)  # fastforward the time
    pv.update_ts()

    plt.show()
