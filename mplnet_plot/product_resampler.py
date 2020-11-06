# imports
import numpy as np


# supp func
def _prodresampler_func(z_ra, height):
    '''
    Returns the closest height to z_tra, the closest height will always be <= height
    '''
    if np.isnan(height):
        return height
    else:
        heightind = np.argmax(z_ra > height)
        return z_ra[heightind]
_prodresampler_vfunc = np.vectorize(_prodresampler_func, excluded=['z_ra'])


# main func
def main(
        productmask_tl2a, resamplez_tra,
):
    '''
    resamples the product mask on to the new resampled work array

    Parameters
        productmask_tl2a (np.ndarray): (time, max number of layers, 2(cldbot, cldtop))
        resamplez_tra (np.ndarray): resampled altitude array with time and range axis
    Return
        resampleprodmask_tl2a (np.ndarray): resampled product heights for
                                            productmask_tl2a
        resampleprodmask_tra (np.ndarray): boolean array indicating the mask of the
                                           product
    '''
    # resampling heights
    resampleprodmask_tl2a = np.array([
        _prodresampler_vfunc(
            z_ra=z_ra,
            height=productmask_tl2a[i]
        )
        for i, z_ra in enumerate(resamplez_tra)
    ])

    # generating mask

    ## retreiving cloud top and bottoms
    maxheight = resamplez_tra.max()
    productmaskbot_tla = productmask_tl2a[..., 0]
    productmaskbot_tla = np.nan_to_num(productmaskbot_tla, nan=maxheight)
    productmasktop_tla = productmask_tl2a[..., 1]
    productmasktop_tla = np.nan_to_num(productmasktop_tla, nan=maxheight)

    ## creating mask layer by layer
    resampleprodmask_trm = np.zeros_like(resamplez_tra)
    for i in range(productmaskbot_tla.shape[1]):
        productmaskbot_ta = productmaskbot_tla[:, i]
        productmasktop_ta = productmasktop_tla[:, i]
        resampleprodmask_trm += (productmaskbot_ta[:, None] <= resamplez_tra)\
            * (resamplez_tra <= productmasktop_ta[:, None])

    resampleprodmask_trm = resampleprodmask_trm.astype(np.bool)

    return resampleprodmask_tl2a, resampleprodmask_trm


# testing
if __name__ == '__main__':
    main()
