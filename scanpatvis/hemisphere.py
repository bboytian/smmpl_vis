# imports
import numpy as np


# params
_thetanumsurf = 2                # for discretisation
_phinumsurf = 1
_phinumints = 6


# main class
class hemisphere:

    def __init__(
            self,
            ax, gridind,
            alpha, color,
            ints_linewidth,

            hemisphere_ps=None,
            r=1,
            grid_lst=[]
    ):
        '''
        has the option to plot a hemisphere without generating any masks if
        hemisphere_ps is not specified

        Parameters
            hemisphere_ps (targetgenerator.hemisphere)
            ax (matplotlib.pyplot.axes): axis onwhich we are plotting
            gridind (int): determines which grid info to plot on specified 2d ax
                    (str): 'all', plots all grids info on 3d ax
            alpha (float): alpha of hemipshere
            color (str): color of hemisphere
            ints_linewidth (float): line of intersect between hem and plane


            hemisphere_ps (scanpat_calc.targetgenerator.hemisphere)
            r (float): radius of hemisphere for display purposes
            grid_lst (list): specified if we want intersection to be plotted

        Methods
            plot: plot surface for 3d axes and intersection for 2d axes

        '''
        # Attributes
        ## plot type
        self.ax = ax
        self.proj3d_boo = '3d' in ax.name

        ## plot display settings
        self.alpha, self.color = alpha, color
        self.ints_linewidth = ints_linewidth

        ## plots
        self.hem_plt = None
        self.ints_pltlst = None

        ## targetgenerator object
        if hemisphere_ps:
            self.r = hemisphere_ps.r  # assuming grids are static
            if gridind == 'all':
                self.grid_lst = hemisphere_ps.grid_lst
            else:
                self.grid_lst = [hemisphere_ps.grid_lst[gridind]]
        else:
            self.r = r
            if gridind == 'all':
                self.grid_lst = grid_lst
            else:
                self.grid_lst = [grid_lst[gridind]]

        # plotting
        self.plot()


    # plot meth
    def plot(self):

        # plotting surface
        if self.proj3d_boo:
            if self.r <= 1:     # in case we are plotting a unit sphere
                thetanum = 10
            else:
                thetanum = _thetanumsurf * int(self.r)
            phinum = _phinumsurf * thetanum
            theta_mat, phi_mat = np.mgrid[0:np.pi/2:thetanum*1j,
                                          0:2*np.pi:phinum*1j]
            x_ara = (self.r * np.sin(theta_mat) * np.cos(phi_mat)).flatten()
            y_ara = (self.r * np.sin(theta_mat) * np.sin(phi_mat)).flatten()
            z_ara = (self.r * np.cos(theta_mat)).flatten()

            self.hem_plt = self.ax.plot_trisurf(
                x_ara, y_ara, z_ara,
                linewidth=0, alpha=self.alpha, color=self.color
            )
        else:
            self.hem_plt = None


        # plotting intersect
        self.ints_pltlst = []
        for grid in self.grid_lst:
            h, l = grid.h, grid.l
            if self.r < h:      # grid lies above hemisphere
                ints_plt = None
            else:
                phinum = _phinumints*int(h)
                phi_ara = np.linspace(0, 2*np.pi, phinum)
                x_ara = np.sqrt(self.r**2 - h**2) * np.cos(phi_ara)
                y_ara = np.sqrt(self.r**2 - h**2) * np.sin(phi_ara)
                z_ara = h * np.ones_like(x_ara)
                if self.proj3d_boo:
                    points_lst = [x_ara, y_ara, z_ara]
                else:
                    points_lst = [x_ara, y_ara]

                # filtering segments of the ring that are not in the plane
                out_mask = (np.abs(x_ara) > l/2) + (np.abs(y_ara) > l/2)
                for ara in points_lst:
                    np.putmask(ara, out_mask, np.nan)

                # plotting
                ints_plt = self.ax.plot(
                    *points_lst,
                    linewidth=self.ints_linewidth, color=self.color
                )

                # storing plot
                self.ints_pltlst.append(ints_plt)
