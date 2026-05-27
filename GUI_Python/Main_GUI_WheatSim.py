from pathlib import Path
import os
import sys
import time #just for checking processign time => delete later 
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

import pandas as pd
import SM_NO3_timeseries_fig
from WriteBiology import WriteBio
from WriteInitCondition import WriteInitCondition
from WriteNit import WriteNit
from WriteWea import WriteWea
from WriteSolute import WriteSol
from WriteGas import WriteGas
from WriteManagement import WriteMan
from WriteClimate import WriteClim
from WriteIrrig import WriteIrrig
from WriteMulch import WriteMulch
from WriteLayer import WriteLayer
from WriteVar import WriteVar
from WriteWatMoveParam import WriteWatMoveP
from WriteNit import WriteNit
from WriteDrip import WriteDrip
from WriteTime import WriteTime
from WriteRun import WriteRun
from WriteWaterBound import WriteWaterBound
from RunCreateSoilExe import RunCreateSoilExe
from UpdateGRD import UpdateGRD
from SM_NO3_timeseries_fig import SM_NO3_timeseries_fig
from SM_2DPlots import SM_2DPlots
from Plant_timeseries_fig import Plant_timeseries_fig


GUI_FONT = ("Segoe UI", 11)
STATUS_FONT = ("Segoe UI", 12)


def read_Excel_tab(excel_path: Path, sheet_name: str) -> pd.DataFrame:
    """Read and return the requested sheet from an Excel workbook, case-insensitively."""
    if not excel_path.exists():
        raise FileNotFoundError(f"Excel file not found: {excel_path}")

    with pd.ExcelFile(excel_path, engine="openpyxl") as xls:
        sheet_lookup = {name.lower(): name for name in xls.sheet_names}
        matched_sheet = sheet_lookup.get(sheet_name.lower())

        if matched_sheet is None:
            available = ", ".join(xls.sheet_names)
            raise ValueError(
                f"Sheet '{sheet_name}' was not found. Available sheets: {available}"
            )
        return pd.read_excel(xls, sheet_name=matched_sheet)


def get_gui_inputs() -> tuple[dict, tk.Tk, tk.StringVar, ttk.Progressbar, tk.Button]:
    """Open a single GUI that collects inputs and later shows simulation progress."""
    defaults = {
        "file": "E:\\GitHub\\WheatSim_GUI\\FSP_Wheat\\FSP_Excel_Input_WH_NT_2025_test.xlsx",
        "sheet": "Description",
        "outdir": "E:\\GitHub\\WheatSim_GUI\\FSP_Wheat\\FSP_NTWH_SIM",
        "WHEATSIM_dir": "E:\\GitHub\\WheatSim_GUI\\WheatSim_exe",
        "CreateSoils_dir": "E:\\GitHub\\WheatSim_GUI\\CreateSoils",
        "weather_csv_dir": "E:\\GitHub\\WheatSim_GUI\\FSP_Wheat\\Weather_CSV",
    }

    result = {}
    root = tk.Tk()
    root.title("WheatSim Input Arguments")
    root.resizable(True, True)
    root.option_add("*Font", GUI_FONT)
    root.minsize(980, 360)
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    frame = tk.Frame(root, padx=12, pady=12)
    frame.grid(row=0, column=0, sticky="nsew")
    frame.columnconfigure(1, weight=1)

    fields = [
        ("file", "Excel File", "file"),
        ("sheet", "Sheet Name", None),
        ("outdir", "Output Root Folder", "dir"),
        ("WHEATSIM_dir", "WheatSim Executable Folder", "dir"),
        ("CreateSoils_dir", "CreateSoils Folder", "dir"),
        ("weather_csv_dir", "Weather CSV Folder", "dir"),
    ]

    entries = {}

    def browse_path(field_key: str, browse_type: str) -> None:
        if browse_type == "file":
            selected = filedialog.askopenfilename(
                title="Select Excel file",
                filetypes=[("Excel files", "*.xlsx *.xlsm *.xls"), ("All files", "*.*")],
            )
        else:
            selected = filedialog.askdirectory(title="Select folder")

        if selected:
            entries[field_key].delete(0, tk.END)
            entries[field_key].insert(0, selected)

    for row_idx, (key, label, browse_type) in enumerate(fields):
        tk.Label(frame, text=label, anchor="w", width=28).grid(row=row_idx, column=0, sticky="w", pady=4)

        entry = tk.Entry(frame, width=70)
        entry.insert(0, defaults[key])
        entry.grid(row=row_idx, column=1, sticky="ew", padx=(0, 8), pady=4)
        entries[key] = entry

        if browse_type:
            tk.Button(
                frame,
                text="Browse",
                command=lambda k=key, bt=browse_type: browse_path(k, bt),
                width=9,
            ).grid(row=row_idx, column=2, sticky="w", pady=4)

    button_frame = tk.Frame(frame)
    button_frame.grid(row=len(fields), column=0, columnspan=3, sticky="e", pady=(10, 0))
    button_frame.columnconfigure(0, weight=1)

    status_var = tk.StringVar(value="Ready to run simulations.")
    tk.Label(frame, textvariable=status_var, anchor="w", font=STATUS_FONT).grid(
        row=len(fields) + 1, column=0, columnspan=3, sticky="ew", pady=(10, 4)
    )

    progress_bar = ttk.Progressbar(
        frame,
        orient="horizontal",
        mode="determinate",
        maximum=1,
        value=0,
        length=500,
    )
    progress_bar.grid(row=len(fields) + 2, column=0, columnspan=3, sticky="ew", pady=(0, 10))

    def on_run() -> None:
        input_file = entries["file"].get().strip()
        if not input_file:
            messagebox.showerror("Missing Input", "Excel file path is required.")
            return

        result.update(
            {
                "file": input_file,
                "sheet": entries["sheet"].get().strip() or "Description",
                "outdir": entries["outdir"].get().strip(),
                "WHEATSIM_dir": entries["WHEATSIM_dir"].get().strip(),
                "CreateSoils_dir": entries["CreateSoils_dir"].get().strip(),
                "weather_csv_dir": entries["weather_csv_dir"].get().strip(),
            }
        )
        status_var.set("Starting simulations...")
        run_btn.config(state="disabled")
        cancel_btn.config(state="disabled")
        close_btn.config(state="disabled")
        root.quit()

    def on_cancel() -> None:
        root.destroy()

    def on_close() -> None:
        root.destroy()

    cancel_btn = tk.Button(button_frame, text="Cancel", command=on_cancel, width=12)
    cancel_btn.grid(row=0, column=0, padx=(0, 8))
    run_btn = tk.Button(button_frame, text="Run", command=on_run, width=12)
    run_btn.grid(row=0, column=1, padx=(0, 8))
    close_btn = tk.Button(button_frame, text="Close", command=on_close, width=12, state="disabled")
    close_btn.grid(row=0, column=2)

    root.mainloop()

    if not result:
        raise SystemExit("Operation cancelled by user.")

    return result, root, status_var, progress_bar, close_btn

#====================================================================
# The main function that loops through each ID in the Description sheet and calls the functions to write each of the files for the simulation.
# ** This Python script is the equivalent of the VBA Sub WriteSelect() in the Excel interface, which loops through each ID and calls the Subs to write each file.
# ** Refer to \ARS-NEA-ACSL-MODELING - Documents\Excel interface\How to use the Excel tool.docx for more details on how the Excel interface works, and the role of the WriteSelect() subroutine.
def main() -> None:
    args, main_win, status_var, progress_bar, close_btn = get_gui_inputs()
    out_dir = Path(args["outdir"])
    weather_dir = Path(args["weather_csv_dir"])
    create_soils_dir = Path(args["CreateSoils_dir"])
    WHEATSIM_dir = Path(args["WHEATSIM_dir"])

    excel_file = Path(args["file"])
    df_descript = read_Excel_tab(excel_file, args["sheet"])

    total_runs = len(df_descript)
    progress_bar["maximum"] = max(total_runs, 1)
    progress_bar["value"] = 0
    status_var.set(f"Preparing simulations... (0/{total_runs})")
    main_win.update_idletasks()
    
    # # Start the stopwatch / counter  
    # start_time = time.process_time() 
    t0 = time.perf_counter()

    # print(f"Read {len(df_descript)} rows and {len(df_descript.columns)} columns from '{args['sheet']}'.")
    
    #loop for each ID
    for idx, row in df_descript.iterrows():
        print(f"\nProcessing ID: {row['ID']}")
        strID = str(row['ID'])
        status_var.set(f"Running simulation {idx + 1}/{total_runs} (ID: {strID})")
        progress_bar["value"] = idx
        main_win.update_idletasks()
        main_win.update()
        
        #Create a new folder for each ID
        sim_folder = out_dir / Path(strID)
        sim_folder.mkdir(exist_ok=True)
        
        #1)write *.bio file
        df_bio = read_Excel_tab(excel_file, "Biology")
        # print(df_bio.head(10))
        WriteBio (strID, df_descript, df_bio, sim_folder)
        
        #2)write *.ini file
        df_init = read_Excel_tab(excel_file, "Init")
        df_soil = read_Excel_tab(excel_file, "Soil")
        WriteInitCondition (strID, df_descript, df_init, df_soil, sim_folder)
        # print(df_init.head(10))
        
        #3) write *.wea file (weather file)
        df_wea = read_Excel_tab(excel_file, "Weather")
        df_climate = read_Excel_tab(excel_file, "Climate")
        df_time = read_Excel_tab(excel_file, "Time")
        WriteWea (strID, df_descript, df_wea, df_climate, df_time, Path(weather_dir), sim_folder)
        
        #4) write *.cli file (climate file)
        WriteClim (strID, df_descript, df_wea, df_climate, sim_folder)
    
        #5)write *.sol file => solute file
        df_solute = read_Excel_tab(excel_file, "Solute")
        WriteSol (strID, df_descript, df_soil, df_solute, sim_folder)

        #6)write *.gas file
        df_gas = read_Excel_tab(excel_file, "Gas")
        WriteGas (strID, df_descript, df_gas, sim_folder)  
        
        #7)write *.man (management) file
        df_fert = read_Excel_tab(excel_file, "Fertilization")
        df_tillage = read_Excel_tab(excel_file, "Tillage")
        WriteMan (strID, df_descript, df_init, df_time, df_fert, df_tillage, sim_folder)
        
        #8)write *.irr file
        df_irrig = read_Excel_tab(excel_file, "Irrig")
        WriteIrrig (strID, df_descript, df_climate, df_irrig, sim_folder)
        
        #9) write *.mul (Mulch/residue file)
        df_MulchDecomp = read_Excel_tab(excel_file, "MulchDecomp")
        df_MulchGeo = read_Excel_tab(excel_file, "MulchGeo")
        WriteMulch (strID, df_descript, df_MulchDecomp, df_MulchGeo, sim_folder)
        
        #10) write *.lyr (soil layer file)
        df_gridratio = read_Excel_tab(excel_file, "GridRatio")
        WriteLayer (strID, df_descript, df_gridratio, df_init, df_soil, sim_folder, create_soils_dir)
       
        #11) write *.time (time file)
        df_time = read_Excel_tab(excel_file, "Time")
        WriteTime (strID, df_descript, df_time, sim_folder)
        
        #12) write *.var (variety file)
        df_variety = read_Excel_tab(excel_file, "Variety")
        WriteVar (strID, df_descript, df_variety, sim_folder)
        
        #13) write *.nit (nitrification file)
        WriteNit (strID, df_descript, df_init, df_soil, sim_folder)
        
        #14) write *.drip (drip irrigation file)
        df_drip = read_Excel_tab(excel_file, "Drip")
        df_dripnodes = read_Excel_tab(excel_file, "DripNodes")
        WriteDrip (strID, df_descript, df_drip, df_dripnodes, sim_folder)           
        
        #15) write WaterMovParam.dat (water movement parameter file)
        df_WaterMovParam = read_Excel_tab(excel_file, "WaterMovParam")
        WriteWatMoveP (strID, df_descript, df_WaterMovParam, sim_folder)
        
        #16) Write WaterBound.DAT => which is not included in ExcleInterface, but WaterBound.DAT is required in run file, so we copy it to each simulation folder
        WriteWaterBound(sim_folder)
        
        #17) write *.run (run file)
        WriteRun (strID, df_descript, sim_folder)       

        #================================================================
        #This step is to replace running *.bat file to run CreateSoilFiles.exe for generating soil files (*.grd, *.nod, *.soi, *.dat) for each simulation.
        #RUN CREATE.SOIL TO GENERATE *.grd, *.nod, *.soi, *.dat files 
        #Note GridGen.dll creates finite element mesh 
        # and Rosetta.exe estimates soil hydraulic properties from soil texture data using pedotransfer functions.
        #================================================================  
        RunCreateSoilExe (strID, df_descript, create_soils_dir, sim_folder)

        #================================================================
        #Update boundary conditions in *.grd file for fertigation (NO3 in rainfall)
        #================================================================  
        UpdateGRD(strID, df_descript, df_soil, sim_folder)

        elapsed_sec = time.perf_counter() - t0
        print(f"1) It took {elapsed_sec:.2f} sec to create input files") 
        
        #================================================================
        #Run GLYCIM executable to run the simulation for each ID. This step is not included in the VBA code, but we can run the simulation after all the input files are prepared.
        #================================================================  
        runname = "Run" + strID + ".dat"  
        run_fname = sim_folder / f"{runname}"
        wheatsim_exe = WHEATSIM_dir / "2dWHEATSIM.exe"
        try: 
            #print(str(wheatsim_exe) + ' '+ str(run_fname))
            os.system(str(wheatsim_exe) + ' '+ str(run_fname))     
        except OSError as e:
            sys.exit("failed to execute twodsoil program, %s", str(e))   
        #print(str(wheatsim_exe) + ' '+ str(run_fname))
        
        #print("It took {0:5.1f}, sec to create input files and run GLYCIM". format(time.process_time() - start_time)) 
        elapsed_sec = time.perf_counter() - t0
        print(f"1) It took {elapsed_sec:.2f} sec to run WHEATSIM") 
        
        #================================================================
        #Make soil moisture & NO3 time-series figures from the output *.g03 file
        #================================================================  
        SM_NO3_timeseries_fig(strID, sim_folder)

        #================================================================
        #Make 2D soil moisture figures from the output *.g03 file
        #================================================================  
        start_date = pd.Timestamp(2002,5,14) #<<<==5/14 sim start time, 5/21 sowing
        end_date = pd.Timestamp(2002,5,30) #<================make changes appropriately
        SM_2DPlots(strID, start_date, end_date, sim_folder)

        # #================================================================
        # #Make plant dry matter, LAI and water stress time-series figures from the output *.g01 file
        # This subroutine is for GLYCIM, not for WHEATSIM, so we will need to make changes to use the output files from WHEATSIM. 
        # #================================================================          
        # Plant_timeseries_fig(strID, sim_folder)
        
        elapsed_sec = time.perf_counter() - t0
        print(f"2) It took {elapsed_sec:.2f} sec to run WHEATSIM and create output files") 

        progress_bar["value"] = idx + 1
        status_var.set(f"Completed simulation {idx + 1}/{total_runs} (ID: {strID})")
        main_win.update_idletasks()
        main_win.update()
               

    elapsed_sec = time.perf_counter() - t0
    print(f"It took {elapsed_sec:.2f} sec to run ALL simulations")
    status_var.set(f"All simulations complete ({total_runs}/{total_runs}).")
    close_btn.config(state="normal")
    main_win.update_idletasks()
    main_win.mainloop()

if __name__ == "__main__":
    main()