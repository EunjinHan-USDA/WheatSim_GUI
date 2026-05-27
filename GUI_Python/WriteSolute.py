from pathlib import Path
import ctypes
from typing import Optional

import pandas as pd


def _normalize_cols(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.columns = [str(c).strip().lower() for c in out.columns]
    return out

def _SoilClassification(
    sand: float,
    silt: float,
) -> str:
    """
    Classify soil texture based on sand, silt, and clay percentages using USDA soil texture triangle.
    
    Parameters:
    - sand: Percentage of sand in the soil (0-100)
    - silt: Percentage of silt in the soil (0-100)
    - clay: Percentage of clay in the soil (0-100)
    
    Returns:
    - A string representing the soil texture class.
    """
    clay= 100.0-sand-silt   # type: ignore # Note: the sum should be 100

    if sand <= 45 and silt <= 40 and clay >= 40:
        texture = "Clay"
    elif sand <= 65 and sand >= 45 and silt <= 20 and clay >= 35 and clay <= 55:
        texture = "Sandy Clay"
    elif sand <= 20 and silt >= 40 and silt <= 60 and clay >= 40 and clay <= 60:
        texture = "Silty Clay"
    elif sand >= 45 and sand <= 80 and silt <= 28 and clay >= 20 and clay <= 35:
        texture = "Sandy Clay Loam"
    elif sand >= 20 and sand <= 45 and silt >= 15 and silt <= 53 and clay >= 27 and clay <= 40:
        texture = "Clay Loam"
    elif sand <= 20 and silt >= 40 and silt <= 73 and clay >= 27 and clay <= 40:
        texture = "Silty Clay Loam"
    elif sand >= 43 and sand <= 85 and silt <= 50 and clay <= 20:
        texture = "Sandy Loam"
    elif sand >= 23 and sand <= 52 and silt >= 28 and silt <= 50 and clay >= 7 and clay <= 27:
        texture = "Loam"
    elif sand <= 50 and silt >= 50 and silt <= 88 and clay <= 27:
        texture = "Silt Loam"
    elif sand <= 20 and silt >= 80 and clay <= 12:
        texture = "Silt"
    elif sand >= 70 and sand <= 90 and silt <= 30 and clay <= 15:
        texture = "Loamy Sand"
    elif sand >= 85 and silt <= 15 and clay <= 10:
        texture = "Sand"
    else:
        texture = "Not Available"
        
    # print(f"For {sand}% Sand, {silt}% Silt, and {clay}% Clay:")
    # print(f"The soil texture class is: {texture}")
    return texture


# Writes the solute file 
# ExcelInterface calls a dll to find soil texture class, BUT here SoilClassification is implemented in Python using the USDA soil texture triangle. 
# ExcelInterface also opens another spreadsheet to look up dispersivity based on texture class, BUT here we use a hardcoded dictionary for dispersivity values based on texture class. 
def WriteSol(
    id_str: str,
    description_df: pd.DataFrame,
    soil_df: pd.DataFrame,
    solute_df: pd.DataFrame,
    file_path_root: Path,
) -> Path:
    """
    Python conversion of VBA Sub WriteSol(idStr As String).

    Expected columns:
    Description: id, soilfile, solute
    Soil: soilfile, sand, silt, clay
    Solute: id, ... (uses columns by position to match VBA rs2(1..4))
    Dispersivity: texturecl, ... (uses column 1 for dispersivity value)
    """

    desc = _normalize_cols(description_df)
    soil = _normalize_cols(soil_df)
    sol = _normalize_cols(solute_df)

    # 1) Description lookup by id
    drow = desc.loc[desc["id"].astype(str) == str(id_str)]
    if drow.empty:
        raise ValueError(f"ID '{id_str}' not found in Description.")
    drow = drow.iloc[0]

    solute_ID = str(drow["solute"]).strip()
    soil_file = str(drow["soilfile"]).strip()

    # Output path (matches current Python pattern: write into simulation folder)
    out_path = file_path_root / f"{solute_ID}.sol"

    # 2) Soil rows for this soilfile (layer count/order)
    soil_rows = soil.loc[soil["soilfile"].astype(str) == soil_file].reset_index(drop=True)
    if soil_rows.empty:
        raise ValueError(f"No Soil rows found for soilFile '{soil_file}'.")

    # 3) Solute row by id = solute_ID
    sol_row = sol.loc[sol["id"].astype(str) == solute_ID]
    if sol_row.empty:
        raise ValueError(f"No Solute row found for id '{solute_ID}'.")
    sol_row = sol_row.iloc[0]

    # VBA uses positional fields rs2(1), rs2(2), rs2(3), rs2(4)
    # Keep same behavior by using DataFrame column position.
    if len(sol.columns) < 5:
        raise ValueError("Solute sheet needs at least 5 columns (id + 4 parameter columns).")
    EPSI = sol_row.iloc[1]
    lUPW = sol_row.iloc[2]
    CourMax = sol_row.iloc[3]
    Diffusion_Coeff = sol_row.iloc[4]

    # 4) Build texture class array per soil layer
    texture_classes = []
    for _, srow in soil_rows.iterrows():
        tclass = _SoilClassification(
            sand=float(srow["sand"]),
            silt=float(srow["silt"]),
        )
        texture_classes.append(tclass)

    #====================================
    # dispersivity lookup.xls has texturecl in column 0 and dispersivity value in column 1
    # a lookup table for soil dispersivity vs soil texture class. 
    dispersivity_lookup = {
    "clay loam": 8.1,
    "clay": 12.8,
    "loam": 4.6,
    "loamy sand": 1.6,
    "sand": 0.8,
    "sandy clay": 10.9,
    "sandy clay loam": 6.0,
    "sandy loam": 3.4,
    "silt": 7,  #Dennis' note: was not in table, had to estimate
    "silty clay": 11,
    "silty clay loam": 9.6,
    "silt loam": 5.6
    }
    #====================================

    # 5) Write .sol file
    with out_path.open("w", encoding="utf-8") as f:
        f.write("*** SOLUTE MOVER PARAMETER INFORMATION ***\n")
        f.write(" Number of solutes\n")
        f.write(" 1\n")
        f.write(" Computational parameters \n")
        f.write(" EPSI        lUpW             CourMax\n")
        f.write(f" {EPSI:<11} {lUPW:<16} {CourMax}\n")
        f.write(" Material Information\n")
        f.write("Solute#, Ionic/molecular diffusion coefficients of solutes \n")
        f.write(f"  1    {Diffusion_Coeff}\n")
        f.write("  Solute#, Layer#, Longitudinal Dispersivity, Transversal Dispersivity (units are cm)\n")

        # VBA loop: lookup dispersivity by texturecl, then print rs_D(1) and rs_D(1)/2
        for i, tclass in enumerate(texture_classes, start=1):
            key = str(tclass).strip().lower()
            disp_val = dispersivity_lookup.get(key)
            f.write(f"1             {i:<12} {disp_val:<9} {disp_val / 2.0}\n")
        f.write("\n")

    return 