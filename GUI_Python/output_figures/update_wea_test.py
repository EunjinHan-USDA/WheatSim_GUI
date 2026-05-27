#!/usr/bin/env python3
import csv
import argparse
from datetime import datetime
from pathlib import Path
import shlex

# ---------- helpers ----------
def try_parse_datetime(s: str):
    if s is None:
        return None
    s = str(s).strip().strip("'").strip('"')
    if not s:
        return None

    fmts = [
        "%m/%d/%Y %H:%M",
        "%m/%d/%Y %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d %H:%M:%S",
        "%m/%d/%Y",
        "%Y-%m-%d",
    ]
    for f in fmts:
        try:
            return datetime.strptime(s, f)
        except ValueError:
            pass

    # Python ISO fallback
    try:
        return datetime.fromisoformat(s)
    except ValueError:
        return None


def normalize(name: str):
    return "".join(ch for ch in name.lower() if ch.isalnum())


def find_col(fieldnames, candidates):
    norm_map = {normalize(c): c for c in fieldnames}
    for cand in candidates:
        key = normalize(cand)
        if key in norm_map:
            return norm_map[key]
    return None


def to_float(v):
    if v is None:
        return None
    s = str(v).strip()
    if s == "":
        return None
    try:
        return float(s)
    except ValueError:
        return None


def fmt_num(x, dec=4):
    if x is None:
        return ""
    s = f"{x:.{dec}f}"
    return s.rstrip("0").rstrip(".") if "." in s else s


# ---------- read historical CSV ----------
def build_obs_lookup(csv_path, source_year=None):
    with open(csv_path, "r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        raise ValueError("Historical CSV has no data rows.")

    fieldnames = reader.fieldnames or []

    # Possible date/time columns
    dt_col = find_col(fieldnames, ["DateTime", "Datetime", "Timestamp", "TimeStamp", "Date", "Time"])
    date_col = find_col(fieldnames, ["Date"])
    time_col = find_col(fieldnames, ["Time"])
    year_col = find_col(fieldnames, ["Year", "YYYY"])
    month_col = find_col(fieldnames, ["Month", "MM"])
    day_col = find_col(fieldnames, ["Day", "DD"])
    hour_col = find_col(fieldnames, ["Hour", "HR", "HOUR"])

    # Weather columns to copy
    rad_col = find_col(fieldnames, ["Rad", "Radiation", "SolarRad", "SolarRadiation"])
    temp_col = find_col(fieldnames, ["Temper", "Temp", "Temperature", "AirTemp"])
    rain_col = find_col(fieldnames, ["rain", "Rain", "Precip", "Precipitation"])
    rh_col = find_col(fieldnames, ["RH", "RelHumidity", "RelativeHumidity", "Humidity"])

    missing = [name for name, col in [("Rad", rad_col), ("Temper", temp_col), ("rain", rain_col), ("RH", rh_col)] if col is None]
    if missing:
        raise ValueError(f"Could not find required weather column(s) in CSV: {missing}")

    lookup = {}
    duplicates = 0

    for r in rows:
        dt = None

        # 1) DateTime-like single column
        if dt_col:
            dt = try_parse_datetime(r.get(dt_col))

        # 2) Date + Time columns
        if dt is None and date_col and time_col:
            dt = try_parse_datetime(f"{r.get(date_col, '')} {r.get(time_col, '')}")

        # 3) Year/Month/Day + optional Hour columns
        if dt is None and year_col and month_col and day_col:
            try:
                y = int(float(r[year_col]))
                m = int(float(r[month_col]))
                d = int(float(r[day_col]))
                h = int(float(r[hour_col])) if hour_col and str(r.get(hour_col, "")).strip() != "" else 0
                dt = datetime(y, m, d, h)
            except Exception:
                dt = None

        # If no datetime parsed, skip row
        if dt is None:
            continue

        if source_year is not None and dt.year != source_year:
            continue

        key = (dt.month, dt.day, dt.hour)
        if key in lookup:
            duplicates += 1

        lookup[key] = {
            "Rad": to_float(r.get(rad_col)),
            "Temper": to_float(r.get(temp_col)),
            "rain": to_float(r.get(rain_col)),
            "RH": to_float(r.get(rh_col)),
        }

    if not lookup:
        year_msg = f" for source year {source_year}" if source_year is not None else ""
        raise ValueError(f"No observation rows matched usable datetime/hour{year_msg}.")

    if duplicates:
        print(f"Warning: {duplicates} duplicate month/day/hour rows in CSV; last occurrence was used.")

    return lookup


# ---------- process WEA ----------
def process_wea(in_wea, out_wea, obs_lookup, target_year=2002):
    with open(in_wea, "r", encoding="utf-8") as f:
        lines = f.readlines()

    if len(lines) < 3:
        raise ValueError("WEA file seems too short.")

    header1 = lines[0].rstrip("\n")
    header2 = lines[1].rstrip("\n")
    data_lines = [ln.rstrip("\n") for ln in lines[2:] if ln.strip()]

    out_lines = [header1, header2]
    updated = 0
    missing = 0

    for ln in data_lines:
        # shlex handles quoted date like '05/12/2002'
        parts = shlex.split(ln)
        # Expected 10 fields:
        # JDay Date Hour Rad Temper rain Wind NConc RH CO2
        if len(parts) < 10:
            # keep as-is if malformed
            out_lines.append(ln)
            continue

        jday = int(float(parts[0]))
        date_str = parts[1].strip("'").strip('"')
        hour = int(float(parts[2]))

        try:
            dt_old = datetime.strptime(date_str, "%m/%d/%Y")
        except ValueError:
            out_lines.append(ln)
            continue

        key = (dt_old.month, dt_old.day, hour)
        obs = obs_lookup.get(key)

        # Keep month/day from WEA, force year to target_year
        dt_new = dt_old.replace(year=target_year)
        new_date = dt_new.strftime("%m/%d/%Y")
        new_jday = dt_new.timetuple().tm_yday

        # Existing values
        rad = to_float(parts[3])
        temp = to_float(parts[4])
        rain = to_float(parts[5])
        wind = parts[6]
        nconc = parts[7]
        rh = to_float(parts[8])
        co2 = parts[9]

        if obs:
            if obs["Rad"] is not None:
                rad = obs["Rad"]
            if obs["Temper"] is not None:
                temp = obs["Temper"]
            if obs["rain"] is not None:
                rain = obs["rain"]
            if obs["RH"] is not None:
                rh = obs["RH"]
            updated += 1
        else:
            missing += 1

        out_ln = (
            f"{new_jday:>4d} "
            f"'{new_date}' "
            f"{hour:>2d} "
            f"{fmt_num(rad):>10s} "
            f"{fmt_num(temp):>10s} "
            f"{fmt_num(rain):>10s} "
            f"{wind:>9s} "
            f"{nconc:>11s} "
            f"{fmt_num(rh):>8s} "
            f"{co2:>6s}"
        )
        out_lines.append(out_ln)

    with open(out_wea, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out_lines) + "\n")

    print(f"Done. Updated rows: {updated}, no matching obs row: {missing}")
    print(f"Output: {out_wea}")


def main():
    p = argparse.ArgumentParser(
        description="Replace Rad/Temper/rain/RH in a .wea file from historical observation CSV."
    )
    p.add_argument("--wea", required=True, help="Input .wea file path")
    p.add_argument("--obs", required=True, help="Historical CSV file path")
    p.add_argument("--out", required=True, help="Output .wea file path")
    p.add_argument("--target-year", type=int, default=2002, help="Year to force in output Date column")
    p.add_argument(
        "--source-year",
        type=int,
        default=None,
        help="If set, only use observation rows from this year (optional).",
    )

    args = p.parse_args()

    wea = Path(args.wea)
    obs = Path(args.obs)
    out = Path(args.out)

    if not wea.exists():
        raise FileNotFoundError(f"WEA file not found: {wea}")
    if not obs.exists():
        raise FileNotFoundError(f"Observation CSV file not found: {obs}")

    lookup = build_obs_lookup(obs, source_year=args.source_year)
    process_wea(wea, out, lookup, target_year=args.target_year)


if __name__ == "__main__":
    main()