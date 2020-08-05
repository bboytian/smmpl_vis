# imports
import multiprocessing as mp

import pandas as pd

from ..globalimports import *
from ...solaris_opcodes.product_calc.nrb_calc import nrb_calc
from ...solaris_opcodes.file_readwrite.mpl_reader import smmpl_reader

# params
_dataf = nrb_calc
_readduration = pd.Timedelta(1, 'h')
_initreaddatatimes = 10

# class
class productvis():

    def __init__(
            self,
            datakey, timeobj,
            lidarname, mplreader
    ):
        self.datakey = datakey
        self.to = timeobj
        self.lidarname = lidarname

        self.starttime = self.to.get_ts()
        self.endtime = self.starttime + _readduration
        self.data_queue = mp.Queue()

        # initial data read
        p = mp.Process(target=self.read_data, args=(_initreaddatatimes,))
        p.start()


    def init_vis(self, ax):
        pass

    def read_data(self, n):
        print(f'this is the {n} round')
        if n == 0:
            pass
        else:
            data_d = _dataf(self.lidarname, smmpl_reader,
                            starttime=self.starttime, endtime=self.endtime)
            if data_d:
                self.data_queue.put(data_d)
            # iterating the next time range to consider
            self.starttime += _readduration
            self.endtime += _readduration
            self.read_data(n-1)


    def update_ts(self):
        # check whether data is empty
        pass

    def update_toseg(self):
        pass





if __name__ == '__main__':
    from ...smmpl_opcodes.scanpat_calc.timeobj import timeobj
    to = timeobj(
        pd.Timestamp('202008040000'),
        pd.Timestamp('202008050300'),
        8,
        pd.Timedelta(1, 'm'),
        pd.Timedelta(30, 'm'),
        None
    )
    pv = productvis(
        None, to, 'smmpl_E2', smmpl_reader
    )

    while True:
        print(pv.data_queue.qsize())
