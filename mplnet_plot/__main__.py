# imports
import matplotlib.pyplot as plt
import matplotlib.colors as pcolors
import numpy as np

from .plot_resampler import main as plot_resampler
from ..solaris_opcodes.product_calc.nrb_calc import chunk_operate
from ..global_imports.smmpl_vis import *

# params


# main func
def main(
        work_ltra,
        z_tra, r_trm, setz_a, setzind_ta,
        ts_ta,
        product_d={}
):
    '''
    Performs two types of plots. Profile plots for each work_tra in work_ltra. and a
    pure product mask plot.

    This function will resample the work arrays such that all the altitudes fit on a
    single grid, making z_tra redundent; i.e. only the first time index is needed for
    the resampled z_tra

    Parameters
        work_ltra (list): list of work_tra (np.ndarray) with time and range axis
        z_tra (np.ndarray): corresponding altitude array
        r_trm (np.ndarray): corresponding mask
        setz_a (list): list of descriptors for the set of altitude arrays in z_tra
        setzind_ta (np.ndarray): indexes for setz_a for the time axis for all tra
                                 arrays
        ts_ta (np.ndarray): timestamp array
        product_d (dict): contains products for plotting
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
                plot_resampler,
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
            norm=pcolors.PowerNorm(0.5)
        )


    # plotting product masks
    if product_d:

        # resampling product location

        # axs[-1].


    # showing plot
    plt.show()


# testing
if __name__ == '__main__':

    # imports
    from ..solaris_opcodes.file_readwrite import smmpl_reader
    from ..solaris_opcodes.product_calc.nrb_calc import main as nrb_calc

    # reading data
    lidarname = 'smmpl_E2'
    mplreader = smmpl_reader
    starttime = LOCTIMEFN('202009220000', UTCINFO)
    endtime = LOCTIMEFN('202009230000', UTCINFO)
    ret_d = nrb_calc(
        lidarname, mplreader,
        starttime=starttime, endtime=endtime,
        genboo=True,
        writeboo=False
    )
    ts_ta = ret_d['Timestamp']
    z_tra = ret_d['z_tra']
    r_tra = ret_d['r_tra']
    r_trm = ret_d['r_trm']
    NRB1_tra = ret_d['NRB1_tra']
    NRB2_tra = ret_d['NRB2_tra']
    NRB_tra = ret_d['NRB_tra']
    SNR1_tra = ret_d['SNR1_tra']
    SNR2_tra = ret_d['SNR2_tra']
    SNR_tra = ret_d['SNR_tra']
    setz_a = ret_d['DeltNbinpadtheta_a']
    setzind_ta = ret_d['DeltNbinpadthetaind_ta']



    main(
        [
            NRB_tra,
            SNR_tra,
        ],
        z_tra, r_trm, setz_a, setzind_ta,
        ts_ta
    )
