import numpy as np
from sarvey import unwrapping


class Parms:
    def __init__(self):
        self.reference_type = 'arc'
        self.window_size_azimuth = 3
        self.window_size_range = 3
        self.demerr_bound_min = -50
        self.demerr_bound_max = 50
        self.velocity_bound_min = -5./100
        self.velocity_bound_max = 5./100
        self.demerr_num_samples = 100
        self.velocity_num_samples = 100
        self.remove_seasonal_before_temp_uw = False
        self.remove_seasonal_after_temp_uw = False


class TemporalUnwrapping:
    def __init__(self, data):
        self.parms = Parms()
        self.data = data
        # TODO: use baselines in ifg_network instead of making a copy
        self.pbase_ifg = None
        self.tbase_ifg = None
        self.az = None
        self.ra = None
        self.slant_range = None
        self.loc_inc = None
        self.design_matrix = None
        self.velocity = None
        self.dem_error = None
        self.ifg_phase = None
        self.model_phase = None
        self.velocity_phase = None
        self.dem_error_phase = None
        self.residual_phase = None
        self.residual_phase_dem = None
        self.residual_phase_velocity = None
        self.temporal_coherence = None
        self.velocity_range = None
        self.dem_error_range = None
        self.model_pbase_linspace = None
        self.model_tbase_lispace = None
        self.gamma_grid = None

    def readGeometry(self, ra: int, az: int):
        self.slant_range = self.data.readSlantRangeForAzRa(ra, az)
        loc_inc_deg = self.data.readIncidenceAngleForAzRa(ra, az)
        self.loc_inc = loc_inc_deg * np.pi / 180

    def temporalUnwrappingDesignMatrix(self, perp_base=None, temp_base=None):
        pbase_ifg = self.pbase_ifg if perp_base is None else perp_base
        tbase_ifg = self.tbase_ifg if temp_base is None else temp_base
        design_matrix = np.zeros((pbase_ifg.size, 2), dtype=np.float32)
        design_matrix[:, 0] = (- 4 * np.pi / self.data.wavelength * pbase_ifg
                               / (self.slant_range * np.sin(self.loc_inc)))
        design_matrix[:, 1] = - 4 * np.pi / self.data.wavelength * tbase_ifg
        return design_matrix

    def readCpxArc(self, ra: int = None, az: int = None, ra_ref: int = None, az_ref: int = None):
        self.readGeometry(ra, az)
        if self.data.network_type == "ifg_stack":
            read_method = self.data.readInterferogramPhaseForAzRa
        else:
            self.data.constructDynamicNetwork()
            read_method = self.data.calculateInterferogramPhaseForAzRa
        self.pbase_ifg = self.data.ifg_network.pbase_ifg
        self.tbase_ifg = self.data.ifg_network.tbase_ifg
        ifg_cpx = read_method(ra, az)
        if az_ref is not None and ra_ref is not None:
            ifg_cpx_ref = read_method(ra_ref, az_ref)
            ifg_cpx = ifg_cpx * np.conjugate(ifg_cpx_ref)
        return ifg_cpx

    def readCpxWindow(self, ra: int = None, az: int = None, wds_ra: int = None, wds_az: int = None):
        self.readGeometry(ra, az)
        if wds_ra is None:
            wds_ra = self.parms.window_size_range
        if wds_az is None:
            wds_az = self.parms.window_size_azimuth
        if self.data.network_type == "ifg_stack":
            read_method = self.data.readInterferogramPhaseForAzRa
        else:
            self.data.constructDynamicNetwork()
            read_method = self.data.calculateInterferogramPhaseForAzRa
        self.pbase_ifg = self.data.ifg_network.pbase_ifg
        self.tbase_ifg = self.data.ifg_network.tbase_ifg
        ifg_cpx = read_method(ra, az)
        ifg_cpx_window = read_method(ra=ra - wds_ra // 2,
                                     az=az - wds_az // 2,
                                     ra2=ra + wds_ra // 2 + 1,
                                     az2=az + wds_az // 2 + 1).reshape((wds_ra * wds_az, -1))
        ifg_cpx_window_neighbors = np.delete(ifg_cpx_window, (wds_ra * wds_az) // 2, axis=0)
        ifg_cpx_ref = np.mean(ifg_cpx_window_neighbors, axis=0)
        ifg_cpx = ifg_cpx * np.conjugate(ifg_cpx_ref)
        return ifg_cpx

    def createIfgNetworkPhase(self, ra: int, az: int, ra_ref: int = None, az_ref: int = None):
        if self.parms.reference_type == 'window':
            ifg_phase = np.angle(self.readCpxWindow(ra, az))
        elif self.parms.reference_type == 'arc':
            ifg_phase = np.angle(self.readCpxArc(ra, az, ra_ref, az_ref))
        return ifg_phase

    def temporal_uw(self, ra: int, az: int, ra_ref: int = None, az_ref: int = None):
        ifg_phase = self.createIfgNetworkPhase(ra, az, ra_ref, az_ref)
        ifg_phase = self.shiftPhase(ifg_phase)

        if self.parms.remove_seasonal_before_temp_uw:  # remove seasonal phase
            # TODO: add ifg_dates to the self.data.ifg_network
            dates = np.array([
                [(self.data.slc_dates[ifg_date[0]] - self.data.slc_dates[0]).days / 365.25,
                 (self.data.slc_dates[ifg_date[1]] - self.data.slc_dates[0]).days / 365.25]
                for ifg_date in self.data.ifg_network.ifg_list])
            seas_phase, ifg_phase = self.estimateAnnual(dates, ifg_phase)

        self.design_matrix = self.temporalUnwrappingDesignMatrix()
        self.dem_error_range = np.linspace(self.parms.demerr_bound_min, self.parms.demerr_bound_max, self.parms.demerr_num_samples)
        self.velocity_range = np.linspace(self.parms.velocity_bound_min, self.parms.velocity_bound_max, self.parms.velocity_num_samples)

        demerr, vel, gamma = unwrapping.oneDimSearchTemporalCoherence(
            demerr_range=self.dem_error_range,
            vel_range=self.velocity_range,
            obs_phase=ifg_phase,
            design_mat=self.design_matrix)

        # demerr_grid, vel_grid = np.meshgrid(demerr_range, vel_range)
        # demerr, vel, gamma = unwrapping.gridSearchTemporalCoherence(
        #                                                             demerr_grid=demerr_grid,
        #                                                             vel_grid=vel_grid,
        #                                                             obs_phase=ifg_phase,
        #                                                             design_mat=self.design_matrix)

        # from scipy import optimize
        # opt_res = optimize.differential_evolution(unwrapping.objFuncTemporalCoherence,
        #                                           bounds=((-1, 1), (-1, 1)),
        #                                           args=(self.design_matrix, ifg_phase, vel_range.max(), demerr_range.max()))
        # gamma = 1 - opt_res.fun
        # demerr = opt_res.x[0] * demerr_range.max()
        # vel = opt_res.x[1] * vel_range.max()

        model_phase, demerror_phase, vel_phase, model_pbase_linspace, model_tbase_lispace = (
            self.modelPhase(demerr, vel, self.pbase_ifg, self.tbase_ifg))
        res_phase, res_phase_dem, res_phase_vel = self.residualPhase(ifg_phase, self.design_matrix, demerr, vel)
        gamma_grid = self.searchSpaceGamma(self.dem_error_range, self.velocity_range, self.design_matrix, ifg_phase)

        if self.parms.remove_seasonal_after_temp_uw:  # remove seasonal phase
            # TODO: get slc_dates from ifg_network when network dynamically created to avoid inconsistencies
            dates = np.array([
                [(self.data.slc_dates[ifg_date[0]] - self.data.slc_dates[0]).days / 365.25,
                 (self.data.slc_dates[ifg_date[1]] - self.data.slc_dates[0]).days / 365.25]
                for ifg_date in self.data.ifg_network.ifg_list])
            seas_phase, res_phase = self.estimateAnnual(dates, res_phase)

        temporal_coherence = np.abs(np.mean(np.exp(1j * res_phase), axis=0))
        self.velocity = vel
        self.dem_error = demerr
        self.temporal_coherence = temporal_coherence
        self.ifg_phase = ifg_phase
        self.residual_phase = res_phase
        self.residual_phase_dem = res_phase_dem
        self.residual_phase_velocity = res_phase_vel
        self.model_phase = model_phase
        self.velocity_phase = vel_phase
        self.dem_error_phase = demerror_phase
        self.model_pbase_linspace = model_pbase_linspace
        self.model_tbase_lispace = model_tbase_lispace
        self.gamma_grid = gamma_grid
        return

    def searchSpaceGamma(self, demerr_range, vel_range, design_matrix, ifg_phase):
        grid_demerr_range, grid_vel_range = np.meshgrid(demerr_range, vel_range)
        gamma_grid = np.array([1 - unwrapping.objFuncTemporalCoherence(
            np.array([grid_demerr_range.flatten()[i], grid_vel_range.flatten()[i]]),
            design_matrix, ifg_phase, 1, 1) for i in range(grid_demerr_range.flatten().shape[0])])
        gamma_grid = gamma_grid.reshape(grid_demerr_range.shape)
        return gamma_grid

    def residualPhase(self, ifg_phase, design_matrix, demerr, vel):
        res_phase_dem = np.angle(np.exp(1j * ifg_phase) * np.conjugate(np.exp(1j * design_matrix[:, 0] * demerr)))
        res_phase_vel = np.angle(np.exp(1j * ifg_phase) * np.conjugate(np.exp(1j * design_matrix[:, 1] * vel)))
        res_phase = np.angle(np.exp(1j * res_phase_dem) * np.conjugate(np.exp(1j * design_matrix[:, 1] * vel)))

        res_phase_dem = self.shiftPhase(res_phase_dem)
        res_phase_vel = self.shiftPhase(res_phase_vel)
        res_phase = self.shiftPhase(res_phase)

        return res_phase, res_phase_dem, res_phase_vel

    def shiftPhase(self, phase):
        return np.angle(np.exp(1j * phase) * np.mean(np.conjugate(np.exp(1j * phase))))

    def modelPhase(self, demerr, vel, pbase, tbase):
        model_pbase_linspace = np.linspace(pbase.min(), pbase.max(), 1000)
        model_tbase_lispace = np.linspace(tbase.min(), tbase.max(), 1000)
        design_matrix_linspace = self.temporalUnwrappingDesignMatrix(perp_base=model_pbase_linspace,
                                                                     temp_base=model_tbase_lispace)
        demerror_phase = np.angle(np.exp(1j * design_matrix_linspace[:, 0] * demerr))
        vel_phase = np.angle(np.exp(1j * design_matrix_linspace[:, 1] * vel))
        model_phase = np.angle(np.exp(1j * demerror_phase) * np.exp(1j * vel_phase))
        return model_phase, demerror_phase, vel_phase, model_pbase_linspace, model_tbase_lispace

    def estimateAnnual(self, ifg_days, this_phase, opt_method='Gradient'):
        """
        Estimated annual signal from the interferometric phase network of an arc.

        :param ifg_days: numpy.ndarray,
            An array containing the reference (1st column) and secondary (2nd column) dates of interferograms.
        :param this_phase: numpy.ndarray,
            An array containing the interferogram phase for the arc.
        :param opt_method: str,
            The optimization method to use. Currently, only 'Gradient' is supported.

        :return: numpy.ndarray,
            The estimated annual signal.

        The function calculates an annual signal from the interferometric phase of an arc.
        The values in ifg_days are represented in years relative to the first image day (where the first image day is 0).
        The first and second columns correspond to the reference and secondary days, respectively.
        """
        # create design_matrix for annual signal
        design_mat = np.zeros((ifg_days.shape[0], 2))
        design_mat[:, 0] = np.sin(ifg_days[:, 0] * 2 * np.pi) - np.sin(ifg_days[:, 1] * 2 * np.pi)
        design_mat[:, 1] = np.cos(ifg_days[:, 0] * 2 * np.pi) - np.cos(ifg_days[:, 1] * 2 * np.pi)

        # TODO: get the search space as a function argument
        sin_amp_range = np.linspace(start=-4, stop=4, num=100)
        cos_amp_range = np.linspace(start=-4, stop=4, num=100)
        # TODO: support DE and 1-D optimizations
        if opt_method == 'Gradient':
            x0 = np.array([0, 0]).T
            sin_amp, cos_amp, gamma = unwrapping.gradientSearchTemporalCoherence(scale_vel=sin_amp_range.max(),
                                                                                 scale_demerr=cos_amp_range.max(),
                                                                                 obs_phase=this_phase,
                                                                                 design_mat=design_mat,
                                                                                 x0=x0)
        phase_annual = np.angle(np.exp(1j * design_mat[:, 0] * sin_amp) * np.exp(1j * design_mat[:, 1] * cos_amp))
        phase_res = np.angle(np.exp(1j * this_phase) * np.conjugate(np.exp(1j * phase_annual)))
        return phase_annual, phase_res
