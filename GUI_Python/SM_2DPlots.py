##Program: 2D plot of 2DSOIL output -g03 NodeGraphics
##Author: Eunjin Han
##Institute: USDA-ARS-ACSL
##Date: November 30, 2022
##===================================================================
from pathlib import Path

from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib import ticker
import pandas as pd
import matplotlib.mlab as mlab
import datetime    #to convert date to doy or vice versa
import os
from datetime import datetime
from matplotlib.cm import ScalarMappable

#==============================================================================
def SM_2DPlots(id_str: str, start_date, end_date, file_path_root: Path,):

    #Create a new folder to save images
    fig_path = file_path_root / Path("2D_Fig")
    fig_path.mkdir(exist_ok=True)

    g03_fname = file_path_root / f"{id_str}.G03"
    df=pd.read_csv(g03_fname)
    df.columns = df.columns.str.replace(' ', '')  # remove special character
    df['Date']=df.Date.str.replace(' ', '')
    # select only a few relevant columns
    df2 = df[['Date', 'X', 'Y', 'hNew', 'thNew', 'Temp','NO3N','CO2Conc','O2Conc', 'N2OConc']] #'ConcN']]
    dt = pd.to_datetime(df2['Date'])

    df2 = df2.assign(
        Month=dt.dt.month,
        Day=dt.dt.day,
        YEAR=dt.dt.year,
        Date_Time=dt,
        mmdd=dt.dt.strftime('%m%d')
    )

    df2 = df2[(df2['Date_Time'] >= start_date)& (df2['Date_Time'] <= end_date)]

    #Maura's CLASSIM code
    # varSoilDict = {"hNew":"Soil Matric Potential\n(cm suction)","thNew":"Soil Water Content\n(cm3/cm3)","Temp":"Soil Temperature\n(oC)", "NO3N":"Nitrogen Concentration\n(mg/L)"}
    varFuncSoilDict = {'hNew':'mean','thNew':'mean','Temp':'mean', 'NO3N':'mean', 'CO2Conc':'mean', 'O2Conc':'mean', 'N2OConc':'mean'}  #NO3N => ConcN
    #param = ["hNew", "thNew","Temp", "NO3N", 'CO2Conc', 'O2Conc', 'N2OConc']
    param = ["hNew", "thNew","Temp", "NO3N"] #, 'CO2Conc', 'O2Conc', 'N2OConc']
    varSoilDict = {"hNew":"Matric Potential\n(log(-h))","thNew":"Vol WC\n(cm3/cm3)","Temp":"Temp\n(oC)", "NO3N":"NO3N\n(mg/L)"
                , "CO2Conc":"CO2 \n(ppm*e-8)", "O2Conc":"O2 \n(ppm*e-8)", "N2OConc":"N2O \n(ppm)"}

    # Convert numeric columns once before date loop
    for key in varFuncSoilDict:
        df2[key] = pd.to_numeric(df2[key], errors='coerce')
    df2 = df2.fillna(0)

    rows = 1
    columns = 4 #7 
    #loop for each date
    for ii, (target_date, df3) in enumerate(df2.groupby('Date', sort=True)):
        df3 = df3.filter(['Date', 'hNew','thNew','Temp', 'NO3N','CO2Conc','O2Conc','N2OConc','Date_Time','mmdd','X','Y'],axis=1)

        df_grouped = df3.groupby(['mmdd','X','Y'], as_index=False).agg(varFuncSoilDict)
        temp_mmdd = df_grouped.mmdd.values[0]

        ## Create image
        fig, ax = plt.subplots(rows,columns,figsize=(8,5))  
        fig.suptitle('2D Soil Water Heat Nitrogen' + str(target_date))
        # for var, i in zip(param, range(0,7)): #4)):
        for var, i in zip(param, range(0,4)):
            title = varSoilDict[var]
            new_df = df_grouped.filter(['X','Y',var],axis=1).copy()

            colorMap = "cool"
            if var == "hNew":
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
                # vmin = 0.1
                # vmax = 0.55
                levels = np.linspace(0.05,0.50, 20)   #<<<=====================
                cf = ax[i].contourf(x, y, z,levels=levels, cmap='RdBu') #colorMap)
                plt.colorbar(cf, ax = ax[i], ticks=[x / 100.0 for x in range(5, 50, 5)], shrink=0.9) 
            elif var == "Temp":
                vmin = 5
                vmax = 30
                levels = np.linspace(5.0,30.0, 19)   #<<<=====================
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
            ax[i].tick_params(labelsize=7)
            ax[i].set_title(title, size="medium")
            ax[i].set_ylabel('Depth (cm)')
            if i > 0:
                ax[i].get_yaxis().set_visible(False)
        fig.tight_layout()
        fig_name = file_path_root / Path("2D_Fig") / (str(ii)+'_'+temp_mmdd + '.png')
        fig.savefig(fig_name)
        plt.close(fig)
