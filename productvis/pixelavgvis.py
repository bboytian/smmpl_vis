# imports
from itertools import chain

import matplotlib.cm as pcm
import numpy as np


# params
_layer_alpha = 0.5


# class
class pixelavgvis():

    def __init__(
            self, mainclass,
            prodkey, prodval, timeobj,
            colormap,

            pixelsize, gridlen, maxheight
    ):
        self.mainclass = mainclass
        self.prodkey = prodkey
        self.prodval = prodval
        self.to = timeobj

        self.ts_ta = None
        self.prodlayer_pAl = None
        self.cmap_pAca = None

        self.ax3d_l = None        # list for axes to plot on
        self.ax2d_l = None        # list for axes to plot on
        self.cmap_sm = pcm.ScalarMappable(cmap=colormap)
        self.plot_d = {}        # nested dictionary; first key points us to the axis
                                # second key points to pixel index, which ultimately
                                # holds a list containing the plots for each layer

        self.plotkey = None
        self.dataplotts = None

        self.pixel_range = range(gridlen**2)
        self.maxheight = maxheight

        # initialisation

        ## grabbing data
        self.get_data()

        ## grid initisalisation
        if gridlen % 2:
            gridrange = np.arange(
                -(gridlen//2)*pixelsize, (gridlen//2 + 1)*pixelsize, pixelsize
            )
        else:
            gridrange = np.arange(
                -(gridlen/2 - 0.5)*pixelsize, (gridlen/2 + 0.5)*pixelsize, pixelsize
            )
        coordlim_gg2a = np.stack(np.meshgrid(gridrange, gridrange)[::-1], axis=-1)
        ## shape (gridlen, gridlen, 2(east, north), 3(left_lim, center, right_lim))
        coordlim_gg23a = np.stack(
            [
                coordlim_gg2a - pixelsize/2,
                coordlim_gg2a,
                coordlim_gg2a + pixelsize/2
            ], axis=-1
        )
        self.coord_p23l = list(chain(*coordlim_gg23a))


    def init_vis(self, axl):
        # only performing plots on 3d axis
        self.ax3d_l = list(filter(lambda x: '3d' in x.name, axl))
        self.ax2d_l = list(filter(lambda x: '3d' not in x.name, axl))
        self.plot_d = {ax: {pixelind:None for pixelind in self.pixel_range}
                       for ax in self.ax3d_l + self.ax2d_l}

    def get_data(self):
        # storing new values
        self.ts_ta = self.mainclass.array_d['Timestamp']
        self.prodlayer_pAl = self.mainclass.data_d[self.prodkey][self.prodval]

        # resetting indices
        self.dataplotts = self.ts_ta[-1]

        self.cmap_pAca = []
        for prodlayer_A in self.prodlayer_pAl:
            self.cmap_pAca.append(
                self.cmap_sm.to_rgba(
                    np.concatenate([prodlayer_A, [0, self.maxheight]])
                )[:-2]
            )

    def update_ts(self):
        '''
        plot only if current timestamp is after the dataplot timestamp
        '''
        # if self.to.get_ts() >= self.dataplotts:
        self._plot_data()


    def update_toseg(self):
        pass

    def _plot_data(self):
        for ax in self.ax3d_l:
            # remove previous plots
            for pixelind in self.pixel_range:
                try:
                    for p in self.plot_d[ax][pixelind]:
                        p.remove()
                except TypeError:  # when no plots are in the data
                    pass

            # plot new plot
                self.plot_d[ax][pixelind] = self._plot_pixel(ax, pixelind)


    def _plot_pixel(self, ax, pixelind):
        '''
        returns a list containing the plots for a specified pixel and axis
        '''
        # creating grid
        coord_23a = self.coord_p23l[pixelind]
        [[e1, e2], [n1, n2]] = coord_23a[:, ::2]
        w1, w2 = -e1, -e2       # convert to west to plot in cartesian coords
                                # since y direction points to the west,
                                # and plot_surface plots in cartesian coords

        # plotting for each height
        plot_l = []
        cmap_Aca = self.cmap_pAca[pixelind]
        for i, prodlayer in enumerate(self.prodlayer_pAl[pixelind]):
            cmap_ca = cmap_Aca[i]
            xx, yy = np.meshgrid([n1, n2], [w1, w2])
            zz = prodlayer * np.ones_like(xx)

            plot_l.append(ax.plot_surface(
                xx, yy, zz, color=cmap_ca, alpha=_layer_alpha
            ))

        return plot_l
