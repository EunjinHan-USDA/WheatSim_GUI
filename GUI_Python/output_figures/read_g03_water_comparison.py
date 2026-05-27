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
# Convert numpy.datetime64 to datetime.datetime
# https://gist.github.com/blaylockbk/1677b446bc741ee2db3e943ab7e4cabd?permalink_comment_id=3775327#file-numpy_datetime_to_datetime-py
def to_datetime(date):
    """
    Converts a numpy datetime64 object to a python datetime object 
    Input:
      date - a np.datetime64 object
    Output:
      DATE - a python datetime object
    """
    timestamp = ((date - np.datetime64('1970-01-01T00:00:00'))
                 / np.timedelta64(1, 's'))
    YY=datetime.utcfromtimestamp(timestamp).year
    Mnt = datetime.utcfromtimestamp(timestamp).month
    day=datetime.utcfromtimestamp(timestamp).day
    # YYMMDD = str(YY)[2:]+'-'+str(Mnt).zfill(2)+str(day).zfill(2)
    YYMMDD = str(Mnt).zfill(2)+'/'+str(day).zfill(2)+'/'+str(YY)[2:]
    # return datetime.utcfromtimestamp(timestamp)
    return YYMMDD

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
#============================================
# read geometry from *.grd and save them into geo_df
def read_grd(fname):
    # fname = r'D:\ACSL_EJ\FSP_Project_Kate\Rotation_sim\ExcelInterface\NT\2002_103_NTSB\2002_103_NTSB.grd'
    f = open(fname,'r')
    count = 0
    for line in f:
        if count == 2:
            # KAT= line[0:6]  #surface ratio
            NumNP = line[6:14]  #internal ratio: ratio of the distance between two neighboring nodes"
            # NumEl = line[14:22]
            # NumBP = line[22:30]
            # IJ = line[30:36]
            NumMat = line[36:43]
            break  #exit out of loop
        count = count +1
    f.close()
    # #make a dictionary
    # grddict = {
    #         "KAT": int(KAT),  #type of system to be analyzed, 1 for axisymmetrical flow, 2 for vertical flow in a cross-section
    #         "NumNP": int(NumNP), #number of nodes
    #         "NumEl": int(NumEl), #number of elements
    #         "NumBP": int(NumBP),  #number of boundary nodes for which boundary conditions are prescribed
    #         "IJ": int(IJ), #maximum number of nodes alnog a transverse grid line
    #         "NumMat": int(NumMat) #total number of soil subdomain in the soil domain => number of layers
    #         }

    #open *grd again to read into a db
    df_grd = pd.read_csv(fname,delim_whitespace=True ,nrows=int(NumNP), skiprows=3)

    # adding column name to the respective columns
    df_grd.columns =['n', 'X', 'Y', 'Layer']
    return df_grd

#============================================
# read *.lyr to get eomult and rowSP)
def read_ini(fname):
    f = open(fname,'r')
    count = 0
    for line in f:
        if count == 2:
            POPROW = line[0:12]  #surface ratio
            ROWSP = line[12:24]  #internal ratio: ratio of the distance between two neighboring nodes"
            Plant_Density = line[24:38]
            IROWANG = line[38:50]
            xSeed  = line[50:64]
            ySeed = line[64:79]
            CEC = line[79:94]
            EOMult = line[94:102]
            break
        count = count +1
    f.close()
    return float(ROWSP), float(EOMult)
#============end of EJ(5/31)

#==============================================================================
working_dir = 'D:\\ACSL_EJ\\FSP_paper\\NT_residue_test\\'
folder_list = ['2003_103_NTSB_0_res', '2003_103_NTSB_dry', '2003_103_NTSB_wet']
sim_id = '2003_103_NTSB'

fig, ax = plt.subplots(5,1,figsize=(8,9))  #two years of data together => total 11 years 
fig.suptitle('Soil water content:  ' +sim_id) #g03_fname[-12:-4])
# c_list = ['C1', 'C2','C3','C4','C6'] #,'C7'] #, 'C8', 'C9']
c_list = ['c', 'r','b','k','g'] #,'C7'] #, 'C8', 'C9']
marker_list = ["^", "*","+",".","x"] 

count = 0
for i in range(3):
    #SSM (surface soil moisture),
    g03_fname = working_dir + folder_list[i] + '\\' + sim_id + '.G03'
    g07_fname = working_dir + folder_list[i] + '\\' + sim_id + '.G07'
    grd_fname = working_dir + folder_list[i] + '\\' + sim_id + '.grd'
    ini_fname = working_dir + folder_list[i] + '\\' + sim_id + '.ini'
    #1)read g03 and g07
    df_g03 = pd.read_csv(g03_fname, parse_dates=['        Date'], delim_whitespace=False) #,skiprows=1)
    df_g07 = pd.read_csv(g07_fname, parse_dates=['           Date'], delim_whitespace=False)  #,skiprows=1)
    # remove special character
    df_g03.columns = df_g03.columns.str.replace(' ', '')
    df_g07.columns = df_g07.columns.str.replace(' ', '')

    #1) Get geometry df by reading *grd
    geo_df = read_grd(grd_fname)
    #2) read *.ini to get eomult and rowSP
    ROWSP, EOMult = read_ini(ini_fname)

    # Merge g03 table with geometry table
    t3 = pd.merge(geo_df,df_g03,how='inner',left_on=['X','Y'],right_on=['X','Y'])

    # Since 2dsoil assigns Y values from the max depth ->0 where the surface is the maximum Depth 
    # and the bottom of the profile is 0, we have to reverse this for the layer file. Thus we 
    # subtract the max depth from all the Y's'
    maxY = max(t3['Y'])
    t3['Y'] = maxY-t3['Y']

    t3['thNewArea'] = t3['thNew'] * t3['Area']
    # t3['thNewNO3NArea'] = t3['thNew'] * t3['NO3N'] * t3['Area']

    # First, we need to group the data by day
    t3 = t3.groupby(['Date','X','Y'],as_index=False).mean()
    t3 = t3.drop(columns=["X","Q","NH4N","hNew","Area"])
    
    # total water profile
    totWatProf = t3.groupby('Date',as_index=False)['thNewArea'].sum()
    totWatProf['totWatProf'] = totWatProf['thNewArea']/(EOMult*ROWSP)*10  #unit mm
    totWatProfMaxY = max(totWatProf['totWatProf'])
    # # NNO3 concentration profile
    # NConcProf = t3.groupby('Date',as_index=False)['thNewNO3NArea'].sum()
    # #N is ug/cm3 soil water. NNO3*10,000 cm2/m2 * 10,000 m2/ha * 1kg/1e9 ug/ (slab width) == kg/ha
    # #NConcProf['NConcProf'] = NConcProf['thNewNO3N']*(14/64)*10000*10000/1000000000
    # NConcProf['NConcProf'] = NConcProf['thNewNO3NArea']*(14/62)/10/(EOMult*ROWSP)  #14 is N out of NO3 (62) molar mass
    # NNO3ConcProfMaxY = max(NConcProf['NConcProf'])

    xdata = np.arange(1,len(totWatProf['Date'].values)+1)
    # tempLay['Date']=tempLay.Date.str.replace(' ', '')
    xdata_date = totWatProf['Date'].values
    xdata_date2 = np.array([to_datetime(xi) for xi in xdata_date])
    # totWatProf['Date']=totWatProf.Date.str.replace(' ', '')
    ydata1 = totWatProf['totWatProf'].values
    ax[0].plot(xdata, ydata1,'-', color=c_list[i], marker=marker_list[i],markersize=3,label = folder_list[count]) #1) total profile NO3
    #======================================================
    # Group by layer
    layers = t3.Layer.unique()
    print('layers = ', layers)
     #i) first layer (5cm)
    layer = layers[0]
    print('layer = ', layer)
    temp = t3.loc[t3['Layer']==layer]
    depth = max(temp['Y'])
    # total water by layer
    totWatLay = temp.groupby(['Date','Layer'],as_index=False)['thNewArea'].sum()
    totWatLay['totWatLay'] = totWatLay['thNewArea']/(EOMult*ROWSP)*10
    ydata = totWatLay['totWatLay'].values
    ax[1].plot(xdata, ydata,color=c_list[i], marker=marker_list[i],markersize=3, label = folder_list[count])
    #==========================================================   
    #ii) second layer (10cm)
    layer = layers[1]
    print('layer = ', layer)
    temp = t3.loc[t3['Layer']==layer]
    # total water by layer
    totWatLay = temp.groupby(['Date','Layer'],as_index=False)['thNewArea'].sum()
    totWatLay['totWatLay'] = totWatLay['thNewArea']/(EOMult*ROWSP)*10
    ydata = totWatLay['totWatLay'].values
    ax[2].plot(xdata, ydata,color=c_list[i], marker=marker_list[i],markersize=3, label = folder_list[count])
    #==========================================================   
    #iii) third layer (21cm)
    layer = layers[2]
    print('layer = ', layer)
    temp = t3.loc[t3['Layer']==layer]
    # total water by layer
    totWatLay = temp.groupby(['Date','Layer'],as_index=False)['thNewArea'].sum()
    totWatLay['totWatLay'] = totWatLay['thNewArea']/(EOMult*ROWSP)*10
    ydata = totWatLay['totWatLay'].values
    ax[3].plot(xdata, ydata,color=c_list[i], marker=marker_list[i],markersize=3, label = folder_list[count])
    #==========================================================   
    #iv) fourth layer (30cm)
    layer = layers[3]
    print('layer = ', layer)
    temp = t3.loc[t3['Layer']==layer]
    # total water by layer
    totWatLay = temp.groupby(['Date','Layer'],as_index=False)['thNewArea'].sum()
    totWatLay['totWatLay'] = totWatLay['thNewArea']/(EOMult*ROWSP)*10
    ydata = totWatLay['totWatLay'].values
    ax[4].plot(xdata, ydata,color=c_list[i], marker=marker_list[i],markersize=3, label = folder_list[count])

    count = count +1
    #==========================================================

ax[0].legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
ax[0].set(ylabel='Water content [mm]') #xlabel='Date',
ax[0].set_title('Total water content in soil profile')
#extract substring of the xtick label
ax[0].set_xticks(np.arange(xdata[0],xdata[-1]+1,8))
ax[0].set_xticklabels([])
ax[0].set_xlim(xdata[0], xdata[-1])
ax[0].set_ylim(0,450)
ax[0].grid(color='0.9')

ax[1].legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
ax[1].set(ylabel='Water content[mm]') 
ax[1].set_title('Total Water at soil layer [5cm]')
#extract substring of the xtick label
ax[1].set_xticks(np.arange(xdata[0],xdata[-1]+1,8))
ax[1].set_xticklabels([])
# ax[1].set_xticklabels(xdata_date[0::8], rotation=90)  #some_list[start:stop:step]
ax[1].set_xlim(xdata[0], xdata[-1])
ax[1].set_ylim(0,50)
ax[1].grid(color='0.9')

ax[2].legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
ax[2].set(ylabel='Water content[mm]') 
ax[2].set_title('Total Water at soil layer [10cm]')
#extract substring of the xtick label
ax[2].set_xticks(np.arange(xdata[0],xdata[-1]+1,8))
ax[2].set_xticklabels([])
# ax[2].set_xticklabels(xdata_date[0::8], rotation=90)  #some_list[start:stop:step]
ax[2].set_xlim(xdata[0], xdata[-1])
ax[2].set_ylim(0,50)
ax[2].grid(color='0.9')

ax[3].legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
ax[3].set(ylabel='Water content[mm]') 
ax[3].set_title('Total Water at soil layer [21cm]')
#extract substring of the xtick label
ax[3].set_xticks(np.arange(xdata[0],xdata[-1]+1,8))
ax[3].set_xticklabels([])
ax[3].set_xlim(xdata[0], xdata[-1])
ax[3].set_ylim(0,50)
ax[3].grid(color='0.9')

ax[4].legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
ax[4].set(ylabel='Water content[mm]') 
ax[4].set(xlabel='Date [MM/DD/YY]') 
ax[4].set_title('Total Water at soil layer [30cm]')
#extract substring of the xtick label
ax[4].set_xticks(np.arange(xdata[0],xdata[-1]+1,8))
ax[4].set_xticklabels(xdata_date2[0::8], rotation=90)  #some_list[start:stop:step]
ax[4].set_xlim(xdata[0], xdata[-1])
ax[4].set_ylim(0,50)
ax[4].grid(color='0.9')

plt.tight_layout()
# fig_name = "D:\\ACSL_EJ\\FSP_Project_Kate\\Seasonal_sim\\residue_effect\\" + g03_fname[-20:-4] + '_'+'g03_water_comparison.jpg'
# plt.savefig(fig_name) #, dpi=150)
plt.show()

