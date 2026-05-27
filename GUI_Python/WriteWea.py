import pandas as pd
from pathlib import Path
from typing import Dict

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


# Sequence of operations (source: weather and climate file.docx)
# 1.	Select WeatherID, ClimateID from the Description table where ID is the value of interest
# 2.	Select climate info from the climate table based on ClimateID
# 3.	Select source_name, source, and time values from the weather table based on ClimateID and WeatherID
# 4.	Select start and end dates from the time table where ID is the value of interest
# 5.	Open the source_name file as a data source
# 6.	Query the data source for weather data based on the values of Time and ClimateID and WeatherID selected previously.
# 7.	Use information from the climate table to determine which fields to write to the weather file
# 8.	Write to a file named after the ID with ‘.wea’ as an extension. File should be placed in the folder named after the ID.

def WriteWea(
    id_str: str,
    description_df: pd.DataFrame,   # Description sheet
    weather_df: pd.DataFrame,       # Weather sheet (Source_name, time, ClimateID, WeatherID)
    climate_df: pd.DataFrame,       # Climate sheet
    time_df: pd.DataFrame,          # Time sheet
    #weather_tables: Dict[str, pd.DataFrame],  # key: Source_name, value: weather data table
    file_path_wea: Path,
    file_path_root: Path,
) -> Path:
    """
    Python version of VBA Sub WriteWea(idStr).

    weather_tables:
      Example: {"MyWeatherTable": df_of_weather_rows}
      where df has columns like:
      daily:  jday, date, srad, tmax, tmin, rain, wind, rh, co2, climateid, weatherid
      hourly: jday, date, hour, srad, temperature, rain, wind, rh, co2, climateid, weatherid
    """

    # Normalize column names for case-insensitive matching
    desc = description_df.copy()
    desc.columns = [c.strip().lower() for c in desc.columns]

    wea = weather_df.copy()
    wea.columns = [c.strip().lower() for c in wea.columns]

    clim = climate_df.copy()
    clim.columns = [c.strip().lower() for c in clim.columns]

    tdf = time_df.copy()
    tdf.columns = [c.strip().lower() for c in tdf.columns]

    # Required columns
    req_desc = {"id", "climateid", "weatherid", "weatherfilename"}
    req_wea = {"climateid", "weatherid", "source_name", "time"}
    req_clim = {"climateid", "dailywind", "relhumid", "dailyco2"}
    req_time = {"id", "startdate", "enddate"}

    if not req_desc.issubset(desc.columns):
        raise ValueError(f"Description missing: {sorted(req_desc - set(desc.columns))}")
    if not req_wea.issubset(wea.columns):
        raise ValueError(f"Weather missing: {sorted(req_wea - set(wea.columns))}")
    if not req_clim.issubset(clim.columns):
        raise ValueError(f"Climate missing: {sorted(req_clim - set(clim.columns))}")
    if not req_time.issubset(tdf.columns):
        raise ValueError(f"Time missing: {sorted(req_time - set(tdf.columns))}")

    # 1) Description row for id_str
    drow = desc.loc[desc["id"].astype(str) == str(id_str)]
    if drow.empty:
        raise ValueError(f"ID '{id_str}' not found in Description.")
    drow = drow.iloc[0]

    climate_id = str(drow["climateid"]).strip()
    weather_id = str(drow["weatherid"]).strip()
    out_filename = str(drow["weatherfilename"]).strip()
    out_path = file_path_root / out_filename  #weather file name (e.g., FSP2002.wea)
    

    # 2) Weather metadata row (source_name + interval)
    wrow = wea.loc[
        (wea["climateid"].astype(str) == climate_id) &
        (wea["weatherid"].astype(str) == weather_id)
    ]
    if wrow.empty:
        raise ValueError(f"No Weather row for ClimateID={climate_id}, WeatherID={weather_id}.")
    wrow = wrow.iloc[0]

    #now get name of weather file
    weather_fname = str(wrow["source_name"]).strip()
    interval = str(wrow["time"]).strip().lower()  # daily/hourly expected

    # 3) check what data are available in the Climate sheet for this climate_id
    crow = clim.loc[clim["climateid"].astype(str) == climate_id]
    if crow.empty:
        raise ValueError(f"No Climate row for ClimateID={climate_id}.")
    crow = crow.iloc[0]

    DailyWind = int(crow["dailywind"]) if pd.notna(crow["dailywind"]) else 0
    DailyConc = int(crow["dailyconc"]) if pd.notna(crow["dailyconc"]) else 0   #EJ added for fertigation
    RelHumid = int(crow["relhumid"]) if pd.notna(crow["relhumid"]) else 0
    DailyCO2 = int(crow["dailyco2"]) if pd.notna(crow["dailyco2"]) else 0
    AvgWind = int(crow["avgwind"]) if pd.notna(crow["avgwind"]) else 0
    AvgRainRate = int(crow["avgrainrate"]) if pd.notna(crow["avgrainrate"]) else 0
    AvgCO2 = int(crow["avgco2"]) if pd.notna(crow["avgco2"]) else 0

    # 4) Time window: startDate - 2, endDate + 4
    tr = tdf.loc[tdf["id"].astype(str) == str(id_str)]
    if tr.empty:
        raise ValueError(f"No Time row for ID={id_str}.")
    tr = tr.iloc[0]

    start_date = pd.to_datetime(tr["startdate"]) - pd.Timedelta(days=2)
    end_date = pd.to_datetime(tr["enddate"]) + pd.Timedelta(days=4)

    # 5) Read weather data from weather csv file
    wea_csv_path = file_path_wea / weather_fname
    if wea_csv_path.exists() and wea_csv_path.is_file():
        wd=pd.read_csv(wea_csv_path) 
        wd.columns = [c.strip().lower() for c in wd.columns]
    else:
        print(f"Error: The file '{wea_csv_path}' does not exist or is not a file.")


    # Must have filter columns
    for col in ("climateid", "weatherid", "date"):
        if col not in wd.columns:
            raise ValueError(f"Weather source '{weather_fname}' missing column '{col}'.")

    wd["date"] = pd.to_datetime(wd["date"])
    wd = wd.loc[
        (wd["climateid"].astype(str) == climate_id) &
        (wd["weatherid"].astype(str) == weather_id) &
        (wd["date"] >= start_date) &
        (wd["date"] <= end_date)
    ].sort_values(["date"] + (["hour"] if "hour" in wd.columns else []))

    # 6) Write output
    with out_path.open("w", encoding="utf-8") as f:
        f.write(f"*** {id_str},  {interval} weather data\n")

        if interval == "daily":
            needed = ["jday", "date", "srad", "tmax", "tmin", "rain"]
            missing = [c for c in needed if c not in wd.columns]
            if missing:
                raise ValueError(f"Daily weather table missing columns: {missing}")

            # f.write(" JDay   Date       Rad      Temper    rain\n")
            header_flag = 0
            for _, r in wd.iterrows():
                parts = [
                    str(r["jday"]),
                    f"'{pd.to_datetime(r['date']).strftime('%m/%d/%Y')}'",
                    str(r["srad"]),
                    str(r["tmax"]),
                    str(r["tmin"]),
                    str(r["rain"]),
                ]
                if header_flag == 0: header_list = " JDay   Date       Rad      Tmax    Tmin    rain"
                if DailyWind > 0 and "wind" in wd.columns:
                    parts.append(f"{str(r['wind']):<7}")
                    if header_flag == 0: header_list = header_list + "     Wind"
                if DailyConc > 0 and "conc" in wd.columns:  #N concentration [ug/cm3] in rainfall=> EJ added for fertigation
                    n_conc = _as_vb_sci(r['conc'])   #N concentration in hourly rainfall is very small, so convert to scientific notation with 4 decimal places, and remove leading zeros in exponent for compatibility with VBA format.
                    parts.append(f"{n_conc:<11}")
                    if header_flag == 0: header_list = header_list + "     NConc"
                if RelHumid > 0 and "rh" in wd.columns:
                    parts.append(f"{str(r['rh']):<7}")
                    if header_flag == 0: header_list = header_list + "     RH"
                if DailyCO2 > 0 and "co2" in wd.columns:
                    parts.append(str(r["co2"]))
                    if header_flag == 0: header_list = header_list + "     CO2"
                if header_flag == 0: 
                    f.write(header_list + "\n")
                    header_flag = 1
                f.write(" ".join(parts) + "\n")
        elif interval == "hourly":
            needed = ["jday", "date", "hour", "srad", "temperature", "rain"]
            missing = [c for c in needed if c not in wd.columns]
            if missing:
                raise ValueError(f"Hourly weather table missing columns: {missing}")

            # (source: weather and climate file.docx)
            # The total number of columns in the weather file is:
            # NCD=4+2*MSW1+MSW2+MSW3+ISOL*MSW4+MSW6+MSW7
            # There is a minimum of 4 columns (radiation, Tmax, Tmin, rainfall)
            # ****The order after these 4 is:
            # Wind, Twet, tdry, IR, Cprec, Rh, CO2

            #f.write(" JDay   Date     Hour     Rad      Temper    rain     Wind   NConc   RH   CO2\n")
            header_flag = 0
            for _, r in wd.iterrows():
                parts = [
                    str(r["jday"]),
                    f"'{pd.to_datetime(r['date']).strftime('%m/%d/%Y')}' {str(r['hour']):<7} {str(r['srad']):<8} {str(r['temperature']):<9} {str(r['rain']):<8}",
                ]
                
                if header_flag == 0: header_list = " JDay   Date     Hour     Rad      Temper    rain"
                # order is important here, as the model expects the fields in a specific order. The presence of the fields is determined by the values in the Climate sheet for this climate_id.
                if DailyWind > 0 and "wind" in wd.columns:
                    parts.append(f"{str(r['wind']):<7}")
                    if header_flag == 0: header_list = header_list + "     Wind"
                if DailyConc > 0 and "conc" in wd.columns:  #N concentration [ug/cm3] in rainfall=> EJ added for fertigation
                    n_conc = _as_vb_sci(r['conc'])   #N concentration in hourly rainfall is very small, so convert to scientific notation with 4 decimal places, and remove leading zeros in exponent for compatibility with VBA format.
                    parts.append(f"{n_conc:<11}")
                    if header_flag == 0: header_list = header_list + "     NConc"
                if RelHumid > 0 and "rh" in wd.columns:
                    parts.append(f"{str(r['rh']):<7}")
                    if header_flag == 0: header_list = header_list + "     RH"
                if DailyCO2 > 0 and "co2" in wd.columns:
                    parts.append(f"{str(r['co2'])}")
                    if header_flag == 0: header_list = header_list + "     CO2"
                if header_flag == 0: 
                    f.write(header_list + "\n")
                    header_flag = 1
                f.write(" ".join(parts) + "\n")
        else:
            raise ValueError(f"Unsupported interval '{interval}'. Expected 'daily' or 'hourly'.")

    return 