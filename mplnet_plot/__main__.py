# imports
import matplotlib.pyplot as plt
import matplotlib.colors as pcolors
import numpy as np

from .workarray_resampler import main as workarray_resampler
from .product_resampler import main as product_resampler
from ..solaris_opcodes.product_calc.nrb_calc import chunk_operate
from ..global_imports.smmpl_vis import *

# params
_marker_l = [                   # number of markers follow number of layers for
    "s",                        # single product
    "X",
    "*",
    "p",
    "P",
    "h",
    "H",
    "v",
    "^",
    "<",
    ">",
    "D",
    "d",
]
_color_l = [                    # number of colors follow number of product types
    'r',                        # should contrast sharply with 'viridis' color map
    'g',
]
_powernormconst = 0.5


# main func
def main(
        work_ltra, productmask_ltl3a,
        z_tra, r_trm, setz_a, setzind_ta,
        ts_ta,
):
    '''
    Performs two types of plots. Profile plots for each work_tra in work_ltra. and a
    pure product mask plot.

    This function will resample the work arrays such that all the altitudes fit on a
    single grid, making z_tra redundent; i.e. only the first time index is needed for
    the resampled z_tra

    Future
        - not able to change the color of the mask plot to the same color as the
          marker

    Parameters
        work_ltra (list): list of work_tra (np.ndarray) with time and range axis
        productmask_ltl3a (np.ndarray): array containing product mask

        z_tra (np.ndarray): corresponding altitude array
        r_trm (np.ndarray): corresponding mask
        setz_a (list): list of descriptors for the set of altitude arrays in z_tra
        setzind_ta (np.ndarray): indexes for setz_a for the time axis for all tra
                                 arrays
        ts_ta (np.ndarray): timestamp array
    '''
    # setting up figure
    nrows = len(work_ltra)
    if product_d:
        nrows += 1
    fig, axs = plt.subplots(nrows, sharex=True)

    # determining array for resampling
    ## find the first instance for each chunk
    ind_a = []
    for i, ind in enumerate(setzind_ta):
        if i not in ind_a:
            ind_a.append(i)
        if len(ind_a) == len(setz_a):
            break
    ## computing array
    zminmax_a = [z_tra[ind][r_trm[ind]][[0, -1]] for ind in ind_a]
    zmin = min([zminmax[0] for zminmax in zminmax_a])
    zmax = max([zminmax[1] for zminmax in zminmax_a])
    zstep = min([setz[0] for setz in setz_a]) * SPEEDOFLIGHT
    resamplez_ra = np.arange(zmin, zmax + zstep, zstep)

    # iterating each working array
    for i, work_tra in enumerate(work_ltra):

        # resampling for plotting
        resamplework_tra, resamplez_tra, resampler_trm, resamplesetz_a =\
            chunk_operate(
                work_tra, z_tra, r_trm, setz_a, setzind_ta,
                workarray_resampler,
                resamplez_ra,
                procnum=MPLNETPROCNUM
            )

        zresamplework_tra = np.nan_to_num(resamplework_tra)
        vmax = zresamplework_tra.max(axis=-1)
        resamplework_tra = resamplework_tra/(vmax[:, None])
        resamplework_tra[resamplework_tra < 0] = 0

        # plotting
        axs[i].pcolormesh(
            *np.meshgrid(ts_ta, resamplez_tra[0]),
            resamplework_tra.T,
            norm=pcolors.PowerNorm(_powernormconst)
        )


    # plotting product masks
    # iterate product types
    for i, productmask_tl3a in enumerate(productmask_ltl3a):
        # resampling product location
        resampleprodmask_tl3a, resampleprodmask_trm = product_resampler(
            productmask_tl3a, resamplez_tra
        )

        # plotting on other work arrays axis
        for k in range(len(axs)-1):
            for j in range(resampleprodmask_tl3a.shape[1]):

                # iterating plot properties
                lind = j%len(_marker_l)
                marker = _marker_l[lind]
                color = _color_l[i]

                # plotting
                resampleprodbot_tla = resampleprodmask_tl3a[:, j, 0]
                resampleprodtop_tla = resampleprodmask_tl3a[:, j, 2]
                axs[k].plot(
                    ts_ta, resampleprodbot_tla,
                    ts_ta, resampleprodtop_tla,
                    marker=marker, linestyle='',
                    color=color
                )

        # plotting on mask axis
        plotmask_trm = resampleprodmask_trm.astype(np.float)
        plotmask_trm[resampleprodmask_trm] = np.nan
        axs[-1].pcolormesh(
            *np.meshgrid(ts_ta, resamplez_tra[0]),
            plotmask_trm.T,
        )


    # showing plot
    plt.show()


# testing
if __name__ == '__main__':

    # imports
    from ..solaris_opcodes.file_readwrite import smmpl_reader, mpl_reader
    from ..solaris_opcodes.product_calc import main as product_calc

    # mutable params
    lidarname, mplreader = 'smmpl_E2', smmpl_reader
    combpol_boo = True
    pixelsize = 5               # [km]
    gridlen = 3

    angularoffset = 140.6                      # [deg]
    latitude, longitude = 1.299119, 103.771232  # [deg]
    elevation = 70                              # [m]


    # computing products
    product_d = product_calc(
        lidarname, mplreader,
        starttime=LOCTIMEFN('202010290000', 0),
        endtime=LOCTIMEFN('202010291200', 0),
        timestep=None, rangestep=None,
        angularoffset=angularoffset,

        combpolboo=True,

        pixelsize=pixelsize, gridlen=gridlen,
        latitude=latitude, longitude=longitude,
        elevation=elevation,
    )

    # parsing data

    ## working arrays
    nrb_d = product_d['nrb']
    ts_ta = nrb_d['Timestamp']
    z_tra = nrb_d['z_tra']
    r_tra = nrb_d['r_tra']
    r_trm = nrb_d['r_trm']
    NRB1_tra = nrb_d['NRB1_tra']
    NRB2_tra = nrb_d['NRB2_tra']
    NRB_tra = nrb_d['NRB_tra']
    SNR1_tra = nrb_d['SNR1_tra']
    SNR2_tra = nrb_d['SNR2_tra']
    SNR_tra = nrb_d['SNR_tra']
    setz_a = nrb_d['DeltNbinpadtheta_a']
    setzind_ta = nrb_d['DeltNbinpadthetaind_ta']
    work_ltra = [
        NRB_tra
    ]

    ## product masks
    cloud_d = product_d['cloud']
    cloudmask_tl3a = cloud_d['mask']
    productmask_ltl3a = [
        cloudmask_tl3a
    ]

    # plotting
    main(
        work_ltra, productmask_ltl3a,
        z_tra, r_trm, setz_a, setzind_ta,
        ts_ta,
    )
