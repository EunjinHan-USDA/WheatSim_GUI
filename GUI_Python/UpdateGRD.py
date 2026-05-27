import pandas as pd
from pathlib import Path
import shutil
from shutil import copyfile

def _normalize_cols(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.columns = [str(c).strip().lower() for c in out.columns]
    return out

def _find_col(df: pd.DataFrame, candidates: list[str], sheet_name: str) -> str:
    cols = set(df.columns)
    for cand in candidates:
        if cand in cols:
            return cand
    raise ValueError(
        f"{sheet_name} missing required column. Tried: {candidates} (found: {sorted(cols)})"
    )
    
def _row_by_id(df: pd.DataFrame, id_str: str, sheet_name: str) -> pd.Series:
    if "id" not in df.columns:
        raise ValueError(f"{sheet_name} missing required column: id")
    rows = df.loc[df["id"].astype(str) == str(id_str)]
    if rows.empty:
        raise ValueError(f"ID '{id_str}' not found in {sheet_name} sheet.")
    return rows.iloc[0]

#Writes the biology file
def UpdateGRD(
    id_str: str,
    description_df: pd.DataFrame,
    soil_df: pd.DataFrame,
    file_path_root: Path,
) -> Path:
    """
    Update surface boundary conditions in the .grd file for fertigation (NO3 in rainfall).
    """
    
    #====need description and soil to get the number of soil layers and the soil file name to match with grid ratio file to get the line number to update in grd file
    desc = _normalize_cols(description_df)
    soil = _normalize_cols(soil_df)
    desc_row = _row_by_id(desc, id_str, "Description")
    soil_file = str(desc_row["soilfile"]).strip()
    soil_file_col = _find_col(soil, ["soilfile", "soil file"], "Soil")
    soil_rows = soil.loc[soil[soil_file_col].astype(str) == soil_file].reset_index(drop=True)
    if soil_rows.empty:
        raise ValueError(f"Soil rows for SoilFile '{soil_file}' not found.")
    num_layer = soil_rows.shape[0]
    #====
    
    grd_fname = file_path_root / f"{id_str}.grd"
    grd_fname_temp = file_path_root / f"{id_str}_temp.grd"
    fr = open(grd_fname, "r")  # opens temp SNX file to read
    fw = open(grd_fname_temp, "w")  # opens SNX file to write
    flag = 0
    while(True):
        temp_str = fr.readline()

        if flag == 1:
            parts = temp_str.split()
            n = parts[0]
            codeW = parts[1]
           # codeC = parts[2] #update with -4 for NO3 in rainfall
            codeH = parts[3]
            codeG = parts[4]
            Width = parts[5]    
            fw.write(f"{n:>5} {codeW:>6} {str(-4):>6} {codeH:>6} {codeG:>6} {Width:>6}\n")
            if int(n) == num_layer:  # After writing the line for the last soil layer, reset flag to stop updating lines
                flag = 0
        else:
            fw.write(temp_str)

        if temp_str[:12] == '    n  CodeW':
            flag = 1

        if not temp_str:  # Check if end of file is reached
            break
    
    fr.close()
    fw.close()
    shutil.copyfile(grd_fname_temp, grd_fname)
    grd_fname_temp.unlink()  # Remove the temporary file
    return 
