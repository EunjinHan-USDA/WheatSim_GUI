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

#'Writes the Nitrogen file
def WriteNit(
    id_str: str,
    description_df: pd.DataFrame,
    init_df: pd.DataFrame,
    soil_df: pd.DataFrame,
    file_path_root: Path,
) -> Path:
    """Python conversion of VBA Sub WriteNit(idStr As String)."""

    desc = _normalize_cols(description_df)
    init = _normalize_cols(init_df)
    soil = _normalize_cols(soil_df)

    req_desc = {"id", "soilfile"}
    req_soil = {
        "soilfile",
        "kh",
        "kl",
        "km",
        "kn",
        "kd",
        "fe",
        "fh",
        "r0",
        "rl",
        "rm",
        "fa",
        "nq",
        "cs",
    }

    if not req_desc.issubset(desc.columns):
        raise ValueError(f"Description missing columns: {sorted(req_desc - set(desc.columns))}")
    if not req_soil.issubset(soil.columns):
        raise ValueError(f"Soil missing columns: {sorted(req_soil - set(soil.columns))}")

    desc_row = desc.loc[desc["id"].astype(str) == str(id_str)]
    if desc_row.empty:
        raise ValueError(f"ID '{id_str}' not found in Description sheet.")
    desc_row = desc_row.iloc[0]

    nitrogen_file_col = _find_col(desc, ["nitrogenfile", "nitrogen_file"], "Description")
    row_spacing_col = _find_col(init, ["rowspacing(cm)", "row spacing(cm)"], "Init")

    soil_file = str(desc_row["soilfile"]).strip()
    nitrogen_file = str(desc_row[nitrogen_file_col]).strip()

    soil_rows = soil.loc[soil["soilfile"].astype(str) == soil_file].reset_index(drop=True)
    if soil_rows.empty:
        raise ValueError(f"Soil entry for SoilFile '{soil_file}' not found.")

    init_row = init.loc[init["id"].astype(str) == str(id_str)]
    if init_row.empty:
        raise ValueError(f"Init entry for ID '{id_str}' not found.")
    row_spacing_cm = float(init_row.iloc[0][row_spacing_col])
    max_x = row_spacing_cm / 100.0

    out_path = file_path_root / nitrogen_file

    with out_path.open("w", encoding="utf-8") as f:
        f.write(f" *** SoilNit parameters for: {id_str}***\n")
        f.write("ROW SPACING (m)\n")
        f.write(f"{max_x}\n")
        f.write("                             Potential rate constants:       Ratios and fractions:\n")
        f.write("  m      kh     kL       km       kn        kd             fe   fh    r0   rL    rm   fa    nq   cs\n")

        for idx, row in soil_rows.iterrows():
            i = idx + 1
            f.write(
                f"{i} {row['kh']} {row['kl']} {row['km']} {row['kn']} {row['kd']} {row['fe']} {row['fh']} "
                f"{row['r0']} {row['rl']} {row['rm']} {row['fa']} {row['nq']} {row['cs']}\n"
            )

        f.write("\n")

    return out_path
