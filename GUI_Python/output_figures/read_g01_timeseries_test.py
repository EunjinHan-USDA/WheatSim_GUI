##Author: Eunjin Han
##Institute: USDA-ARS-ACSL
##Date: April 1, 2026
##===================================================================
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

def _to_datetime(date):
    """
    Converts a numpy datetime64-like value to an MM/DD/YY string.
    """
    return pd.to_datetime(date).strftime("%m/%d/%y")
#==============================================================================
fname = r'D:\ACSL_EJ\Irrigation_DST\Excel2Python\SB_sim_test\2002_103_NTSB\2002_103_NTSB.G01'
df=pd.read_csv(fname)

#output variables in g01
#   date,      jday,      time,    RSTAGE,    VSTAGE,       PFD,    SolRad,      Tair,      Tcan,    Pgross,      Pnet,        
# gs,      PSIL,       LAI,    LAREAT,   totalDM,    rootDM,    stemDM,    leafDM,    seedDM,     podDM,    DeadDM,    Tr_pot,    Tr_act,   
# wstress,   Nstress,     Limit

# #Maura's CLASSIM code
varFuncPlantDict = {'LAI':'mean','wstress':'mean','Tr_pot':'mean','Tr_act':'mean',
                   'totalDM':'mean','rootDM':'mean','stemDM':'mean','leafDM':'mean','seedDM':'mean','podDM':'mean','DeadDM':'mean'}
param = ["LAI", "wstress","Tr_pot" ,"Tr_act", "totalDM", "rootDM","stemDM", "leafDM", "seedDM", "podDM", "DeadDM"]
varPlantDict = {"LAI":"Leaf Area Index","wstress":"water stress", "Tr_pot":"potential transpiration","Tr_act":"actual transpiration",
               "totalDM":"total plant dry weight","rootDM":"root dry weight", "stemDM":"stem dry weight","leafDM":"leaf dry weight","seedDM":"seed dry weight(g/plant)","podDM":"pod dry weight","DeadDM":"dead dry weight"} 

# remove special character
df.columns = df.columns.str.replace(' ', '')

# select only a few relevant columns
df2 = df[['date', 'LAI', 'wstress', 'Tr_pot', 'Tr_act', 'totalDM', 'rootDM', 'stemDM', 'leafDM', 'seedDM', 'podDM', 'DeadDM']]
dt = pd.to_datetime(df2['date'])

df2 = df2.assign(
    Month=dt.dt.month,
    Day=dt.dt.day,
    YEAR=dt.dt.year,
    Date_Time=dt,
    mmdd=dt.dt.strftime('%m%d')
)
# df2['Month'], df2['Day'],df2['YEAR'],df2['Date_Time'],df2['mm-dd']  = zip(*df2['date'].apply(MMDDYYYY))

for key in varFuncPlantDict :
    df2[key] = pd.to_numeric(df2[key],errors='coerce')
df2 = df2.fillna(0)

df_grouped_0 = df2.groupby(['date','mmdd'], as_index=False).agg(varFuncPlantDict )


#=====================================
fig, ax = plt.subplots(3,1,figsize=(8,8))  
fig.suptitle('FSP:  ' + fname[-17:-4])
#fig.suptitle('Plant growth:  ' +id_str) 
c_list = ['k', 'C1', 'C2','C3','C4','C5', 'C6','C7'] #, 'C8', 'C9']
# c_list = ['c', 'r','b','k','g'] #,'C7'] #, 'C8', 'C9'
# marker_list = ["^", "*","+",".","x","v","s"] #, "p", "h", "D", "X"
marker_list = ["^", ".","+",".",".",".","."] #, "p", "h", "D", "X"]

xdata = np.arange(1,len(df_grouped_0['date'].values)+1)
xdata_date = df_grouped_0['date'].values
xdata_date2 = np.array([_to_datetime(xi) for xi in xdata_date])

#1) LAI
ydata1 = df_grouped_0.LAI.values
ax[0].plot(xdata, ydata1,'*-', color=c_list[0], label = 'LAI')

#2) potential vs. actual transpiration
ydata1 = df_grouped_0.Tr_pot.values
ax[1].plot(xdata, ydata1,'^-', color=c_list[1], label = 'Tr_pot')
ydata2 = df_grouped_0.Tr_act.values
ax[1].plot(xdata, ydata2,'*-', color=c_list[2], label = 'Tr_act')

#3) water stress
ydata1 = df_grouped_0.wstress.values
ax[2].plot(xdata, ydata1,'*-', color=c_list[3], label = 'Water stress')

ax[0].set_title('LAI')
ax[0].legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
ax[0].set( ylabel='LAI') 
ax[0].set_xticks(np.arange(xdata[0],xdata[-1]+1,8))
ax[0].set_xticklabels([])
ax[0].set_xlim(xdata[0], xdata[-1])
ax[0].grid(color='0.9')

ax[1].set_title('Potential vs. actual transpiration')
ax[1].legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
ax[1].set(xlabel='Date', ylabel='Transpiration [g/plant/hr]') 
ax[1].set_xticks(np.arange(xdata[0],xdata[-1]+1,8))
ax[1].set_xticklabels([])
ax[1].set_xlim(xdata[0], xdata[-1])
ax[1].grid(color='0.9')

ax[2].set_title('Water Stress Index [actual T / potential T]')
ax[2].legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
ax[2].set( ylabel='Water Stress') 
ax[2].set_xticks(np.arange(xdata[0],xdata[-1]+1,8))
ax[2].set_xticklabels(xdata_date2[0::8], rotation=90)  
ax[2].set_xlim(xdata[0], xdata[-1])
ax[2].set_ylim(0, 1.01)
ax[2].grid(color='0.9')
ax[2].text(
    0.02, 0.03,  # x, y in axes fraction (0..1)
    "[1= no stress, 0= high stress]",
    transform=ax[2].transAxes,
    ha="left",
    va="bottom",
    fontsize=10,
    bbox=dict(facecolor="white", alpha=0.7, edgecolor="gray")
)

plt.tight_layout()
# fig_fname = Path(file_path_root) / f"{id_str}.NO3_by_depth_timeseries.jpg"
# plt.savefig(fig_fname) #, dpi=150)
# plt.close(fig)
plt.show()

#=====================================
#2nd figure for dry matter
fig, ax = plt.subplots(2,1,figsize=(8,6))  
fig.suptitle('FSP:  ' + fname[-17:-4])

#1) totalDM
ax[0].plot(xdata, df_grouped_0.totalDM.values,color=c_list[0], marker=marker_list[0],markersize=3, label = 'totalDM')
ax[0].plot(xdata, df_grouped_0.rootDM.values,color=c_list[1], marker=marker_list[1],markersize=3, label = 'rootDM')
ax[0].plot(xdata, df_grouped_0.DeadDM.values,color=c_list[2], marker=marker_list[2],markersize=3, label = 'deadDM'  )

#2) leaf DM, stem DM, seed DM, pod DM
ax[1].plot(xdata, df_grouped_0.stemDM.values,color=c_list[2], marker=marker_list[1],markersize=3, label = 'stemDM')
ax[1].plot(xdata, df_grouped_0.leafDM.values,color=c_list[3], marker=marker_list[1],markersize=3, label = 'leafDM')
ax[1].plot(xdata, df_grouped_0.seedDM.values,color=c_list[4], marker=marker_list[1],markersize=3, label = 'seedDM')
ax[1].plot(xdata, df_grouped_0.podDM.values,color=c_list[5], marker=marker_list[1],markersize=3, label = 'podDM')


ax[0].set_title('Total Dry Matter')
ax[0].legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
ax[0].set( ylabel='Dry Matter [g/plant]')
ax[0].set_xticks(np.arange(xdata[0],xdata[-1]+1,8))
ax[0].set_xticklabels([])
ax[0].set_xlim(xdata[0], xdata[-1])
ax[0].grid(color='0.9')

ax[1].set_title('Dry Matter by Plant Part')
ax[1].legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
ax[1].set(xlabel='Date', ylabel='Dry Matter [g/plant]')
ax[1].set_xticks(np.arange(xdata[0],xdata[-1]+1,8))
ax[1].set_xticklabels(xdata_date2[0::8], rotation=90)  #some_list[start:stop:step]
ax[1].set_xlim(xdata[0], xdata[-1])
ax[1].grid(color='0.9')

plt.tight_layout()
# fig_fname = Path(file_path_root) / f"{id_str}.NO3_by_depth_timeseries.jpg"
# plt.savefig(fig_fname) #, dpi=150)
# plt.close(fig)
plt.show()