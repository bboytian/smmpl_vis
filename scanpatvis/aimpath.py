# imports
import numpy as np


# class
class aimpath:

    def __init__(
            self,
            ax, gridind,
            linestyle, linewidth, alpha, color,
            aimpath_tg
    ):

        '''
        Future
            - be able to plot projections of path from other grids on each grid

        Parameters
            ax (matplotlib.pyplot.axes)
            gridind (int): determines which grid info to plot on specified 2d ax
                    (str): 'all', plots all grids info on 3d ax
            linestyle (str): linestyle of aimline
            linewidth (float): linewidth of aimline
            alpha (float): alpha of aimline
            color (str): color of aimline

            aimpath_tg (scanpat_calc.targetgenerator.aimpath)

        Methods
            plot_toseg: plot path for each grid for every timeobjseg
            update_toseg: update timeobjseg plot
        '''
        # Attributes
        ## plot type
        self.ax = ax
        self.gridind = gridind
        if gridind == 'all':
            self.allgrid_boo = True
        else:
            self.allgrid_boo = False
        self.proj3d_boo = '3d' in ax.name

        ## plot display settings
        self.linestyle, self.linewidth = linestyle, linewidth
        self.alpha, self.color = alpha, color

        ## plots
        self.aimpath_pltlst = None

        ## object attrs
        ### static
        self.grid_lst = aimpath_tg.grid_lst
        ### changing
        self.aimpath = aimpath_tg
        self.path_ara = None


        # plotting
        self.plot_toseg()


    # plot meth
    def plot_toseg(self):

        # updating relevant attribtues
        self.path_ara = self.aimpath.path_ara
        theta_ara, phi_ara = self.path_ara.T

        # operation
        self.aimpath_pltlst = []

        if self.allgrid_boo:
            g_lst = self.grid_lst
        else:
            g_lst = [self.grid_lst[self.gridind]]

        for i, grid in enumerate(g_lst):

            rhoh_ara = grid.h * np.tan(theta_ara)
            cartpath_ara = np.stack((
                rhoh_ara * np.cos(phi_ara),
                rhoh_ara * np.sin(phi_ara),
                rhoh_ara / np.tan(theta_ara)
            ), axis=1)


            if not self.proj3d_boo: # removing last dimension for plotting
                cartpath_ara = cartpath_ara[..., :-1]

            # plotting
            aimpath_plt = self.ax.plot(
                *cartpath_ara.T,
                linewidth=self.linewidth, linestyle=self.linestyle,
                alpha=self.alpha, color=self.color
            )

            # storing
            self.aimpath_pltlst.append(aimpath_plt)


    # update meth
    def update_toseg(self, aimpath_tg):
        # update relevant target generator objects
        self.aimpath = aimpath_tg

        # removing plot
        for aimpath_plt in self.aimpath_pltlst:
            aimpath_plt[0].remove()

        # plotting
        self.plot_toseg()
