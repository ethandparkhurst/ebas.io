#!/usr/bin/env python
# coding=utf-8
"""
Example for creating an EBAS_1.1 NasaAmes ACSM datafile.
"""
from ebas.io.file import nasa_ames
from nilutility.datatypes import DataObject
from ebas.domain.basic_domain_logic.time_period import estimate_period_code, \
    estimate_resolution_code, estimate_sample_duration_code
import datetime
from ebas.io.ebasmetadata import DatasetCharacteristicList

__version__ = '1.00.00'

def set_fileglobal_metadata(nas):
    """
    Set file global metadata for the EbasNasaAmes file object

    Parameters:
        nas    EbasNasaAmes file object
    Returns:
        None
    """
    # All times reported to EBAS need to be in UTC!
    # Setting the timezone here explicitly should remind you to check your data
    nas.metadata.timezone = 'UTC'

    # Revision information
    nas.metadata.revdate = datetime.datetime(2008, 6, 24, 0, 0, 0)
    nas.metadata.revision = '1'
    nas.metadata.revdesc = \
        'initial revision, Adis_PSAP_lev0_2_lev1 v.0.0_2'

    # Data Originator Organisation
    nas.metadata.org = DataObject(
        OR_CODE='NO01L',
        OR_NAME='Norwegian Institute for Air Research',
        OR_ACRONYM='NILU', OR_UNIT='Atmosphere and Climate Department',
        OR_ADDR_LINE1='Instituttveien 18', OR_ADDR_LINE2=None,
        OR_ADDR_ZIP='2007', OR_ADDR_CITY='Kjeller', OR_ADDR_COUNTRY='Norway')

    # Projects the data are associated to
    nas.metadata.projects = ['GAW-WDCA']

    # Data Originators (PIs)
    nas.metadata.originator = []
    nas.metadata.originator.append(
        DataObject(
            PS_LAST_NAME='Fiebig', PS_FIRST_NAME='Markus',
            PS_EMAIL='someone@somewhere.no',
            PS_ORG_NAME='Norwegian Institute for Air Research',
            PS_ORG_ACR='NILU', PS_ORG_UNIT='Atmosphere and Climate Department',
            PS_ADDR_LINE1='Instituttveien 18', PS_ADDR_LINE2=None,
            PS_ADDR_ZIP='2007', PS_ADDR_CITY='Kjeller',
            PS_ADDR_COUNTRY='Norway',
            PS_ORCID='0000-0003-3754-520X',
        ))
    nas.metadata.originator.append(
        DataObject(
            PS_LAST_NAME=u'Rud', PS_FIRST_NAME='Richard',
            PS_EMAIL='someone@somewhere.no',
            PS_ORG_NAME='Some nice Institute',
            PS_ORG_ACR='WOW', PS_ORG_UNIT='Super interesting division',
            PS_ADDR_LINE1='Street 18', PS_ADDR_LINE2=None,
            PS_ADDR_ZIP='X-9999', PS_ADDR_CITY='Paradise',
            PS_ADDR_COUNTRY='Norway',
            PS_ORCID='0000-0001-9250-9813',
        ))

    # Data Submitters (contact for data technical issues)
    nas.metadata.submitter = []
    nas.metadata.submitter.append(
        DataObject(
            PS_LAST_NAME='Rud', PS_FIRST_NAME='Richard',
            PS_EMAIL='someone@somewhere.no',
            PS_ORG_NAME='Norwegian Institute for Air Research',
            PS_ORG_ACR='NILU', PS_ORG_UNIT='Atmosphere and Climate Department',
            PS_ADDR_LINE1='Instituttveien 18', PS_ADDR_LINE2=None,
            PS_ADDR_ZIP='2007', PS_ADDR_CITY='Kjeller',
            PS_ADDR_COUNTRY='Norway',
            PS_ORCID='0000-0001-9250-9813',
        ))

    # Station metadata
    nas.metadata.station_code = 'FR0020R'
    nas.metadata.platform_code = 'FR0020S'
    nas.metadata.station_name = u'SIRTA'

    nas.metadata.station_wdca_id = 'GAWAFR__GIF'
    nas.metadata.station_gaw_id = 'GIF'
    nas.metadata.station_gaw_name = u'SIRTA',
    nas.metadata.station_landuse = 'Agricultural',
    nas.metadata.station_setting = 'Suburban',
    nas.metadata.station_gaw_type = 'C'
    nas.metadata.station_wmo_region = 6
    nas.metadata.station_latitude = 48.709
    nas.metadata.station_longitude = 2.159
    nas.metadata.station_altitude = 162.0
    nas.metadata.mea_height = 6.0

    # More file global metadata, but those can be overridden per variable
    # See set_variables for examples
    nas.metadata.instr_type = 'aerosol_mass_spectrometer'
    nas.metadata.lab_code = 'FR01L'
    nas.metadata.instr_name = 'ACSM_Aerodyne_Quad_140-142'
    nas.metadata.instr_manufacturer = 'Aerodyne'
    nas.metadata.instr_model = 'Q-ACSM'
    nas.metadata.instr_serialno = '140-142'
    nas.metadata.rescode_sample = '1h'  # Original time res.
    nas.metadata.method = 'FR01L_Aerodyne_Quad_GIF' # Method ref
    nas.metadata.regime = 'IMG'
    nas.metadata.matrix = 'pm1_non_refractory'
    #nas.metadata.comp_name   will be set on variable level
    #nas.metadata.unit        will be set on variable level
    nas.metadata.statistics = 'arithmetic mean'
    nas.metadata.datalevel = '2'
    nas.metadata.mea_height = 4
    nas.metadata.inlet_type = 'Cyclone'
    nas.metadata.inlet_desc = 'Inlet cutpoint=PM1; Comment='
    nas.metadata.hum_temp_ctrl = 'Nafion dryer'
    nas.metadata.hum_temp_ctrl_desc = None
    nas.metadata.vol_std_temp = 273.15
    nas.metadata.vol_std_pressure = 1013.25
    #nas.metadata.detection_limit = (0.2, 'ug/m3')
    nas.metadata.detection_limit_desc = 'Determined by instrument counting statistics, no detection limit flag used' # Detection limit expl.
    nas.metadata.uncertainty_desc = None
    nas.metadata.zero_negative = 'Zero/negative possible' #Zero/negative values code
    nas.metadata.zero_negative_desc = 'Zero and neg. values may appear due to statistical variations at very low concentrations' # Zero/negative values
    nas.metadata.std_method = None
    nas.metadata.comment = 'No SOP currently available'
    nas.metadata.acknowledgements = \
        'For using this data for any kind of publications, you must contact the data originator(s), in terms of acknowledgment'

def set_time_axes(nas):
    """
    Set the time axes and related metadata for the EbasNasaAmes file object.

    Parameters:
        nas    EbasNasaAmes file object
    Returns:
        None
    """
    # define start and end times for all samples
    nas.sample_times = \
        [(datetime.datetime(2008, 1, 1, 0, 0), datetime.datetime(2008, 1, 1, 1, 0)),
         (datetime.datetime(2008, 1, 1, 1, 0), datetime.datetime(2008, 1, 1, 2, 0))]

    #
    # Generate metadata that are related to the time axes:
    #

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
    # Automatic calculation (will work from ebas.io V.3.0.7):
    nas.metadata.resolution = estimate_resolution_code(nas.sample_times)
    # or set it hardcoded:
    # nas.metadata.resolution = '3mo'

    # It's a good practice to use Jan 1st of the year of the first sample
    # endtime as the file reference date (zero point of time axes).
    nas.metadata.reference_date = \
        datetime.datetime(nas.sample_times[0][1].year, 1, 1)

def set_variables(nas):
    """
    Set metadata and data for all variables for the EbasNasaAmes file object.

    Parameters:
        nas    EbasNasaAmes file object
    Returns:
        None
    """
    # variable 1: pressure
    values = [839.4, None]   # missing value is None!
    flags = [[], [999]]
    # [] means no flags for this measurement
    # [999] missing or invalid flag needed because of missing value (None)
    metadata = DataObject()
    metadata.comp_name = 'pressure'
    metadata.unit = 'hPa'
    metadata.matrix = 'instrument'
    metadata.title = 'p_int'
    metadata.characteristics = DatasetCharacteristicList()
    metadata.characteristics.add_parse('Location', 'instrument intlet', 'aerosol_mass_spectrometer', 'pressure')
    nas.variables.append(DataObject(values_=values, flags=flags, flagcol=True,
                                    metadata=metadata))

    # variable 2: temperature
    values = [299.7, None]   # missing value is None!
    flags = [[], [999]]
    metadata = DataObject()
    metadata.comp_name = 'temperature'
    metadata.unit = 'K'
    metadata.matrix = 'instrument'
    metadata.title = 't_int'
    metadata.characteristics = DatasetCharacteristicList()
    metadata.characteristics.add_parse('Location', 'before dryer', 'aerosol_mass_spectrometer', 'temperature')
    nas.variables.append(DataObject(values_=values, flags=flags, flagcol=True,
                                    metadata=metadata))

    # variable 3: relative humidity
    values = [21.2300, None]   # missing value is None!
    flags = [[], [999]]
    metadata = DataObject()
    metadata.comp_name = 'relative_humidity'
    metadata.unit = '%'
    metadata.matrix = 'instrument'
    metadata.title = 'rh_int'
    metadata.characteristics = DatasetCharacteristicList()
    metadata.characteristics.add_parse('Location', 'before dryer', 'aerosol_mass_spectrometer', 'relative_humidity')
    nas.variables.append(DataObject(values_=values, flags=flags, flagcol=True,
                                    metadata=metadata))

    # variable 4: organic_mass, arithmetic mean
    values = [0.5566, None]   # missing value is None!
    flags = [[], [999]]
    metadata = DataObject()
    metadata.comp_name = 'organic_mass'
    metadata.unit = 'ug/m3'
    metadata.title = 'Org'
    metadata.detection_limit = (0.1, 'ug/m3')
    metadata.statistics = 'arithmetic mean'
    nas.variables.append(DataObject(values_=values, flags=flags, flagcol=True,
                                    metadata=metadata))

    # variable 5: organic_mass, uncertainty
    values = [0.5566, None]   # missing value is None!
    flags = [[], [999]]
    metadata = DataObject()
    metadata.comp_name = 'organic_mass'
    metadata.unit = 'ug/m3'
    metadata.title = 'err_Org'
    metadata.statistics = 'uncertainty'
    nas.variables.append(DataObject(values_=values, flags=flags, flagcol=True,
                                    metadata=metadata))

    # variable 6: nitrate, arithmetic mean
    values = [0.5566, None]   # missing value is None!
    flags = [[], [999]]
    metadata = DataObject()
    metadata.comp_name = 'nitrate'
    metadata.unit = 'ug/m3'
    metadata.title = 'NO3'
    metadata.detection_limit = (0.28, 'ug/m3')
    metadata.statistics = 'arithmetic mean'
    nas.variables.append(DataObject(values_=values, flags=flags, flagcol=True,
                                    metadata=metadata))
    # variable 7: nitrate, uncertainty
    values = [0.5566, None]   # missing value is None!
    flags = [[], [999]]
    metadata = DataObject()
    metadata.comp_name = 'nitrate'
    metadata.unit = 'ug/m3'
    metadata.title = 'err_NO3'
    metadata.statistics = 'uncertainty'
    nas.variables.append(DataObject(values_=values, flags=flags, flagcol=True,
                                    metadata=metadata))

    # variable 8: sulphate_total, arithmetic mean
    values = [0.5566, None]   # missing value is None!
    flags = [[], [999]]
    metadata = DataObject()
    metadata.comp_name = 'sulphate_total'
    metadata.unit = 'ug/m3'
    metadata.title = 'SO4'
    metadata.detection_limit = (0.28, 'ug/m3')
    metadata.statistics = 'arithmetic mean'
    nas.variables.append(DataObject(values_=values, flags=flags, flagcol=True,
                                    metadata=metadata))

    # variable 9: sulphate_total, uncertainty
    values = [0.5566, None]   # missing value is None!
    flags = [[], [999]]
    metadata = DataObject()
    metadata.comp_name = 'nitrate'
    metadata.unit = 'ug/m3'
    metadata.title = 'err_SO4'
    metadata.statistics = 'uncertainty'
    nas.variables.append(DataObject(values_=values, flags=flags, flagcol=True,
                                    metadata=metadata))

    # variable 10: ammonium, ug/m3, Detection limit=0.51 ug/m3, Statistics=arithmetic mean
    values = [0.5566, None]   # missing value is None!
    flags = [[], [999]]
    metadata = DataObject()
    metadata.comp_name = 'ammonium'
    metadata.unit = 'ug/m3'
    metadata.title = 'NH4'
    metadata.detection_limit = (0.51, 'ug/m3')
    metadata.statistics = 'arithmetic mean'
    nas.variables.append(DataObject(values_=values, flags=flags, flagcol=True,
                                    metadata=metadata))

    # variable 11: ammonium, ug/m3, Statistics=uncertainty
    values = [0.5566, None]   # missing value is None!
    flags = [[], [999]]
    metadata = DataObject()
    metadata.comp_name = 'ammonium'
    metadata.unit = 'ug/m3'
    metadata.title = 'err_NH4'
    metadata.statistics = 'uncertainty'
    nas.variables.append(DataObject(values_=values, flags=flags, flagcol=True,
                                    metadata=metadata))

    # variable 12: organic_mass, ug/m3, Fraction=Org_44, Statistics=arithmetic mean
    values = [21.2300, None]   # missing value is None!
    flags = [[], [999]]
    metadata = DataObject()
    metadata.comp_name = 'organic_mass'
    metadata.unit = 'ug/m3'
    metadata.title = 'Org_44'
    metadata.statistics = 'arithmetic mean'
    metadata.characteristics = DatasetCharacteristicList()
    metadata.characteristics.add_parse('Fraction', 'Org_44', 'aerosol_mass_spectrometer', 'organic_mass')
    nas.variables.append(DataObject(values_=values, flags=flags, flagcol=True,
                                    metadata=metadata))


    # variable 13: organic_mass, ug/m3, Fraction=Org_43, Statistics=arithmetic mean
    values = [21.2300, None]   # missing value is None!
    flags = [[], [999]]
    metadata = DataObject()
    metadata.comp_name = 'organic_mass'
    metadata.unit = 'ug/m3'
    metadata.title = 'Org_43'
    metadata.statistics = 'arithmetic mean'
    metadata.characteristics = DatasetCharacteristicList()
    metadata.characteristics.add_parse('Fraction', 'Org_43', 'aerosol_mass_spectrometer', 'organic_mass')
    nas.variables.append(DataObject(values_=values, flags=flags, flagcol=True,
                                    metadata=metadata))

    # variable 14: organic_mass, ug/m3, Fraction=Org_60, Statistics=arithmetic mean
    values = [21.2300, None]   # missing value is None!
    flags = [[], [999]]
    metadata = DataObject()
    metadata.comp_name = 'organic_mass'
    metadata.unit = 'ug/m3'
    metadata.title = 'Org_60'
    metadata.statistics = 'arithmetic mean'
    metadata.characteristics = DatasetCharacteristicList()
    metadata.characteristics.add_parse('Fraction', 'Org_60', 'aerosol_mass_spectrometer', 'organic_mass')
    nas.variables.append(DataObject(values_=values, flags=flags, flagcol=True,
                                    metadata=metadata))

    # variable 15: chloride, ug/m3, Detection limit=0.1 ug/m3, Statistics=arithmetic mean
    values = [0.5566, None]   # missing value is None!
    flags = [[], [999]]
    metadata = DataObject()
    metadata.comp_name = 'chloride'
    metadata.unit = 'ug/m3'
    metadata.title = 'Chl'
    metadata.detection_limit = (0.1, 'ug/m3')
    metadata.statistics = 'arithmetic mean'
    nas.variables.append(DataObject(values_=values, flags=flags, flagcol=True,
                                    metadata=metadata))

    # variable 16: chloride, ug/m3, Statistics=uncertainty
    values = [0.5566, None]   # missing value is None!
    flags = [[], [999]]
    metadata = DataObject()
    metadata.comp_name = 'chloride'
    metadata.unit = 'ug/m3'
    metadata.title = 'err_Chl'
    metadata.statistics = 'uncertainty'
    nas.variables.append(DataObject(values_=values, flags=flags, flagcol=True,
                                    metadata=metadata))

def ebas_genfile():
    """
    Main program for ebas_flatcsv
    Created for lexical scoping.

    Parameters:
        None
    Returns:
        none
    """

    # Create an EbasNasaAmes file object
    nas = nasa_ames.EbasNasaAmes()

    # Set file global metadata
    set_fileglobal_metadata(nas)

    # Set the time axes and related metadata
    set_time_axes(nas)

    # Set metadata and data for all variables
    set_variables(nas)

    # write the file:
    nas.write(createfiles=True)
    # createfiles=True
    #     Actually creates output files, else the output would go to STDOUT.
    # You can also specify:
    #     destdir='path/to/directory'
    #         Specify a specific relative or absolute path to a directory the
    #         files should be written to
    #     flags=FLAGS_COMPRESS
    #         Compresses the file size by reducing flag columns.
    #         Flag columns will be less explicit and thus less intuitive for
    #         humans to read.
    #     flags=FLAGS_ALL
    #         Always generate one flag column per variable. Very intuitive to
    #         read, but increases filesize.
    #     The default for flags is: Generate one flag column per file if the
    #     flags are the same for all variables in the file. Else generate one
    #     flag column per variable.
    #     This is a trade-off between the advantages and disadvantages of the
    #     above mentioned approaches.

ebas_genfile()
