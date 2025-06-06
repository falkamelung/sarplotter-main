import os
import numpy as np
from sarvey import objects as SarveyObjects
from sarvey import utils as ut
import logging
from scipy.spatial import KDTree
import h5py as h5
import numpy as np
from datetime import datetime
import glob
from .dynamic_ifg_network import DynamicIfgNetwork

logger = logging.getLogger(__name__)

# filenames as constants
# TODO: read file names from a config file
P1_FILE_DEFAULT = "p1_ifg_wr.h5"
MEAN_AMPLITUDE_FILE_DEFAULT = "background_map.h5"
TEMPORAL_COHERENCE_FILE_DEFAULT = "temporal_coherence.h5"
TEMPORAL_COHERENCE_DATASET_NAME_DEFAULT = "temp_coh"
P2_FILES_DEFAULT = "p2*_ts.h5"
IFG_NETWORK_FILE_DEFAULT = "ifg_network.h5"
SLC_STACK_FILE = "slcStack.h5"
IFG_STACK_FILE = "ifg_stack.h5"
GEOMETRY_RADAR_FILE = "geometryRadar.h5"


# class Metadata:
#     def __init__(self):
#         self.wavelenght = None
#         self.slc_dates = None
#         self.pbase_ifg = None
#         self.tbase_ifg = None


class Data:
    """
    This Class creates a structure for SAR/InSAR data and provides methods to read them.
    """

    def __init__(self, *, data_path: str, input_path: str = None):
        """
        Initialize the Data class.

        :param data_path: The path to the sarvey processing directory that contains amplitude, temporal coherence, etc.
        :param input_path: Optional path to the inputs directory. If not provided, it is set to 'data_path/inputs'.

        """
        self.data_path = data_path
        input_path = os.path.join(data_path, 'inputs') if input_path is None else input_path
        self.input_path = input_path
        # backgrounds
        self.mean_amplitude_file = os.path.join(data_path, MEAN_AMPLITUDE_FILE_DEFAULT)
        self.mean_amplitude = None
        self.mean_amplitude_file_exist = self._fileExists(self.mean_amplitude_file)
        self.temporal_coherence_file = os.path.join(data_path, TEMPORAL_COHERENCE_FILE_DEFAULT)
        self.temporal_coherence_dataset_name = TEMPORAL_COHERENCE_DATASET_NAME_DEFAULT
        self.temporal_coherence = None
        self.temporal_coherence_exist = self._fileExists(self.temporal_coherence_file)
        self.no_background = None
        # data point p1
        self.p1_file = os.path.join(data_path, P1_FILE_DEFAULT)
        self.p1_file_exist = self._fileExists(self.p1_file)
        self.p1 = None
        self.p1_point_tree = None
        # data point p2
        self.p2_files = os.path.join(data_path, P2_FILES_DEFAULT)
        self.p2_file, self.p2_file_exist = self._checkExistingP2Files()
        # self.p2_file_exist = self._fileExists(self.p2_file)
        self.p2 = None
        self.p2_point_tree = None
        self.p2_velocity = None
        self.p2_demerr = None
        self.p2_coherence = None
        # ifg network
        self.ifg_network_file = os.path.join(data_path, IFG_NETWORK_FILE_DEFAULT)
        self.ifg_network_file_exist = self._fileExists(self.ifg_network_file)
        self.ifg_network = None
        # IFG stack
        self.ifg_stack_file = os.path.join(data_path, IFG_STACK_FILE)
        self.ifg_stack_file_exist = self._fileExists(self.ifg_stack_file)
        self.slc_dates_ts = None
        # slc stack
        self.slc_stack_file = os.path.join(input_path, SLC_STACK_FILE)
        self.slc_stack_file_exist = self._fileExists(self.slc_stack_file)
        self.slc_dates = None
        # radar geometry
        self.geometry_radar_file = os.path.join(input_path, GEOMETRY_RADAR_FILE)
        self.geometry_radar_file_exist = self._fileExists(self.geometry_radar_file)
        # attributes
        self.wavelength = None
        self.orbit_direction = None
        self.slc_dimension = None
        self.point_id_image = None

        self.slc_selected_dates = None
        self._readMetadata()
        # dynamic ifg network
        self.network_type = 'ifg_stack'
        self.ifg_dynamic_network = DynamicIfgNetwork(data_path=self.data_path, slc_stack_file=self.slc_stack_file)


    def _fileExists(self, file, data_path=None):
        """
        Check if a file exists in the specified data path.

        :param file: The name of the file to check for existence.
        :param data_path: Optional custom data path. If not provided, the instance's data_path is used.

        :return: True if the file exists, False otherwise.

        """
        if file is None:
            return None
        if data_path is None:
            data_path = self.data_path
        file_path = os.path.join(data_path, file)
        return True if os.path.exists(file_path) else False

    def readMeanAmplitude(self):
        """
        Read SAR mean amplitude from the sarvey processing directory or slcStack and assign it to self.mean_amplitude.

        Returns:
            numpy.ndarray amplitude if the file exists
            None if the amplitude file does not exist
        """
        # TODO: Add error handling for cases where the file exists but cannot be opened or read.
        # TODO: generalize amplitude filename
        if self.mean_amplitude is None:
            file_path = os.path.join(self.data_path, self.mean_amplitude_file)
            if self.mean_amplitude_file_exist:
                obj = SarveyObjects.AmplitudeImage(file_path=file_path)
                obj.open()
                mean_amplitude = obj.background_map
                mean_amplitude[~np.isfinite(mean_amplitude)] = np.nan
                self.mean_amplitude = mean_amplitude
            elif self.slc_stack_file_exist:
                self.mean_amplitude, _ = self.readAmplitudeFromSlc()
        return self.mean_amplitude

    def readTemporalCoherence(self):
        """
        Read temporal coherence from the sarvey processing directory and assign it to self.temporal_coherence.

        Returns:
            numpy.ndarray temporal coherence if the file exists
            None if the temporal coherence file does not exist
        """
        if self.temporal_coherence is None:
            file_path = os.path.join(self.data_path, self.temporal_coherence_file)
            if os.path.exists(file_path):
                temp_coh_obj = SarveyObjects.BaseStack(file=file_path, logger=logger)
                temp_coh = temp_coh_obj.read(dataset_name=self.temporal_coherence_dataset_name)
                self.temporal_coherence = temp_coh
        return self.temporal_coherence

    def readAmplitudeFromSlc(self, ind=None):
        """
        Read SAR amplitude from the slcStack.h5 file and calculate the mean amplitude.

        Returns:
            numpy.ndarray amplitude if the file exists
            None if the slcStack file does not exist
        """
        # TODO: Add error handling for cases where the file exists but cannot be opened or read.
        # TODO: generalize slcStack filename
        if self.mean_amplitude is None or ind is not None:
            file_path = self.slc_stack_file
            if self.slc_stack_file_exist:
                obj = SarveyObjects.slcStack(file_path)
                obj.open()
                date_list = obj.dateList
                if ind is None:  # calculate mean amplitude of a subset
                    interval = int(np.ceil(np.prod(obj.get_size()) / 1e8))  # TODO: read this from config
                    min_interval = int(np.ceil(obj.get_size()[0]/5))        # TODO: read this from config
                    if interval > min_interval:
                        interval = min_interval
                    amplitude = np.mean(np.abs(obj.read(date_list[0::interval])), axis=0)
                else:  # read the ind subset
                    ind = np.array(ind)
                    ind = ind[(ind < len(date_list)) & (ind >= 0)]
                    dates_to_read = [date_list[i] for i in ind]
                    amplitude = np.abs(obj.read(dates_to_read))
                    if ind.size > 1:
                        amplitude = np.mean(amplitude, axis=0)
                amplitude = 10*np.log10(amplitude)
                amplitude[~np.isfinite(amplitude)] = np.nan
        return amplitude, ind


    def readP1(self):
        """
        Read and initialize first order (P1) data.

        If P1 data is not already loaded:
        - Check if the P1 file exists.
        - If the file does not exist, set P1 to -1.
        - If the file exists, initialize P1 using the SarveyObjects.Points class.

        If the P1 point tree is not initialized, create a KDTree for P1 coordinates.

        """
        if self.p1 is None:
            file_path = os.path.join(self.data_path, self.p1_file)
            if not os.path.exists(file_path):
                self.p1 = -1
            else:
                self.p1 = SarveyObjects.Points(file_path=file_path, logger=logger)
                self.p1.open(input_path=self.input_path)
        if self.p1_point_tree is None:
            self.p1_point_tree = KDTree(self.p1.coord_xy[:, [1, 0]])

    def readP2(self):
        """
        Read and initialize second order (P2) data.

        If P2 data is not already loaded:
        - Check if the P2 file exists.
        - If the file does not exist, set P2 to -1.
        - If the file exists, initialize P2 using the SarveyObjects.Points class.

        If the P2 point tree is not initialized, create a KDTree for P2 coordinates.

        """
        if not self.p2_file_exist:
            return
        if self.p2 is None:
            file_path = os.path.join(self.data_path, self.p2_file)
            if not os.path.exists(file_path):
                self.p2 = -1
            else:
                # TODO: load only parts of p2 that are needed
                self.p2 = SarveyObjects.Points(file_path=file_path, logger=logger)
                self.p2.open(input_path=self.input_path)

            self.p2_point_tree = KDTree(self.p2.coord_xy[:, [1, 0]])
            self.readVelocity()

    def _checkExistingP2Files(self):
        p2_files_pattern = os.path.join(self.data_path, self.p2_files)
        p2_files_path = glob.glob(p2_files_pattern)
        self.p2_files = [os.path.basename(file_path) for file_path in p2_files_path]
        if len(self.p2_files)>0:
            return self.p2_files[0], True
        else:
            return None, False

    def updateP2File(self, index):
        """
        return: True if file selection changed, False otherwise
        """
        selected_file = self.p2_files[index]
        if self.p2_file == selected_file:
            return False
        else:
            # TODO: keep the p2 information for previously seleted files if they are not too large
            self.p2_file = selected_file
            self.p2 = None
            self.p2_point_tree = None
            return True

    def readIfgNetwork(self):
        """
        Read the Interferogram (IFG) network.

        If the IFG network is not already loaded, this function attempts to read it from a file specified
        by `self.ifg_network_file` within the `self.data_path`. If the file does not exist, it sets `self.ifg_network`
        to -1. Otherwise, it initializes a new `SarveyObjects.IfgNetwork` object and opens the file.

        :return: None
        """
        if self.ifg_network is None:
            file_path = os.path.join(self.data_path, self.ifg_network_file)
            if not os.path.exists(file_path):
                self.ifg_network = -1
            else:
                self.ifg_network = SarveyObjects.IfgNetwork()
                self.ifg_network.open(path=file_path)

    def readDates(self):
        """
        Read and parse dates associated with the slc images.

        :return: A list of datetime objects
        """
        if self.ifg_network is None:  # load ifg_notwork if not already loaded
            self.readIfgNetwork()
        if self.ifg_network is not None:
            self.slc_dates = [datetime.strptime(date, "%Y-%m-%d") for date in self.ifg_network.dates]
        else:  # TODO: load dates if self.ifg_network is not available
            pass
        return self.slc_dates

    def yyyymmddToDates(self, dates, date_format: str = "%Y%m%d", out_format=None):
        date_ordinal = [datetime.strptime(date, date_format) for date in dates]
        if out_format is None:
            out = [datetime.strptime(date, date_format) for date in dates]
        else:
            out = [date.strftime(out_format) for date in date_ordinal]
        return out

    def _readMetadata(self):
        """
        Reads and sets the metadata from either an slc_stack file or an ifg_stack file.
        If slc_stack file is not available, it will read the metadata from ifg_stack
        Raises an exception if neither an SLC stack file nor an IFG stack file exist.
        """
        if self.slc_stack_file_exist: # TODO: read other alternatives if slc is not available
            h_file = h5.File(os.path.join(self.data_path, self.slc_stack_file))
        if self.ifg_network_file_exist:
            h_file_ifg = h5.File(os.path.join(self.data_path, self.ifg_network_file))
            slc_dates_ts = h_file_ifg['dates'][:]
            slc_dates_ts = [date.decode('utf-8') for date in slc_dates_ts]
            self.slc_dates_ts = self.yyyymmddToDates(slc_dates_ts, date_format="%Y-%m-%d")
        if not self.slc_stack_file_exist and not self.ifg_stack_file_exist:
            raise ("input files do not exist!")
        # TODO: fix reading parameters from ifg_stack when slcstack is not available
        self.wavelength = float(h_file.attrs['WAVELENGTH'])
        self.orbit_direction = h_file.attrs["ORBIT_DIRECTION"].lower()
        slc_dates = h_file['date'][:]
        slc_dates = [date.decode('utf-8') for date in slc_dates]
        self.slc_dates = self.yyyymmddToDates(slc_dates)
        self.slc_selected_dates = self.slc_dates.copy()
        self.slc_dimension = h_file['slc'].shape
        self.slc_pbase = np.array(h_file['bperp'])
        self.slc_pbase = np.array(h_file['bperp'])
        self.n_lines = self.slc_dimension[1]
        self.n_pixels = self.slc_dimension[2]
        self.createPointIds()
        # TODO: alternatively read metadata from ifg_network.h5
        h_file.close()

    def createPointIds(self):
        self.point_id_image = np.arange(0, self.n_lines * self.n_pixels).reshape((self.n_lines, self.n_pixels))

    def readTsForIdx(self, idx: int = None, idx_ref: int = None, remove_topo_error=True):
        """
        Read phase data for a specific index and calculate the difference with a reference index.

        :param remove_topo_error:
        :param idx: Index for the phase data. If provided, read phase data for this index.
        :param idx_ref: Reference index for the phase data. If provided, read phase data for this reference index.

        :return: The difference between phase data at the specified index and the reference index.
        """
        h_file = h5.File(os.path.join(self.data_path, self.p2_file))
        idx_phase_data = 0 if idx is None else h_file['phase'][idx, :]
        idx_ref_phase_data = 0 if idx_ref is None else h_file['phase'][idx_ref, :]

        # calculate topo phase
        phase_topo = 0
        if idx is not None:
            phase_topo += (self.p2.ifg_net_obj.pbase / (self.p2.slant_range[idx] *
                                                        np.sin(self.p2.loc_inc[idx])) * self.p2_demerr[idx])
        if idx_ref is not None:
            phase_topo -= (self.p2.ifg_net_obj.pbase / (self.p2.slant_range[idx_ref] *
                                                        np.sin(self.p2.loc_inc[idx_ref])) * self.p2_demerr[idx_ref])
        phase_topo *= 4 * np.pi / self.wavelength
        if not remove_topo_error:
            phase_topo = 0
        phase_data = idx_phase_data - idx_ref_phase_data - phase_topo
        # TODO: phase to cm conversion
        return phase_data

    def readInterferogramPhaseForAzRa(self, ra: int, az: int, ra2: int = None, az2: int = None):
        """
        Retrieve interferometric phase from the ifg_stack file for the specified azimuth (az) and range (ra) indices.

        :param ra: Range coordinate
        :param az: Azimuth coordinate

        :return: Interferometric phase
        """
        h_file = h5.File(os.path.join(self.data_path, self.ifg_stack_file))
        if az2 is None and ra2 is None:
            ifg_cpx = h_file['ifgs'][az, ra, :]
        else:
            ifg_cpx = h_file['ifgs'][az:az2, ra:ra2, :]
        return ifg_cpx

    def calculateInterferogramPhaseForAzRa(self, ra: int, az: int, ra2: int = None, az2: int = None):
        """
        Calculate interferometric phase from the slc_stack file for the specified azimuth (az) and range (ra) indices.

        :param ra: Range coordinate
        :param az: Azimuth coordinate

        :return: Interferometric phase
        """
        h_file = h5.File(os.path.join(self.data_path, self.slc_stack_file))
        slc_dates = self.yyyymmddToDates([date.decode("utf-8") for date in h_file['date'][:]], out_format="%Y-%m-%d")

        ifg_list_map_to_slc_stack = [(
            slc_dates.index(self.ifg_network.dates[baseline[0]]),
            slc_dates.index(self.ifg_network.dates[baseline[1]]))
            for baseline in self.ifg_network.ifg_list
        ]
        ifg_list = ifg_list_map_to_slc_stack

        if az2 is None and ra2 is None:
            slc_phase = h_file['slc'][:, az, ra]
            ifg_cpx = np.array([slc_phase[this_ifg[0]] * np.conjugate(slc_phase[this_ifg[1]])
                                for this_ifg in ifg_list])
        else:
            slc_phase = h_file['slc'][:, az:az2, ra:ra2]
            ifg_cpx = np.array([slc_phase[this_ifg[0], :, :] * np.conjugate(slc_phase[this_ifg[1], :, :])
                                for this_ifg in ifg_list]).transpose((1, 2, 0))
        h_file.close()
        return ifg_cpx

    def constructDynamicNetwork(self):
        index = [i for i in range(len(self.slc_dates)) if self.slc_dates[i] in self.slc_selected_dates]
        dates = np.array(self.slc_dates)[index]
        self.ifg_dynamic_network.dates = [date.strftime("%Y-%m-%d") for date in dates]
        self.ifg_dynamic_network.slc_pbase = self.slc_pbase[index]
        self.ifg_dynamic_network.slc_tbase = np.array([(date - self.slc_dates[0]).days / 365.25 for date in dates])
        self.ifg_dynamic_network.construct()
        self.ifg_network = self.ifg_dynamic_network.ifg_network

    def readSlantRangeForAzRa(self, ra: int, az: int):
        """
        Retrieve the slant range from the geometry radar file for the specified azimuth (az) and range (ra) indices.

        :param ra: Range coordinate
        :param az: Azimuth coordinate

        :return: slant range
        """
        slant_range = None
        if self.geometry_radar_file_exist:
            h_file = h5.File(os.path.join(self.data_path, self.geometry_radar_file))
            slant_range = h_file['slantRangeDistance'][az, ra]
            h_file.close()
        return slant_range

    def readIncidenceAngleForAzRa(self, ra: int, az: int):
        """
        Retrieve the incidence angle from the geometry radar file for the specified azimuth (az) and range (ra) indices.

        :param ra: Range coordinate
        :param az: Azimuth coordinate

        :return: Incidence angle
        """
        incidence_angle = None
        if self.geometry_radar_file_exist:
            h_file = h5.File(os.path.join(self.data_path, self.geometry_radar_file))
            incidence_angle = h_file['incidenceAngle'][az, ra]
            h_file.close()
        return incidence_angle

    def readVelocity(self):
        self.p2_velocity, self.p2_demerr, _, self.p2_coherence, _, _ = ut.estimateParameters(obj=self.p2, ifg_space=False)

    def phaseToDistance(self, phase, unit="cm"):
        scale_dict = {"mm": 1000, "cm": 100, "dm": 10, "m": 1}
        wavelength = self.wavelength * scale_dict[unit]
        return phase * wavelength / 4 / np.pi

    def convertMetrictUnit(self, data, unit0 = "m", unit1="cm"):
        if len(unit0.split("/")):
            unit0 = unit0.split("/")[0]
            unit1 = unit1.split("/")[0]
        unit_dict = {"mm": 1000, "cm": 100, "dm": 10, "m": 1}
        return data/unit_dict[unit0]*unit_dict[unit1]
