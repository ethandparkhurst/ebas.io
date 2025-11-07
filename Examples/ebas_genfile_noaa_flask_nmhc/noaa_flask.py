#!/usr/bin/env python
# coding: utf-8
"""
$Id$

Conversion tool for NOAA NMHC flask measurements into EBAS NASA Ames.
"""

import logging
import datetime
import math

from itertools import chain
from os.path import basename

from ebas.commandline import EbasCommandline
from ebas.domain.basic_domain_logic.time_period import estimate_period_code
from ebas.io.file.nasa_ames import EbasNasaAmes
from ebas.io.ebasmetadata import DatasetCharacteristicList
from nilutility.datatypes import DataObject
from nilutility.statistics import stddev
from nilutility.numeric import digits_stat
from fileformats.NOAA_NMHC_Flask import NOAA_NMHC_Flask, NOAA_NMHC_Flask_Error

VERSION = "0.1"

class ConversionError(Exception):
    """
    Exception class for conversion errors (main loop will generate an error and
    skip file.
    """
    pass

OUTPUTFILES = []

DEFAULT_REVISION = '1'

STATION_MAP = {
    'ABP': {
        'station_code': 'BR0002G',
        'platform_code': 'BR0002S',
        'station_name': 'Arembepe',
        'station_wdca_id': 'GAWABR__ABP',
        'station_gaw_name': 'Arembepe',
        'station_gaw_id': 'ABP',
        'station_landuse': 'Residential',
        'station_setting': 'Coastal',
        'station_gaw_type': 'G',
        'station_wmo_region': 3,
        'station_latitude': -12.7666667,
        'station_longitude': -38.1666667,
        'station_altitude': 10.0,
    },
    'ALT': {
        'station_code': 'CA0420G',
        'platform_code': 'CA0420S',
        'station_name': 'Alert',
        'station_wdca_id': 'GAWACANUALT',
        'station_gaw_name': 'Alert',
        'station_gaw_id': 'ALT',
        'station_landuse': 'Military reservation',
        'station_setting': 'Polar',
        'station_gaw_type': 'G',
        'station_wmo_region': 4,
        'station_latitude': 82.499146,
        'station_longitude': -62.341526,
        'station_altitude': 210.0,
    },
    'AMT': {
        'station_code': 'US0132R',
        'platform_code': 'US0132S',
        'station_name': 'Argyle',
        'station_wdca_id': 'GAWAUSMEAMT',
        'station_gaw_name': 'Argyle',
        'station_gaw_id': 'AMT',
        'station_landuse': 'Forest',
        'station_setting': 'Rural',
        'station_gaw_type': 'O',
        'station_wmo_region': 4,
        'station_latitude': 45.0299987793,
        'station_longitude': -68.6800003052,
        'station_altitude': 50.0,
    },
    'AMY': {
        'station_code': 'KR0100R',
        'platform_code': 'KR0100S',
        'station_name': 'Anmyeon-do',
        'station_wdca_id': 'GAWAKR__AMY',
        'station_gaw_name': 'Anmyeon-do',
        'station_gaw_id': 'AMY',
        'station_landuse': 'Agricultural',
        'station_setting': 'Coastal',
        'station_gaw_type': 'R',
        'station_wmo_region': 2,
        'station_latitude': 36.538334,
        'station_longitude': 126.330002,
        'station_altitude': 46.0,
    },
    'ASC': {
        'station_code': 'SH0001R',
        'platform_code': 'SH0001S',
        'station_name': 'Ascension Island',
        'station_wdca_id': 'GAWASH__ASC',
        'station_gaw_name': 'Ascension Island',
        'station_gaw_id': 'ASC',
        'station_landuse': 'Gravel and stone',
        'station_setting': 'Coastal',
        'station_gaw_type': 'R',
        'station_wmo_region': 1,
        'station_latitude': -7.966667,
        'station_longitude': -14.400000,
        'station_altitude': 80.0,
    },
    'ASK': {
        'station_code': 'DZ0001G',
        'platform_code': 'DZ0001S',
        'station_name': 'Assekrem',
        'station_wdca_id': 'GAWADA__ASK',
        'station_gaw_name': 'Assekrem',
        'station_gaw_id': 'ASK',
        'station_landuse': 'Desert',
        'station_setting': 'Mountain',
        'station_gaw_type': 'G',
        'station_wmo_region': 1,
        'station_latitude': 23.266670,
        'station_longitude': 5.633330,
        'station_altitude': 2710.0,
    },
    'AZR': {
        'station_code': 'PT0015R',
        'platform_code': 'PT0015S',
        'station_name': 'Serreta (Terceira)',
        'station_wdca_id': 'GAWAPT__AZR',
        'station_gaw_name': 'Serreta (Terceira)',
        'station_gaw_id': 'AZR',
        'station_landuse': 'Forest',
        'station_setting': 'Coastal',
        'station_gaw_type': 'R',
        'station_wmo_region': 6,
        'station_latitude': 38.7700004578,
        'station_longitude': -27.3799991608,
        'station_altitude': 40.0,
    },
    'BAL': {
        'station_code': 'PL0011R',
        'platform_code': 'PL0011M',
        'station_name': 'Baltic Sea',
        'station_wdca_id': None,
        'station_gaw_name': 'Baltic Sea',
        'station_gaw_id': 'BAL',
        'station_landuse': 'Other',
        'station_setting': 'Coastal',
        'station_gaw_type': 'R',
        'station_wmo_region': 6,
        'station_latitude': 55.35,
        'station_longitude': 17.21,
        'station_altitude': 3.0,
    },
    'BKT': {
        'station_code': 'ID1013R',
        'platform_code': 'ID1013S',
        'station_name': 'Bukit Kototabang',
        'station_wdca_id': 'GAWAID__BKT',
        'station_gaw_name': 'Bukit Kototabang',
        'station_gaw_id': 'BKT',
        'station_landuse': 'Forest',
        'station_setting': 'Mountain',
        'station_gaw_type': 'G',
        'station_wmo_region': 5,
        'station_latitude': -0.201940,
        'station_longitude': 100.318100,
        'station_altitude': 864.0,
    },
    'USH': {
        'station_code': 'AR0002G',
        'platform_code': 'AR0002S',
        'station_name': 'Ushuaia',
        'station_wdca_id': 'GAWAAR__USH',
        'station_gaw_name': 'Ushuaia',
        'station_gaw_id': 'USH',
        'station_landuse': 'Airport',
        'station_setting': 'Coastal',
        'station_gaw_type': 'G',
        'station_wmo_region': 3,
        'station_latitude': -54.848464965799998,
        'station_longitude': -68.310691833500002,
        'station_altitude': 18.0,
    },
    'CGO': {
        'station_code': 'AU0002G',
        'platform_code': 'AU0002S',
        'station_name': 'Cape Grim',
        'station_wdca_id': 'GAWAMX__CGO',
        'station_gaw_name': 'Cape Grim',
        'station_gaw_id': 'CGO',
        'station_landuse': 'Grassland',
        'station_setting': 'Coastal',
        'station_gaw_type': 'G',
        'station_wmo_region': 5,
        'station_latitude': -40.682220000000001,
        'station_longitude': 144.68834000000001,
        'station_altitude': 94.0,
    },
    'RPB': {
        'station_code': 'BB0001R',
        'platform_code': 'BB0001S',
        'station_name': 'Ragged Point',
        'station_wdca_id': 'GAWABB__RPB',
        'station_gaw_name': 'Ragged Point',
        'station_gaw_id': 'RPB',
        'station_landuse': 'Residential',
        'station_setting': 'Coastal',
        'station_gaw_type': 'R',
        'station_wmo_region': 4,
        'station_latitude': 13.164999999999999,
        'station_longitude': -59.432000000000002,
        'station_altitude': 15.0,
    },
    'BMW': {
        'station_code': 'BM0001R',
        'platform_code': 'BM0001S',
        'station_name': 'Tudor Hill (Bermuda)',
        'station_wdca_id': 'GAWAGB__BMW',
        'station_gaw_name': 'Tudor Hill (Bermuda)',
        'station_gaw_id': 'BMW',
        'station_landuse': 'Residential',
        'station_setting': 'Coastal',
        'station_gaw_type': 'R',
        'station_wmo_region': 4,
        'station_latitude': 32.264699999999998,
        'station_longitude': -64.878799999999998,
        'station_altitude': 30.0,
    },
    'NAT': {
        'station_code': 'BR0003U',
        'platform_code': 'BR0003S',
        'station_name': 'Natal',
        'station_wdca_id': 'GAWABR__NAT',
        'station_gaw_name': 'Natal',
        'station_gaw_id': 'NAT',
        'station_landuse': 'Residential',
        'station_setting': 'Coastal',
        'station_gaw_type': 'R',
        'station_wmo_region': 3,
        'station_latitude': -5.7952000000000004,
        'station_longitude': -35.185299999999998,
        'station_altitude': 50.0,
    },
    'LLB': {
        'station_code': 'CA0108R',
        'platform_code': 'CA0108S',
        'station_name': 'Lac La Biche (Alberta)',
        'station_wdca_id': 'GAWACAALLLB',
        'station_gaw_name': 'Lac La Biche (Alberta)',
        'station_gaw_id': 'LLB',
        'station_landuse': 'Forest',
        'station_setting': 'Rural',
        'station_gaw_type': 'R',
        'station_wmo_region': 4,
        'station_latitude': 54.953809,
        'station_longitude': -112.466649,
        'station_altitude': 548.0,
    },
    'EIC': {
        'station_code': 'CL0002R',
        'platform_code': 'CL0002S',
        'station_name': 'Easter Island',
        'station_wdca_id': 'GAWAMX__EIC',
        'station_gaw_name': 'Easter Island',
        'station_gaw_id': 'EIC',
        'station_landuse': 'Airport',
        'station_setting': 'Coastal',
        'station_gaw_type': 'R',
        'station_wmo_region': 3,
        'station_latitude': -27.159700000000001,
        'station_longitude': -109.4284,
        'station_altitude': 47.0,
    },
    'HPB': {
        'station_code': 'DE0043G',
        'platform_code': 'DE0043S',
        'station_name': 'Hohenpeissenberg',
        'station_wdca_id': 'GAWADE__HPB',
        'station_gaw_name': 'Hohenpeissenberg',
        'station_gaw_id': 'HPB',
        'station_landuse': 'Grassland',
        'station_setting': 'Mountain',
        'station_gaw_type': 'G',
        'station_wmo_region': 6,
        'station_latitude': 47.801498413099999,
        'station_longitude': 11.009619000000001,
        'station_altitude': 975.0,
    },
    'OXK': {
        'station_code': 'DE0076R',
        'platform_code': 'DE0076S',
        'station_name': 'Ochsenkopf',
        'station_wdca_id': 'GAWADE__OXK',
        'station_gaw_name': 'Ochsenkopf',
        'station_gaw_id': 'OXK',
        'station_landuse': 'Forest',
        'station_setting': 'Mountain',
        'station_gaw_type': 'C',
        'station_wmo_region': 6,
        'station_latitude': 50.030099999999997,
        'station_longitude': 11.808400000000001,
        'station_altitude': 1020.0,
    },
    'SUM': {
        'station_code': 'DK0025G',
        'platform_code': 'DK0025S',
        'station_name': 'Summit',
        'station_wdca_id': 'GAWADK__SUM',
        'station_gaw_name': 'Summit',
        'station_gaw_id': 'SUM',
        'station_landuse': 'Snowfield',
        'station_setting': 'Polar',
        'station_gaw_type': 'G',
        'station_wmo_region': 6,
        'station_latitude': 72.580001831100006,
        'station_longitude': -38.479999542199998,
        'station_altitude': 3238.0,
    },
    'IZO': {
        'station_code': 'ES0018G',
        'platform_code': 'ES0018S',
        'station_name': 'Izana',
        'station_wdca_id': 'GAWAES__IZO',
        'station_gaw_name': 'Izaña (Tenerife)',
        'station_gaw_id': 'IZO',
        'station_landuse': 'Gravel and stone',
        'station_setting': 'Mountain',
        'station_gaw_type': 'G',
        'station_wmo_region': 1,
        'station_latitude': 28.309000000000001,
        'station_longitude': -16.499400000000001,
        'station_altitude': 2373.0,
    },
    'PAL': {
        'station_code': 'FI0096G',
        'platform_code': 'FI0096S',
        'station_name': 'Pallas (Sammaltunturi)',
        'station_wdca_id': 'GAWAFI__PAL',
        'station_gaw_name': 'Pallas',
        'station_gaw_id': 'PAL',
        'station_landuse': 'Forest',
        'station_setting': 'Rural',
        'station_gaw_type': 'G',
        'station_wmo_region': 6,
        'station_latitude': 67.973333332999999,
        'station_longitude': 24.116111110999999,
        'station_altitude': 565.0,
    },
    'CRZ': {
        'station_code': 'FR0040G',
        'platform_code': 'FR0040S',
        'station_name': 'Crozet',
        'station_wdca_id': 'GAWAMX__CRZ',
        'station_gaw_name': 'Crozet',
        'station_gaw_id': 'CRZ',
        'station_landuse': 'Gravel and stone',
        'station_setting': 'Coastal',
        'station_gaw_type': 'R',
        'station_wmo_region': 1,
        'station_latitude': -46.432487000000002,
        'station_longitude': 51.857776000000001,
        'station_altitude': 120.0,
    },
    'HBA': {
        'station_code': 'GB0059G',
        'platform_code': 'GB0059S',
        'station_name': 'Halley',
        'station_wdca_id': 'GAWAGB__HBA',
        'station_gaw_name': 'Halley',
        'station_gaw_id': 'HBA',
        'station_landuse': 'Snowfield',
        'station_setting': 'Polar',
        'station_gaw_type': 'G',
        'station_wmo_region': 7,
        'station_latitude': -75.605000000000004,
        'station_longitude': -26.210000000000001,
        'station_altitude': 30.0,
    },
    'MHD': {
        'station_code': 'IE0031R',
        'platform_code': 'IE0031S',
        'station_name': 'Mace Head',
        'station_wdca_id': 'GAWAIE__MHD',
        'station_gaw_name': 'Mace Head',
        'station_gaw_id': 'MHD',
        'station_landuse': 'Grassland',
        'station_setting': 'Coastal',
        'station_gaw_type': 'G',
        'station_wmo_region': 6,
        'station_latitude': 53.325830000000003,
        'station_longitude': -9.8994400000000002,
        'station_altitude': 5.0,
    },
    'ICE': {
        'station_code': 'IS0091R',
        'platform_code': 'IS0091S',
        'station_name': 'Storhofdi',
        'station_wdca_id': 'GAWAIS__ICE',
        'station_gaw_name': 'Storhofdi',
        'station_gaw_id': 'ICE',
        'station_landuse': 'Grassland',
        'station_setting': 'Coastal',
        'station_gaw_type': 'R',
        'station_wmo_region': 6,
        'station_latitude': 63.399799999999999,
        'station_longitude': -20.288399999999999,
        'station_altitude': 118.0,
    },
    'SYO': {
        'station_code': 'JP0002G',
        'platform_code': 'JP0002S',
        'station_name': 'Syowa',
        'station_wdca_id': 'GAWAJP__SYO',
        'station_gaw_name': 'Syowa',
        'station_gaw_id': 'SYO',
        'station_landuse': 'Snowfield',
        'station_setting': 'Polar',
        'station_gaw_type': 'R',
        'station_wmo_region': 7,
        'station_latitude': -69.004999999999995,
        'station_longitude': 39.590555555999998,
        'station_altitude': 16.0,
    },
    'MKN': {
        'station_code': 'KE0001G',
        'platform_code': 'KE0001S',
        'station_name': 'Mt. Kenya',
        'station_wdca_id': 'GAWAKE__MKN',
        'station_gaw_name': 'Mt. Kenya',
        'station_gaw_id': 'MKN',
        'station_landuse': 'Grassland',
        'station_setting': 'Mountain',
        'station_gaw_type': 'G',
        'station_wmo_region': 1,
        'station_latitude': -0.062199999999999998,
        'station_longitude': 37.297199999999997,
        'station_altitude': 3678.0,
    },
    'TAP': {
        'station_code': 'KR0002R',
        'platform_code': 'KR0002S',
        'station_name': 'Tae-ahn Peninsula',
        'station_wdca_id': 'GAWAKR__TAP',
        'station_gaw_name': 'Tae-ahn Peninsula',
        'station_gaw_id': 'TAP',
        'station_landuse': 'Forest',
        'station_setting': 'Coastal',
        'station_gaw_type': 'R',
        'station_wmo_region': 2,
        'station_latitude': 36.736832999999997,
        'station_longitude': 126.132722,
        'station_altitude': 16.0,
    },
    'MEX': {
        'station_code': 'MX0001R',
        'platform_code': 'MX0001S',
        'station_name': 'High Altitude Global Climate Observation Center',
        'station_wdca_id': 'GAWAMX__MEX',
        'station_gaw_name': 'Mex High Altitude Global Climate Observation Center',
        'station_gaw_id': 'MEX',
        'station_landuse': 'Gravel and stone',
        'station_setting': 'Mountain',
        'station_gaw_type': 'O',
        'station_wmo_region': 4,
        'station_latitude': 18.985842000000002,
        'station_longitude': -97.314432999999994,
        'station_altitude': 4560.0,
    },
    'BSC': {
        'station_code': 'RO0009U',
        'platform_code': 'RO0009S',
        'station_name': 'Constanta (Black Sea)',
        'station_wdca_id': '',
        'station_gaw_name': 'Constanta (Black Sea)',
        'station_gaw_id': 'BSC',
        'station_landuse': 'Urban park',
        'station_setting' : 'Coastal',
        'station_gaw_type': 'R',
        'station_wmo_region': 6,
        'station_latitude': 44.177599999999998,
        'station_longitude': 28.6647,
        'station_altitude': 3.0,
    },
    'TIK': {
        'station_code': 'RU0100R',
        'platform_code': 'RU0100S',
        'station_name': 'Tiksi',
        'station_wdca_id': 'GAWARU__TIK',
        'station_gaw_name': 'Tiksi',
        'station_gaw_id': 'TIK',
        'station_landuse': 'Grassland',
        'station_setting': 'Coastal',
        'station_gaw_type': 'R',
        'station_wmo_region': 2,
        'station_latitude': 71.586166381799998,
        'station_longitude': 128.91882324220001,
        'station_altitude': 8.0,
    },
    'SEY': {
        'station_code': 'SC0001R',
        'platform_code': 'SC0001S',
        'station_name': 'Mahé',
        'station_wdca_id': 'GAWASC__SEY',
        'station_gaw_name': 'Mahé',
        'station_gaw_id': 'SEY',
        'station_landuse': 'Airport',
        'station_setting': 'Coastal',
        'station_gaw_type': 'R',
        'station_wmo_region': 1,
        'station_latitude': -4.6824000000000003,
        'station_longitude': 55.532499999999999,
        'station_altitude': 3.0,
    },
    'CBA': {
        'station_code': 'US0133R',
        'platform_code': 'US0133S',
        'station_name': 'Cold Bay',
        'station_wdca_id': 'GAWAUS__CBA',
        'station_gaw_name': 'Cold Bay (AK)',
        'station_gaw_id': 'CBA',
        'station_landuse': 'Airport',
        'station_setting': 'Coastal',
        'station_gaw_type': 'R',
        'station_wmo_region': 4,
        'station_latitude': 55.210000000000001,
        'station_longitude': -162.72,
        'station_altitude': 25.0,
    },
    'GMI': {
        'station_code': 'US0134R',
        'platform_code': 'US0134S',
        'station_name': 'Guam (Mariana Island)',
        'station_wdca_id': 'GAWAUS__GMI',
        'station_gaw_name': 'Guam (Mariana Island)',
        'station_gaw_id': 'GMI',
        'station_landuse': 'Residential',
        'station_setting': 'Coastal',
        'station_gaw_type': 'R',
        'station_wmo_region': 5,
        'station_latitude': 13.430338000000001,
        'station_longitude': 144.801051,
        'station_altitude': 2.0,
    },
    'KEY': {
        'station_code': 'US0135R',
        'platform_code': 'US0135S',
        'station_name': 'Key Biscayne',
        'station_wdca_id': 'GAWAUSFLKEY',
        'station_gaw_name': 'Key Biscane (FL)',
        'station_gaw_id': 'KEY',
        'station_landuse': 'Urban park',
        'station_setting': 'Coastal',
        'station_gaw_type': 'R',
        'station_wmo_region': 4,
        'station_latitude': 25.665400000000002,
        'station_longitude': -80.158000000000001,
        'station_altitude': 1.0,
    },
    'KUM': {
        'station_code': 'US0136G',
        'platform_code': 'US0136S',
        'station_name': 'Cape Kumukahi',
        'station_wdca_id': 'GAWAUSHIKUM',
        'station_gaw_name': 'Cape Kumukahi (HI)',
        'station_gaw_id': 'KUM',
        'station_landuse': 'Gravel and stone',
        'station_setting': 'Coastal',
        'station_gaw_type': 'R',
        'station_wmo_region': 5,
        'station_latitude': 19.516199,
        'station_longitude': -154.810857,
        'station_altitude': 3.0,
    },
    'LEF': {
        'station_code': 'US0137R',
        'platform_code': 'US0137S',
        'station_name': 'Park Falls',
        'station_wdca_id': 'GAWAUSWILEF',
        'station_gaw_name': 'Park Falls (WI)',
        'station_gaw_id': 'LEF',
        'station_landuse': 'Forest',
        'station_setting': 'Rural','station_gaw_type': 'R',
        'station_wmo_region': 4,
        'station_latitude': 45.945099999999996,
        'station_longitude': -90.273200000000003,
        'station_altitude': 472.0,
    },
    'MID': {
        'station_code': 'US0138G',
        'platform_code': 'US0138S',
        'station_name': 'Sand Island',
        'station_wdca_id': 'GAWAUS__MID',
        'station_gaw_name': 'Sand Island',
        'station_gaw_id': 'MID',
        'station_landuse': 'Airport',
        'station_setting': 'Coastal',
        'station_gaw_type': 'R',
        'station_wmo_region': 5,
        'station_latitude': 28.210000000000001,
        'station_longitude': -177.38,
        'station_altitude': 3.0,
    },
    'PSA': {
        'station_code': 'US0139G',
        'platform_code': 'US0139S',
        'station_name': 'Palmer Station',
        'station_wdca_id': 'GAWAUS__PSA',
        'station_gaw_name': 'Palmer Station',
        'station_gaw_id': 'PSA',
        'station_landuse': 'Snowfield',
        'station_setting': 'Polar',
        'station_gaw_type': 'R',
        'station_wmo_region': 7,
        'station_latitude': -64.774330139200003,
        'station_longitude': -64.054420471200004,
        'station_altitude': 10.0,
    },
    'SHM': {
        'station_code': 'US0140G',
        'platform_code': 'US0140S',
        'station_name': 'Shemya Island',
        'station_wdca_id': 'GAWAUSAKSHM',
        'station_gaw_name': 'Shemya Island',
        'station_gaw_id': 'SHM',
        'station_landuse': 'Grassland',
        'station_setting': 'Coastal',
        'station_gaw_type': 'R',
        'station_wmo_region': 4,
        'station_latitude': 52.711199999999998,
        'station_longitude': 174.126,
        'station_altitude': 23.0,
    },
    'UTA': {
        'station_code': 'US0141R',
        'platform_code': 'US0141S',
        'station_name': 'Wendover',
        'station_wdca_id': 'GAWAUSUTUTA',
        'station_gaw_name': 'Wendover (UT)',
        'station_gaw_id': 'UTA',
        'station_landuse': 'Desert',
        'station_setting': 'Rural',
        'station_gaw_type': 'R',
        'station_wmo_region': 4,
        'station_latitude': 39.901800000000001,
        'station_longitude': -113.71810000000001,
        'station_altitude': 1327.0,
    },
    'MLO': {
        'station_code': 'US1200R',
        'platform_code': 'US1200S',
        'station_name': 'Mauna Loa',
        'station_wdca_id': 'GAWAUSHIMLO',
        'station_gaw_name': 'Mauna Loa (HI)',
        'station_gaw_id': 'MLO',
        'station_landuse': 'Gravel and stone',
        'station_setting': 'Mountain',
        'station_gaw_type': 'G',
        'station_wmo_region': 5,
        'station_latitude': 19.536230087300002,
        'station_longitude': -155.5761566162,
        'station_altitude': 3397.0,
    },
    'SMO': {
        'station_code': 'US6001R',
        'platform_code': 'US6001S',
        'station_name': 'Samoa (Cape Matatula)',
        'station_wdca_id': 'GAWAUS__SMO',
        'station_gaw_name': 'Samoa (Cape Matatula)',
        'station_gaw_id': 'SMO',
        'station_landuse': 'Residential',
        'station_setting': 'Coastal',
        'station_gaw_type': 'G',
        'station_wmo_region': 5,
        'station_latitude': -14.247474670400001,
        'station_longitude': -170.56451416019999,
        'station_altitude': 77.0,
    },
    'SGP': {
        'station_code': 'US6002C',
        'platform_code': 'US6002S',
        'station_name': 'Southern Great Plains E13',
        'station_wdca_id': 'GAWAUSOKSGP',
        'station_gaw_name': 'Southern Great Plains E13 (OK)',
        'station_gaw_id': 'SGP',
        'station_landuse': 'Agricultural',
        'station_setting': 'Rural',
        'station_gaw_type': 'C',
        'station_wmo_region': 4,
        'station_latitude': 36.604999999999997,
        'station_longitude': -97.484999000000002,
        'station_altitude': 318.0,
    },
    'SPO': {
        'station_code': 'US6004G',
        'platform_code': 'US6004S',
        'station_name': 'South Pole',
        'station_wdca_id': 'GAWAUS__SPO',
        'station_gaw_name': 'South Pole',
        'station_gaw_id': 'SPO',
        'station_landuse': 'Snowfield',
        'station_setting': 'Polar',
        'station_gaw_type': 'G',
        'station_wmo_region': 7,
        'station_latitude': -89.996948242200006,
        'station_longitude': -24.7999992371,
        'station_altitude': 2841.0,
    },
    'THD': {
        'station_code': 'US6005G',
        'platform_code': 'US6005S',
        'station_name': 'Trinidad Head',
        'station_wdca_id': 'GAWAUSCATHD',
        'station_gaw_name': 'Trinidad Head (CA)',
        'station_gaw_id': 'THD',
        'station_landuse': 'Residential',
        'station_setting': 'Coastal',
        'station_gaw_type': 'G',
        'station_wmo_region': 4,
        'station_latitude': 41.054100036599998,
        'station_longitude': -124.1510009766,
        'station_altitude': 107.0,
    },
    'CPT': {
        'station_code': 'ZA0001G',
        'platform_code': 'ZA0001S',
        'station_name': 'Cape Point',
        'station_wdca_id': 'GAWAMX__CPT',
        'station_gaw_name': 'Cape Point',
        'station_gaw_id': 'CPT',
        'station_landuse': 'Grassland',
        'station_setting': 'Coastal',
        'station_gaw_type': 'G',
        'station_wmo_region': 1,
        'station_latitude': -34.353479999999998,
        'station_longitude': 18.48968,
        'station_altitude': 230.0,
    },
    'ZEP': {
        'station_code': 'NO0042G',
        'platform_code': 'NO0042S',
        'station_name': 'Zeppelin mountain (Ny-Ålesund)',
        'station_wdca_id': 'GAWANO__ZEP',
        'station_gaw_name': 'Zeppelin Mountain (Ny Ålesund)',
        'station_gaw_id': 'ZEP',
        'station_landuse': 'Gravel and stone',
        'station_setting': 'Polar',
        'station_gaw_type': 'G',
        'station_wmo_region': 6,
        'station_latitude': 78.90715,
        'station_longitude': 11.88668,
        'station_altitude': 474.0,
    },
    'BRW':{
        'station_code': 'US0008R',
        'platform_code': 'US0008S',
        'station_name': 'Barrow',
        'station_wdca_id': 'GAWAUSAKBRW',
        'station_gaw_name': 'Barrow (AK)',
        'station_gaw_id': 'BRW',
        'station_landuse': 'Wetland',
        'station_setting': 'Polar',
        'station_gaw_type': 'G',
        'station_wmo_region': 4,
        'station_latitude': 71.323013,
        'station_longitude': -156.611465,
        'station_altitude': 11.0,
    },
}

PARAMETER_MAP = {

    # Ethane:
    'C2H6': {
        'regime': 'IMG',
        'matrix': 'air',
        'comp_name': 'ethane',
        'unit': 'pmol/mol',
        'DL': 5.0,
        },
    # Propane:
    'C3H8': {
        'regime': 'IMG',
        'matrix': 'air',
        'comp_name': 'propane',
        'unit': 'pmol/mol',
        'DL': 4.0,
        },
# 2020-08: do not convert isoprene yet, QA not finished
#    'C5H8': {
#        'regime': 'IMG',
#        'matrix': 'air',
#        'comp_name': 'isoprene',
#        'unit': 'pmol/mol'
#        },
    # n-butane:
    'nC4H10': {
        'regime': 'IMG',
        'matrix': 'air',
        'comp_name': 'n-butane',
        'unit': 'pmol/mol',
        'DL': 3.0,
        },
    # i-butane:
    'iC4H10': {
        'regime': 'IMG',
        'matrix': 'air',
        'comp_name': '2-methylpropane',
        'unit': 'pmol/mol',
        'DL': 3.0,
        },
    # n-pentane:
    'nC5H12': {
        'regime': 'IMG',
        'matrix': 'air',
        'comp_name': 'n-pentane',
        'unit': 'pmol/mol',
        'DL': 2.0,
        },
    # i-pentane:
    'iC5H12': {
        'regime': 'IMG',
        'matrix': 'air',
        'comp_name': '2-methylbutane',
        'unit': 'pmol/mol',
        'DL': 2.0,
        },
    }

SUBMITTER_MAP = {
    ('Detlev Helmig', 'Detlev.Helmig@colorado.edu'):
        DataObject(
            PS_LAST_NAME='Helmig', PS_FIRST_NAME='Detlev',
            PS_EMAIL='Detlev.Helmig@colorado.edu',
            PS_ORG_NAME='University of Colorado - INSTAAR',
            PS_ORG_ACR='INSTAAR',
            PS_ORG_UNIT='Institute of Arctic and Alpine Research',
            PS_ADDR_LINE1='4001 Discovery Drive', PS_ADDR_LINE2=None,
            PS_ADDR_ZIP='CO 80303', PS_ADDR_CITY='Boulder',
            PS_ADDR_COUNTRY='USA',
            PS_ORCID='0000-0003-1612-1651'),
    ('John Mund', 'John.Mund@noaa.gov'):
        DataObject(
            PS_LAST_NAME='Mund', PS_FIRST_NAME='John',
            PS_EMAIL='John.Mund@noaa.gov',
            PS_ORG_NAME='National Oceanic and Atmospheric Administration',
            PS_ORG_ACR='NOAA GML',
            PS_ORG_UNIT='Global Monitoring Laboratory',
            PS_ADDR_LINE1='325 Broadway R/GML', PS_ADDR_LINE2=None,
            PS_ADDR_ZIP='80305-3328', PS_ADDR_CITY='Boulder',
            PS_ADDR_COUNTRY='USA',
            PS_ORCID=None),
    }

ANA_MAP = {
    ('ARL', 'v1'):
        {
            'ana_technique': 'GC-FID',
            'ana_lab_code': 'US13L',
            'ana_instr_name': 'GC_FID_v1',
            'ana_instr_manufacturer': 'Hewlett Packard',
            'ana_instr_model': 'HP-5890 series II',
            'ana_instr_serialno': None,
        }
    }

# TO BE CLARIFIED:
# Hardcoded resolution code. Could be calculated according to the resolution in
# the data, but be aware that resolution code is an identifying metadata
# element. That means, several submissions of data (consecutive years) will
# only be stored as the same dataset if the resolution code is the same for all
# submissions!
# That might be a problem for time series with varying resolution code
# (sometimes 1 week, sometimes 2 weeks, ...).
# For now, we use a fixed resolution code 1w, hope this is appropriate for all
# measurements.
RESOLUTION_CODE = '1w'

# TO BE CLEARIFIED:
# How long does it take to fill the flask?
SAMPLE_DURATION = '1mn'
SAMPLE_DURATION_DT = datetime.timedelta(minutes=1)


def add_private_args(parser, ebascmdline):  # @UnusedVariable
    # pylint: disable=W0613
    # W0613 Unused argument
    """
    Callback function for commandline.getargs(). Adds private commandline
    arguments.

    Parameters:
        parser       root parser object from commandline.getargs()
        ebascmdline  ebas commandline object
    Returns:
        None
    """
    parser_input_group = parser.add_argument_group('input options')
    parser_input_group.add_argument(
        'filenames', nargs='*',
        help='input file(s), NOAA NMHC flask file format')
    parser_output_group = parser.add_argument_group('output options')
    parser_output_group.add_argument(
        '--revision', default=DEFAULT_REVISION,
        help='data revision to be set in output files.')

def haversine_dist(pos1, pos2, unit='nm'):
    """
    Haversine great circle distance between two points.
    Parameters:
        pos1, pos2   the two position, each (lat, lon)
        unit         result unit ('km', 'nm')
    Returns:
        distance
    Raises:
        ValueError  on unsupported unit
    """
    r_nm = 180*60/math.pi
    unit_factors = {
        "nm": 1,
        "km": 1.852,
        "m": 1852,
    }
    try:
        rad = r_nm * unit_factors[unit]
    except KeyError:
        raise ValueError("unsupported unit '{}'".format(unit))
    lat1, lon1, lat2, lon2 = [math.radians(x) for x in list(pos1) + list(pos2)]
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a__ = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * \
        math.sin(dlon/2)**2
    c__ = 2 * math.asin(math.sqrt(a__))
    return c__ * rad

def get_output_file(series):
    """
    Find a file to be used for output. Basically groups all data from one
    station wit the same measurement intervals and the sae analytical metadata
    in one file.
    Handles errors due to changing metadata.
    Parameteres:
        series    the time series data from the NOAA file
    Returns:
        EbasNasaAmes file object or
        None if none is fitting
    Raises (sub methods):
        ConversionError on any conversion/mapping issue
    """
    # ...
    for fil in OUTPUTFILES:
        ebas_station = get_station(series)
        ebas_analytical = get_analytical(series)
        if fil.metadata.station_code == ebas_station['station_code'] and \
           fil.metadata.ana_technique == ebas_analytical['ana_technique'] and \
           fil.metadata.ana_lab_code == ebas_analytical['ana_lab_code'] and \
           fil.metadata.ana_instr_name == \
               ebas_analytical['ana_instr_name'] and \
           fil.sample_times == get_sample_times(series):
            return fil
    return None

def get_station(series):
    """
    Get the ebas station metadata for a given NOAA timeseries.
    Handles errors due to changing metadata.
    Parameteres:
        series    the time series data from the NOAA file
    Returns:
        ebas station metdata (dict)
    Raises:
        ConversionError on any conversion/mapping issue
    """
    # the data object already makes sure that all rows in the series have the
    # same site code, lat, lon and alt, so it's safe to use element [0]
    try:
        ebas_station = STATION_MAP[series.sample_site_code[0]]
    except KeyError:
        raise ConversionError(
            "Undefined station code '{}', please add station to STATION_MAP"
            .format(series.sample_site_code[0]))
    dist = haversine_dist(
        (ebas_station['station_latitude'], ebas_station['station_longitude']),
       (series.sample_latitude[0], series.sample_longitude[0]), "m")
    if dist > 3000:
        raise ConversionError(
            "Station '{}', EBAS station code '{}': position is {} m appart"
            .format(series.sample_site_code[0], ebas_station['station_name'],
                    dist))
    dist = abs(ebas_station['station_altitude'] - series.sample_elevation[0])
    if dist > 20:
        raise ConversionError(
            "Station '{}', EBAS station code '{}': elevation is {} m appart"
            .format(series.sample_site_code[0], ebas_station['station_name'],
                    dist))
    return ebas_station

def get_analytical(series):
    """
    Get the ebas analytical metadata for a given NOAA timeseries.
    Handles errors due to changing metadata.
    Parameteres:
        series    the time series data from the NOAA file
    Returns:
        ebas analytical metdata (dict)
    Raises:
        ConversionError on any conversion/mapping issue
    """
    # the data object already makes sure that all rows in the series have the
    # same analysis_group_abbr and analysis_instrument, so it's safe to use
    # element [0]
    try:
        return ANA_MAP[(series.analysis_group_abbr[0],
                        series.analysis_instrument[0])]
    except KeyError:
        raise ConversionError(
            "Undefined analysis group / analysis instrument '{} / {}', please "
            "add to ANA_MAP".format(series.analysis_group_abbr[0],
                                    series.analysis_instrument[0]))

def get_parameter(series):
    """
    Get the ebas parameter metadata for a given NOAA timeseries.
    Handles errors due to changing metadata.
    Parameteres:
        series    the time series data from the NOAA file
    Returns:
        ebas parameter metdata (dict)
    Raises:
        ConversionError on any conversion/mapping issue
    """
    # the data object already makes sure that all rows in the series have the
    # same parameter_formula, so it's safe to use element [0]
    try:
        return PARAMETER_MAP[series.parameter_formula[0]]
    except KeyError:
        raise ConversionError(
            "Undefined paramater '{}', please add parameter to "
            "PARAMETER_MAP".format(series.parameter_formula[0]))

def get_sample_times(series):
    """
    Get the ebas sample time list, each [start, end].
    Parameteres:
        series    the time series data from the NOAA file
    Returns:
        ebas sample times (list of lists)
    """
    return [[timestamp, timestamp + SAMPLE_DURATION_DT]
            for timestamp in series.sample_time]

def convert_data(series, lod):
    """
    Convert all data from one series.
    Parameters:
        series   NOAA_NMHC_Flask_Data_Aggregated object (data from input file)
        lod      limit of detection for the parameter
    Returns:
        (values, flags, stddevs, stdflags, sample_counts, scntflags), all lists
    """
    values = []
    flags = []
    stddevs = []
    stdflags = []
    sample_counts = []
    scntflags = []
    mindig = digits_stat(list(chain(*series.analysis_value)))[2]
    if mindig is None:
        rounding = 0
    else:
        rounding = mindig * (-1)
    if rounding < 0:
        rounding += 1
    for i in range(len(series.analysis_flag)):
        # Loop through groups of data with the same timestamp each
        # Analyse the flags and vlaues for this timestamp:
        qual, flg = analyse_flags(
            series.analysis_value[i], series.analysis_flag[i],
            series._line_numbers[i], lod)
        maxqual = max(qual)
        # Find the highest class of quality
        if maxqual == 1:
            # Lowest quality: no aggregation, set missing!
            values.append(None)
            stddevs.append(None)
            stdflags.append([899])
            sample_counts.append(0)
            scntflags.append([0])  ## so far, we need no flags for sample counts
        else:
            # Quality 2 and 3: average all values from this class
            sample_counts.append(len([x for x in qual if x == maxqual]))
            scntflags.append([0])  ## so far, we need no flags for sample counts
            values.append(round(sum(
                [series.analysis_value[i][j]
                 for j in range(len(qual))
                 if qual[j] == maxqual])/float(sample_counts[-1]), rounding))
            std = stddev(
                [series.analysis_value[i][j]
                 for j in range(len(qual))
                 if qual[j] == maxqual])
            if std is None:
                stdflags.append([899])
            else:
                stdflags.append([])
                std = round(std, rounding)
            stddevs.append(std)
        flags.append(list(set(chain(
            *[flg[j]
              for j in range(len(qual))
              if qual[j] == maxqual]))))
    return values, flags, stddevs, stdflags, sample_counts, scntflags

def analyse_flags(analysis_values, analysis_flags, line_numbers, lod):
    """
    Evaluates the original flag values and decides which priority the respective
    value has for aggregating.
    Parameters:
        analysis_values     the measurement values for one sample time
        analysis_flags      the flag information for one sample time
    Returns:
        (qual, flags), both lists

        qual:    quality indicator
                  3: fully valid, prefered for aggregation
                  2: valid with quality issues,
                     use for aggregation if no qual 3 is available
                  1: invalid, never use for aggregation
        propflag the flag information that should be propagated in aggregations.
    """
    logger = logging.getLogger('NOAAFlaskConvert')
    quals = []
    flags = []
    for i in range(len(analysis_flags)):
        if analysis_flags[i] == '...':
            if analysis_values[i] is None:
                raise ConversionError("data line {}: no flags, no data reported"
                                      .format(i+1))
            # no flags, existing value: all green
            flags.append([])
            quals.append(3)
            continue
        flag = []
        qual = set([3])
        # REJECTION FLAG: 1st character
        if analysis_flags[i][0] == 'P':
            # P: inconsistency between two flasks
            flag.append(499)
            if analysis_values[i] is None:
                flag.append(999)
            else:
                flag.append(456)
            qual.add(1)
        elif analysis_flags[i][0] == 'V':
            # V: Insufficient sample volume
            # Email John Mund 2021-09-07
            flag.append(658)
            qual.add(1)
        elif analysis_flags[i][0] == 'A':
            # A: no data obtained
            if analysis_values[i] is not None:
                raise ConversionError("data line {}: flag A but data reported"
                                      .format(i+1))
            flag.append(999)
            qual.add(1)
        elif analysis_flags[i][0] == '*':
            # *: unstable baseline made the peak integration impossible
            flag.append(456)
            qual.add(1)
        elif analysis_flags[i][0] == 'D':
            # D: below the detection limit
            # Before 2021-05: flag D was only used for missing values (999.990)
            # In data revision 2021-05, some newer data (end of 2016) were
            # added. Those data conian value 0.0 and flag D.. now.
            # We accept both.
            if analysis_values[i] is not None and analysis_values[i] != 0.0:
                raise ConversionError(
                    'line {}: BDL flag with value ({})'.format(
                        line_numbers[i], analysis_values[i]))
            flag.append(781)
            analysis_values[i] = lod
            qual.add(3)
        elif analysis_flags[i][0] == 'C':
            # C: contamination was found
            flag.append(599)
            qual.add(1)
        elif analysis_flags[i][0] != '.':
            raise ConversionError("data line {}: unknown REJECTION flag {}"
                                  .format(i+1, analysis_flags[i][0]))
        # special case: value < LOD:
        if analysis_values[i] is not None and analysis_values[i] < lod:
            # 2020-08: Detlev:
            # You may find an analytical result occasionally that may be below
            # these [BDL] values, but those should be very few.
            # The could be replaced with '< DL', or '1/2 DL', whatever system
            # EBAS prefers.
            logger.warning('%d: value %f < lod %f Setting to BDL.',
                           line_numbers[i],
                           analysis_values[i], lod)
            flag.append(781)
            analysis_values[i] = lod

        # SELECTION FLAG: 2nd character
        if analysis_flags[i][1] == 'X':
            # selection flag X: suspected local influence
            # Brendan Blanchard, INSTAAR, Kayako Ticket 13595, 2017-10-19
            flag.append(559)
            qual.add(2)
        elif analysis_flags[i][1] == 'N':
            # selection flag N: Collected outside of optimal sampling
            #                   conditions (non-standard)
            # Email John Mund 2021-09-07
            flag.append(660)
            qual.add(2)
        elif analysis_flags[i][1] != '.':
            raise ConversionError("data line {}: unknown SELECTION flag {}"
                                  .format(i+1, analysis_flags[i][1]))

        # INFROMATION FLAG: 3rd character
        if analysis_flags[i][2] == 'C':
            # C: analysis was performed with a reduced sampling volume
            flag.append(660)
            qual.add(3)
        elif analysis_flags[i][2] == 'P':
            # P: measurement result is preliminary
            raise ConversionError("data line {}: preliminary data, rejected"
                                  .format(i+1))
        elif analysis_flags[i][2] != '.':
            raise ConversionError("data line {}: unknown INFORMATION flag {}"
                                  .format(i+1, analysis_flags[i][2]))

        if analysis_values[i] is None:
            qual.add(1)
            if 999 not in flag:
                flag.append(999)

        # the overall quality after analysing all flags is the minimum quality
        # of all flags
        quals.append(min(qual))
        flags.append(flag)
    return quals, flags

def new_output_file(infile, series, revision):
    """
    Creates a new file for output.
    Paramteres:
        infile      the input file object NOAA_NMHC_Flask
        series      the data series to be processed
    Returns:
        output file (EbasNasaAmes object
    Raises:
        ConversionError if the file could not be generated (metadata mapping
        error)
    """
    nas = EbasNasaAmes()

    ############################################################################
    ### time axes related metadata
    ############################################################################

    nas.sample_times = get_sample_times(series)

    # Meta data which are related to the time axes:
    nas.metadata.period = estimate_period_code(nas.sample_times[0][0],
                                               nas.sample_times[-1][1])
    nas.metadata.duration = SAMPLE_DURATION
    nas.metadata.resolution = RESOLUTION_CODE

    # It's a good practice to use Jan 1st of the year of the first sample
    # endtime as the file reference date (zero point of time axes).
    nas.metadata.reference_date = \
        datetime.datetime(nas.sample_times[0][1].year, 1, 1)

    ############################################################################
    ### file global metadata set according to input file
    ############################################################################

    # Station metadata
    ebas_station = get_station(series)
    for meta in ebas_station.keys():
        nas.metadata[meta] = ebas_station[meta]
    ebas_analytical = get_analytical(series)
    for meta in ebas_analytical.keys():
        nas.metadata[meta] = ebas_analytical[meta]
    nas.metadata.mea_latitude = series.sample_latitude[0]
    nas.metadata.mea_longitude = series.sample_longitude[0]
    nas.metadata.mea_altitude = series.sample_elevation[0]
    nas.metadata.mea_height = series.sample_intake_height[0]

    ############################################################################
    ### hardcoded settings for file global metadata
    ############################################################################

    nas.metadata.datalevel = '2'
    nas.metadata.timezone = 'UTC'

    # Revision information
    nas.metadata.revision = revision
    nas.metadata.revdesc = \
        'initiol revision to ebas, generated with {} V.{}'.format(
            basename(__file__), VERSION)

    # Data Originator Organisation, hardcoded
    nas.metadata.org = DataObject(
        OR_CODE='US06L',
        OR_NAME='National Oceanic and Atmospheric Administration',
        OR_ACRONYM='NOAA/ESRL/GMD',
        OR_UNIT='Earth System Research Laboratory, Global Monitoring Division',
        OR_ADDR_LINE1='325 Broadway', OR_ADDR_LINE2=None,
        OR_ADDR_ZIP='CO 80305-3', OR_ADDR_CITY='Boulder',
        OR_ADDR_COUNTRY='U.S.A.')

    # Projects, hardcoded
    nas.metadata.projects = ['GAW-WDCRG', 'NOAA-GGGRN']

    # Data Originators (PIs), hardcoded Detlev Helmig
    nas.metadata.originator = [
        DataObject(
            PS_LAST_NAME='Helmig', PS_FIRST_NAME='Detlev',
            PS_EMAIL='Detlev.Helmig@colorado.edu',
            PS_ORG_NAME='University of Colorado - INSTAAR',
            PS_ORG_ACR='INSTAAR',
            PS_ORG_UNIT='Institute of Arctic and Alpine Research',
            PS_ADDR_LINE1='4001 Discovery Drive', PS_ADDR_LINE2=None,
            PS_ADDR_ZIP='CO 80303', PS_ADDR_CITY='Boulder',
            PS_ADDR_COUNTRY='USA',
            PS_ORCID='0000-0003-1612-1651'),
        ]
    nas.metadata.submitter = []
    for contact in infile.header.contact:
        try:
            subm = SUBMITTER_MAP[(contact.name, contact.email)]
        except KeyError:
            raise ConversionError(
                "Undefined contact uname '{}', email {}, please add contact to "
                "SUBMITTER_MAP".format(contact.name, contact.email))
        nas.metadata.submitter.append(subm)

    nas.metadata.lab_code = 'US13L'
    nas.metadata.instr_type = 'glass_flask'
    nas.metadata.instr_name = 'glass_flask_{}'.format(
        ebas_station['station_code'])

    # this is just for pre-setting the file global metadata, will be set for
    # each variable again
    nas.metadata.regime = 'IMG'
    nas.metadata.matrix = 'air'
    nas.metadata.comp_name = 'NMHC'
    nas.metadata.unit = 'nmol/mol'
    nas.metadata.statistics = 'arithmetic mean'

    return nas

def convert(cmdline):
    """
    Main program. Created for lexical scoping.

    Parameters:
        cmdline   EbasCommandline object (wrapper)
    Returns:
        none
    """
    logger = logging.getLogger('NOAAFlaskConvert')
    for filnam in cmdline.args.filenames:
        fil = NOAA_NMHC_Flask()
        try:
            fil.read(filnam)
        except IOError:
            logger.error('could not open input file %s', filnam)
            continue
        except NOAA_NMHC_Flask_Error as expt:
            logger.error(expt.message)
            continue
        aggregated = fil.data.aggregate()
        isnewfile = False
        try:
            nas = get_output_file(aggregated)
            if nas is None:
                nas = new_output_file(fil, aggregated, cmdline.args.revision)
                isnewfile = True
            metadata = DataObject()
            ebas_parameter = get_parameter(aggregated)
            for meta in ebas_parameter.keys():
                metadata[meta] = ebas_parameter[meta]
            values, flags, stddevs, stdflags, sample_counts, scntflags = \
                convert_data(aggregated, ebas_parameter['DL'])
        except ConversionError as excpt:
            logger.error(excpt.message)
            logger.info("skipping file '{}' because of errors"
                        .format(filnam))
            continue
        nas.variables.append(DataObject(
            values_=values, flags=flags, metadata=metadata))

        metadata_stddev = metadata.copy()
        metadata_stddev.statistics = 'stddev'
        nas.variables.append(DataObject(
            values_=stddevs, flags=stdflags, metadata=metadata_stddev))

        #refcomp = metadata.comp_name
        #metadata = DataObject(
        #    {
        #        'regime': 'IMG',
        #        'matrix': 'air',
        #        'comp_name': 'sample_count',
        #        'unit': 'no unit',
        #        'characteristics' : DatasetCharacteristicList()})
        #metadata_scnt.characteristics.add_parse(
        #    'Reference component', refcomp, nas.metadata.instr_type,
        #    metadata_scnt.comp_name)

        metadata_scnt = metadata.copy()
        metadata_scnt.statistics = 'sample count'
        metadata_scnt.unit = 'no unit'
        nas.variables.append(DataObject(
            values_=sample_counts, flags=scntflags, metadata=metadata_scnt))

        if isnewfile:
            # don't append the new file before anything went well, otherwise
            # empty files (w/o variables) can be left over if a
            # ConversionError occurs.
            OUTPUTFILES.append(nas)

    now = datetime.datetime.utcnow()
    for nas in  OUTPUTFILES:
        # update revision date to script ent time
        nas.metadata.revdate = now
        nas.write(createfiles=True)

EbasCommandline(
    convert, custom_args=['LOGGING', ],
    private_args=add_private_args,
    help_description='%(prog)s convert NOAA NMHC flask measurements to EBAS '
    'NASA Ames.', version=VERSION).run()
