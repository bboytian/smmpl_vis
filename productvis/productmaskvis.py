# imports
import matplotlib.cm as pcm
import numpy as np

# params
_scatterpointsize = 200

_prodbotmarker = '^'
_prodbotdescrip = 'bottom'
_prodpeakmarker = 'X'
_prodpeakdescrip = 'peak'
_prodtopmarker = '+'
_prodtopdescrip = 'top'

# class
class productmaskvis():

    def __init__(
            self, mainclass,
            prodkey, prodval, timeobj,
            colormap,
    ):
        self.mainclass = mainclass
        self.prodkey = prodkey
        self.prodval = prodval
        self.to = timeobj

        self.ts_ta = None
        self.prodmask_tl3a = None
        self.x_tl3a = None
        self.y_tl3a = None
        self.z_tl3a = None
        self.dirtup_ta = None      # [(phi, theta), ...] [rad], 2 d.p
        self.cmap_tl3ca = None      # (timestamp, maxNbin, RGBA)
        self.datalen = None

        self.xbot_la = None
        self.ybot_la = None
        self.zbot_la = None
        self.xpeak_la = None
        self.ypeak_la = None
        self.zpeak_la = None
        self.xtop_la = None
        self.ytop_la = None
        self.ztop_la = None
        self.cmapbot_lca = None
        self.cmappeak_lca = None
        self.cmaptop_lca = None

        self.ax3d_l = None        # list for axes to plot on
        self.ax2d_l = None        # list for axes to plot on
        self.cmap_sm = pcm.ScalarMappable(cmap=colormap)
        self.plot_d = {}        # holds plots, keys are the direction tuples
                                # ((phi, theta), <descrip>) [rad]
        self.botkey = None
        self.peakkey = None
        self.topkey = None

        self.dataplotts = None
        self.dataplotind = None

        # initialisation
        self.get_data()

    def init_vis(self, axl):
        # only performing plots on 3d axis
        self.ax3d_l = list(filter(lambda x: '3d' in x.name, axl))
        self.ax2d_l = list(filter(lambda x: '3d' not in x.name, axl))
        self.plot_d = {ax: {} for ax in self.ax3d_l + self.ax2d_l}

    def get_data(self):
        # storing new values
        self.ts_ta = self.mainclass.array_d['Timestamp']
        self.prodmask_tl3a = self.mainclass.data_d[self.prodkey][self.prodval]

        # resetting indices
        self.dataplotind = 0
        self.dataplotts = self.ts_ta[0]
        self.datalen = len(self.ts_ta)

        prodmask_tl3a = np.nan_to_num(self.prodmask_tl3a)
        cmap_a = self.cmap_sm.to_rgba(prodmask_tl3a.flatten())
        self.cmap_tl3ca = cmap_a.reshape([*prodmask_tl3a.shape, 4])

        ## setting variable alpha
        self.cmap_tl3ca[..., 3] = 1
        theta_ta = self.mainclass.array_d['theta_ta']
        phi_ta = self.mainclass.array_d['phi_ta']
        self.dirtup_ta = [tuple(dir_l) for dir_l in
                          np.stack([phi_ta, theta_ta], axis=1)]
        self.z_tl3a = self.prodmask_tl3a
        self.x_tl3a = self.z_tl3a \
            * np.tan(theta_ta)[:, None, None] * np.cos(phi_ta)[:, None, None]
        self.y_tl3a = self.z_tl3a \
            * np.tan(theta_ta)[:, None, None] * np.sin(phi_ta)[:, None, None]

    def update_ts(self):
        while self.to.get_ts() >= self.dataplotts:
            # indexing storage
            self.xbot_la = self.x_tl3a[self.dataplotind][:, 0]
            self.ybot_la = self.y_tl3a[self.dataplotind][:, 0]
            self.zbot_la = self.z_tl3a[self.dataplotind][:, 0]
            self.xpeak_la = self.x_tl3a[self.dataplotind][:, 1]
            self.ypeak_la = self.y_tl3a[self.dataplotind][:, 1]
            self.zpeak_la = self.z_tl3a[self.dataplotind][:, 1]
            self.xtop_la = self.x_tl3a[self.dataplotind][:, 2]
            self.ytop_la = self.y_tl3a[self.dataplotind][:, 2]
            self.ztop_la = self.z_tl3a[self.dataplotind][:, 2]
            self.cmapbot_lca = self.cmap_tl3ca[self.dataplotind][:, 0]
            self.cmappeak_lca = self.cmap_tl3ca[self.dataplotind][:, 1]
            self.cmaptop_lca = self.cmap_tl3ca[self.dataplotind][:, 2]

            dir_tup = self.dirtup_ta[self.dataplotind]
            self.botkey = (dir_tup, _prodbotdescrip)
            self.peakkey = (dir_tup, _prodpeakdescrip)
            self.topkey = (dir_tup, _prodtopdescrip)

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
        for ax in self.ax3d_l:
            # remove previous plots
            try:
                self.plot_d[ax][self.botkey].remove()
                self.plot_d[ax][self.peakkey].remove()
                self.plot_d[ax][self.topkey].remove()
            except KeyError:
                pass

            # plot new plot

            ## product bottom
            self.plot_d[ax][self.botkey] = ax.scatter(
                self.xbot_la, self.ybot_la, self.zbot_la,
                c=self.cmapbot_lca,
                s=_scatterpointsize,
                marker=_prodbotmarker,
            )

            ## product peak
            self.plot_d[ax][self.peakkey] = ax.scatter(
                self.xpeak_la, self.ypeak_la, self.zpeak_la,
                c=self.cmappeak_lca,
                s=_scatterpointsize,
                marker=_prodpeakmarker,
            )

            ## product top
            self.plot_d[ax][self.topkey] = ax.scatter(
                self.xtop_la, self.ytop_la, self.ztop_la,
                c=self.cmaptop_lca,
                s=_scatterpointsize,
                marker=_prodtopmarker,
            )

        for ax in self.ax2d_l:
            # remove previous plots
            try:
                self.plot_d[ax][self.botkey].remove()
                self.plot_d[ax][self.peakkey].remove()
                self.plot_d[ax][self.topkey].remove()
            except KeyError:
                pass

            # plot new plot

            ## product bottom
            self.plot_d[ax][self.botkey] = ax.scatter(
                self.xbot_la, self.ybot_la,
                c=self.cmapbot_lca,
                s=_scatterpointsize,
                marker=_prodbotmarker,
            )

            ## product peak
            self.plot_d[ax][self.peakkey] = ax.scatter(
                self.xpeak_la, self.ypeak_la,
                c=self.cmappeak_lca,
                s=_scatterpointsize,
                marker=_prodpeakmarker,
            )

            ## product top
            self.plot_d[ax][self.topkey] = ax.scatter(
                self.xtop_la, self.ytop_la,
                c=self.cmaptop_lca,
                s=_scatterpointsize,
                marker=_prodtopmarker,
            )
