from pathlib import Path

import pandas as pd


def _normalize_cols(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.columns = [str(c).strip().lower() for c in out.columns]
    return out


def WriteMulch(
    id_str: str,
    description_df: pd.DataFrame,
    mulch_decomp_df: pd.DataFrame,
    mulch_geo_df: pd.DataFrame,
    file_path_root: Path,
) -> Path:
    """Python conversion of VBA Sub WriteMulch(idStr As String)."""

    desc = _normalize_cols(description_df)
    geo = _normalize_cols(mulch_geo_df)
    decomp = _normalize_cols(mulch_decomp_df)

    req_desc = {"id", "mulchgeo", "mulchdecomp"}
    req_geo = {
        "id",
        "min_hori_size",
        "diffusion_restriction",
        "longwaveradiationctrl",
        "decomposition_ctrl",
        "deltarshort",
        "deltarlong",
        "omega",
        "epsilon_mulch",
        "alpha_mulch",
        "maxstep in picard iteration",
        "tolerance_head",
        "rho_mulch",
        "pore_space",
        "maxpondingdepth",
    }
    req_decomp = {
        "id",
        "contactfraction",
        "alpha_feeding",
        "carb mass",
        "cell mass",
        "lign mass",
        "carb n mass",
        "cell n mass",
        "lign n mass",
        "carb decomp",
        "cell decomp",
        "lign decomp",
    }

    if not req_desc.issubset(desc.columns):
        raise ValueError(f"Description missing columns: {sorted(req_desc - set(desc.columns))}")
    if not req_geo.issubset(geo.columns):
        raise ValueError(f"MulchGeo missing columns: {sorted(req_geo - set(geo.columns))}")
    if not req_decomp.issubset(decomp.columns):
        raise ValueError(f"MulchDecomp missing columns: {sorted(req_decomp - set(decomp.columns))}")

    desc_row = desc.loc[desc["id"].astype(str) == str(id_str)]
    if desc_row.empty:
        raise ValueError(f"ID '{id_str}' not found in Description sheet.")
    desc_row = desc_row.iloc[0]

    id_str_mulch_geo = str(desc_row["mulchgeo"]).strip()
    id_str_mulch_decomp = str(desc_row["mulchdecomp"]).strip()

    geo_row = geo.loc[geo["id"].astype(str) == id_str_mulch_geo]
    if geo_row.empty:
        raise ValueError(f"MulchGeo entry '{id_str_mulch_geo}' not found.")
    geo_row = geo_row.iloc[0]

    decomp_row = decomp.loc[decomp["id"].astype(str) == id_str_mulch_decomp]
    if decomp_row.empty:
        raise ValueError(f"MulchDecomp entry '{id_str_mulch_decomp}' not found.")
    decomp_row = decomp_row.iloc[0]

    out_path = file_path_root / f"{id_str_mulch_geo}.mul"

    with out_path.open("w", encoding="utf-8") as f:
        f.write("*** Mulch Material information ****  based on g, m^3, J and oC\n")
        f.write("[Basic_Mulch_Configuration]\n")
        f.write("********The mulch grid configuration********\n")
        f.write("Minimal Grid Size for Horizontal Element\n")
        f.write(f"{geo_row['min_hori_size']}\n")
        f.write("********Simulation Specifications (1=Yes; 0=No)********\n")
        f.write("Only_Diffusive_Flux     Neglect_LongWave_Radiation      Include_Mulch_Decomputions\n")
        f.write(
            f"{geo_row['diffusion_restriction']:<13} {geo_row['longwaveradiationctrl']:<13} {geo_row['decomposition_ctrl']}\n"
        )
        f.write("[Mulch_Radiation]\n")
        f.write("********Mulch Radiation Properties********\n")
        f.write("DeltaRshort DeltaRlong  Omega   epsilon_mulch   alpha_mulch\n")
        f.write(
            f"{geo_row['deltarshort']:<13} {geo_row['deltarlong']:<13} {geo_row['omega']:<13} {geo_row['epsilon_mulch']:<13} {geo_row['alpha_mulch']}\n"
        )
        f.write("[Numerical_Controls]\n")
        f.write("********Picard Iteration COntrol********\n")
        f.write("Max Iteration Step (before time step shrinkage) Tolerence for Convergence (%)\n")
        f.write(f"{geo_row['maxstep in picard iteration']:<13} {geo_row['tolerance_head']}\n")
        f.write("[Mulch_Mass_Properties]\n")
        f.write("********Some Basic Information such as density, porosity and empirical parameters********\n")
        f.write("VRho_Mulch g/m3  Pore_Space  Max Held Ponding Depth\n")
        f.write(f"{geo_row['rho_mulch']:<13} {geo_row['pore_space']:<13} {geo_row['maxpondingdepth']}\n")

        f.write("[Mulch_Decomposition]\n")
        f.write("********Overall Factors********\n")
        f.write("Contacting_Fraction Feeding_Coef\n")
        f.write(f"{decomp_row['contactfraction']:<11} {decomp_row['alpha_feeding']}\n")
        f.write("The Fraction of Three Carbon Formats (Initial Value)\n")
        f.write(" Carbonhydrate(CARB)    Holo-Cellulose (CEL)   Lignin (LIG)\n")
        f.write(f"{decomp_row['carb mass']:<13} {decomp_row['cell mass']:<13} {decomp_row['lign mass']}\n")
        f.write("The Fraction of N in Three Carbon Formats (Initial Value)\n")
        f.write(" Carbonhydrate(CARB)    Holo-Cellulose (CEL)   Lignin (LIG)\n")
        f.write(f"{decomp_row['carb n mass']:<13} {decomp_row['cell n mass']:<13} {decomp_row['lign n mass']}\n")
        f.write("The Intrinsic Decomposition Speed of Three Carbon Formats (day^-1)\n")
        f.write(" Carbonhydrate(CARB)    Holo-Cellulose (CEL)   Lignin (LIG)\n")
        f.write(f"{decomp_row['carb decomp']:<13} {decomp_row['cell decomp']:<13} {decomp_row['lign decomp']}\n")

    return out_path
