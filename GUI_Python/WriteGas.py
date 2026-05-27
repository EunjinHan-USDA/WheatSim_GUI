import pandas as pd
from pathlib import Path

def WriteGas(id_str: str, description_df: pd.DataFrame, gas_df: pd.DataFrame, file_path_root: Path) -> Path:
    """
    Python version of the VBA Sub WriteGas(idStr As String).

    Parameters
    ----------
    id_str : str
        The ID to look up in the Description sheet.
    gas_df : pd.DataFrame
        The DataFrame containing gas parameters.
    file_path_root : Path
        The root path where the .gas file will be written.

    Raises
    ------
    ValueError
        If the ID is not found in Description, if a gas entry is not found in
        Gas, or if required columns are missing.
    """
    def _normalize_cols(df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()
        out.columns = [str(c).strip().lower() for c in out.columns]
        return out

    def _require_cols(df: pd.DataFrame, required: set[str], sheet_name: str) -> None:
        cols = set(df.columns)
        if not required.issubset(cols):
            raise ValueError(
                f"{sheet_name} sheet must contain columns: {sorted(required)} "
                f"(found: {sorted(cols)})"
            )

    desc = _normalize_cols(description_df)
    gas = _normalize_cols(gas_df)

    # --- 1) From Description: fetch gas IDs and output file name for the given id ---
    required_desc_cols = {"id", "gas_co2", "gas_o2", "gas_n2o", "gas_file"}
    _require_cols(desc, required_desc_cols, "Description")

    row_desc = desc.loc[desc["id"].astype(str) == str(id_str)]
    if row_desc.empty:
        raise ValueError(f"ID '{id_str}' not found in Description sheet.")

    co2_id = str(row_desc.iloc[0]["gas_co2"]).strip()
    o2_id = str(row_desc.iloc[0]["gas_o2"]).strip()
    n2o_id = str(row_desc.iloc[0]["gas_n2o"]).strip()
    gas_file = str(row_desc.iloc[0]["gas_file"]).strip()

    # --- 2) From Gas: fetch EPSI, bTort, and diffusion coefficients by gas ID ---
    required_gas_cols = {"id", "epsi", "btort", "diffusion_coeff(cm2/day)"}
    _require_cols(gas, required_gas_cols, "Gas")

    row_co2 = gas.loc[gas["id"].astype(str) == co2_id]
    row_o2 = gas.loc[gas["id"].astype(str) == o2_id]
    row_n2o = gas.loc[gas["id"].astype(str) == n2o_id]

    if row_co2.empty:
        raise ValueError(f"Gas entry '{co2_id}' (Description.Gas_CO2) not found in Gas sheet.")
    if row_o2.empty:
        raise ValueError(f"Gas entry '{o2_id}' (Description.Gas_O2) not found in Gas sheet.")
    if row_n2o.empty:
        raise ValueError(f"Gas entry '{n2o_id}' (Description.Gas_N2O) not found in Gas sheet.")

    # VBA uses EPSI and bTort values from the first recordset (CO2 row).
    epsi = row_co2.iloc[0]["epsi"]
    btort = row_co2.iloc[0]["btort"]
    co2_diff = row_co2.iloc[0]["diffusion_coeff(cm2/day)"]
    o2_diff = row_o2.iloc[0]["diffusion_coeff(cm2/day)"]
    n2o_diff = row_n2o.iloc[0]["diffusion_coeff(cm2/day)"]

    # --- 3) Build output path and write .gas file ---
    out_path = file_path_root / f"{gas_file}.gas"

    lines = [
        "*** Gas Movement Parameters Information ***",
        " Number of gases",
        " 3",
        " Computational parameters ",
        " EPSI",
        f" {str(epsi)}",
        " Reduced tortousity rate change with water content (bTort)",
        " for entire soil domain ",
        f" {str(btort)}",
        "Gas diffusion coefficients in air at standard conditions, cm2/day",
        "Gas # 1 (CO2) Gas # 2 (Oxygen) Gas # 3 (N2O)",
        f" {co2_diff:<15} {o2_diff:<15} {n2o_diff:<15}",
    ]

    with out_path.open("w", encoding="utf-8") as f:
        for line in lines:
            f.write(str(line) + "\n")

    return out_path
