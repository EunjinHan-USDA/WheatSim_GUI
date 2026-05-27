import pandas as pd
from pathlib import Path

#Writes the biology file
def WriteBio(id_str: str, description_df: pd.DataFrame, biology_df: pd.DataFrame, file_path_root: Path) -> Path:
    """
    Python version of the VBA Sub WriteBio(idStr As String).

    Parameters
    ----------
    id_str : str
        The ID to look up in the Description sheet.
    biology_df : pd.DataFrame
        The DataFrame containing biology parameters.
    file_path_root : Path
        The root path where the .bio file will be written.

    Raises
    ------
    ValueError
        If the ID is not found in Description, or biology entry not found in Biology,
        or if required columns are missing.
    """
    # --- 1) From Description: fetch 'biology' for the given id ---
    required_desc_cols = {'id', 'biology'}
    actual_desc_cols = {c.lower() for c in description_df.columns}
    if not required_desc_cols.issubset(actual_desc_cols):
        raise ValueError(f"Description sheet must contain columns: {sorted(required_desc_cols)} "
                         f"(found: {sorted(actual_desc_cols)})")

    # Use lowercased column names for robustness
    desc = description_df.copy()
    desc.columns = [c.lower() for c in desc.columns]

    row_desc = desc.loc[desc['id'].astype(str) == str(id_str)]
    if row_desc.empty:
        raise ValueError(f"ID '{id_str}' not found in Description sheet.")

    biology_key = str(row_desc.iloc[0]['biology']).strip()

    # --- 2) From Biology: fetch parameters by biology_key (matches VBA: ID = biology) ---
    required_bio_cols = {'id', 'dthh', 'dthl', 'es', 'th_m', 'tb', 'qt', 'dthd', 'th_d'}
    actual_bio_cols = {c.lower() for c in biology_df.columns}
    if not required_bio_cols.issubset(actual_bio_cols):
        raise ValueError(f"Biology sheet must contain columns: {sorted(required_bio_cols)} "
                         f"(found: {sorted(actual_bio_cols)})")

    bio = biology_df.copy()
    bio.columns = [c.lower() for c in bio.columns]

    row_bio = bio.loc[bio['id'].astype(str) == biology_key]
    if row_bio.empty:
        raise ValueError(f"Biology entry '{biology_key}' (from Description.biology) not found in Biology sheet.")

    # Extract values (these correspond to VBA's rs3(1)..rs3(8); rs3(0) is 'id' and not printed)
    dthH = row_bio.iloc[0]['dthh']
    dthL = row_bio.iloc[0]['dthl']
    es   = row_bio.iloc[0]['es']
    th_m = row_bio.iloc[0]['th_m']
    tb   = row_bio.iloc[0]['tb']
    QT   = row_bio.iloc[0]['qt']
    dthD = row_bio.iloc[0]['dthd']
    th_d = row_bio.iloc[0]['th_d']

    # --- 3) Build output path: FilePathRoot \ path \ biology.bio ---
    # out_dir = file_path_root
    # out_dir.mkdir(parents=True, exist_ok=True)
    out_path = file_path_root / f"{biology_key}.bio"

    # --- 4) Write the file content (replicates VBA's Print #1 lines) ---
    lines = [
        "*** Example 12.3: Parameters of abiotic responce: file 'SetAbio.dat'",
        "Dehumification, mineralization, nitrification dependencies on moisture:",
        " dThH    dThL    es    Th_m",
        f"{dthH}     {dthL}     {es}     {th_m}",
        "  Dependencies of temperature",
        " tb    QT",
        f"{tb}     {QT}",
        "Denitrification dependencies on water content",
        "dThD   Th_d",
        f"{dthD}     {th_d}",
        ""  # final blank line to match the trailing Print
    ]

    with out_path.open('w', encoding='utf-8') as f:
        for line in lines:
            f.write(str(line) + "\n")

    # Optional: emulate 'Debug.Print C.rs2.GetString' by printing the matching Description row
    # (This is just for visibility; you can change to logging as needed.)
    # print("Description row (biology, path) for ID =", id_str)
    # print(row_desc[['biology', 'path']])

    return 
