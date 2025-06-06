import os
import numpy as np
import logging
import h5py as h5
from datetime import datetime
from sarvey import ifg_network
from .config.load_config import loadConfig

config = loadConfig(config_file_name='config.json')

logger = logging.getLogger(__name__)


class DynamicIfgNetwork:
    def __init__(self, data_path=None, slc_stack_file="inputs/slcStack.h5"):
        self.data_path = data_path
        self.slc_stack_file = slc_stack_file
        self.slc_pbase = None
        self.slc_tbase = None
        self.dates = None
        self.selected_dates = None
        # self.loadData()
        self.ifg_network = None
        self.type = "ifg_stack"
        self.max_pbase = np.inf
        self.max_tbase = 60
        self.ref_index = 0
        self.num_link = 1
        self.max_num_ifgs = np.inf
        self.min_num_ifgs = 0

    # def loadData(self):
    #     h_file = h5.File(os.path.join(self.data_path, self.slc_stack_file))
    #     self.slc_pbase = np.array(h_file['bperp'])
    #     dates_datetime = [datetime.strptime(this_date.decode('utf-8'), '%Y%m%d') for this_date in
    #                       np.array(h_file['date'])]
    #     self.dates = [date.strftime("%Y-%m-%d") for date in dates_datetime]
    #     self.slc_tbase = np.array([(this_date - dates_datetime[0]).days / 365.25 for this_date in dates_datetime])
    #     h_file.close()

    def construct(self):

        # if self.selected_dates is not None:
        #     selected_dates = [date.strftime("%Y-%m-%d") for date in self.selected_dates]
        #     dates = [date for date in self.dates if date in selected_dates]
        #     index = [i for i in range(len(self.dates)) if self.dates[i] in selected_dates]
        #     slc_pbase = self.slc_pbase[index]
        #     slc_tbase = self.slc_tbase[index] * 365.25
        #
        #     self.dates = dates

        dates = self.dates
        slc_pbase = self.slc_pbase
        slc_tbase = self.slc_tbase * 365.25

        if self.type == "star":
            ref_idx = self.ref_index if self.ref_index < len(self.dates) else 0
            self.ifg_network = ifg_network.StarNetwork()
            self.ifg_network.configure(pbase=slc_pbase,
                                       tbase=slc_tbase,
                                       ref_idx=ref_idx,
                                       dates=dates)
        elif self.type == "sbas":
            self.ifg_network = ifg_network.SmallBaselineNetwork()
            self.ifg_network.configure(pbase=slc_pbase,
                                       tbase=slc_tbase,
                                       dates=dates,
                                       num_link=self.num_link,
                                       max_tbase=self.max_tbase)
        elif self.type == "improved":
            self.ifg_network = ifg_network.ImprovedNetwork2()
            self.ifg_network.configure(pbase=slc_pbase,
                                       tbase=slc_tbase,
                                       dates=dates,
                                       max_tbase=self.max_tbase,
                                       max_pbase=self.max_pbase,
                                       max_num_ifgs=self.max_num_ifgs,
                                       min_num_ifgs=self.min_num_ifgs)
