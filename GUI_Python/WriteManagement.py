
import pandas as pd
from pathlib import Path

def _normalize_cols(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.columns = [str(c).strip().lower() for c in out.columns]
    return out

def _to_mmddyyyy(value: object) -> str:
    return pd.to_datetime(value).strftime("%m/%d/%Y")

# Writes management files
def WriteMan(
    id_str: str,
    description_df: pd.DataFrame,   # Description sheet
    init_df: pd.DataFrame,       # Init sheet
    time_df: pd.DataFrame,       # Time sheet
    fert_df: pd.DataFrame,       # Fertilization sheet
    tillage_df: pd.DataFrame,       # Tillage sheet
    file_path_root: Path,
) -> Path:
    """
    Python version of VBA WriteIni(idStr).

    Inputs
    Python conversion of VBA Sub WriteMan(idStr As String).

    Parameters
    ----------
    id_str : str
        Simulation ID from Description.ID.
    description_df : pd.DataFrame
        Description sheet with at least ID, Tillage.
    init_df : pd.DataFrame
        Init sheet with RowSpacing(cm) and sowing.
    time_df : pd.DataFrame
        Time sheet with startDate.
    fert_df : pd.DataFrame
        Fertilization sheet for fertilizer and residue info.
    tillage_df : pd.DataFrame
        Tillage sheet for tillage operation lookup by Description.Tillage.
    file_path_root : Path
        Output directory where <id>.man is written.
    """
    # Make lowercase-column copies for case-insensitive matching
    desc = description_df.copy()
    desc = _normalize_cols(description_df)
    init = _normalize_cols(init_df)
    time = _normalize_cols(time_df)
    fert = _normalize_cols(fert_df)
    till = _normalize_cols(tillage_df)

    req_desc = {"id", "tillage"}
    req_init = {"id", "rowspacing(cm)", "sowing"}
    req_time = {"id", "startdate"}
    req_fert = {
        "id",
        "amount",
        "depth",
        "litter_c(kg/ha)",
        "litter_n",
        "manure_c",
        "manure_n",
        "date",
        "date_residue",
        "type(t or m)",
        "rate (t/ha or  cm)",
        "vertical layers",
    }
    req_till = {"id", "till(1/0)", "daysbeforeplanting", "depth"}

    if not req_desc.issubset(set(desc.columns)):
        missing = sorted(req_desc - set(desc.columns))
        raise ValueError(f"Description missing columns: {missing}")
    if not req_init.issubset(set(init.columns)):
        missing = sorted(req_init - set(init.columns))
        raise ValueError(f"Init missing columns: {missing}")
    if not req_time.issubset(set(time.columns)):
        missing = sorted(req_time - set(time.columns))
        raise ValueError(f"Time missing columns: {missing}")
    if not req_fert.issubset(set(fert.columns)):
        missing = sorted(req_fert - set(fert.columns))
        raise ValueError(f"Fertilization missing columns: {missing}")
    if not req_till.issubset(set(till.columns)):
        missing = sorted(req_till - set(till.columns))
        raise ValueError(f"Tillage missing columns: {missing}")

    desc_row = desc.loc[desc["id"].astype(str) == str(id_str)]
    if desc_row.empty:
        raise ValueError(f"ID '{id_str}' not found in Description sheet.")
    desc_row = desc_row.iloc[0]
    tillage_key = str(desc_row["tillage"]).strip()

    init_row = init.loc[init["id"].astype(str) == str(id_str)]
    if init_row.empty:
        raise ValueError(f"ID '{id_str}' not found in Init sheet.")
    init_row = init_row.iloc[0]

    max_x = float(init_row["rowspacing(cm)"]) / 2.0
    sow_date = pd.to_datetime(init_row["sowing"])

    time_row = time.loc[time["id"].astype(str) == str(id_str)]
    if time_row.empty:
        raise ValueError(f"ID '{id_str}' not found in Time sheet.")
    start_date = pd.to_datetime(time_row.iloc[0]["startdate"])

    fert_rows = fert.loc[fert["id"].astype(str) == str(id_str)].reset_index(drop=True)
    fert_count = int(len(fert_rows))

    out_path = file_path_root / f"{id_str}.man"

    with out_path.open("w", encoding="utf-8") as f:
        if fert_count > 0:
            f.write("*** Script for management practices fertilizer, residue and tillage\n")
            f.write("[N Fertilizer]\n")
            f.write("****Script for chemical application module  *******mg/cm2= kg/ha* 0.01*rwsp*eomult*100\n")
            f.write("Number of Fertilizer applications (max=25) mappl is in total mg N applied to grid (1 kg/ha = 1 mg/m2/width of application) application divided by width of grid in cm is kg ha-1\n")
            f.write(f"{fert_count}\n")
            f.write("mAppl is manure, lAppl is litter. Apply as mg/cm2 of slab same units as N\n")
            f.write("tAppl(i)  AmtAppl(i) depth(i) lAppl_C(i) lAppl_N(i)  mAppl_C(i) mAppl_N(i)  (repeat these 3 lines for the number of fertilizer applications)\n")
            for _, row in fert_rows.iterrows():
                factor = 0.01 * max_x / 100.0   # m2 of slab
                amount = round(float(row["amount"]) * factor / 10000.0 * 1000000.0, 3)
                depth = float(row["depth"])
                l_c = float(row["litter_c(kg/ha)"]) * factor / 10000.0 * 1000000.0  #litter
                l_n = float(row["litter_n"]) * factor / 10000.0 * 1000000.0
                m_c = float(row["manure_c"]) * factor / 10000.0 * 1000000.0   #manure
                m_n = float(row["manure_n"]) * factor / 10000.0 * 1000000.0
                if row["date"] is pd.NaT or str(row["date"]).strip() == "":
                    raise ValueError("Fertilizer application missing date.")
                else:
                    date_1 = _to_mmddyyyy(row["date"])
                f.write(f"'{date_1:<2}' {amount:<10} {depth:<10} {l_c:<10} {l_n:<10} {m_c:<10} {m_n}\n")
        else:
            f.write("****Script for chemical application module  *******mg/cm2= kg/ha* 0.01*rwsp*eomult*100\n")
            f.write("Number of Fertilizer applications (max=25) mappl is in total mg N applied to grid \n")
            f.write("(1 kg/ha = 1 mg/m2/width of application) application divided by \n")
            f.write("width of grid in cm is kg ha-1\n")
            f.write("0\n")
            f.write("No fertilization\n")
            f.write("No fertilization\n")

        f.write("[Residue]\n")
        f.write("****Script for residue/mulch application module\n")
        f.write("**** Residue amount can be thickness ('t') or mass ('m')   ***\n")
        f.write("application  1 or 0, 1(yes) 0(no)\n")

        residue_applied = False
        residue_row = fert_rows.iloc[0] if fert_count > 0 else None
        if residue_row is not None:
            residue_date = residue_row["date_residue"]
            residue_rate = pd.to_numeric(residue_row["rate (t/ha or  cm)"], errors="coerce")
            has_date = pd.notna(residue_date) and str(residue_date).strip() != ""
            has_rate = pd.notna(residue_rate) and float(residue_rate) != 0.0
            residue_applied = bool(has_date or has_rate)

        if residue_applied and residue_row is not None:
            f.write("1\n")
            f.write("tAppl_R (i)    't' or 'm'      Mass (gr/m2) or thickness (cm)    vertical layers\n")
            f.write("---either thickness  or Mass\n")
            date_2 = _to_mmddyyyy(residue_row["date_residue"])
            residue_type = str(residue_row["type(t or m)"])
            residue_rate_val = residue_row["rate (t/ha or  cm)"]
            residue_layers = residue_row["vertical layers"]
            f.write(f"'{date_2}'      '{residue_type}'          {residue_rate_val:<19} {residue_layers}\n")
            f.write("\n")
        else:
            f.write("0\n")

        f.write("[Tillage]\n")
        f.write("1: Tillage , 0: No till\n")

        till_row = till.loc[till["id"].astype(str) == tillage_key]
        if till_row.empty:
            raise ValueError(f"Tillage entry '{tillage_key}' not found in Tillage sheet.")
        till_row = till_row.iloc[0]

        till_on = int(float(till_row["till(1/0)"]))
        f.write(f"{till_on}\n")

        if till_on == 1:
            till_date = sow_date - pd.to_timedelta(int(float(till_row["daysbeforeplanting"])), unit="D")
            if till_date <= start_date:
                raise ValueError("tillage too close to start date, please rechoose")
            till_date_text = _to_mmddyyyy(till_date)
            f.write("till_Date   till_Depth\n")
            f.write(f"'{till_date_text}' {till_row['depth']}\n")

    return out_path