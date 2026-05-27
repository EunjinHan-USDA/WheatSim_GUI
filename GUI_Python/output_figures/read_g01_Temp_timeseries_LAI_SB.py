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
#SSM (surface soil moisture), 
# fname = r'D:\Maizsim2\BARC_Nitrogen\NFLN05\BARC05LN.G03'
fname = r'D:\ACSL_EJ\FSP_Project_Kate\Rotation_sim\ExcelInterface\CT\2003_116_CTSB\2003_116_CTSB.G01'
df=pd.read_csv(fname)

#output variables in g01
#   date,      jday,      time,    RSTAGE,    VSTAGE,       PFD,    SolRad,      Tair,      Tcan,    Pgross,      Pnet,        
# gs,      PSIL,       LAI,    LAREAT,   totalDM,    rootDM,    stemDM,    leafDM,    seedDM,     podDM,    DeadDM,    Tr_pot,    Tr_act,   
# wstress,   Nstress,     Limit

# #Maura's CLASSIM code
# varFuncSoilDict = {'hNew':'mean','thNew':'mean','Temp':'mean'}  #'NO3N':'mean',
# param = ["hNew", "thNew","Temp"]
# varSoilDict = {"hNew":"Soil Matric Potential\n(cm suction)","thNew":"Soil Water Content\n(cm3/cm3)","Temp":"Temperature\n(oC)"} #"NO3N":"Nitrogen Concentration\n(mg/L)",\
varFuncSoilDict = {'LAI':'mean','wstress':'mean','Tr_pot':'mean','Tr_act':'mean','seedDM':'mean'}
param = ["LAI", "wstress","Tr_pot" ,"Tr_act", "seedDM"]
varSoilDict = {"LAI":"Leaf Area Index","wstress":"water stress", "Tr_pot":"potential transpiration","Tr_act":"actual transpiration","seedDM":"seed dry weight(g/plant)"} #"NO3N":"Nitrogen Concentration\n(mg/L)",\

df_collection = {}
# remove special character
df.columns = df.columns.str.replace(' ', '')

# select only a few relevant columns
df2 = df[['date', 'LAI', 'wstress', 'Tr_pot', 'Tr_act', 'seedDM']]

df2['Month'], df2['Day'],df2['YEAR'],df2['Date_Time'],df2['mm-dd']  = zip(*df2['date'].apply(MMDDYYYY))

for key in varFuncSoilDict:
    df2[key] = pd.to_numeric(df2[key],errors='coerce')

df2 = df2.fillna(0)

df_grouped_0 = df2.groupby(['date','mm-dd'], as_index=False).agg(varFuncSoilDict)

# df_grouped_0 = df_0.groupby(['mm-dd','X','Y'], as_index=False).agg(varFuncSoilDict)  #wrong!!!!
# df_grouped_1 = df_1.groupby(['mm-dd','X','Y'], as_index=False).agg(varFuncSoilDict)
# df_grouped_2 = df_2.groupby(['mm-dd','X','Y'], as_index=False).agg(varFuncSoilDict)
# df_grouped_3 = df_3.groupby(['mm-dd','X','Y'], as_index=False).agg(varFuncSoilDict)

#=================
#=====================================
# fig, ax = plt.subplots()
fig, ax = plt.subplots(3,1,figsize=(9,8))  #two years of data together => total 11 years 
fig.suptitle('FSP:  ' + fname[-17:-4])
c_list = ['C1', 'C2'] #,'C3','C4'] #, 'C6', 'C7', 'C8', 'C9']
#1) LAI
xdata = np.arange(1,len(df_grouped_0['mm-dd'].values)+1)  #120
xdata_date = df_grouped_0['mm-dd'].values
ydata1 = df_grouped_0.LAI.values

ax[0].plot(xdata, ydata1,'*-', color=c_list[0], label = 'LAI')

# ax[0].legend(ncol=3,loc='lower left')
ax[0].legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
ax[0].set( ylabel='LAI') #xlabel='Date',
ax[0].set_title('LAI')
#extract substring of the xtick label
ax[0].set_xticks(np.arange(xdata[0],xdata[-1]+1,4))
ax[0].set_xticklabels(xdata_date[0::4], rotation=90)  #some_list[start:stop:step]
ax[0].set_xlim(xdata[0], xdata[-1])
ax[0].grid(color='0.9')

# #2)soil water content (cm3/cm3])
# ydata1 = df_grouped_0.wstress.values
# ax[1].plot(xdata, ydata1,'*-', color=c_list[0], label = 'water stress')

# ax[1].legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
# ax[1].set(xlabel='Date [MM-DD]', ylabel='water stress') #xlabel='Date',
# ax[1].set_title('Water Stress')
# #extract substring of the xtick label
# ax[1].set_xticks(np.arange(xdata[0],xdata[-1]+1,4))
# ax[1].set_xticklabels(xdata_date[0::4], rotation=90)  #some_list[start:stop:step]
# ax[1].set_xlim(xdata[0], xdata[-1])
# ax[1].grid(color='0.9')

ydata1 = df_grouped_0.Tr_pot.values
ax[1].plot(xdata, ydata1,'^-', color=c_list[0], label = 'Tr_pot')

ydata2 = df_grouped_0.Tr_act.values
ax[1].plot(xdata, ydata2,'*-', color=c_list[1], label = 'Tr_act')

ax[1].legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
ax[1].set(xlabel='Date [MM-DD]', ylabel='Transpiration [g/plant/hr]') #xlabel='Date',
ax[1].set_title('Potential vs. actual transpiration')
#extract substring of the xtick label
ax[1].set_xticks(np.arange(xdata[0],xdata[-1]+1,4))
ax[1].set_xticklabels(xdata_date[0::4], rotation=90)  #some_list[start:stop:step]
ax[1].set_xlim(xdata[0], xdata[-1])
ax[1].grid(color='0.9')

#3) water stress
xdata = np.arange(1,len(df_grouped_0['mm-dd'].values)+1)  #120
xdata_date = df_grouped_0['mm-dd'].values
ydata1 = df_grouped_0.wstress.values

ax[2].plot(xdata, ydata1,'*-', color=c_list[0], label = 'Water stress')

# ax[0].legend(ncol=3,loc='lower left')
ax[2].legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
ax[2].set( ylabel='Water Stress') #xlabel='Date',
ax[2].set_title('Water Stress')
#extract substring of the xtick label
ax[2].set_xticks(np.arange(xdata[0],xdata[-1]+1,4))
ax[2].set_xticklabels(xdata_date[0::4], rotation=90)  #some_list[start:stop:step]
ax[2].set_xlim(xdata[0], xdata[-1])
ax[2].grid(color='0.9')

plt.tight_layout()
plt.show()
# #plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=None, hspace=None)
# fig.subplots_adjust(left=0.08, right=.962, bottom=0.105, top=0.926, wspace=0.2, hspace=0.48)
# plt.savefig("UK_oat_SM_LAI_input_check.png", dpi=150)

# #================
# rows = 1
# columns = 3

# ## Create image
# fig, ax = plt.subplots(rows,columns,figsize=(9,5))  #two years of data together => total 11 years 
# fig.suptitle('2D Soil Water Heat:  ' + fname[-12:-4] + '-' +target_date)
# for var, i in zip(param, range(0,3)):
#     title = varSoilDict[var]
#     #title, unit = self.varSoilDict[var]
#     new_df = df_collection.filter(['X','Y',var],axis=1)

#     colorMap = "cool"
#     if var == "hNew":
#         colorMap = "cool_r"
#         new_df[var] = new_df[var].abs()
#     new_arr = new_df.values
#     nx = new_df['X'].nunique()
#     ny = new_df['Y'].nunique()
#     x = new_arr[:,0].reshape(nx,ny)
#     y = new_arr[:,1].reshape(nx,ny)
#     z = new_arr[:,2].reshape(nx,ny)
#     maxY = max(map(max, y))
#     y = maxY - y
#     #ax.add_subplot(rows, columns, i)
#     ax[i].invert_yaxis()
#     levels = ticker.MaxNLocator(nbins=15).tick_values(z.min(), z.max())
#     norm = colors.BoundaryNorm(levels, ncolors=256, clip=True)
#     if var == "hNew":
#         cf = ax[i].contourf(x, y, z, locator=ticker.LogLocator(), cmap=colorMap)   
#     else:
#         cf = ax[i].contourf(x, y, z, levels=levels, cmap=colorMap)   
#     fig.colorbar(cf,shrink=0.9)
#     if var == "hNew":
#         ax[i].invert_yaxis()
#     ax[i].tick_params(labelsize=7)
#     ax[i].set_title(title, size="medium")
#     ax[i].set_ylabel('Depth (cm)')
#     if i > 1:
#         ax[i].get_yaxis().set_visible(False)
#     plt.tight_layout()
#     plt.tight_layout()
# plt.show()
