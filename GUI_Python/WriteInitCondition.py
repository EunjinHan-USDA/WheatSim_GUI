import pandas as pd
from pathlib import Path

#Writes the initialization file
def WriteInitCondition(
    id_str: str,
    description_df: pd.DataFrame,
    init_df: pd.DataFrame,
    soil_df: pd.DataFrame,
    file_path_root: Path,
) -> Path:
    """
    Python version of VBA WriteIni(idStr).

    Inputs
    - id_str: target ID
    - description_df: sheet Description
    - init_df: sheet Init
    - soil_df: sheet Soil
    - file_path_root: root output folder (equivalent to C.FilePathRoot)

    Returns
    - Path to written .ini file
    """

    # Make lowercase-column copies for case-insensitive matching
    desc = description_df.copy()
    desc.columns = [c.strip().lower() for c in desc.columns]

    ini = init_df.copy()
    ini.columns = [c.strip().lower() for c in ini.columns]

    soil = soil_df.copy()
    soil.columns = [c.strip().lower() for c in soil.columns]

    # Helper to safely fetch a single row by ID
    def row_by_id(df: pd.DataFrame, key: str) -> pd.Series:
        if "id" not in df.columns:
            raise ValueError("Missing required column: id")
        r = df.loc[df["id"].astype(str) == str(key)]
        if r.empty:
            raise ValueError(f"ID '{key}' not found.")
        return r.iloc[0]

    # Required columns
    req_desc = {"id", "soilfile"}
    req_ini = {
        "id", "seeddepth", "rowspacing(cm)", "population(p/ha)", "rowangle",
        "xseed", "cec", "eomult", "lat", "long", "altitude(m)",
        "autoirrigated", "sowing", "end", # "timestep", #Only SB input files takes TimeStep as input variables. MZ and RY input files hard-coded as "60"
        "nosoilfile", "outputsoilfile"
    }
    req_soil = {"soilfile", "bottom depth"}

    if not req_desc.issubset(set(desc.columns)):
        raise ValueError(f"Description missing columns: {sorted(req_desc - set(desc.columns))}")
    if not req_ini.issubset(set(ini.columns)):
        raise ValueError(f"Init missing columns: {sorted(req_ini - set(ini.columns))}")
    if not req_soil.issubset(set(soil.columns)):
        raise ValueError(f"Soil missing columns: {sorted(req_soil - set(soil.columns))}")

    # Description row
    desc_row = row_by_id(desc, id_str)
    str_soil_file = str(desc_row["soilfile"]).strip()

    # Init row
    ini_row = row_by_id(ini, id_str)

    # Soil max depth for this soilfile
    soil_rows = soil.loc[soil["soilfile"].astype(str) == str_soil_file]
    if soil_rows.empty:
        raise ValueError(f"Soil rows not found for soilfile '{str_soil_file}'.")

    max_depth = pd.to_numeric(soil_rows["bottom depth"], errors="coerce").max()
    if pd.isna(max_depth):
        raise ValueError(f"Could not compute max bottom depth for soilfile '{str_soil_file}'.")

    seed_depth = float(ini_row["seeddepth"])
    depth = float(max_depth) - seed_depth  # same as VBA logic

    row_sp = float(ini_row["rowspacing(cm)"])
    density = float(ini_row["population(p/ha)"]) / 10000.0
    pop_row = row_sp / 100.0 * density

    # Build output file path
    out_path = file_path_root / f"{id_str}.ini"

    # Format dates as mm/dd/yyyy
    date1 = pd.to_datetime(ini_row["sowing"]).strftime("%m/%d/%Y")
    # date2 = pd.to_datetime(ini_row["emergence"]).strftime("%m/%d/%Y")  #emergence only for Glycim, not used in WheatSim
    date3 = pd.to_datetime(ini_row["end"]).strftime("%m/%d/%Y")

    # Write file (equivalent to VBA Print #1 lines)
    lines = [
        f"***Initialization data for {id_str} location",
        "PopRow       RowSP        Plant Density       rowangle       xseed        yseed         cec          eomult",
        f"{pop_row:<12} {row_sp:<12} {density:<20} {ini_row['rowangle']:<14} {ini_row['xseed']:<12} {depth:<12} {ini_row['cec']:<12} {ini_row['eomult']:<12}",
        "Latitude     longitude     Altitude",
        f"{ini_row['lat']:<10} {ini_row['long']:<6} {ini_row['altitude(m)']}",
        "AutoIrrigated",
        f"{ini_row['autoirrigated']}",
        "  Sowing        end         timestep",
        f"'{date1}' '{date3}' {'60'}",         #{ini_row['timestep']}", # "timestep", #Only SB input files takes TimeStep as input variables. MZ and RY input files hard-coded as "60"
        "Output soils data (g03, g04, g05 and g06 files) 1 if true",
        " nosoilfiles  outputsoilfile",
        f"{ini_row['nosoilfile']:<3} {ini_row['outputsoilfile']}",
        "",
    ]

    with out_path.open("w", encoding="utf-8") as f:
        for line in lines:
            f.write(str(line) + "\n")

    return 