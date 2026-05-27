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
import os
# from os import path # path
# import datetime module from datetime
from datetime import datetime
from matplotlib.cm import ScalarMappable

#convert date in MM/DD/YYYY to separate M, D, and Year columns
def MMDDYYYY(x):
    mm = int(x.split('/')[0])
    dd = int(x.split('/')[1])
    YYYY = int(x.split('/')[2])
    date = datetime(YYYY, mm, dd)  #date object
    # mmdd = date.strftime("%Y") + '-' + date.strftime("%m")+ '-' + date.strftime("%d")
    mmdd = date.strftime("%m")+ '-' + date.strftime("%d")

    # # time_data = "25/05/99 02:35:5.523" # consider the time stamp in string format
    # # # day/month/year hours/minutes/seconds-micro
    # # # seconds
    # format_data = "%m/%d/%yyyy"  # format the string in the given format :

    # # Using strptime with datetime we will format
    # # string into datetime
    # date = datetime.strptime(x.strip(), format_data)
    return mm, dd, YYYY, date, mmdd

#==============================================================================

# fname = r'D:\ACSL_EJ\o2Conc_BasedDecompostion\ExcelInterface\Kansas\MOSI06_orig\MOSI06.G03'
# working_dir = 'D:\\ACSL_EJ\\o2Conc_BasedDecompostion\\ExcelInterface\\Kansas\\MOSI06_orig'  #<<<=====================
# working_dir = 'D:\\ACSL_EJ\\o2Conc_BasedDecompostion\\ExcelInterface\\Kansas\\MOSI06'  #<<<=====================
working_dir = 'D:\\ACSL_EJ\\FSP_paper\\Rotation_run\\NT\\103\\2004_103_NTMZ\\'

fig_path = os.path.join(working_dir, "2D_Fig")
# Check whether the specified path exists or not
isExist = os.path.exists(fig_path)
if not isExist:
   os.makedirs(fig_path)    # Create a new directory because it does not exist

# fname = os.path.join(working_dir, "MOSI06.G03") #<<<=====================
fname = os.path.join(working_dir, "2004_103_NTMZ.G03") #<<<=====================
df=pd.read_csv(fname)
# df=pd.read_csv(fname, parse_dates=["Date"])
# df['mm-dd'] = df.Date.map(lambda x: x.strftime('%m-%d'))
# remove special character
df.columns = df.columns.str.replace(' ', '')
df['Date']=df.Date.str.replace(' ', '')
# select only a few relevant columns
df2 = df[['Date', 'X', 'Y', 'hNew', 'thNew', 'Temp','NO3N','CO2Conc','O2Conc', 'N2OConc']] #'ConcN']]
df2['Month'], df2['Day'],df2['YEAR'],df2['Date_Time'],df2['mmdd']   = zip(*df2['Date'].apply(MMDDYYYY))

# date1 = pd.Timestamp(2006,5,4) #<<<=====================
# # date1 = pd.Timestamp(2006,5,7) #<<<=====================
# date2 = pd.Timestamp(2006,6,20) #<<<=====================
date1 = pd.Timestamp(2004,9,27) #<<<=====================
# date1 = pd.Timestamp(2006,5,7) #<<<=====================
date2 = pd.Timestamp(2004,9,27) #<<<=====================
# df2[(df2['Date_Time'] > pd.Timestamp(2006,4,15))]
df2 = df2[(df2['Date_Time'] >= date1)& (df2['Date_Time'] <= date2)]

# target_date = '05/08/2006'
# df2 = df2.loc[df2['Date'] == target_date].filter(['Date', 'hNew','thNew','Temp', 'NO3N','CO2Conc','O2Conc','N2OConc','X','Y'],axis=1)

#Maura's CLASSIM code
# varSoilDict = {"hNew":"Soil Matric Potential\n(cm suction)","thNew":"Soil Water Content\n(cm3/cm3)","Temp":"Soil Temperature\n(oC)", "NO3N":"Nitrogen Concentration\n(mg/L)"}
varFuncSoilDict = {'hNew':'mean','thNew':'mean','Temp':'mean', 'NO3N':'mean', 'CO2Conc':'mean', 'O2Conc':'mean', 'N2OConc':'mean'}  #NO3N => ConcN
param = ["hNew", "thNew","Temp", "NO3N", 'CO2Conc', 'O2Conc', 'N2OConc']
varSoilDict = {"hNew":"Matric Potential\n(log(-h))","thNew":"Vol WC\n(cm3/cm3)","Temp":"Temp\n(oC)", "NO3N":"NO3N\n(mg/L)"
               , "CO2Conc":"CO2 \n(ppm*e-8)", "O2Conc":"O2 \n(ppm*e-8)", "N2OConc":"N2O \n(ppm)"}
# df_collection = {}

rows = 1
columns = 7 #4
#loop for each date
for ii in range(df2.Date.unique().shape[0]):
    target_date = df2.Date.unique()[ii]
    df3 = df2.loc[df2['Date'] == target_date].filter(['Date', 'hNew','thNew','Temp', 'NO3N','CO2Conc','O2Conc','N2OConc','Date_Time','mmdd','X','Y'],axis=1)

    for key in varFuncSoilDict:
        df3[key] = pd.to_numeric(df3[key],errors='coerce')
    df3 = df3.fillna(0)
    # df_grouped = df3.groupby(['Date_Time','X','Y'], as_index=False).agg(varFuncSoilDict)
    df_grouped = df3.groupby(['mmdd','X','Y'], as_index=False).agg(varFuncSoilDict)
    temp_mmdd = df_grouped.mmdd.values[0]

    ## Create image
    fig, ax = plt.subplots(rows,columns,figsize=(12,5))  
    fig.suptitle( fname[-10:] + ' - ' +target_date)
    for var, i in zip(param, range(0,7)): #4)):
        title = varSoilDict[var]
        #title, unit = self.varSoilDict[var]
        # new_df = df_collection.filter(['X','Y',var],axis=1)
        new_df = df_grouped.filter(['X','Y',var],axis=1)

        colorMap = "cool"
        if var == "hNew":
            # colorMap = "cool_r"
            # new_df[var] = new_df[var].abs()
            new_df[var] = np.log10(new_df[var].abs())  #convert to log scale before plotting
        elif var == "O2Conc":
            new_df[var] = new_df[var]/(10**4)  
        elif var == "CO2Conc":
            new_df[var] = new_df[var]/(10**4) 

        new_arr = new_df.values
        nx = new_df['X'].nunique()
        ny = new_df['Y'].nunique()
        x = new_arr[:,0].reshape(nx,ny)
        y = new_arr[:,1].reshape(nx,ny)
        z = new_arr[:,2].reshape(nx,ny)
        maxY = max(map(max, y))
        y = maxY - y
        #ax.add_subplot(rows, columns, i)
        ax[i].invert_yaxis()
        levels = ticker.MaxNLocator(nbins=15).tick_values(z.min(), z.max())
        norm = colors.BoundaryNorm(levels, ncolors=256, clip=True)
        if var == "hNew":
            levels = np.linspace(-1.0,5.0, 20)   #<<<=====================
            cf = ax[i].contourf(x, y, z,levels=levels, cmap='coolwarm') #colorMap)
            plt.colorbar(cf, ax = ax[i], ticks=[x / 10.0 for x in range(-10, 50, 5)], shrink=0.9) 
            # cf = ax[i].contourf(x, y, z, levels=levels, locator=ticker.LogLocator(), cmap=colorMap)
            # plt.colorbar(cf,ax = ax[i],shrink=0.9)
        elif var == "thNew":
            vmin = 0.1
            vmax = 0.45
            # cf = ax[i].contourf(x, y, z,vmin=vmin, vmax=vmax, cmap=colorMap)
            # plt.colorbar(cf, ax = ax[i], ticks=[x / 100.0 for x in range(10, 50, 5)],shrink=0.9)
            # plt.colorbar(cf,ax = ax[i],shrink=0.9)
            levels = np.linspace(0.1,0.45, 20)   #<<<=====================
            cf = ax[i].contourf(x, y, z,levels=levels, cmap='RdBu') #colorMap)
            plt.colorbar(cf, ax = ax[i], ticks=[x / 100.0 for x in range(10, 50, 5)], shrink=0.9) 
        elif var == "Temp":
            vmin = 10
            vmax = 28
            # cf = ax[i].contourf(x, y, z,vmin=vmin, vmax=vmax) #, cmap=colorMap)
            # plt.colorbar(ScalarMappable(norm=cf.norm, cmap=cf.cmap),ax = ax[i], ticks=range(vmin, vmax+5, 5))
            # cf = ax[i].contourf(x, y, z,vmin=vmin, vmax=vmax, cmap=colorMap)
            # plt.colorbar(cf, ax = ax[i], ticks=range(vmin, vmax+2, 2),shrink=0.9)
            levels = np.linspace(10.0,28.0, 19)   #<<<=====================
            cf = ax[i].contourf(x, y, z,levels=levels, cmap='coolwarm')
            plt.colorbar(cf, ax = ax[i], ticks=range(vmin, vmax+2, 2), shrink=0.9)      
        elif var == "CO2Conc":
            vmin = 0
            vmax = 22
            levels = np.linspace(0.0,22.0, 23)   #<<<=====================
            cf = ax[i].contourf(x, y, z,levels=levels, cmap=colorMap)
            plt.colorbar(cf, ax = ax[i], ticks=range(vmin, vmax+2, 2), shrink=0.9)
        elif var == "O2Conc":
            vmin = 0
            vmax = 22
            levels = np.linspace(0.0,22.0, 23)   #<<<=====================
            cf = ax[i].contourf(x, y, z,levels=levels, cmap=colorMap)
            plt.colorbar(cf, ax = ax[i], ticks=range(vmin, vmax+2, 2), shrink=0.9)
        else:
            cf = ax[i].contourf(x, y, z, levels=levels, cmap=colorMap)
            plt.colorbar(cf,ax = ax[i],shrink=0.9)
        # fig.colorbar(cf,shrink=0.9)
        # if var == "hNew":
        #     ax[i].invert_yaxis()
        ax[i].tick_params(labelsize=7)
        ax[i].set_title(title, size="medium")
        ax[i].set_ylabel('Depth (cm)')
        if i > 0:
            ax[i].get_yaxis().set_visible(False)
        plt.tight_layout()
    plt.show()
    # fig_path = os.path.join(working_dir, "2D_Fig")
    # fig_fname = os.path.join(fig_path, str(ii)+'_'+temp_mmdd + '.png')
    # plt.savefig(fig_fname)
