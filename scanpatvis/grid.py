# imports
import numpy as np


# main class
class grid:

    def __init__(
            self,
            ax,
            linewidth, linealpha,
            markersize, markeralpha,
            alpha, color,
            grid_tg,
    ):
        '''
        Parameters
            ax (matplotlib.pyplot.axes)
            linewidth (float): linewidth of grid
            linealpha (float): alpha of grid lines
            markersize (float): size of aimpoints on grid
            markeralpha (float): alpha of aimpoints on grid
            alpha (float): alpha of plane
            color (str): color of all plots

            grid_tg (scanpat_calc.targetgenerator.grid)
        Methods
            plot: plot grid for '3d' and '2d'
        '''
        # Attributes
        ## plot type
        self.ax = ax
        self.proj3d_boo = '3d' in ax.name

        ## plot display settings
        self.markersize, self.markeralpha = markersize, markeralpha
        self.linewidth, self.linealpha =  linewidth, linealpha
        self.alpha, self.color = alpha, color

        ## plots
        self.grid_plt = None
        self.plane_plt = None
        self.scat_plt = None

        ## targetgenerator objects
        self.xp_mat, self.yp_mat = grid_tg.xp_mat, grid_tg.yp_mat
        self.xg_mat, self.yg_mat = grid_tg.xg_mat, grid_tg.yg_mat
        self.zg_mat = grid_tg.zg_mat
        self.x_ara, self.y_ara = grid_tg.x_ara, grid_tg.y_ara
        self.z_ara = grid_tg.z_ara
        self.h = grid_tg.h

        # plotting
        self.plot()


    #  plot meth
    def plot(self):

        # plots
        if self.proj3d_boo:

            # plotting plane
            xp_ara = self.xp_mat.flatten()
            yp_ara = self.yp_mat.flatten()
            zp_ara = self.h*np.ones_like(xp_ara)
            plane_plt = self.ax.plot_trisurf(
                xp_ara, yp_ara, zp_ara,
                linewidth=0, alpha=self.alpha, color=self.color
            )

            # plotting grid
            grid_plt = self.ax.plot_wireframe(
                self.xg_mat, self.yg_mat, self.zg_mat,
                linewidth=self.linewidth,
                alpha=self.linealpha, color=self.color
            )

            # plotting scan target points
            scat_plt = self.ax.scatter(
                self.x_ara, self.y_ara, zs=self.z_ara,
                s=self.markersize, color=self.color
            )


        else:

            # plotting plane
            xp_ara, yp_ara = self.xp_mat.T[0], self.yp_mat[0]
            plane_plt = self.ax.fill_between(
                xp_ara, yp_ara[0], yp_ara[1],
                alpha=self.alpha, color=self.color
            )

            # plotting grid
            grid_plt = None
            xg_ara, yg_ara = self.xg_mat.T[0], self.yg_mat[0] # for 2d gridlines
            for xg in xg_ara:
                self.ax.axvline(xg, linewidth=self.linewidth,
                                alpha=self.linealpha, color=self.color)
            for yg in yg_ara:
                self.ax.axhline(yg, linewidth=self.linewidth,
                                alpha=self.linealpha, color=self.color)

            # plotting scan target points
            scat_plt = self.ax.plot(
                self.x_ara, self.y_ara, 'o',
                markersize=self.markersize,
                alpha=self.markeralpha, color=self.color,
            )

        # Storing
        self.grid_plt = grid_plt
        self.plane_plt = plane_plt
        self.scat_plt = scat_plt
