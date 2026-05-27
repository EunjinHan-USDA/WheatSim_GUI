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


def _get_by_candidates_or_pos(
    row: pd.Series,
    candidates: list[str],
    pos: int,
    sheet_name: str,
) -> object:
    for cand in candidates:
        if cand in row.index:
            return row[cand]

    if pos < len(row):
        return row.iloc[pos]

    raise ValueError(
        f"{sheet_name} is missing expected value for candidates {candidates} or positional index {pos}."
    )


def _to_mmddyyyy(value: object) -> str:
    return pd.to_datetime(value).strftime("%m/%d/%Y")

#Writes the time file
def WriteTime(
    id_str: str,
    description_df: pd.DataFrame,
    time_df: pd.DataFrame,
    file_path_root: Path,
) -> Path:
    """Python conversion of VBA Sub WriteTime(idStr As String)."""

    desc = _normalize_cols(description_df)
    tim = _normalize_cols(time_df)

    if "id" not in desc.columns:
        raise ValueError("Description missing required column: id")
    if "id" not in tim.columns:
        raise ValueError("Time missing required column: id")

    desc_row = desc.loc[desc["id"].astype(str) == str(id_str)]
    if desc_row.empty:
        raise ValueError(f"ID '{id_str}' not found in Description sheet.")
    desc_row = desc_row.iloc[0]

    time_row = tim.loc[tim["id"].astype(str) == str(id_str)]
    if time_row.empty:
        raise ValueError(f"ID '{id_str}' not found in Time sheet.")
    time_row = time_row.iloc[0]

    # Mirrors VBA fields: C.rs(1), C.rs(2), ..., C.rs(10), C.rs("RunToEnd")
    date1 = _to_mmddyyyy(_get_by_candidates_or_pos(time_row, ["initial time", "initialtime", "tini", "startdate"], 1, "Time"))
    date2 = _to_mmddyyyy(_get_by_candidates_or_pos(time_row, ["tfin", "final time", "stoptime", "enddate"], 2, "Time"))
    dt = _get_by_candidates_or_pos(time_row, ["dt"], 3, "Time")
    dt_min = _get_by_candidates_or_pos(time_row, ["dtmin", "dt_min"], 4, "Time")
    dmul1 = _get_by_candidates_or_pos(time_row, ["dmul1"], 5, "Time")
    dmul2 = _get_by_candidates_or_pos(time_row, ["dmul2"], 6, "Time")
    out_daily = _get_by_candidates_or_pos(time_row, ["outputdaily", "dailyoutput", "output_daily", "daily"], 7, "Time")
    out_hourly = _get_by_candidates_or_pos(time_row, ["outputhourly", "hourlyoutput", "output_hourly", "hourly"], 8, "Time")
    wea_daily = _get_by_candidates_or_pos(time_row, ["weatherdaily", "weadaily", "weather_daily"], 9, "Time")
    wea_hourly = _get_by_candidates_or_pos(time_row, ["weatherhourly", "weahourly", "weather_hourly"], 10, "Time")
    run_to_end_col = _find_col(tim, ["runtoend", "runtoendofsoilmodel"], "Time")
    run_to_end = time_row[run_to_end_col]

    out_path = file_path_root / f"{id_str}.tim"

    with out_path.open("w", encoding="utf-8") as f:
        f.write("*** SYNCHRONIZER INFORMATION *****************************\n")
        f.write("Initial time       dt       dtMin     DMul1    DMul2    tFin\n")
        f.write(f"'{date1}'    {dt:<10} {dt_min:<10} {dmul1:<7} {dmul2:<7} '{date2}'\n")
        f.write("Output variables, 1 if true  Daily    Hourly\n")
        f.write(f"{out_daily:<11} {out_hourly}\n")
        f.write(" Daily       Hourly   Weather data frequency. if daily enter 1   0; if hourly enter 0  1  \n")
        f.write(f"{wea_daily:<11} {wea_hourly}\n")
        f.write("run to end of soil model if 1, when crop matures the model ends, otherwise continues to stop date in time file\n")
        f.write(f"{run_to_end}\n")
        f.write("\n")

    return out_path
