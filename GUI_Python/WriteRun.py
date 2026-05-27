from pathlib import Path
import pandas as pd


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


# Write run file
def WriteRun(
    id_str: str,
    description_df: pd.DataFrame,
    file_path_root: Path,
) -> Path:
    """Python conversion of VBA Sub WriteRun(idStr As String)."""

    desc = _normalize_cols(description_df)
    base_path = Path(file_path_root)
    workspace_root = base_path.parent

    if "id" not in desc.columns:
        raise ValueError("Description missing required column: id")
    
    weather_col = _find_col(desc, ["weatherfilename", "weather_file_name"], "Description")
    biology_col = _find_col(desc, ["biology"], "Description")
    climate_col = _find_col(desc, ["climatefile", "climate_file"], "Description")
    nitrogen_col = _find_col(desc, ["nitrogenfile", "nitrogen_file"], "Description")
    solute_col = _find_col(desc, ["solute"], "Description")
    soil_col = _find_col(desc, ["soilfile", "soil_file"], "Description")
    mulch_col = _find_col(desc, ["mulchgeo", "mulch_geo"], "Description")
    gas_col = _find_col(desc, ["gas_file", "gasfile"], "Description")
    variety_col = _find_col(desc, ["varietyfile", "variety_file"], "Description")
    watermov_col = _find_col(desc, ["watermovparam", "watermovparamid"], "Description")

    desc_row = desc.loc[desc["id"].astype(str) == str(id_str)]
    if desc_row.empty:
        raise ValueError(f"ID '{id_str}' not found in Description sheet.")
    desc_row = desc_row.iloc[0]

    out_path = base_path / f"run{id_str}.dat"

    with out_path.open("w", encoding="utf-8") as f:
        f.write(str(base_path / str(desc_row[weather_col]).strip()) + "\n")
        f.write(str(base_path / f"{id_str}.tim") + "\n")
        f.write(str(base_path / f"{str(desc_row[biology_col]).strip()}.bio") + "\n")
        f.write(str(base_path / str(desc_row[climate_col]).strip()) + "\n")
        f.write(str(base_path / str(desc_row[nitrogen_col]).strip()) + "\n")
        f.write(str(base_path / f"{str(desc_row[solute_col]).strip()}.sol") + "\n")
        f.write(str(base_path / f"{str(desc_row[gas_col]).strip()}.gas") + "\n")
        f.write(str(base_path / str(desc_row[soil_col]).strip()) + "\n")
        f.write(str(base_path / f"{str(desc_row[mulch_col]).strip()}.mul") + "\n")
        f.write(str(base_path / f"{id_str}.man") + "\n")
        f.write(str(base_path / f"{id_str}.irr") + "\n")
        f.write(str(base_path / f"{id_str}.drp") + "\n")
        f.write(str(base_path / f"{str(desc_row[watermov_col]).strip()}.dat") + "\n")
        f.write(str(base_path / "WaterBound.DAT") + "\n")
        f.write(str(base_path / f"{id_str}.ini") + "\n")
        f.write(str(base_path / str(desc_row[variety_col]).strip()) + "\n")
        f.write(str(base_path / f"{id_str}.grd") + "\n")
        f.write(str(base_path / f"{id_str}.nod") + "\n")
        f.write(str(base_path / "MassBl.dat") + "\n")
        f.write(str(base_path / f"{id_str}.g01") + "\n")
        f.write(str(base_path / f"{id_str}.g02") + "\n")
        f.write(str(base_path / f"{id_str}.G03") + "\n")
        f.write(str(base_path / f"{id_str}.G04") + "\n")
        f.write(str(base_path / f"{id_str}.G05") + "\n")
        f.write(str(base_path / f"{id_str}.G06") + "\n")
        f.write(str(base_path / f"{id_str}.G07") + "\n")
        f.write(str(base_path / "MassBl.out") + "\n")
        f.write(str(base_path / "MassBlRunOff.out") + "\n")
        f.write(str(base_path / "MassBlMulch.out") + "\n")

    return 
