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
    df_grd = pd.read_csv(
    fname,
    sep=r"\s+",
    skiprows=4,
    nrows=NumNP,
    header=None,
    names=["n", "X", "Y", "Layer"],
    usecols=[0, 1, 2, 3]  #Read only columns at positions 0, 1, 2, and 3 from the file
)
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
working_dir = 'D:\\ACSL_EJ\\Irrigation_DST\\Parallel_run_climatology\\SB_sim_ens_run\\'
folder_list = ['2002_103_NTSB']
sim_id = '2002_103_NTSB'

fig, ax = plt.subplots(3,1,figsize=(9,8))  #two years of data together => total 11 years
fig.suptitle('Soil water content:  ' +sim_id) #g03_fname[-12:-4])
c_list = ['k', 'C1', 'C2','C3','C4','C5', 'C6','C7'] #, 'C8', 'C9']
# c_list = ['c', 'r','b','k','g'] #,'C7'] #, 'C8', 'C9']
# marker_list = ["^", "*","+",".","x","v","s"] #, "p", "h", "D", "X"]
marker_list = ["^", ".","+",".",".",".","."] #, "p", "h", "D", "X"]


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

# First, we need to group the data by day
t3 = t3.groupby(['Date','X','Y'],as_index=False).mean()
t3 = t3.drop(columns=["X","Q","NH4N","hNew","Area"])

# total water profile
totWatProf = t3.groupby('Date',as_index=False)['thNewArea'].sum()
totWatProf['totWatProf'] = totWatProf['thNewArea']/(EOMult*ROWSP)*10  #unit mm
#totWatProfMaxY = max(totWatProf['totWatProf'])

# Store current simulation total profile water in a dedicated DataFrame.
totWatProf_df = totWatProf[['Date', 'totWatProf']].rename(
    columns={'totWatProf': 'current_totWatProf'}
)

#read ouptut for each individual histroical year and plot them together
for i in range(1996,2020+1):
    print(i)
    hist_year = i
    hist_g03_fname = working_dir + folder_list[0] + '\\' + sim_id + '_' + str(hist_year) + '\\' + sim_id + '_' + str(hist_year) + '.G03'
    df_hist_g03 = pd.read_csv(hist_g03_fname, parse_dates=['        Date'], delim_whitespace=False) #,skiprows=1)
    df_hist_g03.columns = df_hist_g03.columns.str.replace(' ', '')
    t3_hist = pd.merge(geo_df,df_hist_g03,how='inner',left_on=['X','Y'],right_on=['X','Y'])
    t3_hist = t3_hist[['X','Y','Layer','thNew','Area','Date']]  #*******
    maxY = max(t3_hist['Y'])
    t3_hist['Y'] = maxY-t3_hist['Y']
    t3_hist['thNewArea'] = t3_hist['thNew'] * t3_hist['Area']
    t3_hist = t3_hist.groupby(['Date','X','Y'],as_index=False).mean()
    #t3_hist = t3_hist.drop(columns=["X","Q","NH4N","hNew","Area"])
    totWatProf_hist = t3_hist.groupby('Date',as_index=False)['thNewArea'].sum()
    totWatProf_hist['totWatProf'] = totWatProf_hist['thNewArea']/(EOMult*ROWSP)*10  #unit mm
    #save into a df
    #if size of totWatProf_hist['totWatProf'] is smaller than totWatProf['totWatProf'], skip this year (because simulation is not complete due to orthomin terminate)
    if len(totWatProf_hist['totWatProf']) < len(totWatProf['totWatProf']):
        print(f"Skipping historical year {hist_year} due to incomplete simulation.")
        continue
    else:
        totWatProf_df['totWatProf_' + str(hist_year)] = totWatProf_hist['totWatProf'].values

#compute the mean, std, and quantiles of 5% and 95% of total profile water across all historical years for each date
totWatProf_df_temp = totWatProf_df.copy()
totWatProf_df['totWatProf_hist_mean'] = totWatProf_df_temp[[col for col in totWatProf_df_temp.columns if col.startswith('totWatProf_')]].mean(axis=1)
totWatProf_df['totWatProf_hist_std'] = totWatProf_df_temp[[col for col in totWatProf_df_temp.columns if col.startswith('totWatProf_')]].std(axis=1)
totWatProf_df['totWatProf_hist_5%'] = totWatProf_df_temp[[col for col in totWatProf_df_temp.columns if col.startswith('totWatProf_')]].quantile(0.05, axis=1)
totWatProf_df['totWatProf_hist_95%'] = totWatProf_df_temp[[col for col in totWatProf_df_temp.columns if col.startswith('totWatProf_')]].quantile(0.95, axis=1)

xdata = np.arange(1,len(totWatProf['Date'].values)+1)
xdata_date = totWatProf['Date'].values
xdata_date2 = np.array([_to_datetime(xi) for xi in xdata_date])
ydata1 = totWatProf['totWatProf'].values
ax[0].plot(xdata, ydata1,'-', color=c_list[0], marker=marker_list[0],markersize=3,label = 'Total profile water') 
ax[0].plot(xdata, totWatProf_df['totWatProf_hist_mean'].values,'-', color=c_list[1], marker=marker_list[1],markersize=3,label = 'Historical mean') 
ax[0].fill_between(xdata, totWatProf_df['totWatProf_hist_5%'].values, totWatProf_df['totWatProf_hist_95%'].values, color=c_list[1], alpha=0.2, label='Historical 5-95%') 
#======================================================
# Group by layer
layer_daily = (t3.groupby(['Date', 'Layer'], as_index=False).agg(thNewArea_sum=('thNewArea', 'sum'),
thNew_mean=('thNew', 'mean'))
)
layer_daily['totWatLay'] = layer_daily['thNewArea_sum'] / (EOMult * ROWSP) * 10

mm_pivot = layer_daily.pivot(index='Date', columns='Layer', values='totWatLay')
vwc_pivot = layer_daily.pivot(index='Date', columns='Layer', values='thNew_mean')

for layer in mm_pivot.columns:
    depth = layer_depth[int(layer) - 1]
    ax[1].plot(xdata, mm_pivot[layer].values, color=c_list[int(layer)], marker=marker_list[int(layer)],markersize=3, label = "Depth= " + str(round(depth,1)) + 'cm')
    ax[2].plot(xdata, vwc_pivot[layer].values, color=c_list[int(layer)], marker=marker_list[int(layer)],markersize=3, label = "Depth= " + str(round(depth,1)) + 'cm')


# for i in range(len(layer_depth)):
#     temp = t3.loc[t3['Layer']==i+1]
#     depth = layer_depth[i]
#     # print('layer = ', i+1, 'depth = ', depth)
#     # total water by layer
#     totWatLay = temp.groupby(['Date','Layer'],as_index=False)['thNewArea'].sum()
#     totWatLay['totWatLay'] = totWatLay['thNewArea']/(EOMult*ROWSP)*10
#     ydata = totWatLay['totWatLay'].values
#     ax[1].plot(xdata, ydata,color=c_list[i+1], marker=marker_list[i],markersize=3, label = "Depth= " + str(round(depth,1)) + 'cm')

#     # volumetric water content by layer
#     watContLay = temp.groupby(['Date','Layer'],as_index=False)['thNew'].mean()
#     ydata1 = watContLay['thNew'].values
#     ax[2].plot(xdata, ydata1,'-', color=c_list[i+1], marker=marker_list[i],markersize=3, label = "Depth= " + str(round(depth,1)) + 'cm')



ax[0].set_title('Total profile water content [mm]')
ax[0].legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
ax[0].set(ylabel='Soil water content[mm]')
#extract substring of the xtick label
ax[0].set_xticks(np.arange(xdata[0],xdata[-1]+1,8))
ax[0].set_xticklabels([])
ax[0].set_xlim(xdata[0], xdata[-1])
ax[0].grid(color='0.9')

ax[1].set_title('Water content by layer [mm]')
ax[1].legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
ax[1].set(ylabel='Soil water content[mm]')
#extract substring of the xtick label
ax[1].set_xticks(np.arange(xdata[0],xdata[-1]+1,8))
ax[1].set_xticklabels([])
ax[1].set_xlim(xdata[0], xdata[-1])
# ax.set_ylim(-300,450)
# ax2.set_ylim(0,40)
ax[1].grid(color='0.9')

ax[2].set_title('Volumetric water content by layer')
ax[2].legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
ax[2].set(ylabel='soil moisture [cm$^3$/cm$^3$]')
#extract substring of the xtick label
ax[2].set_xticks(np.arange(xdata[0],xdata[-1]+1,8))
ax[2].set_xticklabels(xdata_date2[0::8], rotation=90)  #some_list[start:stop:step]
ax[2].set_xlim(xdata[0], xdata[-1])
ax[2].grid(color='0.9')


plt.tight_layout()
# fig_name = "D:\\ACSL_EJ\\FSP_Project_Kate\\Seasonal_sim\\residue_effect\\" + g03_fname[-20:-4] + '_'+'g03_water_comparison.jpg'
# plt.savefig(fig_name) #, dpi=150)
plt.show()

