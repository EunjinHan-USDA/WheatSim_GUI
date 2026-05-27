##Program: 2D plot of 2DSOIL output -g03 NodeGraphics
##Author: Eunjin Han
##Institute: USDA-ARS-ACSL
##Date: November 30, 2022
##===================================================================
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib import ticker
#from sklearn.metrics import mean_squared_error, r2_score
import pandas as pd
import matplotlib.mlab as mlab
import datetime    #to convert date to doy or vice versa
from os import path # path
# import datetime module from datetime
from datetime import datetime

#convert date in MM/DD/YYYY to separate M, D, and Year columns
def MMDDYYYY(x):    
    mm = int(x.split('/')[0])
    dd = int(x.split('/')[1])
    YYYY = int(x.split('/')[2])
    date = datetime(YYYY, mm, dd)  #date object
    date = date.strftime("%Y") + '-' + date.strftime("%m")+ '-' + date.strftime("%d")
    mmdd=str(mm)+'-'+str(dd)

    # # time_data = "25/05/99 02:35:5.523" # consider the time stamp in string format
    # # # day/month/year hours/minutes/seconds-micro
    # # # seconds
    # format_data = "%m/%d/%yyyy"  # format the string in the given format :
 
    # # Using strptime with datetime we will format string into datetime
    # date = datetime.strptime(x.strip(), format_data)
    return mm, dd, YYYY, date, mmdd #, date2

#==============================================================================
working_dir = 'D:\\ACSL_EJ\\FSP_Project_Kate\\Seasonal_sim\\residue_effect\\'
# sim_list = ['2011_117_NTMZ_R0', '2011_117_NTMZ_R1', '2011_117_NTMZ_R2' ,'2011_117_NTMZ_R3', '2011_117_NTMZ_R4']
# sim_list = ['2017_117_NTMZ_R0', '2017_117_NTMZ_R1', '2017_117_NTMZ_R2' ,'2017_117_NTMZ_R3', '2017_117_NTMZ_R4']
sim_list = ['2011_103_NTSB_R0', '2011_103_NTSB_R1', '2011_103_NTSB_R2' ,'2011_103_NTSB_R3', '2011_103_NTSB_R4'] 
# sim_list = ['2017_103_NTSB_R0', '2017_103_NTSB_R1', '2017_103_NTSB_R2' ,'2017_103_NTSB_R3', '2017_103_NTSB_R4']

fig, ax = plt.subplots(5,1,figsize=(9,10))  #two years of data together => total 11 years 
fig.suptitle('SB dry matter:  ' + sim_list[0][:13]) #g03_fname[-12:-4])
# c_list = ['C1', 'C2','C3','C4','C6'] #,'C7'] #, 'C8', 'C9']
c_list = ['c', 'r','b','k','g'] #,'C7'] #, 'C8', 'C9']
marker_list = ["^", "*","+",".","x"] 

for i in range(5):
    sim_id = sim_list[i]
    g01_fname = working_dir + sim_id + '\\' + sim_id + '.G01'
    df=pd.read_csv(g01_fname)

    #output variables in g01
    #   date,      jday,      time,    RSTAGE,    VSTAGE,       PFD,    SolRad,      Tair,      Tcan,    Pgross,      Pnet,        
    # gs,      PSIL,       totalDM,    LAREAT,   totalDM,    rootDM,    stemDM,    leafDM,    seedDM,     podDM,    DeadDM,    stemDM,    leafDM,   
    # rootDM,   Nstress,     Limit

    # #Maura's CLASSIM code
    # varFuncSoilDict = {'hNew':'mean','thNew':'mean','Temp':'mean'}  #'NO3N':'mean',
    # param = ["hNew", "thNew","Temp"]
    # varSoilDict = {"hNew":"Soil Matric Potential\n(cm suction)","thNew":"Soil Water Content\n(cm3/cm3)","Temp":"Temperature\n(oC)"} #"NO3N":"Nitrogen Concentration\n(mg/L)",\
    varFuncSoilDict = {'LAI':'mean','totalDM':'mean','rootDM':'mean','leafDM':'mean','seedDM':'mean'}
    param = ["LAI", "totalDM","rootDM", "leafDM", "seedDM"]
    varSoilDict = {"LAI":"Leaf Area Index","totalDM":"total plant dry weight","rootDM":"root dry weight", "leafDM":"leaf dry weigt","seedDM":"seed dry weight(g/plant)"} #,"podDM":"seed dry weight(g/plant)","DeadDM":"dead plant dry weight"} #"NO3N":"Nitrogen Concentration\n(mg/L)",\

    df_collection = {}
    # remove special character
    df.columns = df.columns.str.replace(' ', '')

    # select only a few relevant columns
    df2 = df[['date', 'LAI', 'totalDM', 'rootDM', 'leafDM', 'seedDM']]

    df2['Month'], df2['Day'],df2['YEAR'],df2['Date_Time'],df2['mm-dd']  = zip(*df2['date'].apply(MMDDYYYY))

    for key in varFuncSoilDict:
        df2[key] = pd.to_numeric(df2[key],errors='coerce')

    df2 = df2.fillna(0)

    df_grouped_0 = df2.groupby(['date','mm-dd'], as_index=False).agg(varFuncSoilDict)

    #1) LAI
    xdata = np.arange(1,len(df_grouped_0['mm-dd'].values)+1)  #120
    xdata_date = df_grouped_0['mm-dd'].values
    ax[0].plot(xdata, df_grouped_0.LAI.values,color=c_list[i], marker=marker_list[i],markersize=3, label = sim_id[-2:])

    #2) totalDM
    ax[1].plot(xdata, df_grouped_0.totalDM.values,color=c_list[i], marker=marker_list[i],markersize=3, label = sim_id[-2:])

    #3) rootDM
    ax[2].plot(xdata, df_grouped_0.rootDM.values,color=c_list[i], marker=marker_list[i],markersize=3, label = sim_id[-2:])

    #4) leafDM
    ax[3].plot(xdata, df_grouped_0.leafDM.values,color=c_list[i], marker=marker_list[i],markersize=3, label = sim_id[-2:])

    #5) seedDM
    ax[4].plot(xdata, df_grouped_0.seedDM.values,color=c_list[i], marker=marker_list[i],markersize=3, label = sim_id[-2:])

#=================
#==========================================================

ax[0].legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
ax[0].set(ylabel='LAI') #xlabel='Date',
ax[0].set_title('Leaf Area Index')
#extract substring of the xtick label
ax[0].set_xticks(np.arange(xdata[0],xdata[-1]+1,8))
ax[0].set_xticklabels([])
ax[0].set_xlim(xdata[0], xdata[-1])
ax[0].set_ylim(0,5)
ax[0].grid(color='0.9')

ax[1].legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
ax[1].set(ylabel='Dry weight [g/plant]') #xlabel='Date',
ax[1].set_title('Total plant dry matter')
#extract substring of the xtick label
ax[1].set_xticks(np.arange(xdata[0],xdata[-1]+1,8))
ax[1].set_xticklabels([])
ax[1].set_xlim(xdata[0], xdata[-1])
ax[1].set_ylim(0,40)
ax[1].grid(color='0.9')

ax[2].legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
ax[2].set(ylabel='Dry weight [g/plant]') #xlabel='Date',
ax[2].set_title('Root dry matter')
#extract substring of the xtick label
ax[2].set_xticks(np.arange(xdata[0],xdata[-1]+1,8))
ax[2].set_xticklabels([])
ax[2].set_xlim(xdata[0], xdata[-1])
ax[2].set_ylim(0,10)
ax[2].grid(color='0.9')

ax[3].legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
ax[3].set(ylabel='Dry weight [g/plant]') #xlabel='Date',
ax[3].set_title('Leaf dry matter')
#extract substring of the xtick label
ax[3].set_xticks(np.arange(xdata[0],xdata[-1]+1,8))
ax[3].set_xticklabels([])
ax[3].set_xlim(xdata[0], xdata[-1])
ax[3].set_ylim(0,8)
ax[3].grid(color='0.9')

ax[4].legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
ax[4].set(xlabel='Date [MM/DD]', ylabel='Dry weight [g/plant]') #xlabel='Date',
ax[4].set_title('Seed dry matter')
#extract substring of the xtick label
ax[4].set_xticks(np.arange(xdata[0],xdata[-1]+1,8))
ax[4].set_xticklabels(xdata_date[0::8], rotation=90)  #some_list[start:stop:step]
ax[4].set_xlim(xdata[0], xdata[-1])
ax[4].set_ylim(0,15)
ax[4].grid(color='0.9')
plt.tight_layout()
fig_name = working_dir + sim_list[0][:14]+ '_DM_ts.jpg'
plt.savefig(fig_name) #, dpi=150)
plt.show()
#------------------------------------------------
