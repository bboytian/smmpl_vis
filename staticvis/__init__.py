# imports
from .gridline_calc import main as gridline_calc


# params
_3dlinewidth = 1
_2dlinewidth = 1
_linecolor = 'k'
_linestyle = '-'

_3dgridheight = 15


# class
class staticvis():

    def __init__(
            self,
            pixelsize, gridlen,
            plotbot_boo=True
    ):

        self.axlim = pixelsize*gridlen/2
        self.lines_l = gridline_calc(pixelsize, gridlen, _3dgridheight, plotbot_boo)

    def init_vis(self, axl):

        ax3d_l = list(filter(lambda x: '3d' in x.name, axl))
        ax2d_l = list(filter(lambda x: '3d' not in x.name, axl))

        for ax3d in ax3d_l:
            self._plot_3d(ax3d)

        for ax2d in ax2d_l:
            self._plot_2d(ax2d)


    def _plot_3d(self, ax):

        # plotting pixel grid
        # draws a grid on the ground and at the specified 3D grid height
        for line in self.lines_l:
            ax.plot(
                *line,
                linewidth=_3dlinewidth, color=_linecolor, marker='',
                linestyle=_linestyle
            )

    def _plot_2d(self, ax):

        # plotting pixel grid
        for line in self.lines_l[:3]:  # hardcoded assumption here
            ax.plot(
                *line[:2],
                linewidth=_2dlinewidth, color=_linecolor, marker='',
                linestyle=_linestyle
            )

    def update_ts(self):
        pass

    def update_toseg(self):
        pass




if __name__ == '__main__':
    import matplotlib.pyplot as plt

    fig3d = plt.figure(figsize=(10, 10), constrained_layout=True)
    ax3d = fig3d.add_subplot(111, projection='3d')

    fig2d, ax2d = plt.subplots()

    sv = staticvis(
        5, 3
    )
    sv.init_vis([ax3d, ax2d])

    plt.show()
