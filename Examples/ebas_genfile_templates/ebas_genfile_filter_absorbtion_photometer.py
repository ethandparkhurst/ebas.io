#!/usr/bin/env python
# coding=utf-8
"""
$Id: ebas_genfile_filter_absorbtion_photometer.py 1631 2017-05-23 16:11:07Z pe $

Example for creating an EBAS_1.1 NasaAmes datafile.
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
            PS_EMAIL='Markus.Fiebig@nilu.no',
            PS_ORG_NAME='Norwegian Institute for Air Research',
            PS_ORG_ACR='NILU', PS_ORG_UNIT='Atmosphere and Climate Department',
            PS_ADDR_LINE1='Instituttveien 18', PS_ADDR_LINE2=None,
            PS_ADDR_ZIP='2007', PS_ADDR_CITY='Kjeller',
            PS_ADDR_COUNTRY='Norway',
            PS_ORCID='https://orcid.org/0000-0003-3754-520X',
        ))
    nas.metadata.originator.append(
        DataObject(
            PS_LAST_NAME=u'Someone', PS_FIRST_NAME='Else',
            PS_EMAIL='Someone@somewhere.no',
            PS_ORG_NAME='Some nice Institute',
            PS_ORG_ACR='WOW', PS_ORG_UNIT='Super interesting division',
            PS_ADDR_LINE1='Street 18', PS_ADDR_LINE2=None,
            PS_ADDR_ZIP='X-9999', PS_ADDR_CITY='Paradise',
            PS_ADDR_COUNTRY='Norway',
            PS_ORCID=None,
        ))

    # Data Submitters (contact for data technical issues)
    nas.metadata.submitter = []
    nas.metadata.submitter.append(
        DataObject(
            PS_LAST_NAME='Fiebig', PS_FIRST_NAME='Markus',
            PS_EMAIL='Markus.Fiebig@nilu.no',
            PS_ORG_NAME='Norwegian Institute for Air Research',
            PS_ORG_ACR='NILU', PS_ORG_UNIT='Atmosphere and Climate Department',
            PS_ADDR_LINE1='Instituttveien 18', PS_ADDR_LINE2=None,
            PS_ADDR_ZIP='2007', PS_ADDR_CITY='Kjeller',
            PS_ADDR_COUNTRY='Norway',
            PS_ORCID=None,
        ))

    # Station metadata
    nas.metadata.station_code = 'NO0001R'
    nas.metadata.platform_code = 'NO0001S'
    nas.metadata.station_name = u'Birkenes'

    nas.metadata.station_wdca_id = 'GAWANO__BIR'
    nas.metadata.station_gaw_id = 'BIR'
    nas.metadata.station_gaw_name = u'Birkenes Atmospheric Observatory',
    # nas.metadata.station_airs_id =    # N/A
    nas.metadata.station_other_ids = '201(NILUDB)'
    # nas.metadata.station_state_code =  # N/A
    nas.metadata.station_landuse = 'Forest',
    nas.metadata.station_setting = 'Rural',
    nas.metadata.station_gaw_type = 'R'
    nas.metadata.station_wmo_region = 6
    nas.metadata.station_latitude = 58.380
    nas.metadata.station_longitude = 8.250
    nas.metadata.station_altitude = 220.0

    # More file global metadata, but those can be overridden per variable
    # See set_variables for examples
    nas.metadata.instr_type = 'filter_absorption_photometer'
    nas.metadata.lab_code = 'NO01L'
    nas.metadata.instr_name = 'Radiance-Research_PSAP-3W_BIR_dry'
    nas.metadata.instr_manufacturer = 'Radiance-Research'
    nas.metadata.instr_model = 'PSAP-3W'
    nas.metadata.instr_serialno = '12345678'
    nas.metadata.rescode_sample = '6mn'  # Original time res.
    nas.metadata.method = 'NO01L_abs_coef_PSAP_v1'
    nas.metadata.regime = 'IMG'
    nas.metadata.matrix = 'pm10'
    #nas.metadata.comp_name   will be set on variable level
    #nas.metadata.unit        will be set on variable level
    nas.metadata.statistics = 'arithmetic mean'
    nas.metadata.datalevel = '2'
    nas.metadata.mea_height = 4
    nas.metadata.inlet_type = 'Impactor--direct'
    nas.metadata.inlet_desc = \
        'PM10 at ambient humidity inlet, Digitel, flow 140 l/min'
    nas.metadata.hum_temp_ctrl = 'None'
    nas.metadata.hum_temp_ctrl_desc = \
        'passive, sample heated from atmospheric to lab temperature'
    nas.metadata.vol_std_temp = 273.15
    nas.metadata.vol_std_pressure = 1013.25
    nas.metadata.detection_limit = (0.1, '1/Mm')
    nas.metadata.detection_limit_desc = \
        'Determined by instrument noise characteristics, no'
    nas.metadata.uncertainty_desc = \
        'typical value of unit-to-unit variability as estimated by Bond et al., 1999.'
    nas.metadata.zero_negative = 'Zero/negative possible'
    nas.metadata.zero_negative_desc = \
        'Zero and neg. values may appear due to statistical variations at ' +\
        'very low concentrations'
    nas.metadata.std_method = 'Single-angle_Correction=Bond1999'
    nas.metadata.qa = []
    nas.metadata.qa.append(
        DataObject({
            'qa_number': 1,
            'qm_id': 'WCCAP-AP-2015-1',
            'qa_date': datetime.datetime(2015, 9, 25),
            'qa_doc_url': 'http://www.actris-ecac.eu/files/ECAC-report-AP-2015-1-7_NILU_AP-121.pdf'
            })) 
    nas.metadata.comment = \
        'Standard Bond et al. 1999 values for K1 and K2 used at all wavelengths'
    nas.metadata.acknowledgements = \
        'Request acknowledgement details from data originator'

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
    metadata.characteristics.add_parse('Location', 'instrument internal', 'filter_absorption_photometer', 'pressure')
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
    metadata.characteristics.add_parse('Location', 'instrument internal', 'filter_absorption_photometer', 'temperature')
    nas.variables.append(DataObject(values_=values, flags=flags, flagcol=True,
                                    metadata=metadata))

    # variable 3: aerosol_absorption_coefficient, 470 nm
    values = [0.5566, None]   # missing value is None!
    flags = [[], [999]]
    metadata = DataObject()
    metadata.comp_name = 'aerosol_absorption_coefficient'
    metadata.unit = '1/Mm'
    metadata.title = 'abs470'
    metadata.uncertainty = (6, '%')
    metadata.characteristics = DatasetCharacteristicList()
    metadata.characteristics.add_parse('Wavelength', '450 nm', 'filter_absorption_photometer', 'aerosol_absorption_coefficient')
    nas.variables.append(DataObject(values_=values, flags=flags, flagcol=True,
                                    metadata=metadata))

    # variable 4: aerosol_absorption_coefficient, 520 nm
    values = [0.3196, None]   # missing value is None!
    flags = [[], [999]]
    metadata = DataObject()
    metadata.comp_name = 'aerosol_absorption_coefficient'
    metadata.unit = '1/Mm'
    metadata.title = 'abs520'
    metadata.uncertainty = (6, '%')
    metadata.characteristics = DatasetCharacteristicList()
    metadata.characteristics.add_parse('Wavelength', '520 nm', 'filter_absorption_photometer', 'aerosol_absorption_coefficient')
    nas.variables.append(DataObject(values_=values, flags=flags, flagcol=True,
                                    metadata=metadata))

    # variable 5: aerosol_absorption_coefficient, 660 nm
    values = [0.3956, None]   # missing value is None!
    flags = [[], [999]]
    metadata = DataObject()
    metadata.comp_name = 'aerosol_absorption_coefficient'
    metadata.unit = '1/Mm'
    metadata.title = 'abs660'
    metadata.uncertainty = (6, '%')
    metadata.characteristics = DatasetCharacteristicList()
    metadata.characteristics.add_parse('Wavelength', '660 nm', 'filter_absorption_photometer', 'aerosol_absorption_coefficient')
    nas.variables.append(DataObject(values_=values, flags=flags, flagcol=True,
                                    metadata=metadata))

    # variable 6: aerosol_absorption_coefficient, 470 nm, 15.87 percentile
    values = [0.5566, None]   # missing value is None!
    flags = [[], [999]]
    metadata = DataObject()
    metadata.comp_name = 'aerosol_absorption_coefficient'
    metadata.unit = '1/Mm'
    metadata.statistics = 'percentile:15.87'
    metadata.title = 'abs470'
    metadata.uncertainty = (6, '%')
    metadata.characteristics = DatasetCharacteristicList()
    metadata.characteristics.add_parse('Wavelength', '450 nm', 'filter_absorption_photometer', 'aerosol_absorption_coefficient')
    nas.variables.append(DataObject(values_=values, flags=flags, flagcol=True,
                                    metadata=metadata))

    # variable 7: aerosol_absorption_coefficient, 520 nm, 15.87 percentile
    values = [0.3196, None]   # missing value is None!
    flags = [[], [999]]
    metadata = DataObject()
    metadata.comp_name = 'aerosol_absorption_coefficient'
    metadata.unit = '1/Mm'
    metadata.statistics = 'percentile:15.87'
    metadata.title = 'abs520'
    metadata.uncertainty = (6, '%')
    metadata.characteristics = DatasetCharacteristicList()
    metadata.characteristics.add_parse('Wavelength', '520 nm', 'filter_absorption_photometer', 'aerosol_absorption_coefficient')
    nas.variables.append(DataObject(values_=values, flags=flags, flagcol=True,
                                    metadata=metadata))

    # variable 8: aerosol_absorption_coefficient, 660 nm, 15.87 percentile
    values = [0.3956, None]   # missing value is None!
    flags = [[], [999]]
    metadata = DataObject()
    metadata.comp_name = 'aerosol_absorption_coefficient'
    metadata.statistics = 'percentile:15.87'
    metadata.unit = '1/Mm'
    metadata.title = 'abs660'
    metadata.uncertainty = (6, '%')
    metadata.characteristics = DatasetCharacteristicList()
    metadata.characteristics.add_parse('Wavelength', '660 nm', 'filter_absorption_photometer', 'aerosol_absorption_coefficient')
    nas.variables.append(DataObject(values_=values, flags=flags, flagcol=True,
                                    metadata=metadata))

    # variable 9: aerosol_absorption_coefficient, 470 nm, 84.13 percentile
    values = [0.5566, None]   # missing value is None!
    flags = [[], [999]]
    metadata = DataObject()
    metadata.comp_name = 'aerosol_absorption_coefficient'
    metadata.unit = '1/Mm'
    metadata.statistics = 'percentile:84.13'
    metadata.title = 'abs470'
    metadata.uncertainty = (6, '%')
    metadata.characteristics = DatasetCharacteristicList()
    metadata.characteristics.add_parse('Wavelength', '450 nm', 'filter_absorption_photometer', 'aerosol_absorption_coefficient')
    nas.variables.append(DataObject(values_=values, flags=flags, flagcol=True,
                                    metadata=metadata))

    # variable 7: aerosol_absorption_coefficient, 520 nm, 84.13 percentile
    values = [0.3196, None]   # missing value is None!
    flags = [[], [999]]
    metadata = DataObject()
    metadata.comp_name = 'aerosol_absorption_coefficient'
    metadata.unit = '1/Mm'
    metadata.statistics = 'percentile:84.13'
    metadata.title = 'abs520'
    metadata.uncertainty = (6, '%')
    metadata.characteristics = DatasetCharacteristicList()
    metadata.characteristics.add_parse('Wavelength', '520 nm', 'filter_absorption_photometer', 'aerosol_absorption_coefficient')
    nas.variables.append(DataObject(values_=values, flags=flags, flagcol=True,
                                    metadata=metadata))

    # variable 8: aerosol_absorption_coefficient, 660 nm, 84.13 percentile
    values = [0.3956, None]   # missing value is None!
    flags = [[], [999]]
    metadata = DataObject()
    metadata.comp_name = 'aerosol_absorption_coefficient'
    metadata.statistics = 'percentile:84.13'
    metadata.unit = '1/Mm'
    metadata.title = 'abs660'
    metadata.uncertainty = (6, '%')
    metadata.characteristics = DatasetCharacteristicList()
    metadata.characteristics.add_parse('Wavelength', '660 nm', 'filter_absorption_photometer', 'aerosol_absorption_coefficient')
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
