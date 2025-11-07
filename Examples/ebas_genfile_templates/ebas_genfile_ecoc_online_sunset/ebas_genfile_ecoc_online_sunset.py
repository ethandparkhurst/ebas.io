#!/usr/bin/env python
"""
This script converts files from an online Sunset Laboratories EC/OC instrument
to EBAS Nasa Ames (data level 2).
"""

import pandas
import logging
import datetime
import re
from ebas.commandline import EbasCommandline
from ebas.io.ebasmetadata import DatasetCharacteristicList
from ebas.io.file.nasa_ames import EbasNasaAmes
from ebas.domain.basic_domain_logic.time_period import estimate_period_code, \
     estimate_resolution_code, estimate_sample_duration_code
from nilutility.datatypes import DataObject
from nilutility.statistics import median

from ebas_genfile_ecoc_online_sunset__config import \
    TIMEZONE_OFFSET, \
    STD_PRESURE, STD_TEMPERATURE, \
    LASER_TEMP_CORRECTION_THRESHOLD, \
    DENUDER_USED, DENUDER_EFFICIENCY, DENUDER_EFFICIENCY_UNC, \
    DETECTION_LIMIT_EC, DETECTION_LIMIT_OC, DETECTION_LIMIT_TC, \
    UNCERTAINTY_DESC, GLOBAL_METADATA

__version__ = '1.0'

HEADERLINES = 3

class ReadError(Exception):
    """
    Exception class used by GetData in case of errors.
    """
    pass

class GetData(object):
    """
    Data source class for Sunset laboratoies' output files
    """
    # expected header elements for the standard conditions file (_Res)
    HEADERS_STD = [
        u'Sample ID',
        u'Thermal/Optical OC (ugC/STPm^3)',
        u'Thermal/Optical EC (ugC/STPm^3)',
        u'OC=TC-BC (ugC/STPm^3)',
        u'BC (ugC/STPm^3)',
        u'TC (ugC/STPm^3)',
        u'Start Date/Time',
        u'Mid-time of Collection',
        u'Sample Volume - STP m^3',
        u'OC(ug)',
        u'OC unc',
        u'EC(ug)',
        u'EC unc',
        u'CC(ug/m^3)',
        u'CC unc',
        u'TC(ug)',
        u'TC unc',
        u'EC/TC ratio',
        u'CalConst',
        u'Punch Area',
        u'calibration area',
        u'transit time',
        u'Split time(sec)',
        u'Manual split?(sec)',
        u'Init.Abs.',
        u'Abs.Coef.',
        u'Atm.Pres.mmHg',
        u'Atm.Temp.degC',
        u'OCPk1-ug C',
        u'OCPk2-ug C',
        u'OCPk3-ug C',
        u'OCPk4-ug C',
        u'Pyrolized C ug',
        u'True EC ug C',
        u'BC ug C',
        u'BC ABS',
        u'OptABS Coef',
        u'CO2_ndirC3',
        u'CO2_ndirC2',
        u'CO2_ndirC1',
        u'CO2_ndirC0',
        u'NDIR_Type',
        u'Laser-Temp Correction',
        u'SBasic Ver',
        u'Inst VBasic Ver']

    # expected header elements for the ambient conditions file (_LCRes)
    HEADERS_AMB = [
        u'Sample ID',
        u'Thermal/Optical OC (ugC/LCm^3)',
        u'Thermal/Optical EC (ugC/LCm^3)',
        u'OC=TC-BC (ugC/LCm^3)',
        u'BC (ugC/LCm^3)',
        u'TC (ugC/LCm^3)',
        u'Start Date/Time',
        u'Mid-time of Collection',
        u'Sample Volume Local Condition Actual m^3',
        u'Sample Time minutes',
        u'Cal Peak Area',
        u'Laser/Temp Correction',
        u'SBasic Ver',
        u'Inst VBasic Ver',
        u'Atm.Pres.mmHg',
        u'Atm.Temp.degC',
        u'SCT',
        u'Q',
        u'LC',
        u'BC',
        u'CC',
        u'PA',
        u'A0',
        u'Optxi',
        u'SD',
        u'SpT',
        u'TT',
        u'CA',
        u'NegC',
        u'HighC',
        u'NS']

    def __init__(self, basename):
        """
        Initialize the data source.
        Parameters:
            None
        Reurns:
            None
        Raises:
            ReadError in case of any problem
        """
        self.data_std = pandas.read_csv(
            basename + '_Res.csv', delimiter=',', header=HEADERLINES,
            skipinitialspace=True, engine='python')
        # Make sure we understand the file format:
        if list(self.data_std.columns) != self.__class__.HEADERS_STD:
            raise ReadError("{}: File format error".format(
                basename + '_Res.csv'))

        self.data_amb = pandas.read_csv(
            basename + '_LCRes.csv', delimiter=',', header=HEADERLINES,
            skipinitialspace=True, engine='python')
        # Make sure we understand the file format:
        if list(self.data_amb.columns) != self.__class__.HEADERS_AMB:
            raise ReadError("{}: File format error".format(
                basename + '_LCRes.csv'))

        # initialize data attributes used for property methods
        self._start_times = None
        self._end_times = None
        self._pres_avg = None
        self._pres_avg_flags = None
        self._temp_avg = None
        self._temp_avg_flags = None

        self._tc_avg = None
        self._tc_avg_flags = None
        self._tc_unc = None
        self._tc_unc_flags = None
        self._oc_avg = None
        self._oc_avg_flags = None
        self._oc_unc = None
        self._oc_unc_flags = None
        self._ec_avg = None
        self._ec_avg_flags = None
        self._ec_unc = None
        self._ec_unc_flags = None
        self._oc1_avg = None
        self._oc1_avg_flags = None
        self._oc2_avg = None
        self._oc2_avg_flags = None
        self._oc3_avg = None
        self._oc3_avg_flags = None
        self._oc4_avg = None
        self._oc5_avg_flags = None
        self._ocpyr_avg = None
        self._ocpyr_avg_flags = None

    def _get_times(self):
        """
        Convert and check timestamps.
        """
        # get date/times from std file
        dtstr = self.data_std["Start Date/Time"].map(str.strip)
        self._start_times = pandas.to_datetime(
            dtstr, format='%m/%d/%Y %I:%M:%S %p').map(
                lambda x: x + TIMEZONE_OFFSET)
        dtstr = self.data_std["Mid-time of Collection"].map(str.strip)
        mid_times = pandas.to_datetime(
            dtstr, format='%m/%d/%Y %I:%M:%S %p').map(
                lambda x: x + TIMEZONE_OFFSET)
        delta = mid_times - self._start_times
        self._end_times = self._start_times + 2* delta

        # check date/time consistency with amb file
        if (self.data_std["Start Date/Time"] != \
                self.data_amb["Start Date/Time"]).any() or \
           (self.data_std["Mid-time of Collection"] != \
                self.data_amb["Mid-time of Collection"]).any():
            raise ReadError(
                "date/time inconsistency between amb and std file")
        if (delta.map(lambda x: round(x.total_seconds()*2/60, 1)) != \
                self.data_amb["Sample Time minutes"].map(int)).any():
            raise ReadError(
                "date/time inconsistency between amb and std file")

    @property
    def start_times(self):
        """
        Property method for accessing the start times (datetime.datetime) [UTC]
        """
        if self._start_times is None:
            self._get_times()
        return self._start_times

    @property
    def end_times(self):
        """
        Property method for accessing the end times (datetime.datetime) [UTC]
        """
        if self._end_times is None:
            self._get_times()
        return self._end_times

    def _get_conditions(self):
        """
        Convert and check atmospheric contitions (pressure/temperture, check
        consistency of std volume and ambient volume)
        """
        # convert pressure from mmHg to hPa
        self._pres_avg = self.data_amb["Atm.Pres.mmHg"].map(
            lambda x: x * 1.33322387415)
        self._pres_avg_flags = [[] for x in self._pres_avg]
        # convert temperature from degC to K
        self._temp_avg = self.data_amb["Atm.Temp.degC"].map(
            lambda x: x + 273.15)
        self._temp_avg_flags = [[] for x in self._temp_avg]

        # check pressure/temperature consistency with amb file
        if (self.data_std["Atm.Pres.mmHg"] !=
                self.data_amb["Atm.Pres.mmHg"]).any():
            raise ReadError(
                "Atm.Pres.mmHg differes between amb and std file: " + str(
                    self.data_std["Start Date/Time"][
                        self.data_std["Atm.Pres.mmHg"].index[
                            self.data_std["Atm.Pres.mmHg"] ==
                            self.data_amb["Atm.Pres.mmHg"]]]))
        if (self.data_std["Atm.Temp.degC"] !=
                self.data_amb["Atm.Temp.degC"]).any():
            raise ReadError("Atm.Temp.degC differes between amb and std file")
        # check if ambient volume and std condition volume are consistent
        # but: both volumes are obviously caculated based on minute values
        # (flow, pressure and temperature on minute resolution)
        # thus, we check if they are nearly equal (0.1 permill)
        diff = (self.data_amb["Sample Volume Local Condition Actual m^3"] *
                (293.15 * self._pres_avg) /
                (self._temp_avg * 1013.25) - \
                self.data_std["Sample Volume - STP m^3"]).map(lambda x: abs(x))
        if (diff / self.data_amb["Sample Volume Local Condition Actual m^3"] \
                > 0.0001).any() or \
           (diff / self.data_std["Sample Volume - STP m^3"] > 0.0001).any():
            raise ReadError(
                "ambient/standard conditions volumes are inconsistent")

    @property
    def pres_avg(self):
        """
        Property method for accessing the pressure values [hPa].
        """
        if self._pres_avg is None:
            self._get_conditions()
        return self._pres_avg

    @property
    def pres_avg_flags(self):
        """
        Property method for accessing the flags for the pressure values.
        """
        if self._pres_avg_flags is None:
            self._get_conditions()
        return self._pres_avg_flags

    @property
    def temp_avg(self):
        """
        Property method for accessing the temperature values [K].
        """
        if self._temp_avg is None:
            self._get_conditions()
        return self._temp_avg

    @property
    def temp_avg_flags(self):
        """
        Property method for accessing the flags for the temperature values.
        """
        if self._temp_avg_flags is None:
            self._get_conditions()
        return self._temp_avg_flags

    def _get_data(self):
        """
        Convert and check all ec/oc/tc/oc1-4/ocpyr data.
        """
        self._tc_avg = self.data_std["TC(ug)"] / \
            self.data_amb["Sample Volume Local Condition Actual m^3"]
        self._tc_unc = self.data_std["TC unc"] / \
            self.data_amb["Sample Volume Local Condition Actual m^3"]
        self._ec_avg = self.data_std["EC(ug)"] /\
            self.data_amb["Sample Volume Local Condition Actual m^3"]
        self._ec_unc = self.data_std["EC unc"] /\
            self.data_amb["Sample Volume Local Condition Actual m^3"]
        self._oc_avg = self.data_std["OC(ug)"] /\
            self.data_amb["Sample Volume Local Condition Actual m^3"]
        self._oc_unc = self.data_std["OC unc"] /\
            self.data_amb["Sample Volume Local Condition Actual m^3"]

        self._oc1_avg = self.data_std["OCPk1-ug C"] /\
            self.data_amb["Sample Volume Local Condition Actual m^3"]
        self._oc2_avg = self.data_std["OCPk2-ug C"] /\
            self.data_amb["Sample Volume Local Condition Actual m^3"]
        self._oc3_avg = self.data_std["OCPk3-ug C"] /\
            self.data_amb["Sample Volume Local Condition Actual m^3"]
        self._oc4_avg = self.data_std["OCPk4-ug C"] /\
            self.data_amb["Sample Volume Local Condition Actual m^3"]
        self._ocpyr_avg = self.data_std["Pyrolized C ug"] /\
            self.data_amb["Sample Volume Local Condition Actual m^3"]

        # QA: invalidate all values where laser temperature correction is
        # below threshold
        def extract_laser_temp_corr(val):
            reg = re.match(r'1Linear-(\d*\.\d*)$', val)
            if reg is None:
                raise ReadError('unknown laser temp correction "{}"'
                                .format(val))
            return float(reg.group(1))
        invalidate = self.data_std['Laser-Temp Correction'].map(
            extract_laser_temp_corr).map(
                lambda x: True if x < LASER_TEMP_CORRECTION_THRESHOLD
                else False)

        self._tc_avg = self._tc_avg.where(~invalidate, other=None)
        self._tc_avg_flags = [[659, 999] if x else [] for x in invalidate]
        for i in range(len(self._tc_avg_flags)):
            if self._tc_avg[i] is not None and self._tc_avg[i] < \
                    DETECTION_LIMIT_TC:
                self._tc_avg_flags[i].append(781)
        self._tc_unc = self._tc_unc.where(~invalidate, other=None)
        self._tc_unc_flags = [[659, 999] if x else [] for x in invalidate]

        self._ec_avg = self._ec_avg.where(~invalidate, other=None)
        self._ec_avg_flags = [[659, 999] if x else [] for x in invalidate]
        for i in range(len(self._ec_avg_flags)):
            if self._ec_avg[i] is not None and self._ec_avg[i] \
                    < DETECTION_LIMIT_EC:
                self._ec_avg_flags[i].append(781)
        self._ec_unc = self._ec_unc.where(~invalidate, other=None)
        self._ec_unc_flags = [[659, 999] if x else [] for x in invalidate]

        self._oc_avg = self._oc_avg.where(~invalidate, other=None)
        self._oc_avg_flags = [[659, 999] if x else [] for x in invalidate]
        for i in range(len(self._oc_avg_flags)):
            if self._oc_avg[i] is not None and self._oc_avg[i] \
                    < DETECTION_LIMIT_OC:
                self._oc_avg_flags[i].append(781)
        self._oc_unc = self._oc_unc.where(~invalidate, other=None)
        self._oc_unc_flags = [[659, 999] if x else [] for x in invalidate]

        self._oc1_avg = self._oc1_avg.where(~invalidate, other=None)
        self._oc1_avg_flags = [[659, 999] if x else [] for x in invalidate]
        self._oc2_avg = self._oc2_avg.where(~invalidate, other=None)
        self._oc2_avg_flags = [[659, 999] if x else [] for x in invalidate]
        self._oc3_avg = self._oc3_avg.where(~invalidate, other=None)
        self._oc3_avg_flags = [[659, 999] if x else [] for x in invalidate]
        self._oc4_avg = self._oc4_avg.where(~invalidate, other=None)
        self._oc4_avg_flags = [[659, 999] if x else [] for x in invalidate]
        self._ocpyr_avg = self._ocpyr_avg.where(~invalidate, other=None)
        self._ocpyr_avg_flags = [[659, 999] if x else [] for x in invalidate]


        # check consistency
        # TC (OC, EC) / ambient Volume ~= ambient concentration
        # the ambient concentrations are calculated on a finer temporal
        # resolution, so we allow for some difference (0.00002) here
        ind = (abs(self._tc_avg - self.data_amb['TC (ugC/LCm^3)']) \
               >= 0.00002).nonzero()[0]
        if ind != []:
            raise ReadError(
                'inconsistent ambient TC concentration in lines {}'.format(
                    ", ".join([str(i+HEADERLINES) for i in ind])))
        ind = (abs(self._ec_avg - \
                   self.data_amb['Thermal/Optical EC (ugC/LCm^3)']) \
               >= 0.00002).nonzero()[0]
        if ind != []:
            raise ReadError(
                'inconsistent ambient EC concentration in lines {}'.format(
                    ", ".join([str(i+HEADERLINES) for i in ind])))
        ind = (abs(self._oc_avg - \
                   self.data_amb['Thermal/Optical OC (ugC/LCm^3)']) \
               >= 0.00002).nonzero()[0]
        if ind != []:
            raise ReadError(
                'inconsistent ambient OC concentration in lines {}'.format(
                    ", ".join([str(i+HEADERLINES) for i in ind])))
        # TC == OC + EC in ambient file
        # all three variables are rounded to 6 digits, so the maximum rounding
        # error should be less than 0.000015
        ind = (abs(self.data_amb['TC (ugC/LCm^3)'] - \
                   self.data_amb['Thermal/Optical EC (ugC/LCm^3)'] - \
                   self.data_amb['Thermal/Optical OC (ugC/LCm^3)']) \
               >= 0.000015).nonzero()[0]
        if ind != []:
            raise ReadError(
                'inconsistent ambient TC concentration == ambient EC + OC '
                'concentration in lines {}'.format(
                    ", ".join([str(i+HEADERLINES) for i in ind])))
        # TC == OC + EC in standard conditions
        # all three variables are rounded to 6 digits, so the maximum rounding
        # error should be less than 0.000015
        ind = (abs(self.data_std['TC (ugC/STPm^3)'] - \
                   self.data_std['Thermal/Optical EC (ugC/STPm^3)'] - \
                   self.data_std['Thermal/Optical OC (ugC/STPm^3)']) \
               >= 0.000015).nonzero()[0]
        if ind != []:
            raise ReadError(
                'inconsistent std TC concentration == std EC + OC '
                'concentration in lines {}'.format(
                    ", ".join([str(i+HEADERLINES) for i in ind])))
        # TC == OC + mass
        # all three variables are rounded to 6 digits, so the maximum rounding
        # error should be less than 0.000015
        ind = (abs(self.data_std['TC(ug)'] - \
                   self.data_std['EC(ug)'] - \
                   self.data_std['OC(ug)'])
                >= 0.000015).nonzero()[0]
        if ind != []:
            raise ReadError(
                'inconsistent std TC mass == EC + OC mass in lines {}'.format(
                    ", ".join([str(i+HEADERLINES) for i in ind])))

    @property
    def tc_avg(self):
        """
        Property method for accessing the TC averages.
        """
        if self._tc_avg is None:
            self._get_data()
        return self._tc_avg

    @property
    def tc_avg_flags(self):
        """
        Property method for accessing flags for the TC averages.
        """
        if self._tc_avg_flags is None:
            self._get_data()
        return self._tc_avg_flags

    @property
    def tc_unc(self):
        """
        Property method for accessing the TC uncertainties.
        """
        if self._tc_unc is None:
            self._get_data()
        return self._tc_unc

    @property
    def tc_unc_flags(self):
        """
        Property method for accessing the flags for the TC uncertainties.
        """
        if self._tc_unc_flags is None:
            self._get_data()
        return self._tc_unc_flags

    @property
    def oc_avg(self):
        """
        Property method for accessing the TC averages.
        """
        if self._oc_avg is None:
            self._get_data()
        return self._oc_avg

    @property
    def oc_avg_flags(self):
        """
        Property method for accessing flags for the TC averages.
        """
        if self._oc_avg_flags is None:
            self._get_data()
        return self._oc_avg_flags

    @property
    def oc_unc(self):
        """
        Property method for accessing the TC uncertainties.
        """
        if self._oc_unc is None:
            self._get_data()
        return self._oc_unc

    @property
    def oc_unc_flags(self):
        """
        Property method for accessing the flags for the TC uncertainties.
        """
        if self._oc_unc_flags is None:
            self._get_data()
        return self._oc_unc_flags

    @property
    def ec_avg(self):
        """
        Property method for accessing the TC averages.
        """
        if self._ec_avg is None:
            self._get_data()
        return self._ec_avg

    @property
    def ec_avg_flags(self):
        """
        Property method for accessing flags for the TC averages.
        """
        if self._ec_avg_flags is None:
            self._get_data()
        return self._ec_avg_flags

    @property
    def ec_unc(self):
        """
        Property method for accessing the TC uncertainties.
        """
        if self._ec_unc is None:
            self._get_data()
        return self._ec_unc

    @property
    def ec_unc_flags(self):
        """
        Property method for accessing the flags for the TC uncertainties.
        """
        if self._ec_unc_flags is None:
            self._get_data()
        return self._ec_unc_flags

    @property
    def oc1_avg(self):
        """
        Property method for accessing the TC averages.
        """
        if self._oc1_avg is None:
            self._get_data()
        return self._oc1_avg

    @property
    def oc1_avg_flags(self):
        """
        Property method for accessing flags for the TC averages.
        """
        if self._oc1_avg_flags is None:
            self._get_data()
        return self._oc1_avg_flags

    @property
    def oc2_avg(self):
        """
        Property method for accessing the TC averages.
        """
        if self._oc2_avg is None:
            self._get_data()
        return self._oc2_avg

    @property
    def oc2_avg_flags(self):
        """
        Property method for accessing flags for the TC averages.
        """
        if self._oc2_avg_flags is None:
            self._get_data()
        return self._oc2_avg_flags

    @property
    def oc3_avg(self):
        """
        Property method for accessing the TC averages.
        """
        if self._oc3_avg is None:
            self._get_data()
        return self._oc3_avg

    @property
    def oc3_avg_flags(self):
        """
        Property method for accessing flags for the TC averages.
        """
        if self._oc3_avg_flags is None:
            self._get_data()
        return self._oc3_avg_flags

    @property
    def oc4_avg(self):
        """
        Property method for accessing the TC averages.
        """
        if self._oc4_avg is None:
            self._get_data()
        return self._oc4_avg

    @property
    def oc4_avg_flags(self):
        """
        Property method for accessing flags for the TC averages.
        """
        if self._oc4_avg_flags is None:
            self._get_data()
        return self._oc4_avg_flags

    @property
    def ocpyr_avg(self):
        """
        Property method for accessing the TC averages.
        """
        if self._ocpyr_avg is None:
            self._get_data()
        return self._ocpyr_avg

    @property
    def ocpyr_avg_flags(self):
        """
        Property method for accessing flags for the TC averages.
        """
        if self._ocpyr_avg_flags is None:
            self._get_data()
        return self._ocpyr_avg_flags

    @property
    def flow_ambient(self):
        """
        Property method for accessing the ambient flow [l / min].
        """
        return self.data_amb["Sample Volume Local Condition Actual m^3"] / \
               self.data_amb["Sample Time minutes"] * 1000

    @property
    def punch_area(self):
        """
        Property method for accessing the punch size [cm2].
        """
        return self.data_std['Punch Area']


def add_private_args(parser, cmdline):  # pylint: disable=W0613
    # W0613: Unused argument 'cmdline'
    """
    Callback function for commandline.getargs(). Adds private commandline
    arguments.

    Parameters:
        parser    root parser object from commandline.getargs()
    Returns:
        None
    """
    parser_input_group = parser.add_argument_group('input options')
    parser_input_group.add_argument(
        'basename',
        help='input file path and base name (..._LCRes.csv and ...Res.csv ' +\
             'will be used)')

def set_time(nas, source):
    """
    Set time axis data and meatdata related to time axis.
    Parameters:
        nas     EbasNasAmes object
        source  GetData object
    Returns:
        None
    """
    # time axis data:
    nas.sample_times = [(source.start_times[i].to_pydatetime(),
                         source.end_times[i].to_pydatetime())
                        for i in range(len(source.start_times))]

    # period code is an estimate of the current submissions period, so it should
    # always be calculated from the actual time axes, like this:
    nas.metadata.period = estimate_period_code(nas.sample_times[0][0],
                                               nas.sample_times[-1][1])

    # Sample duration can be set automatically
    nas.metadata.duration = estimate_sample_duration_code(nas.sample_times)
    # or set it hardcoded:
    # nas.metadata.duration = '3mo'

    # Resolution code can be set automatically
    # But be aware that resolution code is an identifying metadata element.
    # That means, several submissions of data (multiple years) will
    # only be stored as the same dataset if the resolution code is the same
    # for all submissions!
    # That might be a problem for time series with varying resolution code
    # (sometimes 2 months, sometimes 3 months, sometimes 9 weeks, ...). You
    # might consider using a fixed resolution code for those time series.
    nas.metadata.resolution = estimate_resolution_code(nas.sample_times)

    # or set it hardcoded:
    # nas.metadata.resolution = '3mo'
    nas.metadata.resolution = estimate_resolution_code(nas.sample_times)

    # the original resolution code (sampling resolution) is in this case the
    # same:
    nas.metadata.rescode_sample = nas.metadata.resolution

    # It's a good practice to use Jan 1st of the year of the first sample
    # endtime as the file reference date (zero point of time axes).
    nas.metadata.reference_date = \
        datetime.datetime(nas.sample_times[0][1].year, 1, 1)

def set_variables(nas, source):
    """
    """
    # variable: total carbon
    metadata = DataObject(
        comp_name='total_carbon',
        unit='ug C/m3',
        detection_limit=(DETECTION_LIMIT_TC, 'ug C/m3'),
        title='TC')
    nas.variables.append(DataObject(values_=source.tc_avg.values,
                                    flags=source.tc_avg_flags,
                                    metadata=metadata))
    # variable: total carbon uncertainty
    metadata = DataObject(
        comp_name='total_carbon',
        statistics='uncertainty',
        unit='ug C/m3',
        title='TC_unc')
    nas.variables.append(DataObject(values_=source.tc_unc.values,
                                    flags=source.tc_unc_flags,
                                    metadata=metadata))

    # variable: elemental carbon
    metadata = DataObject(
        comp_name='elemental_carbon',
        unit='ug C/m3',
        detection_limit=(DETECTION_LIMIT_EC, 'ug C/m3'),
        title='EC')
    nas.variables.append(DataObject(values_=source.ec_avg.values,
                                    flags=source.ec_avg_flags,
                                    metadata=metadata))
    # variable: elemental carbon uncertainty
    metadata = DataObject(
        comp_name='elemental_carbon',
        statistics='uncertainty',
        unit='ug C/m3',
        title='EC_unc')
    nas.variables.append(DataObject(values_=source.ec_unc.values,
                                    flags=source.ec_unc_flags,
                                    metadata=metadata))

    # variable: organic carbon
    metadata = DataObject(
        comp_name='organic_carbon',
        unit='ug C/m3',
        detection_limit=(DETECTION_LIMIT_OC, 'ug C/m3'),
        title='OC')
    nas.variables.append(DataObject(values_=source.oc_avg.values,
                                    flags=source.oc_avg_flags,
                                    metadata=metadata))
    # variable: organic carbon uncertainty
    metadata = DataObject(
        comp_name='organic_carbon',
        statistics='uncertainty',
        unit='ug C/m3',
        title='OC_unc')
    nas.variables.append(DataObject(values_=source.oc_unc.values,
                                    flags=source.oc_unc_flags,
                                    metadata=metadata))

    # orcanic carbon positive artifact:
    if DENUDER_USED and DENUDER_EFFICIENCY is not None and \
       DENUDER_EFFICIENCY < 100:
        # add OC, Artifact=positive
        metadata = DataObject(
            comp_name='organic_carbon',
            unit='ug C/m3',
            title='OC_pos')
        metadata.characteristics = DatasetCharacteristicList()
        metadata.characteristics.add_parse(
            'Artifact', 'positive', nas.metadata.instr_type, metadata.comp_name,
            data_level=nas.metadata.datalevel)
        pos_art = source.oc_avg * (100-DENUDER_EFFICIENCY) / 100.0
        # where source.oc_avg is None, pos_art becomes nan
        # change all nan to None:
        pos_art = pos_art.where(pandas.notnull(pos_art), None)
        nas.variables.append(DataObject(
            values_=pos_art.values,
            flags=source.oc_avg_flags, # use the same flag as for oc
            metadata=metadata))
        if DENUDER_EFFICIENCY_UNC is not None:
            metadata = DataObject(
                comp_name='organic_carbon',
                statistics='uncertainty',
                unit='ug C/m3',
                title='OC_pos_unc')
            metadata.characteristics = DatasetCharacteristicList()
            pos_art_unc = pos_art * DENUDER_EFFICIENCY_UNC / 100.0
            # where pos_art is None, pos_art_unc becomes nan
            # change all nan to None:
            pos_art_unc = pos_art_unc.where(pandas.notnull(pos_art_unc), None)
            metadata.characteristics.add_parse(
                'Artifact', 'positive', nas.metadata.instr_type,
                metadata.comp_name, data_level=nas.metadata.datalevel)
            nas.variables.append(DataObject(
                values_=pos_art_unc.values,
                flags=source.oc_avg_flags,  # use the same flag as for oc
                metadata=metadata))

    # variable: organic carbon OC1
    metadata = DataObject(
        comp_name='organic_carbon',
        unit='ug C/m3',
        title='OC_peak1')
    nas.variables.append(DataObject(values_=source.oc1_avg.values,
                                    flags=source.oc1_avg_flags,
                                    metadata=metadata))
    metadata.characteristics = DatasetCharacteristicList()
    metadata.characteristics.add_parse(
        'Fraction', 'OC1', nas.metadata.instr_type, metadata.comp_name,
        data_level=nas.metadata.datalevel)

    # variable: organic carbon OC2
    metadata = DataObject(
        comp_name='organic_carbon',
        unit='ug C/m3',
        title='OC_peak2')
    nas.variables.append(DataObject(values_=source.oc2_avg.values,
                                    flags=source.oc2_avg_flags,
                                    metadata=metadata))
    metadata.characteristics = DatasetCharacteristicList()
    metadata.characteristics.add_parse(
        'Fraction', 'OC2', nas.metadata.instr_type, metadata.comp_name,
        data_level=nas.metadata.datalevel)

    # variable: organic carbon OC3
    metadata = DataObject(
        comp_name='organic_carbon',
        unit='ug C/m3',
        title='OC_peak3')
    nas.variables.append(DataObject(values_=source.oc3_avg.values,
                                    flags=source.oc3_avg_flags,
                                    metadata=metadata))
    metadata.characteristics = DatasetCharacteristicList()
    metadata.characteristics.add_parse(
        'Fraction', 'OC3', nas.metadata.instr_type, metadata.comp_name,
        data_level=nas.metadata.datalevel)

    # variable: organic carbon OC4
    metadata = DataObject(
        comp_name='organic_carbon',
        unit='ug C/m3',
        title='OC_peak4')
    nas.variables.append(DataObject(values_=source.oc4_avg.values,
                                    flags=source.oc4_avg_flags,
                                    metadata=metadata))
    metadata.characteristics = DatasetCharacteristicList()
    metadata.characteristics.add_parse(
        'Fraction', 'OC4', nas.metadata.instr_type, metadata.comp_name,
        data_level=nas.metadata.datalevel)

    # variable: organic carbon OCPyr
    metadata = DataObject(
        comp_name='organic_carbon',
        unit='ug C/m3',
        title='OC_pyr')
    nas.variables.append(DataObject(values_=source.ocpyr_avg.values,
                                    flags=source.ocpyr_avg_flags,
                                    metadata=metadata))
    metadata.characteristics = DatasetCharacteristicList()
    metadata.characteristics.add_parse(
        'Fraction', 'OCPyr', nas.metadata.instr_type, metadata.comp_name,
        data_level=nas.metadata.datalevel)

    # variable: pressure
    metadata = DataObject(
        comp_name='pressure',
        unit='hPa',
        title='press')
    nas.variables.append(DataObject(values_=source.pres_avg.values,
                                    flags=source.pres_avg_flags,
                                    metadata=metadata))
    # variable: temperature
    metadata = DataObject(
        comp_name='temperature',
        unit='K',
        title='temp')
    nas.variables.append(DataObject(values_=source.temp_avg.values,
                                    flags=source.temp_avg_flags,
                                    metadata=metadata))

    # check consistency of flow rate:
    medflow = median(source.flow_ambient)
    if abs(medflow - nas.metadata.flow_rate) / nas.metadata.flow_rate > 0.1:
        raise ValueError(
            'median flow calculated by sample volume / sample time ({}) is '
            'more then 10 %  off the specified flow rate in the metadata ({})'
            .format(medflow, nas.metadata.flow_rate))

    # check consistency of punch area:
    medpunch = median(source.punch_area)
    if abs(medpunch - nas.metadata.filter_area) / nas.metadata.filter_area > 0.1:
        raise ValueError(
            'median punch area ({}) is more then 10 %  off the specified '
            'exposed filter area in the metadata ({})'
            .format(medpunch, nas.metadata.filter_area))

    # check consistency of flow, exposed filter area and filter face velocity:
    ffv_calc = nas.metadata.flow_rate * 1000 / 60 / nas.metadata.filter_area
    if abs(ffv_calc - nas.metadata.filter_face_velocity) / \
       nas.metadata.filter_face_velocity > 0.1:
        raise ValueError(
            'Filter face velocity specified in metadata ({}) is inconsistent '
            'with flow rate ({}) and exposed filter area ({}) specified in '
            'metadata'.format(
                nas.metadata.filter_face_velocity, nas.metadata.flow_rate,
                nas.metadata.filter_area))

def ebas_genfile(cmdline):
    """
    Main program for ebas_genfile_ec-oc_online_sunset
    Created for lexical scoping.

    Parameters:
        cmdline   EbasCommandline object (wrapper)
    Returns:
        none
    """
    logger = logging.getLogger('ebas_genfile_ec-oc_online_sunset')
    args = cmdline.args
    source = GetData(args.basename)

    nas = EbasNasaAmes()
    nas.metadata.update(GLOBAL_METADATA)

    set_time(nas, source)
    set_variables(nas, source)

    nas.write(createfiles=True)


EbasCommandline(
    ebas_genfile,
    custom_args=['CONFIG', 'LOGGING'],
    private_args=add_private_args,
    help_description='%(prog)s generate EC/OC online NASA Anmes file from ' + \
        'Sunset.instrument output',
    version=__version__).run()
