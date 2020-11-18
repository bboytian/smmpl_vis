# imports
from copy import deepcopy
import datetime as dt
import math
import time

import matplotlib.animation as pan
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

# from . import plotshapes as ps
from .global_imports.smmpl_vis import *

# class
class visualiser:

    def __init__(
            self,
            timeobj,
            interval=0,

            scanpatvis=None,
            productvis=None,
            staticvis=None,

    ):
        '''
        1. other plot params stored in plotshapes.__init__.plotshapes
        2. timeobj is manipulated here and only here

        Future
            - see whether we can derive realtime_boo internally, and not from
              timeobj

        Parameters
            timeobj (scanpat_calc.timeobj)
            interval (float): [ms] interval between frames by during animation
            visobjects...: visualisation objects, each object symbolising a
                           visualisation protocol
        '''
        # Attributes
        self.to = timeobj
        self.interval = interval

        self.realtime_boo = REALTIMEBOO
        self.utcinfo = timeobj.get_utcinfo()

        self.viewazimuth = VIEWAZIMUTHSTART

        self.visobjects = [
            scanpatvis,
            productvis,
            staticvis
        ]
        self.visobjects = [x for x in self.visobjects if x]
        self.scanpatvis = scanpatvis
        self.ps = None
        self.productvis = productvis
        self.staticvis = staticvis

        self.ax3d = None
        self.ax2d_l = []
        self.fig3d = None
        self.fig2d_l = []
        self.animation3d = None
        self.animation2d_l = []

        # figure creation
        ## 3d plot
        fig3d = plt.figure(figsize=(10, 10), constrained_layout=True)
        ax3d = fig3d.add_subplot(111, projection='3d')
        ax3d.pbaspect = [SCALE, SCALE, SCALE]
        ax3d.set_xlabel('South -- North')
        ax3d.set_ylabel('East -- West')
        ax3d.set_xlim([-CURLYL/2, CURLYL/2])
        ax3d.set_ylim([-CURLYL/2, CURLYL/2])
        ax3d.set_zlim([0, CURLYL])

        self.ax3d = ax3d
        self.fig3d = fig3d

        ## grid projection visualisation plot
        self.ax2d_l = []
        if self.scanpatvis:
            self.ps = self.scanpatvis.ps
            lengrid_lst_tg = len(self.ps.grid_lst)
            ax2dnum = math.ceil(math.sqrt(lengrid_lst_tg))
            fig2d, axs2d = plt.subplots(ax2dnum, ax2dnum, figsize=(8, 10))
            try:                    # handles the event where we only have one grid
                self.ax2d_l += list(axs2d.flatten())
            except AttributeError:
                self.ax2d_l.append(axs2d)
            for i in range(lengrid_lst_tg):
                ax = self.ax2d_l[i]
                ax.set_xlabel('South -- North')
                ax.set_ylabel('East -- West')
                axlim = self.ps.grid_lst[i].l/2 * 1.2
                ax.set_xlim([-axlim, axlim])
                ax.set_ylim([-axlim, axlim])
                ax.margins(0)

        ## projection of products
        if self.staticvis and self.productvis:
            figprod2d, axprod2d = plt.subplots()
            axprod2d.set_xlim([-self.staticvis.axlim, self.staticvis.axlim])
            axprod2d.set_ylim([-self.staticvis.axlim, self.staticvis.axlim])
            self.ax2d_l.append(axprod2d)

        if self.scanpatvis:
            self.fig2d_l.append(fig2d)
        if self.staticvis and self.productvis:
            self.fig2d_l.append(figprod2d)

        # meta initialisation
        self.fig3d.suptitle(self.to.get_ts())
        for fig in self.fig2d_l:
            fig.suptitle(self.to.get_ts())
        self.ax3d.view_init(VIEWELEVATION, VIEWAZIMUTHSTART)

        # visobjects init_vis
        for visobject in self.visobjects:
            visobject.init_vis([ax3d, *self.ax2d_l])

        # animation object creation
        self.animation3d = pan.FuncAnimation(
            self.fig3d, self.update,
            interval=self.interval,
            frames=np.arange(int(self.to.Deltatime/self.to.deltatime))
        )

        for fig in self.fig2d_l:
            self.animation2d_l.append(pan.FuncAnimation(
                fig, self.update,
                interval=self.interval,
                frames=np.arange(int(self.to.Deltatime/self.to.deltatime))
            ))


        # animate

        # showing plot
        if not SAVEANIMATION2D and not SAVEANIMATION3D:
            plt.show()

        # saving file
        if SAVEANIMATION3D:
            self.animation3d.save(
                DIRCONFN(SAVEDIR, SAVEFILE.format(
                    self.to.starttime, self.to.endtime, SAVE3DNAME
                )),
                'ffmpeg', fps=VIDEOFPS
            )

        if SAVEANIMATION2D:
            animation2d = self.animation2d_l[SAVE2DIND]
            animation2d.save(
                DIRCONFN(SAVEDIR, SAVEFILE.format(
                    self.to.starttime, self.to.endtime, SAVE2DNAME.format(SAVE2DIND)
                )),
                'ffmpeg', fps=VIDEOFPS
            )


    def update(self, scapegoat):
        '''
        Parameters
            scapegoat: a filler for all animation update functions
        '''
        # time keeping
        print('seg: {}/{}, '.format(*self.to.get_tosegpos()),
              'time: {}'.format(self.to.get_ts()))

        # iterate ts
        tsstop_boo = self.to.next_ts()  # boolean returned

        # iterate toseg
        if tsstop_boo:                   # moving on to next timeobj segment
            tosegstop_boo = self.to.next_toseg()

            if tosegstop_boo:              # stop plotting
                self.animation3d.event_source.stop()
                for animation2d in self.animation2d_l:
                    animation2d.event_source.stop()

        # update for toseg
            else:
                self.update_ts()
                self.update_toseg()

        # update for ts
        else:
            self.update_ts()

        # wait for clock if plotting in real time
        if self.realtime_boo:
            self.wait()


    def update_ts(self):

        if ROTATE3DFIG:
            self.viewazimuth += VIEWROTDISCRETE
            if self.viewazimuth > 360:
                self.viewazimuth -= 360
            self.ax3d.view_init(VIEWELEVATION, self.viewazimuth)

        for visobject in self.visobjects:
            visobject.update_ts()

        self.fig3d.suptitle(self.to.get_ts())
        for fig in self.fig2d_l:
            fig.suptitle(self.to.get_ts())

    def update_toseg(self):
        for visobject in self.visobjects:
            visobject.update_toseg()

    def wait(self):
        '''
        this accounts for any temporary lag in computation which crosses over
        into the next timestamp
        tip: fps shld be chosen such that computation is able to catch up in
        the next frame
        '''
        waittime = (
            self.to.get_ts()
            - LOCTIMEFN(dt.datetime.now(), self.utcinfo)
        ).total_seconds()
        try:
            time.sleep(waittime)
        except ValueError:      # if waittime is negative
            print('\tlag in update, overflow into next timestamp')
