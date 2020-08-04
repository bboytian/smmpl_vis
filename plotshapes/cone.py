# imports
import matplotlib.patches as mpatch
import mpl_toolkits.mplot3d.art3d as mpart
import numpy as np


# params
## discretization params
ZNUMSURF = 1
PHINUMSURF = 1
PHINUMINTS = 4
RHONUMINTS = 1
LNUMSWATH = 10

## default plot paramsA
THETAS = 0.05                   # [rad]


# class
class cone:

    def __init__(
            self,
            ax, gridind,
            timeobj, sunforecaster,
            r,
            swath_boo,
            alpha, color,
            ints_linewidth,

            cone_tg=None,
            thetas=0, phis=0,
            Thetas=THETAS,
            grid_lst=[]
    ):
        '''
        has the option to plot a static cone if cont_tg is not specified,
        the cone should not programmed to animate in plotshape.__init__

        Parameters
            ax (matplotlib.pyplot.axes)
            gridind (int): determines which grid info to plot on specified 2d ax
                    (str): 'all', plots all grids info on 3d ax
                           can be None if not cone_tg
            timeobj (scanpat_calc.timeobj): can be None if not cone_tg
            sunforecaster (scanpat_calc.sunforecaster): can be None if not cone_tg
            swath_boo (boolean): whether to plot swath, simple cone otherwise
            alpha (float): alpha of cone and swath
            color (str): color of cone and swath
            ints_linewidth (float): linewidth of line of intersect surface

            cone_tg (scanpat_calc.targetgenerator.cone)
            thetas, phis (float): direction of cone, specified if cone_tg==None
            r (float): [km] height of cone
            grid_lst (list): specified if we want intersection to be plotted


        Methods
            plot_ts: plots cone
            plot_toseg: plots cone swath
            update_ts: update timestamp plot
            update_toseg: update timeobjseg plot, does NOT update timestamp plot
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
        self.swath_boo = swath_boo
        self.alpha, self.color = alpha, color
        self.color = color
        self.ints_linewidth = ints_linewidth

        ## plots
        self.cone_plt = None
        self.ints_pltlst = None
        self.swathints_pltlst = None

        ## object attribtues
        self.to, self.sf = timeobj, sunforecaster
        self.r = r
        if cone_tg:
            # static
            if self.allgrid_boo:
                self.grid_lst = cone_tg.grid_lst
            else:
                self.grid_lst = [cone_tg.grid_lst[gridind]]
            self.Thetas = cone_tg.Thetas
            # changing
            self.thetas, self.phis = self.sf.get_angles(self.to.get_ts())
            self.cone = cone_tg
            self.swath_pathlst = None
        else:         # static cone, not animated
            self.thetas, self.phis = thetas, phis
            self.Thetas = Thetas
            if self.allgrid_boo:
                self.grid_lst = grid_lst
            else:
                if gridind:
                    self.grid_lst = [grid_lst[gridind]]
                else:
                    self.grid_lst = []


        # plotting
        self.plot_ts()
        if swath_boo:
            self.plot_toseg()


    # plot methods

    def plot_ts(self):

        rot_mat = np.matrix([      # rot about y in thetas then about z in phi
            [np.cos(self.phis)*np.cos(self.thetas), -np.sin(self.phis),
             np.cos(self.phis)*np.sin(self.thetas)],
            [np.sin(self.phis)*np.cos(self.thetas), np.cos(self.phis),
             np.sin(self.phis)*np.sin(self.thetas)],
            [-np.sin(self.thetas), 0, np.cos(self.thetas)]
        ])

        # Plotting surface
        if self.proj3d_boo:

            # generating upright cone
            znum = ZNUMSURF * int(self.r)
            phinum = PHINUMSURF * int(self.r)
            z_mat, phi_mat = np.mgrid[0:self.r:znum*1j, 0:2*np.pi:phinum*1j]
            rho_mat = z_mat * np.tan(self.Thetas)
            x_ara = (rho_mat * np.cos(phi_mat)).flatten()
            y_ara = (rho_mat * np.sin(phi_mat)).flatten()
            z_ara = z_mat.flatten()
            vec_mat = np.matrix([x_ara, y_ara, z_ara])

            # rotating cone
            grid_len = len(z_mat)
            x_mat, y_mat, z_mat = [ara.reshape(grid_len, grid_len) for ara in\
                                  rot_mat * vec_mat]
            # plotting
            self.cone_plt = self.ax.plot_surface(
                x_mat, y_mat, z_mat,
                linewidth=0, alpha=self.alpha, color=self.color
            )
        else:
            self.cone_plt = None


        # plotting intersection
        self.ints_pltlst = []
        for grid in self.grid_lst:
            h, l = grid.h, grid.l

            if self.thetas + self.Thetas >= np.pi/2: # handling undefined region
                ints_plt = None

            else:
                # generating tilted cone slice
                phinum = PHINUMINTS * int(h)
                rhonum = RHONUMINTS * int(h)

                phi_ara = np.linspace(0, 2*np.pi, phinum)
                z_ara = h / (np.cos(self.thetas)\
                    - np.tan(self.Thetas)*np.sin(self.thetas)*np.cos(phi_ara))
                rhoh = z_ara * np.tan(self.Thetas)
                x_ara = rhoh  * np.cos(phi_ara)
                y_ara = rhoh * np.sin(phi_ara)
                vec_mat = np.matrix([x_ara, y_ara, z_ara])

                # rotating cone
                x_ara, y_ara, z_ara = np.array(rot_mat * vec_mat)

                if self.proj3d_boo:
                    points_ara = np.array([x_ara, y_ara, z_ara])
                else:
                    points_ara = np.array([x_ara, y_ara])

                # filtering portions that are not in the plane
                out_mask = (np.abs(x_ara) > l/2) + (np.abs(y_ara) > l/2)
                points_ara = points_ara[:, ~out_mask]

                # plotting
                ints_plt = self.ax.plot(
                    *points_ara,
                    linewidth=self.ints_linewidth, color=self.color
            )

            # storing plot
            self.ints_pltlst.append(ints_plt)


    def plot_toseg(self):

        # updating attributes
        self.swath_pathlst = self.cone.swath_pathlst

        self.swathints_pltlst = []
        for i, grid in enumerate(self.grid_lst):
            h = grid.h
            if self.allgrid_boo:
                swath_path = self.swath_pathlst[i]
            else:
                swath_path = self.swath_pathlst[self.gridind]

            try:
                swathints_plt = self.ax.add_patch(
                    mpatch.PathPatch(swath_path,
                    alpha=self.alpha, color=self.color)
                )
                if self.proj3d_boo:
                    mpart.pathpatch_2d_to_3d(swathints_plt, z=h)
            except AttributeError: # swath path is outside the grid
                swathints_plt = None

            # storing
            self.swathints_pltlst.append(swathints_plt)



    # update methods

    def update_ts(self, thetas, phis):
        # getting new angles
        self.thetas, self.phis = thetas, phis

        # removing plot
        try:
            for ints_plt in self.ints_pltlst:
                ints_plt[0].remove()
        except TypeError:       # when suncone is below horizon;ints_plt == None
            pass
        try:
            self.cone_plt.remove()
        except AttributeError:  # handles '2d' proj where cone_plt == None
            pass

        # plotting
        self.plot_ts()


    def update_toseg(self, cone_tg):
        # updating relevant targetgenerator object
        self.cone = cone_tg

        # removing plot
        for swathints_plt in self.swathints_pltlst:
            try:
                swathints_plt.remove()
            except AttributeError: # in the event swath path is outside the grid
                pass

        # plotting
        self.plot_toseg()
