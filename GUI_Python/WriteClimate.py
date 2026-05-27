import pandas as pd
from pathlib import Path
from typing import Dict

def _normalize_cols(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.columns = [str(c).strip().lower() for c in out.columns]
    return out

#Climate file
def WriteClim(
    id_str: str,
    description_df: pd.DataFrame,
    weather_df: pd.DataFrame,
    climate_df: pd.DataFrame,
    file_path_root: Path,
) -> Path:
    """Python conversion of VBA Sub WriteClim(idStr)."""

    desc = _normalize_cols(description_df)
    wea = _normalize_cols(weather_df)
    clim = _normalize_cols(climate_df)

    req_desc = {"id", "climatefile", "climateid"}
    req_wea = {"climateid", "time"}
    req_clim = {
        "climateid",
        "latitude",
        "longitude",
        "dailybulb",
        "dailywind",
        "rainintensity",
        "dailyconc",  #daily concentration of N in rainfall
        "furrow",
        "relhumid",
        "dailyco2",
        "bsolar",
        "btemp",
        "atemp",
        "erain",
        "bwind",
        "bir",
        "avgwind", #If, wind, rainIntensity, dailyConc or CO2 are 0 then the averages must be input. 
        "avgrainrate",  #If, wind, rainIntensity, dailyConc or CO2 are 0 then the averages must be input. 
        "chemconc",  #If, wind, rainIntensity, dailyConc or CO2 are 0 then the averages must be input. 
        "rh",
        "avgco2",  #If, wind, rainIntensity, dailyConc or CO2 are 0 then the averages must be input. 
        "altitude"
    }

    if not req_desc.issubset(desc.columns):
        raise ValueError(f"Description missing: {sorted(req_desc - set(desc.columns))}")
    if not req_wea.issubset(wea.columns):
        raise ValueError(f"Weather missing: {sorted(req_wea - set(wea.columns))}")
    if not req_clim.issubset(clim.columns):
        raise ValueError(f"Climate missing: {sorted(req_clim - set(clim.columns))}")

    drow = desc.loc[desc["id"].astype(str) == str(id_str)]
    if drow.empty:
        raise ValueError(f"ID '{id_str}' not found in Description.")
    drow = drow.iloc[0]

    climate_id = str(drow["climateid"]).strip()
    out_filename = str(drow["climatefile"]).strip()
    out_path = file_path_root / out_filename

    crow = clim.loc[clim["climateid"].astype(str) == climate_id]
    if crow.empty:
        raise ValueError(f"No Climate row for ClimateID={climate_id}.")
    crow = crow.iloc[0]

    wrow = wea.loc[wea["climateid"].astype(str) == climate_id]
    if wrow.empty:
        raise ValueError(f"No Weather row for ClimateID={climate_id}.")
    weather_time = str(wrow.iloc[0]["time"]).strip().lower()

    labels = []
    values = []

    #If, wind, rainIntensity, dailyConc or CO2 are 0 then the averages must be input. 
    # The Max number of average values is 4. The minimum number is 0. 
    if int(crow["dailywind"]) == 0:
        labels.append("wind")
        values.append(str(crow["avgwind"]))
    if int(crow["rainintensity"]) == 0 and weather_time == "daily":
        labels.append("irav (cm/hr)")
        values.append(str(crow["avgrainrate"]))
    if int(crow["dailyconc"]) == 0:
        labels.append("ChemConc (ppm)")
        values.append(str(crow["chemconc"]))
    if int(crow["dailyco2"]) == 0:
        labels.append("CO2 (ppm)")
        values.append(str(crow["avgco2"]))

    with out_path.open("w", encoding="utf-8") as f:
        f.write(f"***STANDARD METEOROLOGICAL DATA  Header fle for {climate_id}\n")
        f.write("Latitude Longitude\n")
        f.write(f"{crow['latitude']} {crow['longitude']}\n")
        f.write("^Daily Bulb T(1) ^ Daily Wind(2) ^RainIntensity(3) ^Daily Conc^(4) ,Furrow(5) ^Rel_humid(6) ^CO2(7)\n")
        f.write(
            f"{crow['dailybulb']:<20} {crow['dailywind']:<14} {crow['rainintensity']:<17} "
            f"{crow['dailyconc']:<15} {crow['furrow']:<11} {crow['relhumid']:<10} {crow['dailyco2']}\n"
        )
        f.write("Parameters for changing of units: BSOLAR BTEMP ATEMP ERAIN BWIND BIR \n")
        f.write(" BSOLAR is 1e6/3600 to go from j m-2 h-1 to wm-2\n")
        f.write(
            f"{crow['bsolar']:<7} {crow['btemp']:<13} {crow['atemp']:<13} {crow['erain']:<13} {crow['bwind']:<13} {crow['bir']}\n"
        )
        f.write("Average values for the site\n")
        f.write("none (additional line to avoid errors)\n")

        if labels:
            f.write(" ".join(labels) + "\n")
            f.write(" " + " ".join(values) + "\n")
        else:
            f.write("\n")

    return out_path