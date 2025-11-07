# -*- coding: utf-8 -*-
"""
Configuration for ebas_genfile_ecoc_online_sunset

This file needs to be edited and adopted for each station/instrument
"""

import datetime
from nilutility.datatypes import DataObject
from ebas.io.file.nasa_ames import EbasNasaAmes

# configuration:

# all timestamps in ebas MUST be UTC. If your instrument timestamps are in
# another timezone, set the offset here.
# e.g. Instrument runs on MEZ (winter time):
#      TIMEZONE_OFFSET = datetime.timedelta(hours=-1)
TIMEZONE_OFFSET = datetime.timedelta(hours=-1)

STD_PRESURE = 101325   # standard pressure used for "Sample Volume - STP m^3"
STD_TEMPERATURE = 293.15    # standard temperature used for "Sample Volume - STP m^3"

LASER_TEMP_CORRECTION_THRESHOLD = 0.9
# values below threshold will be set to missing and flagged with 659

DENUDER_USED = False
# True / False
DENUDER_EFFICIENCY = None
# denuder efficiency [%]
# None .... unknown
# this will be used to generate a variable for "organic_carbon, Artifact=positive"
DENUDER_EFFICIENCY_UNC = None
# the uncertainty of the efficiency determination [%]
# None .... unknown
# this will be used to generate a variable for "organic_carbon, Artifact=positive, Statistics=uncertainty"

DETECTION_LIMIT_EC = 0.4  # detection limit [ug C/m3] (ambient)
DETECTION_LIMIT_OC = 0.4  # detection limit [ug C/m3] (ambient)
DETECTION_LIMIT_TC = 0.4  # detection limit [ug C/m3] (ambient)



# Metadata for NASA Ames File:

# uncertainty description, will be used as applicable for variable metadata
UNCERTAINTY_DESC = 'As calculated by instrument software.'

GLOBAL_METADATA = DataObject()

# Revision information
# set manual if another date is needed
GLOBAL_METADATA.revdate = datetime.datetime.utcnow()
GLOBAL_METADATA.revision = '1'
GLOBAL_METADATA.revdesc = 'initial revision'

# Data Originator Organisation
GLOBAL_METADATA.org = DataObject(
    OR_CODE='HU03L',
        OR_NAME='University of Szeged',
        OR_ACRONYM='SZTE',
        OR_UNIT='Optics and Quantumelectrinics Department',
        OR_ADDR_LINE1=u'Dóm square 9', OR_ADDR_LINE2=None,
        OR_ADDR_ZIP='6720', OR_ADDR_CITY='Szeged', OR_ADDR_COUNTRY='Hungary')

# Projects the data are associated to
GLOBAL_METADATA.projects = ['EMEP']

# Data Originators (PIs)
GLOBAL_METADATA.originator = []
GLOBAL_METADATA.originator.append(
    DataObject(
        PS_LAST_NAME='Ajtai', PS_FIRST_NAME='Tibor',
        PS_EMAIL='ajtai@titan.physx.u-szeged.hu',
        PS_ORG_NAME='University of Szeged',
        PS_ORG_ACR='SZTE',
        PS_ORG_UNIT='Optics and Quantumelectrinics Department',
        PS_ADDR_LINE1=u'Dóm square 9', PS_ADDR_LINE2=None,
        PS_ADDR_ZIP='6720',
        PS_ADDR_CITY='Szeged',
        PS_ADDR_COUNTRY='Hungary',
        PS_ORCID=None,
    ))

# Data Submitters (contact for data technical issues)
GLOBAL_METADATA.submitter = []
GLOBAL_METADATA.submitter.append(
    DataObject(
        PS_LAST_NAME=u'Kun Szabó', PS_FIRST_NAME='Fruzsina',
        PS_EMAIL='kszfruzsina@titan.physx.u-szeged.hu',
        PS_ORG_NAME='University of Szeged',
        PS_ORG_ACR='SZTE',
        PS_ORG_UNIT='Optics and Quantumelectrinics Department',
        PS_ADDR_LINE1=u'Dóm square 9', PS_ADDR_LINE2=None,
        PS_ADDR_ZIP='6720',
        PS_ADDR_CITY='Szeged',
        PS_ADDR_COUNTRY='Hungary',
        PS_ORCID=None,
    ))
GLOBAL_METADATA.submitter.append(
    DataObject(
        PS_LAST_NAME='Motika', PS_FIRST_NAME=u'Gábor',
        PS_EMAIL='motika.gabor@gmail.com',
        PS_ORG_NAME='University of Szeged',
        PS_ORG_ACR='SZTE',
        PS_ORG_UNIT='Optics and Quantumelectrinics Department',
        PS_ADDR_LINE1=u'Dóm square 9', PS_ADDR_LINE2=None,
        PS_ADDR_ZIP='6720',
        PS_ADDR_CITY='Szeged',
        PS_ADDR_COUNTRY='Hungary',
        PS_ORCID=None,
    ))


# Station metadata
GLOBAL_METADATA.station_code = 'HU0002R'
GLOBAL_METADATA.platform_code = 'HU0002S'
GLOBAL_METADATA.station_name = 'K-puszta'
GLOBAL_METADATA.station_wdca_id = 'GAWAHU__KPS'
GLOBAL_METADATA.station_gaw_id = 'KPS'
GLOBAL_METADATA.station_gaw_name = u'K-Puszta'
# GLOBAL_METADATA.station_airs_id =    # N/A
# GLOBAL_METADATA.station_other_ids =  # N/A
# GLOBAL_METADATA.station_state_code =  # N/A
GLOBAL_METADATA.station_landuse = 'Forest'
GLOBAL_METADATA.station_setting = 'Rural'
GLOBAL_METADATA.station_gaw_type = 'R'
GLOBAL_METADATA.station_wmo_region = 6
GLOBAL_METADATA.station_latitude = 46.966820
GLOBAL_METADATA.station_longitude = 19.545776
GLOBAL_METADATA.station_altitude = 122.0

# More file global metadata
# only for large station areas, if the instrument position is significantly different from the station position:
# GLOBAL_METADATA.mea_latitude =
# GLOBAL_METADATA.mea_longitude =
# GLOBAL_METADATA.mea_altitude =
GLOBAL_METADATA.mea_height = 4.0  # hight of the inlet [m AGL]
GLOBAL_METADATA.lab_code = 'HU03L'
GLOBAL_METADATA.instr_type = 'online_thermal-optical_analysis'
GLOBAL_METADATA.instr_name = 'SunsetLaboratoryOCEC_HU2'
GLOBAL_METADATA.instr_manufacturer = 'Sunset Laboratory'
GLOBAL_METADATA.instr_model = 'Model-4 Semi-Continuous Field Analyzer'
GLOBAL_METADATA.instr_serialno = 'RT3266'
GLOBAL_METADATA.method = 'HU03L_rtquartz'
GLOBAL_METADATA.std_method = 'TEMP=EUSAAR_2'
GLOBAL_METADATA.regime = 'IMG'
GLOBAL_METADATA.matrix = 'pm10'
#GLOBAL_METADATA.comp_name   will be set on variable level
#GLOBAL_METADATA.unit        will be set on variable level
GLOBAL_METADATA.statistics = 'arithmetic mean'  # will be overridden for some variables
GLOBAL_METADATA.datalevel = '2'

GLOBAL_METADATA.inlet_type = 'Impactor--direct'
# legal values:
# from ebas.domain.masterdata.it import EbasMasterIT
# EbasMasterIT().META.keys()
GLOBAL_METADATA.inlet_desc = 'stainless steel tube'

GLOBAL_METADATA.flow_rate = 8.0  # l/min
GLOBAL_METADATA.filter_face_velocity = 102.09  # cm/s
GLOBAL_METADATA.filter_area = 1.306  # cm2 (exposed)
# Additional information from the instrument manufacturer:
# The punch area (2.01 cm2, 16 mm diameter) includes the wall thickness of the
# quartz insert which is not subject to aerosol deposition during the
# collection. The deposit area (1.306 cm2) is internal area of the quartz
# insert, excluding the quartz wall.
GLOBAL_METADATA.filter_descr = 'Circular 16 mm diameter punches cut from WhatmanQM-A47mm'
GLOBAL_METADATA.medium = 'Quartz'

GLOBAL_METADATA.filter_prefiring = 'Prefired by previous analysis'
# legal values:
# from ebas.domain.masterdata.fp import EbasMasterFP
# EbasMasterFP().META.keys()
# Not prefired / Prefired by previous analysis
# alternatively, if prefired: (temp [K], time [h]), e.g.:
# GLOBAL_METADATA.filter_prefiring = (923.0, 8.0)

GLOBAL_METADATA.filter_conditioning = 'None'
# else use (temp [k], RH [%], time [h]), e.g.:
# GLOBAL_METADATA.filter_conditioning = (293.15, 50, 48)

GLOBAL_METADATA.sample_prep = 'None'
# legal values:
# from ebas.domain.masterdata.sp import EbasMasterSP
# EbasMasterSP().META.keys()

GLOBAL_METADATA.blank_corr = False
# legal values:
# True / False (blank corrected or not)

if DENUDER_USED:
    GLOBAL_METADATA.artifact_corr = 'Positive only'
    GLOBAL_METADATA.artifact_corr_desc = \
        'The positive artifact of OC was accounted for by placing a denuder upstream ' +\
        'of the instrument.'
    if DENUDER_EFFICIENCY is not None:
        GLOBAL_METADATA.artifact_corr_desc += ' The denuder collection efficiency is {} %.'.format(DENUDER_EFFICIENCY)
        if DENUDER_EFFICIENCY < 100:
            GLOBAL_METADATA.artifact_corr_desc += \
                ' The remaining positive artifact due to the inefficiency is reported '\
                'in a separate variable (Artifact=positive).'
    else:
        GLOBAL_METADATA.artifact_corr_desc += ' The denuder collection efficiency is unknown.'
else:
    GLOBAL_METADATA.artifact_corr = 'None'
    GLOBAL_METADATA.artifact_corr_desc = 'No denuder used.'

GLOBAL_METADATA.charring_corr = 'By laser transmission'
# legal values:
# from ebas.domain.masterdata.cc import EbasMasterCC
# EbasMasterCC().META.keys()
# None / By laser reflection / By laser transmission

GLOBAL_METADATA.hum_temp_ctrl = 'None'
# legal values:
# from ebas.domain.masterdata.ht import EbasMasterHT
# EbasMasterHT().META.keys()
GLOBAL_METADATA.hum_temp_ctrl_desc = 'filter kept at ambient conditions'

GLOBAL_METADATA.vol_std_temp = 'ambient'
# for EC/OC measurements, all measurements should be expressed as ambient.
# Please use only 'ambient' as shown here. The program converts all data to ambient conditions.

GLOBAL_METADATA.vol_std_pressure = 'ambient'
# for EC/OC measurements, all measurements should be expressed as ambient.
# Please use only 'ambient' as shown here. The program converts all data to ambient conditions.

GLOBAL_METADATA.zero_negative = 'Zero/negative possible'
# legal values:
# from ebas.domain.masterdata.zn import EbasMasterZN
# EbasMasterZN().META.keys()
# Zero possible', 'Zero/negative impossible', 'Zero/negative possible
GLOBAL_METADATA.zero_negative_desc = 'Zero and neg. values may appear due to statistical variations at very low concentrations'

GLOBAL_METADATA.acknowledgements = 'Request acknowledgement details from data originator'

GLOBAL_METADATA.timezone ='UTC'  # only UTC allowed

GLOBAL_METADATA.comment = None
# Any comments? - free text
