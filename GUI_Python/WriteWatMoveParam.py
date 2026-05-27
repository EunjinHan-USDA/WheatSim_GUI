from pathlib import Path
import pandas as pd


def _normalize_cols(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.columns = [str(c).strip().lower() for c in out.columns]
    return out

def _as_vb_sci(value: object) -> str:
    # VBA "0.0000E+0" style (single exponent digit when possible).
    txt = f"{float(value):.4E}"
    if "E" not in txt:
        return txt
    mantissa, exponent = txt.split("E")
    sign = exponent[0]
    digits = exponent[1:].lstrip("0")
    if digits == "":
        digits = "0"
    return f"{mantissa}E{sign}{digits}"

def WriteWatMoveP(
    id_str: str,
    description_df: pd.DataFrame,
    WaterMovParam_df: pd.DataFrame,
    file_path_root: Path,
) -> Path:
    """Python conversion of VBA Sub WriteWatMoveP(idStr As String)."""

    desc = _normalize_cols(description_df)
    wmp = _normalize_cols(WaterMovParam_df)
    
    req_desc = {"id", "watermovparam"}
    req_wmp = {"id", "maxit", "tolth", "tolh", "hcrita", "hcrits", "dtmx", "htab1", "htabn", "epsi.heat", "epsi.solute"}


    if not req_desc.issubset(desc.columns):
        raise ValueError(f"Description missing columns: {sorted(req_desc - set(desc.columns))}")
    if not req_wmp.issubset(wmp.columns):
        raise ValueError(f"WaterMovParam missing columns: {sorted(req_wmp - set(wmp.columns))}")

    desc_row = desc.loc[desc["id"].astype(str) == str(id_str)]
    if desc_row.empty:
        raise ValueError(f"ID '{id_str}' not found in Description sheet.")
    desc_row = desc_row.iloc[0]

    id_str_watermovparam = str(desc_row["watermovparam"]).strip()
    wmp_row = wmp.loc[wmp["id"].astype(str) == id_str_watermovparam]
    if wmp_row.empty:
        raise ValueError(f"WaterMovParam entry '{id_str_watermovparam}' not found.")
    wmp_row = wmp_row.iloc[0]

    out_path = file_path_root / f"{id_str_watermovparam}.dat"

    hcrits = _as_vb_sci(wmp_row["hcrits"])
    hcrita = _as_vb_sci(wmp_row["hcrita"])

    with out_path.open("w", encoding="utf-8") as f:
        f.write(" *** WATER MOVER PARAMETERINFORMATION **************************\n")
        f.write(
            "MaxIt   TolTh   TolH      hCritA     hCritS     DtMx       htab1      htabN    EPSI.Heat    EPSI.Solute\n"
        )
        f.write(
            f"{wmp_row['maxit']:<7} {wmp_row['tolth']:<7} {wmp_row['tolh']:<7} {hcrita:<11} {hcrits:<11} "
            f"{wmp_row['dtmx']:<10} {wmp_row['htab1']:<10} {wmp_row['htabn']:<10} "
            f"{wmp_row['epsi.heat']:<10} {wmp_row['epsi.solute']}\n"
        )

    return out_path
