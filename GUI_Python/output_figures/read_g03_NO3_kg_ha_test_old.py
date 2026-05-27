##Program: 2D plot of 2DSOIL output -g03 NodeGraphics
##Author: Eunjin Han
##Institute: USDA-ARS-ACSL
##Date: November 30, 2022
##===================================================================
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from os import path # path

def _to_datetime(date):
    """
    Converts a numpy datetime64-like value to an MM/DD/YY string.
    """
    return pd.to_datetime(date).strftime("%m/%d/%y")

#============================================
# read geometry from *.grd and save them into geo_df
def _read_grd(fname):
    f = open(fname,'r')
    temp_str = f.readline() #first line header: ***************** GRID GENERATOR INFORMATION
    temp_str = f.readline() #second line header:  KAT   NumNP    NumEl   NumBP    IJ   NumMat
    temp_str = f.readline()
    values = [x for x in temp_str.split()]
    NumNP = int(values[1])
   # NumMat = int(values[7])
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
# read *.INI to get eomult and rowSP)
def _read_ini_ROWSP_EOMult(fname):
    f = open(fname,'r')
    temp_str = f.readline() #first line header:  ***Initialization data for 2002_101_CTSB location
    temp_str = f.readline() #second line header:  PopRow       RowSP        Plant Density       rowangle       xseed        yseed         cec          eomult
    temp_str = f.readline()
    values = [float(x) for x in temp_str.split()]
    ROWSP = values[1]
    EOMult = values[7]
    f.close()
    return ROWSP, EOMult

#==============================================================================
working_dir = 'D:\\ACSL_EJ\\Irrigation_DST\\Excel2Python\\SB_sim_test\\'
folder_list = ['2002_103_NTSB']
sim_id = '2002_103_NTSB'
# working_dir = 'C:\\Users\\Eunjin.Han\\Documents\\CLASSIM_dev\\run\\'
# folder_list = ['4']
# sim_id = 'Proj_NE_Site'

fig, ax = plt.subplots(2,1,figsize=(9,5))  #two years of data together => total 11 years
fig.suptitle('Soil water content:  ' +sim_id) #g03_fname[-12:-4])
c_list = ['k', 'C1', 'C2','C3','C4','C5', 'C6','C7'] #, 'C8', 'C9']
# c_list = ['c', 'r','b','k','g'] #,'C7'] #, 'C8', 'C9']
marker_list = ["^", "*","+",".","x","v","s"] #, "p", "h", "D", "X"]


#SSM (surface soil moisture),
g03_fname = working_dir + folder_list[0] + '\\' + sim_id + '.G03'
g07_fname = working_dir + folder_list[0] + '\\' + sim_id + '.G07'
grd_fname = working_dir + folder_list[0] + '\\' + sim_id + '.grd'
ini_fname = working_dir + folder_list[0] + '\\' + sim_id + '.ini'
#1)read g03 and g07
df_g03 = pd.read_csv(g03_fname, parse_dates=['        Date'], delim_whitespace=False) #,skiprows=1)
df_g07 = pd.read_csv(g07_fname, parse_dates=['           Date'], delim_whitespace=False)  #,skiprows=1)
# remove special character
df_g03.columns = df_g03.columns.str.replace(' ', '')
df_g07.columns = df_g07.columns.str.replace(' ', '')

#1) Get geometry df by reading *grd
geo_df = _read_grd(grd_fname)
#2) read *.ini to get eomult and rowSP
ROWSP, EOMult = _read_ini_ROWSP_EOMult(ini_fname)

#find depth of each layer by finding the max Y value for each layer
maxY = geo_df['Y'].max()
geo_df_temp = geo_df.copy()
geo_df_temp['Y'] = maxY - geo_df_temp['Y']
# Compute each layer depth in one pass (ordered by layer id)
layer_depth = geo_df_temp.groupby('Layer', sort=True)['Y'].max().tolist()
# print(layer_depth)

# Merge g03 table with geometry table
t3 = pd.merge(geo_df,df_g03,how='inner',left_on=['X','Y'],right_on=['X','Y'])

# Since 2dsoil assigns Y values from the max depth ->0 where the surface is the maximum Depth
# and the bottom of the profile is 0, we have to reverse this for the layer file. Thus we
# subtract the max depth from all the Y's'
maxY = max(t3['Y'])
t3['Y'] = maxY-t3['Y']

t3['thNewArea'] = t3['thNew'] * t3['Area']
t3['thNewNO3NArea'] = t3['thNew'] * t3['NO3N'] * t3['Area']  #thNew[cm3/cm3] * NO3N[ug/cm3] * Area[cm3] => ug NO3N

# First, we need to group the data by day
t3 = t3.groupby(['Date','X','Y'],as_index=False).mean()
t3 = t3.drop(columns=["X","Q","NH4N","hNew","Area"])

# NNO3 concentration profile
NConcProf = t3.groupby('Date',as_index=False)['thNewNO3NArea'].sum()
#NO3 is ug/cm3 soil water.
#N/NO3 = 14/62 (molar mass ratio). 
# Total N mass in unit area: thNewNO3NArea[ug]/(slab area or width)
# => [ug/cm2] * 10^4 m2/ha * 10^4 cm2/m2 * 1kg/10^9 ug = [kg/ha]
# N as NO3 [kg/ha] = NConcProf['thNewNO3NArea'] [ug] * (14/62) / (EOMult*ROWSP) (for slab width in cm) /10 (for unit conversion) 
NConcProf['NConcProf'] = NConcProf['thNewNO3NArea']*(14/62)/10/(EOMult*ROWSP)  # [kg/ha]
NNO3ConcProfMaxY = max(NConcProf['NConcProf'])

xdata = np.arange(1,len(NConcProf['Date'].values)+1)
xdata_date = NConcProf['Date'].values
xdata_date2 = np.array([_to_datetime(xi) for xi in xdata_date])
ydata1 = NConcProf['NConcProf'].values
ax[0].plot(xdata, ydata1,'-', color=c_list[0], marker=marker_list[0],markersize=3,label = 'Total profile NO3') #1) total profile NO3
#======================================================
# Group by layer
for i in range(len(layer_depth)):
    temp = t3.loc[t3['Layer']==i+1]
    depth = layer_depth[i]
    NConcLay = temp.groupby(['Date','Layer'],as_index=False)['thNewNO3NArea'].sum()
    NConcLay['NConcLay'] = NConcLay['thNewNO3NArea']*(14/62)/10/(EOMult*ROWSP)  # [kg/ha]
    ydata = NConcLay['NConcLay'].values
    ax[1].plot(xdata, ydata,color=c_list[i+1], marker=marker_list[i],markersize=3, label = "Depth= " + str(round(depth,1)) + 'cm')

ax[0].set_title('Total profile NO3-N[kg/ha]')
# ax[0].legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
ax[0].set(ylabel='NO3-N [kg/ha]')
#extract substring of the xtick label
ax[0].set_xticks(np.arange(xdata[0],xdata[-1]+1,8))
ax[0].set_xticklabels([])
ax[0].set_xlim(xdata[0], xdata[-1])
ax[0].grid(color='0.9')

ax[1].set_title('NO3-N content by layer [kg/ha]')
ax[1].legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
ax[1].set(ylabel='NO3-N [kg/ha]')
#extract substring of the xtick label
ax[1].set_xticks(np.arange(xdata[0],xdata[-1]+1,8))
ax[1].set_xticklabels(xdata_date2[0::8], rotation=90)  #some_list[start:stop:step]
ax[1].set_xlim(xdata[0], xdata[-1])
# ax.set_ylim(-300,450)
# ax2.set_ylim(0,40)
ax[1].grid(color='0.9')

plt.tight_layout()
# fig_name = "D:\\ACSL_EJ\\FSP_Project_Kate\\Seasonal_sim\\residue_effect\\" + g03_fname[-20:-4] + '_'+'g03_water_comparison.jpg'
# plt.savefig(fig_name) #, dpi=150)
plt.show()

