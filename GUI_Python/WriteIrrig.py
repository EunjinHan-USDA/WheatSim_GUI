from pathlib import Path
import pandas as pd

def _normalize_cols(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.columns = [str(c).strip().lower() for c in out.columns]
    return out

def _to_mmddyyyy(value: object) -> str:
    return pd.to_datetime(value).strftime("%m/%d/%Y")

def WriteIrrig(
    id_str: str,
    description_df: pd.DataFrame,
    climate_df: pd.DataFrame,
    irrig_df: pd.DataFrame,
    file_path_root: Path,
) -> Path:
    """
    Python conversion of VBA Sub WriteIrrig(idStr As String).
    """

    desc = _normalize_cols(description_df)
    clim = _normalize_cols(climate_df)
    irrig = _normalize_cols(irrig_df)

    req_desc = {"id", "climateid", "location"}
    req_clim = {"climateid", "avgrainrate"}
    req_irrig = {
        "id",
        "type",
        "date_start",
        "date_end",
        "amount (mm/day)",
        "depth (mm)",
        "start_hour",
        "end_hour",
    }

    if not req_desc.issubset(desc.columns):
        raise ValueError(f"Description missing columns: {sorted(req_desc - set(desc.columns))}")
    if not req_clim.issubset(clim.columns):
        raise ValueError(f"Climate missing columns: {sorted(req_clim - set(clim.columns))}")
    if not req_irrig.issubset(irrig.columns):
        raise ValueError(f"Irrig missing columns: {sorted(req_irrig - set(irrig.columns))}")

    desc_row = desc.loc[desc["id"].astype(str) == str(id_str)]
    if desc_row.empty:
        raise ValueError(f"ID '{id_str}' not found in Description sheet.")
    desc_row = desc_row.iloc[0]

    climate_id = str(desc_row["climateid"]).strip()
    location = str(desc_row["location"]).strip()
    out_path = file_path_root / f"{id_str}.irr"

    clim_rows = clim.loc[clim["climateid"].astype(str) == climate_id]
    if "location" in clim.columns:
        clim_rows = clim_rows.loc[clim_rows["location"].astype(str) == location]
    if clim_rows.empty:
        raise ValueError(f"No Climate row for ClimateID='{climate_id}' and Location='{location}'.")
    avg_rain_rate = clim_rows.iloc[0]["avgrainrate"]

    irrig_rows = irrig.loc[irrig["id"].astype(str) == str(id_str)].reset_index(drop=True)

    def _rows_for(irrig_type: str) -> pd.DataFrame:
        return irrig_rows.loc[
            irrig_rows["type"].astype(str).str.lower() == irrig_type.lower()
        ].reset_index(drop=True)

    sprinkler_rows = _rows_for("sprinkler")
    flood_h_rows = _rows_for("flood_h")
    flood_r_rows = _rows_for("flood_r")

    with out_path.open("w", encoding="utf-8") as f:
        sprinkler_count = len(sprinkler_rows)
        if sprinkler_count > 0:
            f.write("*** Script for irrigation ***\n")
            f.write("[Sprinkler]\n")
            f.write("Sprinkler irrigation\n")
            f.write("Average irrigation rate (cm/hour)\n")
            f.write(f"{avg_rain_rate}\n")
            f.write("Number of irrigation application\n")
            f.write(f"{sprinkler_count}\n")
            f.write("Date        AmtIrrAppl (cm/day)\n")
            for _, row in sprinkler_rows.iterrows():
                date_1 = _to_mmddyyyy(row["date_start"])
                irrig_amt = float(row["amount (mm/day)"]) / 10.0
                f.write(f"'{date_1}' {irrig_amt}\n")
        else:
            f.write("****Script for Irrigation\n")
            f.write("[Sprinkler]\n")
            f.write("Sprinkler irrigation\n")
            f.write("Average irrigation rate (cm/hour)\n")
            f.write(f"{avg_rain_rate}\n")
            f.write("Number of irrigation application\n")
            f.write("0\n")
            f.write("No Irrigation\n")

        flood_h_count = len(flood_h_rows)
        if flood_h_count > 0:
            f.write("[Flood_H]\n")
            f.write("Flood irrigation as depth of water\n")
            f.write("Number of flood irrigations as head\n")
            f.write(f"{flood_h_count}\n")
            f.write("Ponding Depth (cm) Irrigation start date and  hour/  Irrigation stop date and hour/ - one line for each application\n")
            for _, row in flood_h_rows.iterrows():
                date_1 = _to_mmddyyyy(row["date_start"])
                date_2 = _to_mmddyyyy(row["date_end"])
                irrig_depth = float(row["depth (mm)"]) / 10.0
                f.write(f"{irrig_depth}     '{date_1}' {row['start_hour']} '{date_2}' {row['end_hour']}\n")
        else:
            f.write("[Flood_H]\n")
            f.write("Flood irrigation as depth of water (cm)\n")
            f.write("Number of flood irrigations as head (cm)\n")
            f.write("0\n")
            f.write("No flood Irrigation\n")

        flood_r_count = len(flood_r_rows)
        if flood_r_count > 0:
            f.write("[Flood_R]\n")
            f.write("Flood irrigation as rate applied (cm/day)\n")
            f.write("Number of flood irrigations as rate (cm)\n")
            f.write(f"{flood_r_count}\n")
            f.write("Ponding depth (cm), rate (cm/day) Irrigation start date and  hour/  Irrigation stop date and hour/ - one line for each application\n")
            for _, row in flood_r_rows.iterrows():
                date_1 = _to_mmddyyyy(row["date_start"])
                date_2 = _to_mmddyyyy(row["date_end"])
                irrig_depth = float(row["depth (mm)"]) / 10.0
                irrig_rate = float(row["amount (mm/day)"]) / 10.0
                f.write(f"{irrig_depth}     {irrig_rate}     '{date_1}' {row['start_hour']} '{date_2}' {row['end_hour']}\n")
        else:
            f.write("[Flood_R]\n")
            f.write("Flood irrigation as rate applied (cm/day)\n")
            f.write("Number of flood irrigations as rate\n")
            f.write("0\n")
            f.write("No flood Irrigation\n")

    return out_path
