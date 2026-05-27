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
# working_dir = 'D:\\ACSL_EJ\\FSP_Project_Kate\\Seasonal_sim\\residue_effect\\'
# # sim_list = ['2011_117_NTMZ_R0', '2011_117_NTMZ_R1', '2011_117_NTMZ_R2' ,'2011_117_NTMZ_R3', '2011_117_NTMZ_R4']
# # sim_list = ['2017_117_NTMZ_R0', '2017_117_NTMZ_R1', '2017_117_NTMZ_R2' ,'2017_117_NTMZ_R3', '2017_117_NTMZ_R4']
# sim_list = ['2011_103_NTSB_R0', '2011_103_NTSB_R1', '2011_103_NTSB_R2' ,'2011_103_NTSB_R3', '2011_103_NTSB_R4'] 
# # sim_list = ['2017_103_NTSB_R0', '2017_103_NTSB_R1', '2017_103_NTSB_R2' ,'2017_103_NTSB_R3', '2017_103_NTSB_R4']

working_dir = 'D:\\ACSL_EJ\\FSP_paper\\'

sce_list = ['Rotation_run','Rotation_run_noCC_noRes']
label_list = ['W(CC_R)','T(CC_R)', 'W(NCC_NR)','T(NCC_NR)']

# plot = 103  #NT
# sim_name = '2017_103_NTSB'  #NT
# iTill = 'NT'

# plot = 117  #NT
# sim_name = '2018_117_NTSB'  #NT
# sim_name = '2012_117_NTSB'  #NT
# iTill = 'NT'

plot = 104  #NT
sim_name = '2013_104_NTSB'  #NT
iTill = 'NT'

fig, ax = plt.subplots(figsize=(7,4)) 
fig.suptitle('Total soil water content and surface soil temperature [5cm]:  '+ sim_name)
# c_list = ['C1', 'C2','C3','C4','C6'] #,'C7'] #, 'C8', 'C9']
c_list = ['c', 'C1','b','C4'] #,'g'] #,'C7'] #, 'C8', 'C9']
marker_list = ["^", "*","+",".","x"] 
line_style = ['dotted','solid']
ax2 = ax.twinx()

count = 0
for i in range(len(sce_list)):
    sim_id = sim_name

    #SSM (surface soil moisture),
    g03_fname = working_dir + sce_list[i] + '\\' + iTill+ '\\' + str(plot) + '\\' + sim_id + '\\' + sim_id+ '.g03'
    g07_fname = working_dir + sce_list[i] + '\\' + iTill+ '\\' + str(plot) + '\\' + sim_id + '\\' + sim_id+ '.g07'
    grd_fname = working_dir + sce_list[i] + '\\' + iTill+ '\\' + str(plot) + '\\' + sim_id + '\\' + sim_id+ '.grd'
    ini_fname = working_dir + sce_list[i] + '\\' + iTill+ '\\' + str(plot) + '\\' + sim_id + '\\' + sim_id+ '.ini'

    #1)read g03 and g07
    df_g03 = pd.read_csv(g03_fname) #,skiprows=1)
    df_g07 = pd.read_csv(g07_fname) #,skiprows=1)
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

    varFuncSoilDict = {'Temp':'mean'}
    t3_temp = t3.copy()
    for key in varFuncSoilDict:
        t3_temp[key] = pd.to_numeric(t3_temp[key],errors='coerce')
    t3_temp['Month'], t3_temp['Day'],t3_temp['YEAR'],t3_temp['Date_Time'],t3_temp['mm-dd']  = zip(*t3_temp['Date'].apply(MMDDYYYY))
    df_grouped_0 = t3_temp.groupby(['Date','mm-dd'], as_index=False).agg(varFuncSoilDict)
    xdata = np.arange(1,len(df_grouped_0['mm-dd'].values)+1)  #120
    xdata_date = df_grouped_0['mm-dd'].values
    print(xdata_date) #for debugging


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

    xdata = np.arange(1,len(totWatProf['Date'].values)+1)  #120
    totWatProf['Date']=totWatProf.Date.str.replace(' ', '')
    # xdata_date = totWatProf['Date'].values
    ydata1 = totWatProf['totWatProf'].values
    ax.plot(xdata, ydata1,'-', color=c_list[count], linestyle=line_style[i], marker=marker_list[i],markersize=3,label = label_list[count])  #1) total profile NO3

    #==============================================================================
    #==============================================================================
#   Get temperature data
    #======================================================
    # Group by layer
    layers = t3.Layer.unique()
     #i) first layer (5cm)
    layer = layers[0]
    print('layer = ', layer)
    temp = t3.loc[t3['Layer']==layer]
    depth = max(temp['Y'])
    # temperature by layer
    tempLay = temp.groupby(['Date','Layer'],as_index=False)['Temp'].mean()
    xdata = np.arange(1,len(tempLay['Date'].values)+1)
    # tempLay['Date']=tempLay.Date.str.replace(' ', '')
    # xdata_date = tempLay['Date'].values

    ydata = tempLay['Temp'].values
    ax2.plot(xdata, ydata, color=c_list[count+1], linestyle=line_style[i], marker=marker_list[i],markersize=3, label = label_list[count+1]) 

    count = count + 2

    #==========================================================
# ax.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
# plt.legend(ncol=1,loc='upper left')
ax.set(ylabel='Total soil water content [mm]') 
ax.set(xlabel='Date [mm-dd]') 
# ax.set_title('Total Water at soil layer [30cm]')
#extract substring of the xtick label
ax.set_xticks(np.arange(xdata[0],xdata[-1]+1,8))
ax.set_xticklabels(xdata_date[0::8], rotation=90)  #some_list[start:stop:step]

# ax.set_xlim(xdata[0], xdata[-1])
ax.set_ylim(-300,450)
ax2.set_ylim(0,40)
ax.grid(color='0.9')

ax2.set(ylabel='Soil temperature [5cm] ($^\circ$C)') 

ax.legend(loc=0)
ax2.legend(loc='lower center')

plt.tight_layout()
# fig_name = "D:\\ACSL_EJ\\FSP_paper\\Rotation_run_out_analysis\\Fig\\" + sim_name + '_'+'g03_water_comparison.jpg'
# plt.savefig(fig_name) #, dpi=150)
plt.show()
