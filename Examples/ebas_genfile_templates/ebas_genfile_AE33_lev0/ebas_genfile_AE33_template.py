#!/usr/bin/env python
# coding=utf-8
"""
Example for creating an EBAS Nasa Ames lev 0 datafile from the instrument
raw data file.

This script has been kindly provided by Athina Kalogridi from NCSR Demokritos,
Greece
"""
from ebas.io.file import nasa_ames
from nilutility.datatypes import DataObject
from ebas.domain.basic_domain_logic.time_period import estimate_period_code, \
    estimate_resolution_code, estimate_sample_duration_code
import datetime
from ebas.io.ebasmetadata import DatasetCharacteristicList
import pandas as pd
import math
__version__ = '1.00.00'



f = 'AE33_input_lev0_template.txt'
f_metadata='AE33_metadata_lev0_template.csv'
#Input f and f_metadata files have the variables values and metadata in same column and positions
first_column=1 #(first column with variable to process) 
last_column=86# (last column to process)
index_flag_col=87 #(nb column with flag data)
tresol=1 #sample duration in minutes
destdir_out='.'


###############Read Input Data##############
df=pd.read_csv(f, delimiter=',', header=0,nrows=3, engine='python') #Specify nb_lines of header, delimiter etc
df = df.where((pd.notnull(df)), None) #Replace nan values with None
start_times_df=pd.to_datetime(df['DateTime_UTC'],format='%Y-%m-%d %H:%M:%S') #Specify format of datetime column to read. The column in called by the header name
names=list(df.columns.values) 
numb_col=df.shape[1]


#Read metadata##############################################################################
df_metadata=pd.read_csv(f_metadata, delimiter=';', header=0, nrows=13)

##############################################################################################################################

def rounding(val):
    if val==None:
        return None
    else:
        return round(val , 7)

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
    nas.metadata.datadef='EBAS_1.1'
    nas.metadata.type='TI' # I am not sure it is coded this way
    nas.metadata.timezone = 'UTC'#OK

    # Revision information
    #nas.metadata.revdate = datetime.datetime(2018, 05, 07, 15, 35, 00) # date when the file was created or last updated
    nas.metadata.revdate = datetime.datetime.now()-datetime.timedelta(hours=3) #OK
    
    nas.metadata.revision = '1' #Version OK
    nas.metadata.revdesc = 'initial submission'# Version description OK
    nas.metadata.statistics='arithmetic mean' #ok
    nas.metadata.datalevel = '0'#OK
    nas.metadata.rescode_sample ='1s' #Orig. time res.: 
    
    # Data Originator Organisation
    nas.metadata.org = DataObject(
        OR_CODE='GR05L',
        OR_NAME='NCSR Demokritos',
        OR_ACRONYM='DEM', OR_UNIT='URL',
        OR_ADDR_LINE1='Ag.Paraskevi', OR_ADDR_LINE2=None,
        OR_ADDR_ZIP='15310', OR_ADDR_CITY='Athens', OR_ADDR_COUNTRY='Greece')

    # Projects the data are associated to
    nas.metadata.projects = ['ACTRIS']

    # Data Originators (PIs)
    nas.metadata.originator = []
    nas.metadata.originator.append(
        DataObject(
            PS_LAST_NAME='Eleftheriadis', PS_FIRST_NAME='Konstantinos', PS_EMAIL='elefther@ipta.demokritos.gr',
            PS_ORG_NAME='NCSR Demokritos',
            PS_ORG_ACR='DEM', PS_ORG_UNIT='ERL',
            PS_ADDR_LINE1='Ag.Paraskevi', PS_ADDR_LINE2=None,
            PS_ADDR_ZIP='15310', PS_ADDR_CITY='Athens',
            PS_ADDR_COUNTRY='Greece',
            PS_ORCID='0000-0003-2265-4905'))        
    nas.metadata.originator.append(
        DataObject(
            PS_LAST_NAME=u'Kalogridis', PS_FIRST_NAME='Athina-Cerise', PS_EMAIL='akalogridi@ipta.demokritos.gr',
            PS_ORG_NAME='NCSR Demokritos',
            PS_ORG_ACR='DEM', PS_ORG_UNIT='ERL',
            PS_ADDR_LINE1='Ag.Paraskevi', PS_ADDR_LINE2=None,
            PS_ADDR_ZIP='15310', PS_ADDR_CITY='Athens',
            PS_ADDR_COUNTRY='Greece',
            PS_ORCID=None))

    # Data Submitters (contact for data technical issues)
    nas.metadata.submitter = []
    nas.metadata.submitter.append(
        DataObject(
            PS_LAST_NAME=u'Kalogridis', PS_FIRST_NAME='Athina-Cerise', PS_EMAIL='akalogridi@ipta.demokritos.gr',
            PS_ORG_NAME='NCSR Demokritos',
            PS_ORG_ACR='DEM', PS_ORG_UNIT='ERL',
            PS_ADDR_LINE1='Ag.Paraskevi', PS_ADDR_LINE2=None,
            PS_ADDR_ZIP='15310', PS_ADDR_CITY='Athens',
            PS_ADDR_COUNTRY='Greece',
            PS_ORCID=None))#should ve in the format 9999-9999-9999-999 (submission tool does not accept IDs with X letters in the code)

    # Station metadata
    nas.metadata.station_code = 'GR0100B'
    nas.metadata.platform_code = 'GR0100S'
    nas.metadata.station_name = u'DEM_Athens'
    nas.metadata.station_wdca_id = 'GAWAGR__DEM'
    nas.metadata.station_gaw_id = 'DEM'
    nas.metadata.station_gaw_name = u'Demokritos Athens'
    # nas.metadata.station_airs_id =    # N/A
    #nas.metadata.station_other_ids = ''
    # nas.metadata.station_state_code =  # N/A
    nas.metadata.station_landuse = 'Forest'
    nas.metadata.station_setting = 'Urban and center city'
    nas.metadata.station_gaw_type = 'R'
    nas.metadata.station_wmo_region = 6
    nas.metadata.station_latitude = 37.9949989319
    nas.metadata.station_longitude = 23.8159999847
    nas.metadata.station_altitude = 270.0
    nas.metadata.mea_latitude = 37.995
    nas.metadata.mea_longitude = 23.816
    nas.metadata.mea_altitude=270.0
    nas.metadata.mea_height=10
    
    # More file global metadata, but those can be overridden per variable
    # See set_variables for examples
    nas.metadata.comp_name = 'equivalent_black_carbon'
    #nas.metadata.unit='ug/m3' #or maybe comment it here and give it in the variables?
    nas.metadata.matrix = 'pm10'
        
    nas.metadata.lab_code = 'GR05L'
    nas.metadata.instr_type = 'filter_absorption_photometer'
    nas.metadata.instr_name = 'Magee_AE33_DEM_dry'
    nas.metadata.instr_manufacturer='Magee'
    nas.metadata.instr_model='AE33' 
    nas.metadata.instr_serialno = 'AE33-S02--00186'
    nas.metadata.method = 'GR05L_abs_coef_AE33_v1'
    nas.metadata.std_method='Single-angle_Correction=Drinovec2015'
    nas.metadata.inlet_type='Impactor--direct'
    nas.metadata.inlet_desc='PM10 impactor for a nominal flow of 30L/min'
    nas.metadata.flow_rate=5##in l/min (unit wil be displayed automatically)   
    nas.metadata.filter_type='Magee M8050'   
    nas.metadata.hum_temp_ctrl='Nafion dryer'
    nas.metadata.hum_temp_ctrl_desc='The sample is dried in a Nafion dryer by counterflow of dry air'
    nas.metadata.vol_std_temp=273.15##OK. here check..i thought it was 293.15 
    nas.metadata.vol_std_pressure=1013.25 #OK #should be a float and not an integer
    #nas.metadata.detection_limit=[0.10, 'ng/m3']  #to be set in the set_variables
    #nas.metadata.detection_limit_desc=None
    #nas.metadata.uncertainty=None     
    nas.metadata.uncertainty_desc='typical value of unit to unit variability'
    nas.metadata.zero_negative='Zero/negative possible'
    nas.metadata.zero_negative_desc='Zero and neg. values may appear due to statistical variations at very low concentrations'
    nas.metadata.max_attenuation=100.0 
    nas.metadata.leakage_factor_zeta=0.07 
    nas.metadata.comp_thresh_atten1=10.0
    nas.metadata.comp_thresh_atten2=30.0 
    nas.metadata.comp_param_kmin=-0.005
    nas.metadata.comp_param_kmax=0.015
    nas.metadata.qm_id='WCCAP-AP­‐2017-2‐5' #QA measure ID
    nas.metadata.qm_doc_date='20171018' #QA document dat
    nas.metadata.qm_doc_url='http://www.actris-ecac.eu/files/ECAC-report-AP-2017-2-5.pdf' #QA document URL
    nas.metadata.comment='calibration factor / mean ratio = 1.00; sample_spot_area= 5.7e-5 m2' 
    nas.metadata.acknowledgements='Request acknowledgment details from data originator'
    #nas.metadata.regime='IMG'#OK
    

def set_time_axes(nas):
    """
    Set the time axes and related metadata for the EbasNasaAmes file object.

    Parameters:
        nas    EbasNasaAmes file object
    Returns:
        None
    """
    # define start and end times for all samples
    start_times_list=start_times_df.tolist()
    start_times_dt_list=[start_times_list[i].to_pydatetime()for i in range(len(start_times_list))]
    end_times_df=start_times_df+datetime.timedelta(minutes=tresol)
    end_times_list=end_times_df.tolist()
    end_times_dt_list=[end_times_list[i].to_pydatetime()for i in range(len(start_times_list))]
    nas.sample_times=list(zip(start_times_dt_list,end_times_dt_list))
    #nas.sample_times = \
    #    [(datetime.datetime(2008, 1, 1, 0, 0), datetime.datetime(2008, 1, 1, 1, 0)),
    #     (datetime.datetime(2008, 1, 1, 1, 0), datetime.datetime(2008, 1, 1, 2, 0)),
    #     (datetime.datetime(2008, 1, 1, 2, 0), datetime.datetime(2008, 1, 1, 3, 0)),
    #     (datetime.datetime(2008, 1, 1, 3, 0), datetime.datetime(2008, 1, 1, 4, 0)),
    #     (datetime.datetime(2008, 1, 1, 4, 0), datetime.datetime(2008, 1, 1, 5, 0)),
    #     (datetime.datetime(2008, 1, 1, 5, 0), datetime.datetime(2008, 1, 1, 6, 0)),
    #     (datetime.datetime(2008, 1, 1, 6, 0), datetime.datetime(2008, 1, 1, 7, 0)),
    #     (datetime.datetime(2008, 1, 1, 7, 0), datetime.datetime(2008, 1, 1, 8, 0))]

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
    # 
    #nas.metadata.duration = '5mn'

    # Resolution code can be set automatically
    # But be aware that resolution code is an identifying metadata element.
    # That means, several submissions of data (multiple years) will
    # only be stored as the same dataset if the resolution code is the same
    # for all submissions!
    # That might be a problem for time series with varying resolution code
    # (sometimes 2 months , sometimes 3 months, sometimes 9 weeks, ...). You
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

    x=first_column
    while x < last_column+1:
        col=df.take([x],axis=1)
        values=col.values.T.tolist()[0]
        values=list(map(rounding, values))
        col_metadata=df_metadata.take([x],axis=1)
    #values=[25,45]
        col_flag=df.take([index_flag_col],axis=1).astype(int)
        flags=col_flag.values.tolist() #flags = [[], [632, 665], [999], []], [] means no flags for this measurement
        #flags = [[]]*len(values) 
        metadata = DataObject()
        metadata.comp_name = col_metadata[0:1].values.T.tolist()[0][0]
        metadata.unit = col_metadata[1:2].values.T.tolist()[0][0]               
        metadata.matrix=col_metadata[2:3].values.T.tolist()[0][0]   
        metadata.title=col_metadata[3:4].values.T.tolist()[0][0]
    
        LOD=float(col_metadata[4:5].values.T.tolist()[0][0])
        if math.isnan(LOD)==False: 
            metadata.detection_limit = [LOD, 'ug/m3']
            metadata.detection_limit_desc=col_metadata[5:6].values.T.tolist()[0][0]
        pass 
    
        uncertainty=float(col_metadata[6:7].values.T.tolist()[0][0])
        if math.isnan(uncertainty)==False: 
            metadata.uncertainty = [uncertainty, '%']
        pass 
        
        mass_abs_cross_section=float(col_metadata[7:8].values.T.tolist()[0][0])
        if math.isnan(mass_abs_cross_section)==False: 
            metadata.mass_abs_cross_section = '%f' %(mass_abs_cross_section)#unit in m2/g will be automatically applied in the output file
        pass     
    
    
        multi_scattering_corr_fact=float(col_metadata[8:9].values.T.tolist()[0][0])
        if math.isnan(multi_scattering_corr_fact)==False: 
            metadata.multi_scattering_corr_fact = multi_scattering_corr_fact
        pass     
    
        filter_area=float(col_metadata[9:10].values.T.tolist()[0][0])
        if math.isnan(filter_area)==False: 
            metadata.filter_area = '%f' % (filter_area)#unit in cm2 will be automatically applied
        pass 

        #Characteristics    
        if col_metadata[10:11].values.T.tolist()[0][0]=='None':
            nas.variables.append(DataObject(values_=values, flags=flags, flagcol=True,metadata=metadata))
        else:
            metadata.characteristics = DatasetCharacteristicList()
            Characteristic_type=col_metadata[10:11].values.T.tolist()[0][0]
            Value=col_metadata[11:12].values.T.tolist()[0][0]
            Instrument_type=col_metadata[12:13].values.T.tolist()[0][0]
            metadata.characteristics.add_parse(Characteristic_type, Value, Instrument_type, metadata.comp_name, data_level=nas.metadata.datalevel)  
            nas.variables.append(DataObject(values_=values, flags=flags, flagcol=True,metadata=metadata))
                                
        x+=1
          
            

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
    nas.write(createfiles=True,destdir=destdir_out)
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
