from pathlib import Path
import pandas as pd


def _normalize_cols(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.columns = [str(c).strip().lower() for c in out.columns]
    return out

def _to_mmddyyyy(value: object) -> str:
    return pd.to_datetime(value).strftime("%m/%d/%Y")


def _to_vb_time_hour(value: object) -> float:
    """Equivalent of VBA: Int(time * 24) + Minute(time) / 60."""
    if pd.isna(value):
        return 0.0

    if isinstance(value, (int, float)):
        frac_day = float(value) % 1.0
        hours_total = frac_day * 24.0
        return int(hours_total) + (int((hours_total - int(hours_total)) * 60.0) / 60.0)

    ts = pd.to_datetime(value)
    return ts.hour + ts.minute / 60.0

#Creates file for drip irrigation if used
def WriteDrip(
    id_str: str,
    description_df: pd.DataFrame,
    drip_df: pd.DataFrame,
    dripnodes_df: pd.DataFrame,
    file_path_root: Path,
) -> Path:
    """Python conversion of VBA Sub WriteDrip(idStr As String)."""

    desc = _normalize_cols(description_df)
    drip = _normalize_cols(drip_df)
    dripnodes = _normalize_cols(dripnodes_df)

    req_desc = {"id"}
    # req_drip = {"id", "date", "rate(cm/hr)", "starttime", "stoptime", "distance"}
    # req_nodes = {"id", "date", "rate(cm/hr)", "starttime", "stoptime", "distance"}

    if not req_desc.issubset(desc.columns):
        raise ValueError(f"Description missing columns: {sorted(req_desc - set(desc.columns))}")
    # if not req_drip.issubset(drip.columns):
    #     raise ValueError(f"Drip missing columns: {sorted(req_drip - set(drip.columns))}")
    # if not req_nodes.issubset(dripnodes.columns):
    #     raise ValueError(f"DripNodes missing columns: {sorted(req_nodes - set(dripnodes.columns))}")

    desc_row = desc.loc[desc["id"].astype(str) == str(id_str)]
    if desc_row.empty:
        raise ValueError(f"ID '{id_str}' not found in Description sheet.")
    out_path = file_path_root / f"{id_str}.drp"

    drip_rows = drip.loc[drip["id"].astype(str) == str(id_str)].reset_index(drop=True)
    drip_count = len(drip_rows)
    
    if drip_count > 1: 
        node_rows = dripnodes.loc[dripnodes["id"].astype(str) == str(id_str)].reset_index(drop=True)
        if len(node_rows) > 0:
            xnodes = [int(n) for n in node_rows["nodes"].tolist()]
            max_node = len(xnodes)
    
        with out_path.open("w", encoding="utf-8") as f:
            f.write("*****Script for Drip application module  ******* mAppl is cm water per hour to a 45 x 30 cm area\n")
            f.write("Number of Drip irrigations(max=25)  \n")
            f.write(f"{drip_count}\n")

            if drip_count > 1:
                f.write(
                    "tAppl_start(i) time tAppl_stop(i) time  mAppl(i),  NumNodes(i)  (repeat these 3 lines for the number of drip applications)\n"
                )

                for i, row in drip_rows.iterrows():
                    date_1 = _to_mmddyyyy(row["date"])
                    start_time = _to_vb_time_hour(row["starttime"])
                    stop_time = _to_vb_time_hour(row["stoptime"])
                    rate = row["rate(cm/hr)"]

                    f.write(f"'{date_1}' {start_time} '{date_1}' {stop_time} {rate} {max_node}\n")
                    f.write(f"Nodes for the Application {i + 1}\n")

                    for j in range(0, max_node, 15):
                        chunk = xnodes[j : j + 15]
                        f.write(" ".join(str(v) for v in chunk) + "\n")

                f.write("\n")
    else:
        with out_path.open("w", encoding="utf-8") as f:
            f.write("*****Script for Drip application module  ******* mAppl is cm water per hour to a 45 x 30 cm area\n")
            f.write("Number of Drip irrigations(max=25)  \n")
            f.write(f" {drip_count}\n")
            f.write("No drip irrigation\n")

    return 
