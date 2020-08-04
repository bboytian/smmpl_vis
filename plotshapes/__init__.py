# imports
from .aimlines import aimlines
from .aimlines_check import aimlines_check
from .aimpath import aimpath
from .cone import cone
from .grid import grid
from .hemisphere import hemisphere

from ..globalimports import *


# main class
class plotshapes:

    def __init__(
            self,
            ax, gridind,
            timeobj,
            sunforecaster,
            plotshapes_tg,
    ):
        '''
        Attributes with 'self' in the front are to be animated

        Future
            - lidar cone to be directed to move with scan_event

        Parameters
            ax (plt.Axes): ax we want to plot on
            gridind (int): determines which grid info to plot on specified 2d ax
                    (str): 'all', plots all grids info on 3d ax
            timeobj (scanpat_calc.timeobj)
            sunforecaster (scanpat_calc.sunforecaster)
            plotshapes_tg (scanpat_calc.targetgenerator.plotshapes)
        '''

        ## plot params
        hem_alpha = 0.2
        hemints_linewidth = 2

        cone_alpha = 0.2
        coneints_linewidth = hemints_linewidth

        grid_markersize = 5
        grid_markeralpha = 0.2
        grid_linewidth = 0.5
        grid_linealpha = 0.6
        grid_alpha = 0.4
        grid_colorstartind = 6

        aimlines_linewidth = 1
        aimlines_alpha = 0.2
        aimlines_linestyle = '-'
        aimlines_color = 'k'
        aimlines_markersize = grid_markersize

        aimlinescheck_linestyle, aimlinescheck_linewidth = '-', 3
        aimlinescheck_markersize = grid_markersize
        aimlinescheck_alpha, aimlinescheck_color = 1, 'orange'

        aimpath_linewidth = 1.5
        aimpath_alpha = 0.3
        aimpath_linestyle = '-'
        aimpath_color = 'b'

        ## other plot values
        cone_height = 20        # [km]

        # object attributes
        self.to = timeobj
        self.sf = sunforecaster


        # init

        ## scanpat_calc visualisation objects  using plotshapes_tg
        grid_lst_tg = plotshapes_tg.grid_lst
        lidar_hem_tg = plotshapes_tg.lidar_hem
        sun_cone_tg = plotshapes_tg.sun_cone
        targ_aimlines_tg = plotshapes_tg.targ_aimlines
        targ_aimpath_tg = plotshapes_tg.targ_aimpath

        if gridind == 'all':
            grid_lst = [
                grid(
                    ax,
                    grid_linewidth, grid_linealpha,
                    grid_markersize, grid_markeralpha,
                    grid_alpha, 'C{}'.format(grid_colorstartind+i),

                    grid_tg
                ) for i, grid_tg in enumerate(grid_lst_tg)
            ]
        else:
            grid_obj = grid(
                ax,
                grid_linewidth, grid_linealpha,
                grid_markersize, grid_markeralpha,
                grid_alpha, 'C{}'.format(grid_colorstartind+gridind),

                grid_lst_tg[gridind]
            )

        lidar_hem = hemisphere(
            ax, gridind,
            hem_alpha, 'C3',
            hemints_linewidth,

            lidar_hem_tg
        )
        self.sun_cone = cone(
            ax, gridind,
            timeobj, sunforecaster,
            cone_height,
            True,               # swath_boo
            cone_alpha, 'C1',
            coneints_linewidth,

            sun_cone_tg
        )
        self.targ_aimlines = aimlines(
            ax, gridind,
            aimlines_linestyle, aimlines_linewidth,
            aimlines_markersize,
            aimlines_alpha, aimlines_color,
            grid_colorstartind,

            targ_aimlines_tg
        )
        self.targ_aimpath = aimpath(
            ax, gridind,
            aimpath_linestyle, aimpath_linewidth,
            aimpath_alpha, aimpath_color,

            targ_aimpath_tg
        )


        ## other visualisation objects
        unit_hem = hemisphere(  # shows the blind range of the lidar
            ax, gridind,
            hem_alpha, 'C2',
            hemints_linewidth,

            r=0.3,
            grid_lst=grid_lst_tg
        )
        self.lidar_cone = cone(
            ax, gridind,
            timeobj, sunforecaster,
            cone_height,
            False,              # swath_boo
            1, 'C2',
            coneints_linewidth*2,

            thetas=0, phis=0,
            Thetas=0.005,
            grid_lst=grid_lst_tg,
        )
        if SHOWCHECKBOO:
            self.sp_aimlinescheck = aimlines_check(
                ax, gridind,
                aimlinescheck_linestyle, aimlinescheck_linewidth,
                aimlinescheck_markersize,
                aimlinescheck_alpha, aimlinescheck_color,

                self.to.get_ts(),
                targ_aimlines_tg
            )



    # update methods

    def update_ts(self):
        '''
        for the sake of animation
        '''
        self.sun_cone.update_ts(*self.sf.get_angles(self.to.get_ts()))

    def update_toseg(
            self,
            sun_cone_tg,
            targ_aimlines_tg,
            targ_aimpath_tg,
    ):
        '''
        updates sunswath, aimlines and aimpath

        Parameters
          sun_cone_tg (scanpat_calc.targetgenerator.plotshapes.sun_cone)
          targ_aimline_tg (scanpat_calc.targetgenerator.plotshapes.targ_aimline)
          targ_aimpath_tg (scanpat_calc.targetgenerator.plotshapes.targ_aimpath)
        '''
        self.sun_cone.update_toseg(sun_cone_tg)
        self.targ_aimlines.update_toseg(targ_aimlines_tg)
        self.targ_aimpath.update_toseg(targ_aimpath_tg)
        if SHOWCHECKBOO:
            self.sp_aimlinescheck.update_toseg(self.to.get_ts(), targ_aimlines_tg)
