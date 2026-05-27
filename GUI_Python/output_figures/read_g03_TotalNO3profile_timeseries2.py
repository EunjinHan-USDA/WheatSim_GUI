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
working_dir = 'D:\\ACSL_EJ\\FSP_Project_Kate\\Seasonal_sim\\residue_effect\\'
# sim_list = ['2011_117_NTMZ_R0', '2011_117_NTMZ_R1', '2011_117_NTMZ_R2' ,'2011_117_NTMZ_R3', '2011_117_NTMZ_R4']
sim_list = ['2017_117_NTMZ_R0', '2017_117_NTMZ_R1', '2017_117_NTMZ_R2' ,'2017_117_NTMZ_R3', '2017_117_NTMZ_R4']

fig, ax = plt.subplots(5,1,figsize=(9,10))  #two years of data together => total 11 years 
fig.suptitle('NO3 (kg[N]/ha):  ' + sim_list[0][:13]) #g03_fname[-12:-4])
# c_list = ['C1', 'C2','C3','C4','C6'] #,'C7'] #, 'C8', 'C9']
c_list = ['c', 'r','b','k','g'] #,'C7'] #, 'C8', 'C9']
marker_list = ["^", "*","+",".","x"] 

# for i in range(len(sim_list)):
for i in range(5):
    sim_id = sim_list[i]
    working_dir + sim_id + '\\' + sim_id + '.lyr'

    #SSM (surface soil moisture),
    g03_fname = working_dir + sim_id + '\\' + sim_id + '.G03'
    g07_fname = working_dir + sim_id + '\\' + sim_id + '.G07'
    #1)read g03 and g07
    df_g03 = pd.read_csv(g03_fname) #,skiprows=1)
    df_g07 = pd.read_csv(g07_fname) #,skiprows=1)
    # remove special character
    df_g03.columns = df_g03.columns.str.replace(' ', '')
    df_g07.columns = df_g07.columns.str.replace(' ', '')

    grd_fname = working_dir + sim_id + '\\' + sim_id + '.grd'
    #1-1) Get geometry df by reading *grd
    geo_df = read_grd(grd_fname)

    # read *.lyr to get eomult and rowSP
    ini_fname = working_dir + sim_id + '\\' + sim_id + '.ini'
    ROWSP, EOMult = read_ini(ini_fname)


    # Merge g03 table with geometry table
    t3 = pd.merge(geo_df,df_g03,how='inner',left_on=['X','Y'],right_on=['X','Y'])

    # Since 2dsoil assigns Y values from the max depth ->0 where the surface is the maximum Depth
    # and the bottom of the profile is 0, we have to reverse this for the layer file. Thus we
    # subtract the max depth from all the Y's'
    maxY = max(t3['Y'])
    t3['Y'] = maxY-t3['Y']

    t3['thNewArea'] = t3['thNew'] * t3['Area']
    t3['thNewNO3NArea'] = t3['thNew'] * t3['NO3N'] * t3['Area']

    # First, we need to group the data by day
    t3 = t3.groupby(['Date','X','Y'],as_index=False).mean()
    t3 = t3.drop(columns=["X","Q","NH4N","hNew","Area"])

    # NNO3 concentration profile
    NConcProf = t3.groupby('Date',as_index=False)['thNewNO3NArea'].sum()
    #N is ug/cm3 soil water. NNO3*10,000 cm2/m2 * 10,000 m2/ha * 1kg/1e9 ug/ (slab width) == kg/ha
    #NConcProf['NConcProf'] = NConcProf['thNewNO3N']*(14/64)*10000*10000/1000000000
    NConcProf['NConcProf'] = NConcProf['thNewNO3NArea']*(14/62)/10/(EOMult*ROWSP)  #14 is N out of NO3 (62) molar mass
    NNO3ConcProfMaxY = max(NConcProf['NConcProf'])

    # fig, ax = plt.subplots(2,1,figsize=(9,6))  #two years of data together => total 11 years
    # fig.suptitle('NO3 (kg[N]/ha):  ' + g03_fname[-12:-4])
    # c_list = ['C1', 'C2','C3','C4','C6','C7'] #, 'C8', 'C9']
    xdata = np.arange(1,len(NConcProf['Date'].values)+1)  #120
    NConcProf['Date']=NConcProf.Date.str.replace(' ', '')
    xdata_date = NConcProf['Date'].values
    ydata1 = NConcProf['NConcProf'].values
    ax[0].plot(xdata[50:], ydata1[50:],'-', color=c_list[i], marker=marker_list[i],markersize=3,label = sim_id[-2:])  #1) total profile NO3

    #======================================================
    # total NO3 [N] by layer
    # Group by layer
    layers = t3.Layer.unique()
    ii = 0
    for layer in layers:
        temp = t3.loc[t3['Layer']==layer]
        depth = max(temp['Y'])
        # NNO3 concentration by layer
        NConcLay = temp.groupby(['Date','Layer'],as_index=False)['thNewNO3NArea'].sum()
        #N is ug/cm3 soil water. NNO3*10,000 cm2/m2 * 10,000 m2/ha * 1kg/1e9 ug/ (slab width) == kg/ha
        #NConcProf['NConcProf'] = NConcProf['thNewNO3N']*(14/64)*10000*10000/1000000000
        NConcLay['NConcLay'] = NConcLay['thNewNO3NArea']*(14/62)/10/(EOMult*ROWSP)  #14 is N out of NO3 (62) molar mass
        ydata = NConcLay['NConcLay'].values
        ax[ii+1].plot(xdata[50:], ydata[50:], color=c_list[i], marker=marker_list[i],markersize=3, label = sim_id[-2:]) #'Layer =' + str(int(depth))+ ' cm')
        if layer == 4:
            break
        ii = ii + 1
#==========================================================

xdata = xdata[50:]
xdata_date = xdata_date[50:]
ax[0].legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
ax[0].set(ylabel='NO3 kg[N]/ha') #xlabel='Date',
ax[0].set_title('Total soil Nitrogen Concentration')
#extract substring of the xtick label
ax[0].set_xticks(np.arange(xdata[0],xdata[-1]+1,8))
ax[0].set_xticklabels([])
ax[0].set_xlim(xdata[0], xdata[-1])
ax[0].set_ylim(0,190)
ax[0].grid(color='0.9')

ax[1].legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
ax[1].set(ylabel='NO3 kg[N]/ha') #xlabel='Date',
ax[1].set_title('Soil Nitrogen by Layer [L=1, 5cm]')
#extract substring of the xtick label
ax[1].set_xticks(np.arange(xdata[0],xdata[-1]+1,8))
ax[1].set_xticklabels([])
ax[1].set_xlim(xdata[0], xdata[-1])
ax[1].set_ylim(0,160)
ax[1].grid(color='0.9')

ax[2].legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
ax[2].set(ylabel='NO3 kg[N]/ha') #xlabel='Date',
ax[2].set_title('Soil Nitrogen by Layer [L=2, 10cm]')
#extract substring of the xtick label
ax[2].set_xticks(np.arange(xdata[0],xdata[-1]+1,8))
ax[2].set_xticklabels([])
ax[2].set_xlim(xdata[0], xdata[-1])
ax[2].set_ylim(0,40)
ax[2].grid(color='0.9')

ax[3].legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
ax[3].set(ylabel='NO3 kg[N]/ha') #xlabel='Date',
ax[3].set_title('Soil Nitrogen by Layer [L=3, 21cm]')
#extract substring of the xtick label
ax[3].set_xticks(np.arange(xdata[0],xdata[-1]+1,8))
ax[3].set_xticklabels([])
ax[3].set_xlim(xdata[0], xdata[-1])
ax[3].set_ylim(0,60)
ax[3].grid(color='0.9')

ax[4].legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
ax[4].set(xlabel='Date [MM/DD]', ylabel='NO3 kg[N]/ha') #xlabel='Date',
ax[4].set_title('Soil Nitrogen by Layer [L=4, 30cm]')
#extract substring of the xtick label
ax[4].set_xticks(np.arange(xdata[0],xdata[-1]+1,8))
ax[4].set_xticklabels(xdata_date[0::8], rotation=90)  #some_list[start:stop:step]
ax[4].set_xlim(xdata[0], xdata[-1])
ax[4].set_ylim(0,20)
ax[4].grid(color='0.9')
plt.tight_layout()
fig_name = working_dir + sim_list[0][:14]+ '_NO3_MZ_ts.jpg'
plt.savefig(fig_name) #, dpi=150)
plt.show()

#======================================================================================

