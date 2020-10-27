# imports
import numpy as np


# main func
def main(
        productmask_ta, resamplez_tra,
):
    '''
    resamples the product mask on to the new resampled work array

    Parameters
        productmask_ta (np.ndarray): along the time axis is an array of lists
                                     indicating the start and end of a product layer
        resamplez_tra (np.ndarray): resampled altitude array with time and range axis
    Return
        resampleprodmask_ta (np.ndarray): resampled productmask_ta
        resampleprodmask_tra (np.ndarray): boolean array indicating the mask of the
                                           product
    '''



    return resampleprodmask_ta, resampleprodmask_tra


# testing
if __name__ == '__main__':
    main()
