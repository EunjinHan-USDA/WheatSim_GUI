import pandas as pd
from pathlib import Path


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

# Creates the layer file that is input to the CreateSoils program and writes the batch files needed to run the program
def WriteLayer(
    id_str: str,
    description_df: pd.DataFrame,
    gridratio_df: pd.DataFrame,
    init_df: pd.DataFrame,
    soil_df: pd.DataFrame,
    file_path_root: Path,
    file_path_createsoil: Path,
) -> Path:
    """
    Python conversion of VBA Sub WriteLayer(idStr As String).
    """

    desc = _normalize_cols(description_df)
    grid = _normalize_cols(gridratio_df)
    init = _normalize_cols(init_df)
    soil = _normalize_cols(soil_df)

    if "id" not in desc.columns:
        raise ValueError("Description missing required column: id")
    if "soilfile" not in desc.columns:
        raise ValueError("Description missing required column: soilfile")

    desc_row = _row_by_id(desc, id_str, "Description")
    soil_file = str(desc_row["soilfile"]).strip()

    grid_soil_col = _find_col(grid, ["soilfile", "soil file"], "GridRatio")
    grid_rows = grid.loc[grid[grid_soil_col].astype(str) == soil_file]
    if grid_rows.empty:
        raise ValueError(f"GridRatio row for SoilFile '{soil_file}' not found.")
    grid_row = grid_rows.iloc[0]

    sr1_col = _find_col(grid, ["sr1"], "GridRatio")
    ir1_col = _find_col(grid, ["ir1"], "GridRatio")
    sr2_col = _find_col(grid, ["sr2"], "GridRatio")
    ir2_col = _find_col(grid, ["ir2"], "GridRatio")
    planting_depth_col = _find_col(grid, ["plantingdepth", "planting depth"], "GridRatio")
    xlimit_root_col = _find_col(grid, ["xlimitroot", "x limit for roots"], "GridRatio")
    init_rt_mass_col = _find_col(grid, ["initrtmass", "init rt mass"], "GridRatio")
    bottom_bc_col = _find_col(grid, ["bottombc", "bottom bc"], "GridRatio")
    gas_bc_top_col = _find_col(grid, ["gasbctop", "gas bc top"], "GridRatio")
    gas_bc_bottom_col = _find_col(grid, ["gasbcbottom", "gas bc bottom"], "GridRatio")

    init_row = _row_by_id(init, id_str, "Init")
    row_spacing_col = _find_col(init, ["rowspacing(cm)", "row spacing(cm)"], "Init")

    soil_file_col = _find_col(soil, ["soilfile", "soil file"], "Soil")
    soil_rows = soil.loc[soil[soil_file_col].astype(str) == soil_file].reset_index(drop=True)
    if soil_rows.empty:
        raise ValueError(f"Soil rows for SoilFile '{soil_file}' not found.")

    bottom_depth_col = _find_col(soil, ["bottom depth"], "Soil")
    init_type_col = _find_col(soil, ["init type"], "Soil")
    om_col = _find_col(soil, ["om (%/100)"], "Soil")
    humus_c_col = _find_col(soil, ["humus_c"], "Soil")
    humus_n_col = _find_col(soil, ["humus_n"], "Soil")
    litter_c_col = _find_col(soil, ["litter_c"], "Soil")
    litter_n_col = _find_col(soil, ["litter_n"], "Soil")
    manure_c_col = _find_col(soil, ["manure_c"], "Soil")
    manure_n_col = _find_col(soil, ["manure_n"], "Soil")
    no3_col = _find_col(soil, ["no3 (ppm)", "no3(ppm)"], "Soil")
    nh4_col = _find_col(soil, ["nh4"], "Soil")
    hnew_col = _find_col(soil, ["hnew"], "Soil")
    tmpr_col = _find_col(soil, ["tmpr"], "Soil")
    co2_col = _find_col(soil, ["co2(ppm)", "co2"], "Soil")
    o2_col = _find_col(soil, ["o2(ppm)", "o2"], "Soil")
    n2o_col = _find_col(soil, ["n2o(ppm)", "n2o"], "Soil")
    sand_col = _find_col(soil, ["sand"], "Soil")
    silt_col = _find_col(soil, ["silt"], "Soil")
    clay_col = _find_col(soil, ["clay"], "Soil")
    bd_col = _find_col(soil, ["bd"], "Soil")
    th33_col = _find_col(soil, ["th33"], "Soil")
    th1500_col = _find_col(soil, ["th1500"], "Soil")
    thr_col = _find_col(soil, ["thr"], "Soil")
    ths_col = _find_col(soil, ["ths"], "Soil")
    tha_col = _find_col(soil, ["tha"], "Soil")
    th_col = _find_col(soil, ["th"], "Soil")
    alfa_col = _find_col(soil, ["alfa"], "Soil")
    n_col = _find_col(soil, ["n"], "Soil")
    ks_col = _find_col(soil, ["ks"], "Soil")
    kk_col = _find_col(soil, ["kk"], "Soil")
    thk_col = _find_col(soil, ["thk"], "Soil")

    out_path = Path(file_path_root) / f"{id_str}.lyr"

    with out_path.open("w", encoding="utf-8") as f:
        f.write("surface ratio    internal ratio: ratio of the distance between two neighboring nodes\n")
        f.write(f"{grid_row[sr1_col]:<11} {grid_row[ir1_col]:<11} {grid_row[sr2_col]:<11} {grid_row[ir2_col]:<11}\n")

        f.write("Row Spacing\n")
        f.write(f"{init_row[row_spacing_col]}\n")

        f.write(" Planting Depth  X limit for roots \n")
        f.write(f"{grid_row[planting_depth_col]:<11} {grid_row[xlimit_root_col]:<11} {grid_row[init_rt_mass_col]:<11}\n")
        f.write("Surface water Boundary Code  surface and bottom Gas boundary codes(for all bottom nodes) 1 constant -2 seepage face,  7 drainage 4 atmospheric\n")
        f.write("water boundary code for bottom layer, gas BC for the surface and bottom layers \n")
        f.write(f"{grid_row[bottom_bc_col]:<11} {grid_row[gas_bc_top_col]:<11} {grid_row[gas_bc_bottom_col]:<11}\n")
        f.write(
            " Bottom depth Init Type  OM (%/100)    Humus_C     Humus_N      Litter_C      Litter_N      Manure_C      Manure_N "
            "      no3(ppm)           NH4          hNew           Tmpr  "
            "          CO2         O2         N2O      Sand       Silt        Clay          BD         TH33       TH1500  "
            "thr ths tha th  Alfa    n   Ks  Kk  thk\n"
        )
        f.write(
            " cm         w/m            Frac        ug/cm3       ug/cm3       ug/cm3        ug/cm3        ug/cm3        ug/cm3            ppm          ppm       "
            "       cm           0C            ppm            ppm          ppm       ----  fraction---             g/cm3        cm3/cm3     cm3/cm3\n"
        )

        for _, row in soil_rows.iterrows():
            f.write(
                f"{row[bottom_depth_col]:<11} '{row[init_type_col]}'          {row[om_col]:<13.7f} "
                f" {row[humus_c_col]:<11.3f} {row[humus_n_col]:<12.3f} {row[litter_c_col]:<13.3f} {row[litter_n_col]:<13.3f} "
                f"{row[manure_c_col]:<13.3f} {row[manure_n_col]:<14.3f} {row[no3_col]:<15.3f} {row[nh4_col]:<13.3f} {row[hnew_col]:<15} {row[tmpr_col]:<14} "
                f"{row[co2_col]:<9} {row[o2_col]:<13} {row[n2o_col]:<7} "
                f"{float(row[sand_col]) / 100.0:<11.3f} {float(row[silt_col]) / 100.0:<11.3f} {float(row[clay_col]) / 100.0:<11.3f} "
                f"{row[bd_col]:<11.3f} {row[th33_col]:<11} {row[th1500_col]:<5} {row[thr_col]:<4} {row[ths_col]:<4} {row[tha_col]:<4} "
                f"{row[th_col]:<4} {row[alfa_col]:<4} {row[n_col]:<4} {row[ks_col]:<4} {row[kk_col]:<4} {row[thk_col]}\n"
            )

    soil_file2 = soil_file[:-4] if soil_file.lower().endswith(".soi") else Path(soil_file).stem
    batch_path = Path(file_path_root) / "grid1.bat"
    create_soils_exe = Path(file_path_createsoil) / "CreateSoilFiles.exe"

    with batch_path.open("w", encoding="utf-8") as f:
        f.write(f'"{create_soils_exe}" "{out_path}" /GN {id_str} /SN {soil_file2}\n')
        f.write("del output\n")
        f.write("del element_elm\n")
        f.write("del grid_bnd\n")
        f.write("del datagen2.dat\n")
        f.write("Dir  *.*  >dir.txt\n")

    return 