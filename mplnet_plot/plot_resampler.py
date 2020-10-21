# imports
import numpy as np
from scipy.interpolate import interp1d


# main func
def main(
        work_tra, z_ra, r_rm, setz,
        resamplez_ra,
):
    '''
    resamples the chunk according to (zmin, zmax, zstep).
    all points outside of the resample range are set to np.nan

    Parameters
        work_tra (np.ndarray): data array with 2 axis (time, range)
        z_ra (np.ndarray): range array to take derivative w.r.t
        r_rm (np.ndarray): corresponding mask array
        setz (tuple): descriptors for z_ra, contains Delt, Nbin, pad, theta
        resamplez_ra (np.ndarray): the array to resample to
    Return
        dzwork_tra (np.ndarray): first derivative of work_tra
        retz_ra (np.ndarray): corresponding range array
        retr_rm (np.ndarray): corresponding mask array, all True
        setz (list): unchanged
    '''
    # applying mask
    ret_tra = work_tra[:, r_rm]
    retz_ra = z_ra[r_rm]

    # interpolating for resampling
    ret_tra = interp1d(
        retz_ra, ret_tra, axis=1,
        kind='linear', bounds_error=False, fill_value=np.nan
    )(resamplez_ra)

    # computing new boolean array from extrapolation
    reretz_ra = interp1d(
        retz_ra, retz_ra,
        kind='linear', bounds_error=False, fill_value=np.nan
    )(resamplez_ra)
    resampleboo_ra = ~np.isnan(reretz_ra)

    # changing setz
    setz[1] = resamplez_ra.shape[0]  # number of bins has changed

    return ret_tra, resamplez_ra, resampleboo_ra, setz


# testing
if __name__ == '__main__':
    main()
