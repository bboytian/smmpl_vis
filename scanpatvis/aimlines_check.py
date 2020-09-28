# imports
import datetime as dt
import os

import numpy as np
import pandas as pd

from ..global_imports.smmpl_vis import *


# supp function
def _datestrfmt_funcfunc(start):
    def datestrfmt_func(datestr):
        return datestr[start:start+TIMELEN]
    return datestrfmt_func


# class
class aimlines_check:

    def __init__(
            self,
            ax, gridind,
            linestyle, linewidth,
            markersize,
            alpha, color,

            timestamp,
            aimlines_ps
    ):
        '''
        Plots the calculated scan patterns on both 2D and 3D axes

        Parameters
            ax (matplotlib.pyplot.axes)
            gridind (int): determines which grid info to plot on specified 2d ax
                    (str): 'all', plots all grids info on 3d ax
            linestyle (str): linestyle of aimline
            linewidth (float): linewidth of aimline
            markersize (float): size of marker on 2D plot
            alpha (float): alpha of aimline
            color (str): color of aimline

            timestamp (datetime like): timestamp which would be used to search for
                                       scan pattern
            aimlines_ps (scanpat_calc.targetgenerator.aimlines)

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
        self.markersize = markersize
        self.alpha, self.color = alpha, color

        ## plots
        self.aimlines_pltlst = None

        ## obj attrs
        self.grid_lst = aimlines_ps.grid_lst

        ## data attrs
        self.dir_a = None
        self.ts = timestamp.replace(tzinfo=None)

        # plotting
        self.plot_toseg(timestamp)


    # main meth
    def plot_toseg(self, timestamp):

        # updating
        self.ts = timestamp.replace(tzinfo=None)
        ## searching for scanpattern
        today = self.ts
        yesterday = today - dt.timedelta(1)
        today_dir = DIRCONFN(MPLDATADIR, DATEFMT.format(today))
        yesterday_dir = DIRCONFN(MPLDATADIR, DATEFMT.format(yesterday))
        data_filelst = os.listdir(today_dir) + os.listdir(yesterday_dir)
        data_filelst = list(filter(
            lambda x: SCANPATFILE[SCANPATDATEIND:] in x,
            data_filelst
        ))
        sdate_ara = list(map(_datestrfmt_funcfunc(SCANPATSDATEIND), data_filelst))
        edate_ara = list(map(_datestrfmt_funcfunc(SCANPATEDATEIND), data_filelst))
        sdate_ara = pd.to_datetime(sdate_ara)
        edate_ara = pd.to_datetime(edate_ara)
        boo_ara = (sdate_ara <= today) * (today < edate_ara)
        try:
            scanpat_dir = data_filelst[np.argwhere(boo_ara)[0][0]]
        except IndexError:
            raise Exception(
                'scanpattern for {} to {} not calculated'.
                format(DATEFMT.format(yesterday), DATEFMT.format(today))
            )
        scanpat_dir = DIRCONFN(today_dir, scanpat_dir)
        scanpat_dir = scanpat_dir.replace('\\', '/')  # os.listdir creates '\'
                                                      # in windows
        ## reading scanpat file
        self.dir_a = np.deg2rad(np.loadtxt(scanpat_dir, delimiter=','))
        thetal_a, phi_a = LIDAR2SPHEREFN(self.dir_a, np.deg2rad(ANGOFFSET))

        # operation
        self.aimlines_pltlst = []
        for i, grid in enumerate(self.grid_lst):

            # plotting
            if self.proj3d_boo:

                # computing cartisian points
                z_ara = np.ones_like(thetal_a) * grid.h
                r_ara = z_ara/np.cos(thetal_a)
                x_ara = r_ara * np.sin(thetal_a) * np.cos(phi_a)
                y_ara = r_ara * np.sin(thetal_a) * np.sin(phi_a)

                # plotting
                indinsertara = range(0, len(x_ara), 1)
                x_ara = np.insert(x_ara, indinsertara, 0)
                y_ara = np.insert(y_ara, indinsertara, 0)
                z_ara = np.insert(z_ara, indinsertara, 0)

                aimlines_plt = self.ax.plot(
                    x_ara, y_ara, z_ara,
                    linewidth=self.linewidth, linestyle=self.linestyle,
                    alpha=self.alpha, color=self.color
                )

            else:

                phi_ara = phi_a
                theta_ara = thetal_a

                if self.allgrid_boo:
                    r_ara = grid.h * np.tan(theta_ara)
                else:
                    r_ara = self.grid_lst[self.gridind].h * np.tan(theta_ara)
                x_ara = r_ara * np.cos(phi_ara)
                y_ara = r_ara * np.sin(phi_ara)

                # plotting
                aimlines_plt = self.ax.plot(
                    x_ara, y_ara, 'o',
                    markersize=self.markersize,
                    color=self.color
                )

            # storing
            self.aimlines_pltlst.append(aimlines_plt)


    # update meth
    def update_toseg(self, aimlines_ps):
        # updating relevant target generator objects
        self.aimlines = aimlines_ps

        # removing plot
        for aimlines_plt in self.aimlines_pltlst:
            aimlines_plt[0].remove()

        # plotting
        self.plot_toseg()
