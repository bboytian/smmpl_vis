# imports
import datetime as dt
import math
import time

import matplotlib.animation as pan
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

# from . import plotshapes as ps
from .global_imports import *

# class
class visualiser:

    def __init__(
            self,
            timeobj,
            interval=0,
            *visobjects
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
            visobjects: visualisation objects, each object symbolising a
                        visualisation protocol
        '''
        # Attributes
        self.to = timeobj
        self.interval = interval
        self.visobjects = visobjects

        self.realtime_boo = self.to.get_realtimeboo()
        self.utcinfo = self.to.get_utcinfo()

        self.viewazimuth = VIEWAZIMUTHSTART


        # init

        ## figure creation
        ### 3d plot
        fig3d = plt.figure(figsize=(10, 10), constrained_layout=True)
        ax3d = fig3d.add_subplot(111, projection='3d')
        ax3d.pbaspect = [SCALE, SCALE, SCALE]
        ax3d.set_xlabel('South -- North')
        ax3d.set_ylabel('East -- West')
        ax3d.set_xlim([-CURLYL/2, CURLYL/2])
        ax3d.set_ylim([-CURLYL/2, CURLYL/2])
        ax3d.set_zlim([0, CURLYL])

        ### grid projection visualisation plot
        axs2d = []
        # lengrid_lst_tg = len(self.ps_tg.grid_lst)
        # ax2dnum = math.ceil(math.sqrt(lengrid_lst_tg))
        # fig2d, axs2d = plt.subplots(ax2dnum, ax2dnum, figsize=(8, 10))
        # try:                    # handles the event where we only have one grid
        #     axs2d = axs2d.flatten()
        # except AttributeError:
        #     axs2d = [axs2d]
        # for i in range(lengrid_lst_tg):
        #     ax = axs2d[i]
        #     ax.set_xlabel('South -- North')
        #     ax.set_ylabel('East -- West')
        #     axlim = self.ps_tg.grid_lst[i].l/2 * 1.2
        #     ax.set_xlim([-axlim, axlim])
        #     ax.set_ylim([-axlim, axlim])
        #     ax.margins(0)

        self.ax3d_l = [ax3d]
        self.fig3d_l = [fig3d]
        self.tstxt_l = [ax3d.text(
            0, 0, CURLYL, self.to.get_ts()
        )
                        for i, ax3d in enumerate(self.ax3d_l)]

        ## visobjects init_vis
        for visobject in self.visobjects:
            visobject.init_vis([ax3d, *axs2d])


        # show
        self.animation3d = pan.FuncAnimation(
            fig3d, self.update,
            interval=self.interval,
            frames=np.arange(int(self.to.Deltatime/self.to.deltatime))
        )
        # self.animation3d.save(
        #     '/home/tianli/Desktop/trial.mp4',
        #     # writer=pan.FFMpegWriter(fps=10),
        #     'ffmpeg', fps=VIDEOFPS
        # )

        plt.show()

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

        for ax3d in self.ax3d_l:

            self.viewazimuth += VIEWROTDISCRETE
            if self.viewazimuth > 360:
                self.viewazimuth -= 360
            ax3d.view_init(VIEWELEVATION, self.viewazimuth)

        for visobject in self.visobjects:
            visobject.update_ts()

        for tstxt in self.tstxt_l:
            tstxt.remove()
        self.tstxt_l = [ax3d.text(
            0, 0, CURLYL, self.to.get_ts()
        )
                        for i, ax3d in enumerate(self.ax3d_l)]

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
