
import pandas as pd
import numpy as np
import math
from math import modf
import matplotlib.dates as md
import os
from os import path
import glob, re, shutil
import datetime
from datetime import date, timedelta as td
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import linregress


############1.Directory where are stored the Input AE33 files (from the instrument)###############
nom_rep_in =r'C:\Users\ERLX220\Desktop\test'
scanfic= '*.dat'

########################2.OUTPUT FILE##########################################
delimiter_out=',' 
f_new_rep=nom_rep_in
f_new_name='AE33_input_lev0_TEMPLATE.txt'

################################################################################
sigmas=[18.47, 14.54, 13.14, 11.58, 9.89, 7.77, 7.19]#instrumental sigma for AE33
C_instr=1.39 ###for tape M8060 (1.57 for tape M8050)
#C0=3.3 ?? ###Co value for AE33 under discussion

#######Correction Factors#######################################################
#for level 0, keep all F=1
Fstp=1        #(21.11+273)/(273) *(1013.25/1013.25)  #correction to 0 degrees and 1013.25hPa ##Fstp=1.077
Fspot=1       #(Fspot=Ameas/Ainstr)  ##Ainstr=0.785cm2
Fflow=1       # (Qinstr(slpm)/Qref(lpm)   *    Tref(K)/T0,instr(K)  x   P0,instr(hPa)/Pref(hPa). Where Qinstr. and Qref are the flows measured with the instrument and determined with a reference volume flow meter, respectively.
##The flow of the volume flow meter is converted using the temperature Tref and pressure Pref ,which are typically the ambient or room temperature or pressure near the reference flow meter. ##Also the standard temperatureT0,instr and standard pressure P0,instr of the instrument have to be considered 
Fmscat=1      #=C_instr/C0 multple scattering correction factor

#####################List of input files to import##############################
ficlist= glob.glob(path.join(nom_rep_in, scanfic))
dfs = []
for filename in ficlist:
     dfs.append(pd.read_table(filename,skiprows=4,skipinitialspace=True,index_col=False,delimiter=r"\s+",parse_dates=[[0,1]],usecols=[i for i in range(0,67)],engine='python'))

df = pd.concat(dfs, ignore_index=True)# Concatenate AE33 data files into one DataFrame
df=df.rename(index=str, columns={"Date(yyyy/MM/dd);_Time(hh:mm:ss);":"DateTime"})
df['DateTime']=pd.to_datetime(df['DateTime'],format='%Y-%m-%d %H:%M:%S')
#df['DateTime']+=np.timedelta64(td(hours=-2)) # to uncomment if time conversion is needed
df.columns = df.columns.str.replace(';', '')
start_date=str(df['DateTime'][0])
end_date=str(df['DateTime'][-1])
#print(list(df)) # print headers
print('Loaded data from %s until %s' %(start_date,end_date)) 
#print df.dtypes

##############################Count number of filter changes####################
TapeAdvCounts=df['TapeAdvCount'][-1:]-df['TapeAdvCount'][0]
print('number of Tape advances=%i' %TapeAdvCounts)
#
###########Create dataframe collection based on TapeAdv Counts#################
#dictionnary of dataframes. Each dataframe corresponds to one filter change
dataframe_collection = {k: v for k, v in df.groupby('TapeAdvCount')}

########Iterative processing of each dataframe #################################
for key in list(dataframe_collection.keys()):
    print(key)
    df=dataframe_collection[key]
    for channel in [1,2,3,4,5,6,7]:
        print(channel)
        for sensor in [1,2]:
            #calculate attenuation coefficients
            df['att%i_%i'%(sensor,channel)]=(-100*np.log (df['Sen%iCh%i'%(sensor,channel)]/df['RefCh%i'%(channel)]))
            df['att%i_%i'%(sensor,channel)]= df['att%i_%i'%(sensor,channel)]-df['att%i_%i'%(sensor,channel)].min(axis=None)
#            #calculate absorption coefficients
            df['abs%i_%i'%(sensor,channel)]=Fstp*Fspot*Fflow*Fmscat*df['BC%i%i'%(channel,sensor)]*sigmas[channel-1]/1000
            df['abs_%i'%(channel)]=Fstp*Fspot*Fflow*Fmscat*df['BC%i'%channel]*sigmas[channel-1]/1000
            # # #convert BC from ng/m3 to ug/m3
            df['EBC%i_%i'%(sensor,channel)]=Fstp*Fspot*Fflow*Fmscat*df['BC%i%i'%(channel,sensor)]/1000
            df['EBC_%i'%(channel)]=Fstp*Fspot*Fflow*Fmscat*df['BC%i'%(channel)]/1000
            
big_frame = pd.concat(dataframe_collection, axis=0)
big_frame=big_frame.reset_index(inplace=False) 

##########################Format output table##################################
# #Create new columns
big_frame['NWv'] = 7
big_frame['numflag'] = 0
##########################FLAGGING##############################################
#EBAS flags 
#0:valid,
#999:missing, 
#652: valid/construction nearby,
#459: extreme value: unspeicified error, 
#460: contamination suspected, 
#456: invalidated by data originator

#####the following are just EXAMPLES of how to set the different flags:
######Example 1: flags based on specifc dates
#mask = (big_frame['DateTime'] > '2016-03-21 23:50:00') & (df['DateTime'] <= '2016-03-21 23:56:00') #uncomment if wanted
#big_frame['numflag']= big_frame['numflag'].where(~mask, other=652) #uncomment if wanted


###flags depending on the instrumental status
big_frame['numflag']=big_frame['numflag'].where(big_frame['Status']!=1,456)#Instrumental Status=1: Tape advance
big_frame['numflag']=big_frame['numflag'].where(big_frame['Status']!=2,456)#Instrumental Status=2: first measurement obtainin ATN0

######flags after Detecting outliers in a Pandas dataframe using a rolling standard deviation
big_frame=big_frame.set_index('DateTime')
r = big_frame.rolling(window=10)  # Create a rolling object (no computation yet)
mps = r.mean() + 3. * r.std()  # Combine a mean and stdev on that object
big_frame['numflag'] = big_frame['numflag'].where(big_frame.abs_5 < mps.abs_5, 459)
big_frame=big_frame.reset_index(inplace=False) 

#Plot abs / color coded depending on flag
big_frame['index'] = big_frame.index
ax=big_frame.plot.scatter(x='index',y='abs_5', c='numflag',colormap='viridis')

######################Rename columns as in the EBAS template####################
big_frame = big_frame.rename(columns={
'RefCh1': 'ref_1', 'Sen1Ch1': 'sens1_1', 'Sen2Ch1': 'sens2_1','K1':'k_1',
'RefCh2': 'ref_2', 'Sen1Ch2' : 'sens1_2', 'Sen2Ch2': 'sens2_2','K2':'k_2',
'RefCh3': 'ref_3', 'Sen1Ch3' : 'sens1_3', 'Sen2Ch3': 'sens2_3','K3':'k_3',
'RefCh4': 'ref_4', 'Sen1Ch4' : 'sens1_4', 'Sen2Ch4': 'sens2_4','K4':'k_4',
'RefCh5': 'ref_5', 'Sen1Ch5' : 'sens1_5', 'Sen2Ch5': 'sens2_5','K5':'k_5',
'RefCh6': 'ref_6', 'Sen1Ch6' : 'sens1_6', 'Sen2Ch6': 'sens2_6','K6':'k_6',
'RefCh7': 'ref_7', 'Sen1Ch7' : 'sens1_7', 'Sen2Ch7': 'sens2_7','K7':'k_7',
'Flow1': 'flow1', 
'Flow2': 'flow2',
'FlowC': 'flowC',
'Pressure(Pa)': 'refpress',
'Temperature(\xc2\xb0C)': 'reftemp',
'BB(%)':'BB',
'ContTemp': 'Tcntrl',
'SupplyTemp': 'Tsupply',
'Status':'STinst',
'ContStatus':'STcnt',
'DetectStatus':'STdet',
'LedStatus':'STled',
'ValveStatus':'STvalv',
'LedTemp':'T_LED',
'TapeAdvCount':'tpcnt'})

##############select columns to be stored in the output file####################
big_frame= big_frame[["DateTime","refpress","reftemp","flow1","flow2","flowC","Tcntrl","Tsupply","T_LED","STinst","STcnt","STdet","STled","STvalv","tpcnt","BB","NWv",
"ref_1","sens1_1","sens2_1","EBC1_1","EBC2_1","EBC_1","k_1","abs_1","att1_1","att2_1",
"ref_2","sens1_2","sens2_2","EBC1_2","EBC2_2","EBC_2","k_2","abs_2","att1_2","att2_2",
"ref_3","sens1_3","sens2_3","EBC1_3","EBC2_3","EBC_3","k_3","abs_3","att1_3","att2_3",
"ref_4","sens1_4","sens2_4","EBC1_4","EBC2_4","EBC_4","k_4","abs_4","att1_4","att2_4",
"ref_5","sens1_5","sens2_5","EBC1_5","EBC2_5","EBC_5","k_5","abs_5","att1_5","att2_5",
"ref_6","sens1_6","sens2_6","EBC1_6","EBC2_6","EBC_6","k_6","abs_6","att1_6","att2_6",
"ref_7","sens1_7","sens2_7","EBC1_7","EBC2_7","EBC_7","k_7","abs_7","att1_7","att2_7",
"numflag"]]

############################write output file###################################
fileout_new=path.join(f_new_rep, f_new_name)
big_frame.to_csv(fileout_new, sep=delimiter_out,float_format='%.6f', index=False)