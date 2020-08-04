# imports
import numpy as np


# class
class aimlines:

    def __init__(
            self,
            ax, gridind,
            linestyle, linewidth,
            markersize,
            alpha, color,
            grid_colorstartind,

            aimlines_tg
    ):
        '''
        Parameters
            ax (matplotlib.pyplot.axes)
            gridind (int): determines which grid info to plot on specified 2d ax
                    (str): 'all', plots all grids info on 3d ax
            linestyle (str): linestyle of aimline
            linewidth (float): linewidth of aimline
            markersize (float): size of marker on 2D plot
            alpha (float): alpha of aimline
            color (str): color of aimline
            grid_colorstartind (int): color from which grid iterates,
                                      for plotting points

            aimlines_tg (scanpat_calc.targetgenerator.aimlines)

        Methods
            plot_toseg: plot targets for each grid for every timeobjseg
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
        self.markersize=markersize
        self.alpha, self.color = alpha, color
        self.grid_colorstartind = grid_colorstartind

        ## plots
        self.aimlines_pltlst = None

        ## object attrs
        ### static
        self.grid_lst = aimlines_tg.grid_lst
        ### changing
        self.aimlines = aimlines_tg
        self.coord_matlst = None
        self.mask_matlst = None
        self.dir_matlst = None

        # plotting
        self.plot_toseg()


    # main meth
    def plot_toseg(self):

        # updating attributes
        self.coord_matlst = self.aimlines.coord_matlst
        self.mask_matlst = self.aimlines.mask_matlst
        self.dir_matlst = self.aimlines.dir_matlst

        # operation
        self.aimlines_pltlst = []
        for i, grid in enumerate(self.grid_lst):

            mask_mat = self.mask_matlst[i]

            # plotting
            if self.proj3d_boo:

                coord_mat = self.coord_matlst[i]
                x_ara = coord_mat[..., 0][mask_mat].flatten()
                y_ara = coord_mat[..., 1][mask_mat].flatten()
                z_ara = coord_mat[..., 2][mask_mat].flatten()

                aralen = len(x_ara)
                r_ara = range(0, aralen, 2)
                x_ara = np.insert(x_ara, r_ara, 0)
                y_ara = np.insert(y_ara, r_ara, 0)
                z_ara = np.insert(z_ara, r_ara, 0)

                aimlines_plt = self.ax.plot(
                    x_ara, y_ara, z_ara,
                    linewidth=self.linewidth, linestyle=self.linestyle,
                    alpha=self.alpha, color=self.color
                )

            else:

                dir_mat = self.dir_matlst[i]
                theta_ara = dir_mat[..., 1][mask_mat].flatten()
                phi_ara = dir_mat[..., 2][mask_mat].flatten()

                if self.allgrid_boo:
                    r_ara = grid.h * np.tan(theta_ara)
                else:
                    r_ara = self.grid_lst[self.gridind].h * np.tan(theta_ara)
                x_ara = r_ara * np.cos(phi_ara)
                y_ara = r_ara * np.sin(phi_ara)

                aimlines_plt = self.ax.plot(
                    x_ara, y_ara, 'o',
                    markersize=self.markersize,
                    color='C{}'.format(self.grid_colorstartind+i)
                )

            # storing
            self.aimlines_pltlst.append(aimlines_plt)


    # update meth
    def update_toseg(self, aimlines_tg):
        # updating relevant target generator objects
        self.aimlines = aimlines_tg

        # removing plot
        for aimlines_plt in self.aimlines_pltlst:
            aimlines_plt[0].remove()

        # plotting
        self.plot_toseg()
