#!/usr/bin/env python
# coding=utf-8
"""
$Id: ebas_genfile.py 1630 2017-05-23 16:10:23Z pe $

Example for creating an EBAS_1.1 NasaAmes datafile.

This Example is not thought to be used for any actual data submission.
It should show the concept and give examples of how to use the ebas-io package
to generate an EBAS  Nasa Ames file.

For concrete examples for specific submission templates (instrument types),
please have a look in the ebas_genfile_templates subdirectory.

"""
from ebas.io.file import nasa_ames
from nilutility.datatypes import DataObject
from ebas.domain.basic_domain_logic.time_period import estimate_period_code, \
    estimate_resolution_code, estimate_sample_duration_code
import datetime

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
    nas.metadata.revdate = datetime.datetime(2015, 2, 13, 12, 54, 21)
    nas.metadata.revision = '1.1a'
    nas.metadata.revdesc = \
        'initiol revision to ebas, generated with MyDataTool 1.22'

    # Data Originator Organisation
    nas.metadata.org = DataObject(
        OR_CODE='APP', #NOT RIGHT, ASK JPS
        OR_NAME='Appalachian Atmospheric Interdisciplinary Research Program',
        OR_ACRONYM='AppalAIR', OR_UNIT='Department of Physics and Astronomy',
        OR_ADDR_LINE1='525 Rivers Street', OR_ADDR_LINE2=None,
        OR_ADDR_ZIP='28608', OR_ADDR_CITY='Boone', OR_ADDR_COUNTRY='United States of America')

    # Projects the data are associated to
    nas.metadata.projects = ['GAW-WDCA', 'AppalAIR']

    # Data Originators (PIs)
    nas.metadata.originator = []
    nas.metadata.originator.append(
        DataObject(
            PS_LAST_NAME='Sherman', PS_FIRST_NAME='James', PS_EMAIL='shermanjp@appstate.edu',
            PS_ORG_NAME='Appalachian Atmospheric Interdisciplinary Research Program',
            PS_ORG_ACR='AppalAIR', PS_ORG_UNIT='Department of Physics and Astronomy',
            PS_ADDR_LINE1='525 Rivers Street', PS_ADDR_LINE2=None,
            PS_ADDR_ZIP='28608', PS_ADDR_CITY='Boone',
            PS_ADDR_COUNTRY='United States of America',
            PS_ORCID=None,
        ))
    nas.metadata.originator.append(
        DataObject(
            PS_LAST_NAME=u'Parkhurst', PS_FIRST_NAME='Ethan', PS_EMAIL='parkhursted@appstate.edu',
            PS_ORG_NAME='Appalachian Atmospheric Interdisciplinary Research Program',
            PS_ORG_ACR='AppalAIR', PS_ORG_UNIT='Department of Physics and Astronomy',
            PS_ADDR_LINE1='525 Rivers Street', PS_ADDR_LINE2=None,
            PS_ADDR_ZIP='28608', PS_ADDR_CITY='Boone',
            PS_ADDR_COUNTRY='United States of America',
            PS_ORCID=None,
        ))
    nas.metadata.originator.append(
        DataObject(
            PS_LAST_NAME=u'Kitteringham', PS_FIRST_NAME='Ryan', PS_EMAIL='kitteringhamrr@appstate.edu',
            PS_ORG_NAME='Appalachian Atmospheric Interdisciplinary Research Program',
            PS_ORG_ACR='AppalAIR', PS_ORG_UNIT='Department of Physics and Astronomy',
            PS_ADDR_LINE1='525 Rivers Street', PS_ADDR_LINE2=None,
            PS_ADDR_ZIP='28608', PS_ADDR_CITY='Boone',
            PS_ADDR_COUNTRY='United States of America',
            PS_ORCID=None,
        ))

    # Data Submitters (contact for data technical issues)
    nas.metadata.submitter = []
    nas.metadata.submitter.append(
        DataObject(
            PS_LAST_NAME=u'Parkhurst', PS_FIRST_NAME='Ethan', PS_EMAIL='parkhursted@appstate.edu',
            PS_ORG_NAME='Appalachian Atmospheric Interdisciplinary Research Program',
            PS_ORG_ACR='AppalAIR', PS_ORG_UNIT='Department of Physics and Astronomy',
            PS_ADDR_LINE1='525 Rivers Street', PS_ADDR_LINE2=None,
            PS_ADDR_ZIP='28608', PS_ADDR_CITY='Boone',
            PS_ADDR_COUNTRY='United States of America',
            PS_ORCID=None,
        ))

    # Station metadata
    nas.metadata.station_code = 'NO0042G' #ASK JPS FOR STATION AND PLATFORM CODES
    nas.metadata.platform_code = 'NO0042S'
    nas.metadata.station_name = u'AppalAIR'

    nas.metadata.station_wdca_id = 'GAWANO__ZEP'
    nas.metadata.station_gaw_id = 'ZEP'
    nas.metadata.station_gaw_name = u'AppalAIR'
    # nas.metadata.station_airs_id =    # N/A
    nas.metadata.station_other_ids = '721 (NILUDB)'
    # nas.metadata.station_state_code =  # N/A
    nas.metadata.station_landuse = 'Residential'
    nas.metadata.station_setting = 'Mountain'
    nas.metadata.station_gaw_type = 'G'
    nas.metadata.station_wmo_region = 6
    nas.metadata.station_latitude = 36.212801
    nas.metadata.station_longitude = -81.692592
    nas.metadata.station_altitude = 1079.0

    # More file global metadata, but those can be overridden per variable
    # See set_variables for examples
    nas.metadata.instr_type = 'passive_puf'
    nas.metadata.lab_code = 'NO01L'
    nas.metadata.instr_name = 'puf_42'
    nas.metadata.method = 'NO01L_gc_ms'
    nas.metadata.regime = 'IMG'
    nas.metadata.matrix = 'air'
    #nas.metadata.comp_name   will be set on variable level
    #nas.metadata.unit        will be set on variable level
    nas.metadata.statistics = 'arithmetic mean'
    nas.metadata.datalevel = '2'

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
        [(datetime.datetime(2014, 1, 1, 11, 0), datetime.datetime(2014, 3, 7, 13, 22)),
         (datetime.datetime(2014, 3, 7, 13, 57), datetime.datetime(2014, 6, 12, 11, 32)),
         (datetime.datetime(2014, 6, 12, 11, 47), datetime.datetime(2014, 9, 15, 17, 3)),
         (datetime.datetime(2014, 9, 15, 17, 3), datetime.datetime(2014, 12, 15, 14, 42))]

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
    # variable 1: examples for missing values and flagging
    values = [1.22, 2.33, None, 4.55]   # missing value is None! #HERE IS WHERE WE NEED TO IMPORT CSV FILES, NEED TO GENERATE FLAGS BEFOREHAND
    flags = [[], [632, 665], [999], []]
    # [] means no flags for this measurement
    # [999] missing or invalid flag needed because of missing value (None)
    # [632, 665] multiple flags per measurement possible
    metadata = DataObject()
    metadata.comp_name = 'HCB'
    metadata.unit = 'pg/m3'
    # alternatively, you could set all metadata at once:
    # metadata = DataObject(comp_name='HCB', unit = 'pg/m3')
    nas.variables.append(DataObject(values_=values, flags=flags, flagcol=True,
                                    metadata=metadata))

    # variable 2: examples for overridden metadata, uncertainty and detection
    # limit
    values = [1.22, 2.33, 3.44, 4.55]#HERE IS WHERE WE NEED TO IMPORT CSV FILES, NEED TO GENERATE FLAGS BEFOREHAND
    flags = [[], [], [], []]
    metadata = DataObject()
    metadata.comp_name = 'benz_a_anthracene'
    metadata.unit = 'ng/m3'
    # matrix is different for this variable. Generally, you can override most
    # elements of nas.metadata on a per-variable basis by just setting the
    # according nas.variables[i].metadata element.
    metadata.matrix = 'air+aerosol'
    # additionally, we also specify uncertainty and detection limit for this
    # variable:
    metadata.detection_limit = [0.10, 'ng/m3']
    # detection limit unit must always be the same as the variable's unit!
    metadata.uncertainty = [0.12, 'ng/m3']
    # uncertainty unit is either the same as the variable's unit, ot '%' for
    # relative uncertainty:
    # metadata.uncertainty = [10.0, '%']
    nas.variables.append(DataObject(values_=values, flags=flags, flagcol=True,
                                    metadata=metadata))

    # variable 3: uncertainty will be specified for each sample (see variable 4)#HERE IS WHERE WE NEED TO IMPORT CSV FILES, NEED TO GENERATE FLAGS BEFOREHAND
    values = [1.22, 2.33, 3.44, 4.55]
    flags = [[], [], [], []]
    metadata = DataObject()
    metadata.comp_name = 'PCB_101'
    metadata.unit = 'pg/m3'
    nas.variables.append(DataObject(values_=values, flags=flags, flagcol=True,
                                    metadata=metadata))

    # variable 4: this variable contains the uncertainties for varable 3
    values = [0.22, 0.33, 0.44, 0.55]
    flags = [[], [], [], []]
    metadata = DataObject()
    metadata.comp_name = 'PCB_101'
    metadata.unit = 'pg/m3'
    # this is what makes this variable the uncetainty time series:
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
