from datetime import time
from pathlib import Path
import pandas as pd
import subprocess
import os
import time as time_module

def _normalize_cols(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.columns = [str(c).strip().lower() for c in out.columns]
    return out

# (Source: How to use the Excel tool.docx))
# In the CreateSoils folder, copy the files from the CreateSoils folder
# CreateSoilsFiles.exe
# Rosetta.exe
# GridGenDll.DLL
# Vangenuch.xls
# CreateSoil program notes.pdf

# The executables and secondary files needed are described below.
# The following files are used to create the grid and soil files. These are not executed by the vba code but are executed in a separate DOS command file: 
# 1)CreateSoilFIles.exe 	This program calls GridGen.DLL and Rosetta.exe
# 2)GridGen.DLL	a fortran dll that creates the finite element mesh
# 3)Rosetta.exe	A program that uses pedotransfer functions and a neural net to estimate soil hydraulic properties from soil texture data. The program (source code was obtained from:
# https://www.ars.usda.gov/pacific-west-area/riverside-ca/agricultural-water-efficiency-and-salinity-research-unit/docs/model/rosetta-model/
#  The program was mostly written by Marcel Schapp
#--------------------
# CreateSoilFiles.exe usage:

# The excel interface creates a batch file called grid1.bat. This is an example of the contents:
# D:\Maizsim07\CreateSoils\CreateSoilFiles.exe "D:\MAIZSIM07\AgMipEt\Iowa06\Iowa06.lyr" /GN Iowa06 /SN Harps
# del output
# del element_elm
# del grid_bnd
# del datagen2.dat
# Dir  *.*  >dir.txt

# To use CreateSoilFiles.exe on its own:
# The command (see above) is called from the path where soil and grid files should be stored. 
# The command line requires a fully formed path to the executable’s source because the executable is in a different folder than the one where the files are created.
# The  input file (…lyr) also needs a fully formed path. This makes the location of the layer file and location of the program independent of where it is run from. 
# The arguments GN and SN are the grid name and soil name.


def RunCreateSoilExe (
    id_str: str,
    description_df: pd.DataFrame,   # for soil name
    file_path_createsoil: Path,    # for CreateSoilFiles.exe path
    file_path_root: Path,    #for *.lyr file path
) -> Path:
    """Python conversion of VBA Sub WriteWatMoveP(idStr As String)."""

    desc = _normalize_cols(description_df)

    req_desc = {"id", "soilname"}

    if not req_desc.issubset(desc.columns):
        raise ValueError(f"Description missing columns: {sorted(req_desc - set(desc.columns))}")

    desc_row = desc.loc[desc["id"].astype(str) == str(id_str)]
    if desc_row.empty:
        raise ValueError(f"ID '{id_str}' not found in Description sheet.")
    desc_row = desc_row.iloc[0]
    target_soilname = str(desc_row["soilname"]).strip()

    lyr_path = Path(file_path_root) / f"{id_str}.lyr"
    createsoil_path = Path(file_path_createsoil) / "CreateSoilFiles.exe"

    #================================================================
    #RUN CREATE.SOIL TO GENERATE GRD FILE
    #================================================================     
    # print(createsoil_path)
    # print(lyr_path)
    pp = subprocess.Popen([createsoil_path, lyr_path, "/GN", str(id_str), "/SN", target_soilname], cwd=file_path_root)
    while pp.poll() is None:
        time_module.sleep(1)
    print("Process ended, ret code:", pp.returncode)
    # os.chdir(field_path)  #change directory 
    # os.system('del output')  #command in grid1.bat file
    # os.system('del element_elm')
    # os.system('del grid_bnd')
    # os.system('del datagen2.dat')
    os.system('Dir  *.*  >dir.txt')
       
    return 
