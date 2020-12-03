# imports
import matplotlib.cm as pcm
import numpy as np

# params
_layer_alpha = 0.3


# class
class pixelavgvis():

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
        self.prodlayer_pAl = None
        self.cmap_pAca = None
        self.coordlim_gg23a =

        self.ax3d_l = None        # list for axes to plot on
        self.ax2d_l = None        # list for axes to plot on
        self.cmap_sm = pcm.ScalarMappable(cmap=colormap)
        self.plot_d = {}        # nested dictionary; first key points us to the axis
                                # second key points to pixel index, which ultimately
                                # holds a list containing the plots for each layer

        self.plotkey = None
        self.dataplotts = None

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
        coordlim_gg2a = np.stack(np.meshgrid(gridrange, gridrange), axis=-1)
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
        self.plot_d = {ax: {} for ax in self.ax3d_l + self.ax2d_l}

    def get_data(self):
        # storing new values
        self.ts_ta = self.mainclass.array_d['Timestamp']
        self.prodlayer_pAl = self.mainclass.data_d[self.prodkey][self.prodval]

        # resetting indices
        self.dataplotts = self.ts_ta[-1]

        self.cmap_pAca = []
        for prodlayer_A in self.prodlayer_pAl:
            self.cmap_pAca.append(self.cmap_sm.to_rgba(prodlayer_A))

    def update_ts(self):
        '''
        plot only if current timestamp is after the dataplot timestamp
        '''
        if self.to.get_ts() > self.dataplotts:
            self._plot_data()
        else:
            pass

    def update_toseg(self):
        pass

    def _plot_data(self):
        for ax in self.ax3d_l:
            # remove previous plots
            try:
                for _, val in self.plot_d.items():

                self.plot_d[ax][self.botkey].remove()
            except KeyError:
                pass

            # plot new plot


        for ax in self.ax2d_l:
            # remove previous plots
            try:
                self.plot_d[ax][self.botkey].remove()
            except KeyError:
                pass

            # plot new plot

    def _plot_pixel(self, pixelind, heights_a):
