# imports
import matplotlib.cm as pcm
import numpy as np

from ..global_imports.smmpl_vis import *


# params
_nrbmaxthres = np.log(500 + 1)
_alphascale = 0.5
_scatterpointsize = 150


# class
class arrayvis():

    def __init__(
            self, mainclass,
            datakey, timeobj,
            colormap,
    ):
        self.mainclass = mainclass
        self.datakey = datakey
        self.to = timeobj

        self.ts_ta = None
        self.x_tra = None
        self.y_tra = None
        self.z_tra = None
        self.r_trm = None
        self.dirtup_ta = None      # [(phi, theta), ...] [rad], 2 d.p
        self.cmap_trca = None      # (timestamp, maxNbin, RGBA)
        self.datalen = None

        self.x_ra = None
        self.y_ra = None
        self.z_ra = None
        self.r_rm = None
        self.dir_tup = None     # (phi, theta) [rad], 2 d.p
        self.cmap_rca = None

        self.ax_l = None        # list for axes to plot on
        self.cmap_sm = pcm.ScalarMappable(cmap=colormap)
        self.plot_d = {}        # holds plots, keys are the direction tuples
                                # (phi, theta) [rad]

        self.dataplotts = None
        self.dataplotind = None

        # initialisation
        self.get_data()


    def init_vis(self, axl):
        # only performing plots on 3d axis
        self.ax_l = list(filter(lambda x: '3d' in x.name, axl))

    def get_data(self):
        # storing new values
        self.ts_ta = self.mainclass.array_d['Timestamp']
        self.r_trm = self.mainclass.array_d['r_trm']

        # resetting indices
        self.dataplotind = 0
        self.dataplotts = self.ts_ta[0]
        self.datalen = len(self.ts_ta)

        data_trca = self.mainclass.array_d[self.datakey]
        data_trca[              # base linin negative and nan values
            ((data_trca < 0) + np.isnan(data_trca)).astype(np.bool)
        ] = 0
        data_trca += 1
        data_trca = np.log(data_trca)  # log scaling for vis
        data_trca /= _nrbmaxthres  # setting upper limit
        data_trca[data_trca > 1] = 1
        self.cmap_trca = self.cmap_sm.to_rgba(data_trca)

        ## setting variable alpha
        self.cmap_trca[..., 3] = data_trca * _alphascale

        r_tra = self.mainclass.array_d['r_tra']
        theta_ta = self.mainclass.array_d['theta_ta']
        phi_ta = self.mainclass.array_d['phi_ta']
        self.x_tra = r_tra * np.sin(theta_ta)[:, None] * np.cos(phi_ta)[:, None]
        self.y_tra = r_tra * np.sin(theta_ta)[:, None] * np.sin(phi_ta)[:, None]
        self.z_tra = r_tra * np.cos(theta_ta)[:, None]
        self.dirtup_ta = [tuple(dir_l) for dir_l in
                          np.stack([phi_ta, theta_ta], axis=1)]


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
            if self.dataplotind >= self.datalen:
                break
            self.dataplotts = self.ts_ta[self.dataplotind]

    def update_toseg(self):
        pass

    def _plot_data(self):
        for ax in self.ax_l:
            # remove previous plots
            try:
                self.plot_d[self.dir_tup].remove()
                pass
            except KeyError:
                pass

            # plot new plot
            self.plot_d[self.dir_tup] = ax.scatter(
                self.x_ra, self.y_ra, self.z_ra,
                c=self.cmap_rca,
                s=_scatterpointsize,
            )
