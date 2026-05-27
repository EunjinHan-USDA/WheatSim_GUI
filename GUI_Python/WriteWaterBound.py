from pathlib import Path
import pandas as pd

# Write WaterBound.DAT
def WriteWaterBound(
    file_path_root: Path,
) -> Path:

    out_path = Path(file_path_root) / "WaterBound.DAT"

    with out_path.open("w", encoding="utf-8") as f:
        f.write("*** WATER MOVER TIME-DEPENDENT BOUNDARY" + "\n")
        f.write(" Time  Node  VarB" + "\n")
        f.write(" 252.542"+ "\n")
        f.write("   6 0.000000E+000" + "\n")
        f.write("   7 0.000000E+000" + "\n")
        f.write("   12 0.000000E+000"+ "\n")
        f.write("   13 0.000000E+000" + "\n")
    return out_path
