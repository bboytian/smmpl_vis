# imports
import datetime as dt
import math
import time

import matplotlib.animation as pan
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

from . import plotshapes as ps
from .global_imports import *

# params
CURLYL = 30                     # plot limits of 2D axis
SCALE = 1.3                     # scaling for 2D axis display size


# class
class visualiser:

    def __init__(
            self,
            timeobj, sunforecaster,
            qscanpat, qscanevent,
            interval=0,
    ):
        '''
        1. other plot params stored in plotshapes.__init__.plotshapes
        2. timeobj is manipulated here and only here

        Future
            - has to be able to get scan position from scan_event, when
               seperated into another package

        Parameters
            timeobj (scanpat_calc.timeobj)
            sunforecaster (scanpat_calc.sunforecaster)
            qscanpat (multiprocessing.Queue): contains data from scanpat_calc
            *qscanevent (multiprocessing.Queue): contains data from scan_event
            interval (float): [ms] interval between frames by during animation

            * asterisks indicate not implemented yet
        '''
        # Attributes
        self.to = timeobj
        self.qscanpat = qscanpat
        self.qscanevent = qscanevent

        self.realtime_boo = self.to.get_realtimeboo()
        self.utcinfo = self.to.get_utcinfo()
        self.interval = interval


        # init

        ## getting original data
        self.ps_tg = qscanpat.get(True) # wait for scanpat_calc to put in 1st ps

        ## figure creation
        fig3d = plt.figure(figsize=(10, 10), constrained_layout=True)
        ax3d = fig3d.add_subplot(111, projection='3d')
        ax3d.pbaspect = [SCALE, SCALE, SCALE]
        ax3d.set_xlabel('South -- North')
        ax3d.set_ylabel('East -- West')
        ax3d.set_xlim([-CURLYL/2, CURLYL/2])
        ax3d.set_ylim([-CURLYL/2, CURLYL/2])
        ax3d.set_zlim([0, CURLYL])

        self.proj3d_ps = ps.plotshapes(
            ax3d, 'all',
            timeobj,
            sunforecaster,
            self.ps_tg,
        )

        ### grid projection visualisation plot
        lengrid_lst_tg = len(self.ps_tg.grid_lst)
        ax2dnum = math.ceil(math.sqrt(lengrid_lst_tg))
        fig2d, axs2d = plt.subplots(ax2dnum, ax2dnum, figsize=(8, 10))
        try:                    # handles the event where we only have one grid
            axs2d = axs2d.flatten()
        except AttributeError:
            axs2d = [axs2d]
        self.proj2d_pslst = []  # one plotshpae obj for each grid
        for i in range(lengrid_lst_tg):
            ax = axs2d[i]
            ax.set_xlabel('South -- North')
            ax.set_ylabel('East -- West')
            axlim = self.ps_tg.grid_lst[i].l/2 * 1.2
            ax.set_xlim([-axlim, axlim])
            ax.set_ylim([-axlim, axlim])
            ax.margins(0)
            self.proj2d_pslst.append(
                ps.plotshapes(
                    ax, i,
                    timeobj,
                    sunforecaster,
                    self.ps_tg,
                )
            )


        # show
        self.animation3d = pan.FuncAnimation(
            fig3d, self.update,
            interval=self.interval,
            frames=np.arange(self.to.equivtime.total_seconds()*self.to.fps)
        )
        self.animation2d = pan.FuncAnimation(
            fig2d, self.update,
            interval=self.interval,
            frames=np.arange(self.to.equivtime.total_seconds()*self.to.fps)
        )
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
                self.animation2d.event_source.stop()
                plt.close()

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
        self.proj3d_ps.update_ts()
        for proj2d_ps in self.proj2d_pslst:
            proj2d_ps.update_ts()

    def update_toseg(self):
        self.ps_tg = self.qscanpat.get(False)
        sun_cone_tg = self.ps_tg.sun_cone
        targ_aimlines_tg = self.ps_tg.targ_aimlines
        targ_aimpath_tg = self.ps_tg.targ_aimpath

        self.proj3d_ps.update_toseg(
            sun_cone_tg,
            targ_aimlines_tg,
            targ_aimpath_tg,
        )
        for proj2d_ps in self.proj2d_pslst:
            proj2d_ps.update_toseg(
                sun_cone_tg,
                targ_aimlines_tg,
                targ_aimpath_tg,
            )


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
            msg_str = '\tlag in update, overflow into next timestamp'
            print(msg_str)
