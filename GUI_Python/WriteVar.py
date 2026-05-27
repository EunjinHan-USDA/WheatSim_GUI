from pathlib import Path
import pandas as pd

def _normalize_cols(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.columns = [str(c).strip().lower() for c in out.columns]
    return out


def _fmt(v: object) -> str:
    if pd.isna(v):
        return ""
    return str(v)

# Writes Variety file. Note that it inserts some lines of data that are not in the database. This is for manually changing some of the advanced parameters
def WriteVar(
    id_str: str,
    description_df: pd.DataFrame,
    variety_df: pd.DataFrame,
    file_path_root: Path,
) -> Path:
    """Python conversion of VBA Sub WriteVar(idStr As String) for wheat variety files."""

    desc = _normalize_cols(description_df)
    var = _normalize_cols(variety_df)

    req_desc = {"id", "hybrid", "varietyfile", "path"}
    req_var = {
        "hybrid",
        "ddbase",
        "ddopt",
        "ddmax",
        "t_ref",
        "t_trans",
        "t_ea/r",
        "t_ds/r",
        "t_dh/r",
        "phyllochron",
        "half_phyllochron",
        "plastochrone",
        "fpibpa",
        "srpa",
        "drpa",
        "tspa",
        "iepa",
        "jtpa",
        "bootpa",
        "headpa",
        "antspa",
        "antepa",
        "matpa",
        "rrrm",
        "rrry",
        "rvrl",
        "alpm",
        "alpy",
        "rtwl",
        "rtminwtperarea",
        "epsi",
        "lupw",
        "courmax",
        "diffx",
        "diffz",
        "velz",
        "isink",
        "rroot",
        "consti_m",
        "constk_m",
        "cmin0_m",
        "consti_y",
        "constk_y",
        "cmin0_y",
    }

    if not req_desc.issubset(desc.columns):
        raise ValueError(f"Description missing columns: {sorted(req_desc - set(desc.columns))}")
    if not req_var.issubset(var.columns):
        raise ValueError(f"variety missing columns: {sorted(req_var - set(var.columns))}")

    desc_row = desc.loc[desc["id"].astype(str) == str(id_str)]
    if desc_row.empty:
        raise ValueError(f"ID '{id_str}' not found in Description sheet.")
    desc_row = desc_row.iloc[0]

    hybrid = str(desc_row["hybrid"]).strip()
    variety_file = str(desc_row["varietyfile"]).strip()
    sim_path = str(desc_row["path"]).strip()

    var_row = var.loc[var["hybrid"].astype(str) == hybrid]
    if var_row.empty:
        raise ValueError(f"variety entry for hybrid '{hybrid}' not found.")
    var_row = var_row.iloc[0]

    out_dir = Path(file_path_root)
    if sim_path and out_dir.name.lower() != sim_path.lower():
        out_dir = out_dir / sim_path
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / variety_file

    with out_path.open("w", encoding="utf-8") as f:
        f.write("wheat variety\n")
        f.write("phyllochrons numbers for cereal phenology, the last one will be based on gdd\n")
        f.write("ddbase  ddopt   ddmax   T_ref   T_trans T_Ea/R  T_DS/R  T_DH/R\n")
        f.write(
            " ".join(
                [
                    _fmt(var_row["ddbase"]),
                    _fmt(var_row["ddopt"]),
                    _fmt(var_row["ddmax"]),
                    _fmt(var_row["t_ref"]),
                    _fmt(var_row["t_trans"]),
                    _fmt(var_row["t_ea/r"]),
                    _fmt(var_row["t_ds/r"]),
                    _fmt(var_row["t_dh/r"]),
                ]
            )
            + "\n"
        )
        f.write("Phyllochron Half_Phyllochron Plastochrone\n")
        f.write(
            " ".join(
                [
                    _fmt(var_row["phyllochron"]),
                    _fmt(var_row["half_phyllochron"]),
                    _fmt(var_row["plastochrone"]),
                ]
            )
            + "\n"
        )
        f.write("fpibpa  srpa    drpa    tspa    iepa    jtpa    bootpa  headpa  antspa  antepa  matpa\n")
        f.write(
            " ".join(
                [
                    _fmt(var_row["fpibpa"]),
                    _fmt(var_row["srpa"]),
                    _fmt(var_row["drpa"]),
                    _fmt(var_row["tspa"]),
                    _fmt(var_row["iepa"]),
                    _fmt(var_row["jtpa"]),
                    _fmt(var_row["bootpa"]),
                    _fmt(var_row["headpa"]),
                    _fmt(var_row["antspa"]),
                    _fmt(var_row["antepa"]),
                    _fmt(var_row["matpa"]),
                ]
            )
            + "\n"
        )

        f.write("[SoilRoot]\n")
        f.write("*** WATER UPTAKE PARAMETER INFORMATION **************************\n")
        f.write(" RRRM       RRRY    RVRL\n")
        f.write(" ".join([_fmt(var_row["rrrm"]), _fmt(var_row["rrry"]), _fmt(var_row["rvrl"])]) + "\n")
        f.write(" ALPM    ALPY     RTWL    RtMinWtPerUnitArea\n")
        f.write(
            " ".join(
                [
                    _fmt(var_row["alpm"]),
                    _fmt(var_row["alpy"]),
                    _fmt(var_row["rtwl"]),
                    _fmt(var_row["rtminwtperarea"]),
                ]
            )
            + "\n"
        )

        f.write("[RootDiff]\n")
        f.write(" *** ROOT MOVER PARAMETER INFORMATION ***\n")
        f.write("EPSI        lUpW             CourMax\n")
        f.write(" ".join([_fmt(var_row["epsi"]), _fmt(var_row["lupw"]), _fmt(var_row["courmax"])]) + "\n")
        f.write("Diffusivity and geotropic velocity\n")
        f.write(" ".join([_fmt(var_row["diffx"]), _fmt(var_row["diffz"]), _fmt(var_row["velz"])]) + "\n")

        f.write("[SoilNitrogen]\n")
        f.write("*** NITROGEN ROOT UPTAKE PARAMETER INFORMATION **************************\n")
        f.write("ISINK    Rroot         \n")
        f.write(" ".join([_fmt(var_row["isink"]), _fmt(var_row["rroot"])]) + "\n")
        f.write("ConstI   Constk     Cmin0 \n")
        f.write(" ".join([_fmt(var_row["consti_m"]), _fmt(var_row["constk_m"]), _fmt(var_row["cmin0_m"])]) + "\n")
        f.write(" ".join([_fmt(var_row["consti_y"]), _fmt(var_row["constk_y"]), _fmt(var_row["cmin0_y"])]) + "\n")

        # These advanced gas-exchange constants are intentionally fixed text in the original VBA.
        f.write("[Gas_Exchange Species Parameters]\n")
        f.write(" **** for photosynthesis calculations ***\n")
        f.write("EaVp    EaVc    Eaj     Hj      Sj    TPU25   Vcm25    Jm25    Rd25    Ear       g0    g1\n")
        f.write("47101   64801   37001   220000  710   15      91       190    1       66400   0.02   11.17\n")
        f.write("*** Second set of parameters for Photosynthesis ****\n")
        f.write("f    scatt  Kc25    Ko25    Eac     Eao\n")
        f.write("0.15    0.15   342      254    59400    36000\n")
        f.write("**** Third set of photosynthesis parameters ****\n")
        f.write("sensitivity (sf) Reference_Potential_(phyf, bars) stomaRatio\n")
        f.write("4.2               -0.5                             1.2\n")
        f.write("**** Secondary parameters for miscelanious equations ****\n")
        f.write("internal_CO2_Ratio   SC_param      BLC_param\n")
        f.write("0.7                   1.57           1.36\n")
        f.write("***** Q10 parameters for respiration and leaf senescence\n")
        f.write("Q10MR Q10LeafSenescense\n")
        f.write("2.0                     2.0\n")
        f.write("**** parameters for calculating the rank of the largest leaf and potential length of the leaf based on rank\n")
        f.write("leafNumberFactor_a1 leafNumberFactor_b1 leafNumberFactor_a2 leafNumberFactor_b2\n")
        f.write("-10.61                   0.25                   -5.99           0.27\n")
        f.write("**************Leaf Morphology Factors *************\n")
        f.write("LAF        WLRATIO         A_LW\n")
        f.write(" 1.37          0.106           0.75\n")
        f.write("*******************Temperature factors for growth *****************************\n")
        f.write("T_base                 T_opt            t_ceil  t_opt_GDD\n")
        f.write("8.0                   32.1              43.7       34.0\n")
        f.write("\n")

    return out_path
