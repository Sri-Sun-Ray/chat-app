import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel, ttk
from tkcalendar import DateEntry
from datetime import datetime
import pandas as pd
import subprocess
import re
import os
import json
import time
from collections import Counter

# --- Persistent reference file config logic ---
CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".signal_tool_config.json")
DEFAULT_REFERENCE_FILE = os.path.join(os.path.dirname(__file__), "default_reference.csv")

def save_last_reference_path(path):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump({"last_reference": path}, f)
    except Exception as e:
        print("Error saving reference path:", e)

def load_last_reference_path():
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                return data.get("last_reference", "")
        return ""
    except Exception as e:
        print("Error loading reference path:", e)
        return ""

class SignalComparator:
    def __init__(self, root):
        self.root = root
        self.selected_signals = []
        self.last_category = ""
        self.reference_data = None
        self.last_export_path = ""
        
        # --- UI Style ---
        root.title("Version 0.1")
        root.geometry("610x600")
        root.configure(bg="#f0f0f0")
        root.resizable(False, False)
        
        # --- Main Frame ---
        main = tk.Frame(root, padx=15, pady=15, bg="#f0f0f0")
        main.pack(fill=tk.BOTH, expand=True)
        
        # --- Header ---
        header = tk.Label(main, text="Data Comparison Tool", font=("Helvetica", 14, "bold"), fg="#4a90e2", bg="#f0f0f0")
        header.pack(pady=(0, 15))
        
        # --- File Selection Frame ---
        file_frame = tk.Frame(main, bg="#f0f0f0")
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Reference File (Disabled with Settings Icon)
        tk.Label(file_frame, text="Reference File:", font=("Helvetica", 10, "bold"), fg="#333", bg="#f0f0f0", anchor='w').pack(fill=tk.X, pady=(0, 5))
        ref_frame = tk.Frame(file_frame, bg="#f0f0f0")
        ref_frame.pack(fill=tk.X, pady=(2, 5))
        self.entryRef = tk.Entry(ref_frame, width=10, state='disabled', bg="#fff", relief="solid", bd=2)
        self.entryRef.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        settings_btn = tk.Button(ref_frame, text="⚙️", command=self.open_settings, width=5, font=("Helvetica", 13), bg="#4a90e2", fg="#fff", relief="flat", bd=1)
        settings_btn.pack(side=tk.RIGHT)
        settings_btn.bind("<Enter>", lambda e: settings_btn.config(bg="#357abd"))
        settings_btn.bind("<Leave>", lambda e: settings_btn.config(bg="#4a90e2"))
        self.create_tooltip(settings_btn, "Update Reference File")
        
        # Load last used reference file or default file if available
        last_path = load_last_reference_path()
        if last_path and os.path.exists(last_path):
            self.entryRef.config(state='normal')
            self.entryRef.insert(0, last_path)
            self.entryRef.config(state='disabled')
            try:
                self.reference_data = pd.read_csv(last_path)
                self.reference_data.columns = self.reference_data.columns.str.strip().str.upper()
            except Exception as e:
                print("Failed to load saved reference file:", e)
        elif os.path.exists(DEFAULT_REFERENCE_FILE):
            self.entryRef.config(state='normal')
            self.entryRef.insert(0, DEFAULT_REFERENCE_FILE)
            self.entryRef.config(state='disabled')
            try:
                self.reference_data = pd.read_csv(DEFAULT_REFERENCE_FILE)
                self.reference_data.columns = self.reference_data.columns.str.strip().str.upper()
                save_last_reference_path(DEFAULT_REFERENCE_FILE)
            except Exception as e:
                print("Failed to load default reference file:", e)
        
        # Data Logger File
        tk.Label(file_frame, text="Data Logger File:", font=("Helvetica", 10, "bold"), fg="#333", bg="#f0f0f0", anchor='w').pack(fill=tk.X, pady=(0, 5))
        logger_frame = tk.Frame(file_frame, bg="#f0f0f0")
        logger_frame.pack(fill=tk.X, pady=(3, ))
        self.entryLogger = tk.Entry(logger_frame, width=30, bg="#fff", relief="solid", bd=2)
        self.entryLogger.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        tk.Button(logger_frame, text="Browse", command=self.select_logger, width=8, bg="#4a90e2", fg="#fff", relief="flat", bd=2).pack(side=tk.RIGHT)
        
        # EI File
        tk.Label(file_frame, text="EI File:", font=("Helvetica", 10, "bold"), fg="#333", bg="#f0f0f0", anchor='w').pack(fill=tk.X, pady=(0, 5))
        ei_frame = tk.Frame(file_frame, bg="#f0f0f0")
        ei_frame.pack(fill=tk.X, pady=(2, 5))
        self.entryEI = tk.Entry(ei_frame, width=30, bg="#fff", relief="solid", bd=2)
        self.entryEI.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        tk.Button(ei_frame, text="Browse", command=self.select_ei, width=8, bg="#4a90e2", fg="#fff", relief="flat", bd=2).pack(side=tk.RIGHT)
        
        # Time tolerance
        tk.Label(file_frame, text="Time Tolerance (ms):", font=("Helvetica", 10, "bold"), fg="#333", bg="#f0f0f0", anchor='w').pack(fill=tk.X, pady=(0, 5))
        tolerance_frame = tk.Frame(file_frame, bg="#f0f0f0")
        tolerance_frame.pack(fill=tk.X, pady=(2, 10))
        self.tolerance_spinbox = tk.Spinbox(tolerance_frame, from_=-10000, to=10000, increment=1, width=10, bg="#fff", relief="solid", bd=2)
        self.tolerance_spinbox.delete(0, tk.END)
        self.tolerance_spinbox.insert(0, '0')
        self.tolerance_spinbox.pack(side=tk.LEFT)
        
        # --- Filter Section ---
        filter_frame = tk.Frame(main, bg="#e6f0fa", bd=2, relief="solid")
        filter_frame.pack(fill=tk.X, pady=(0, 10), padx=5)
        
        tk.Label(filter_frame, text="Filter Options:", font=("Helvetica", 11, "bold"), fg="#4a90e2", bg="#e6f0fa").pack(anchor='w', padx=10, pady=5)
        
        # Radio button variable
        self.filter_option = tk.StringVar(value="total")
        
        # Three-column layout for filter options
        columns_frame = tk.Frame(filter_frame, bg="#e6f0fa")
        columns_frame.pack(fill=tk.X, pady=5, padx=10)
        
        # Column 1: Total
        total_frame = tk.Frame(columns_frame, bg="#e6f0fa")
        total_frame.pack(side=tk.LEFT, padx=10, fill=tk.Y)
        tk.Radiobutton(total_frame, text="Total", variable=self.filter_option, value="total",
                       command=self.on_filter_change, bg="#e6f0fa", fg="#333", activebackground="#e6f0fa").pack(anchor='w', pady=2)
        tk.Label(total_frame, text="", bg="#e6f0fa").pack(anchor='w', pady=2)
        
        # Column 2: Between Dates
        self.between_dates_frame = tk.Frame(columns_frame, bg="#e6f0fa")
        self.between_dates_frame.pack(side=tk.LEFT, padx=10, fill=tk.Y)
        tk.Radiobutton(self.between_dates_frame, text="Between Dates", variable=self.filter_option, value="between_dates",
                       command=self.on_filter_change, bg="#e6f0fa", fg="#333", activebackground="#e6f0fa").pack(anchor='w', pady=2)
        tk.Label(self.between_dates_frame, text="From Date:", font=("Helvetica", 9), fg="#333", bg="#e6f0fa").pack(anchor='w')
        self.from_date_picker_dates = DateEntry(self.between_dates_frame, date_pattern='yyyy-mm-dd', width=12, bg="#fff", bd=2, relief="solid")
        self.from_date_picker_dates.pack(anchor='w', pady=(2, 5))
        tk.Label(self.between_dates_frame, text="To Date:", font=("Helvetica", 9), fg="#333", bg="#e6f0fa").pack(anchor='w')
        self.to_date_picker_dates = DateEntry(self.between_dates_frame, date_pattern='yyyy-mm-dd', width=12, bg="#fff", bd=2, relief="solid")
        self.to_date_picker_dates.pack(anchor='w', pady=(2, 5))
        
        # Column 3: Between DateTime
        self.between_datetime_frame = tk.Frame(columns_frame, bg="#e6f0fa")
        self.between_datetime_frame.pack(side=tk.LEFT, padx=10, fill=tk.Y)
        tk.Radiobutton(self.between_datetime_frame, text="Between DateTime", variable=self.filter_option, value="between_datetime",
                       command=self.on_filter_change, bg="#e6f0fa", fg="#333", activebackground="#e6f0fa").pack(anchor='w', pady=2)
        date_time_frame = tk.Frame(self.between_datetime_frame, bg="#e6f0fa")
        date_time_frame.pack(anchor='w', pady=2)
        tk.Label(date_time_frame, text="From Date:", font=("Helvetica", 9), fg="#333", bg="#e6f0fa").pack(side=tk.LEFT, padx=(0, 5))
        self.from_date_picker_datetime = DateEntry(date_time_frame, date_pattern='yyyy-mm-dd', width=12, bg="#fff", bd=2, relief="solid")
        self.from_date_picker_datetime.pack(side=tk.LEFT, padx=(0, 10))
        from_time_frame = tk.Frame(date_time_frame, bg="#e6f0fa")
        from_time_frame.pack(side=tk.LEFT)
        tk.Label(from_time_frame, text="From Time:", font=("Helvetica", 9), fg="#333", bg="#e6f0fa").pack(side=tk.LEFT)
        self.from_time_entry = tk.Entry(from_time_frame, width=12, bg="#fff", bd=0)
        self.from_time_entry.pack(side=tk.LEFT, padx=(0, 5))
        self.from_time_entry.insert(0, "00:00:00.000")
        to_date_time_frame = tk.Frame(self.between_datetime_frame, bg="#e6f0fa")
        to_date_time_frame.pack(anchor='w', pady=2)
        tk.Label(to_date_time_frame, text="To Date:", font=("Helvetica", 9), fg="#333", bg="#e6f0fa").pack(side=tk.LEFT, padx=(0, 5))
        self.to_date_picker_datetime = DateEntry(to_date_time_frame, date_pattern='yyyy-mm-dd', width=12, bg="#fff", bd=2, relief="solid")
        self.to_date_picker_datetime.pack(side=tk.LEFT, padx=(0, 10))
        to_time_frame = tk.Frame(to_date_time_frame, bg="#e6f0fa")
        to_time_frame.pack(side=tk.LEFT)
        tk.Label(to_time_frame, text="To Time:", font=("Helvetica", 9), fg="#333", bg="#e6f0fa").pack(side=tk.LEFT)
        self.to_time_entry = tk.Entry(to_time_frame, width=12, bg="#fff", bd=0)
        self.to_time_entry.pack(side=tk.LEFT, padx=(0, 5))
        self.to_time_entry.insert(0, "23:59:59.999")
        
        # Store all date/time widgets for enabling/disabling
        self.date_widgets = [
            self.from_date_picker_dates,
            self.to_date_picker_dates
        ]
        
        self.datetime_widgets = [
            self.from_date_picker_datetime,
            self.from_time_entry,
            self.to_date_picker_datetime,
            self.to_time_entry
        ]
        
        # --- Comparison Buttons ---
        button_frame = tk.Frame(main, bg="#f0f0f0")
        button_frame.pack(fill=tk.X, pady=(10, 10))
        
        tk.Button(button_frame, text="Compare Tracks", command=lambda: self.perform_comparison("TRACKS", "TRACK"), width=15, bg="#4a90e2", fg="#fff", relief="flat", bd=2).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Compare Points", command=lambda: self.perform_comparison("POINTS", "POINTS"), width=15, bg="#4a90e2", fg="#fff", relief="flat", bd=2).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Compare Signals", command=lambda: self.perform_comparison("SIGNALS", "SIGNALS"), width=15, bg="#4a90e2", fg="#fff", relief="flat", bd=2).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Compare All", command=lambda: self.perform_comparison("ALL", "ALL"), width=15, bg="#4a90e2", fg="#fff", relief="flat", bd=2).pack(side=tk.LEFT, padx=5)
        
        # --- File link label ---
        self.file_link_label = tk.Label(main, text="", cursor="hand2", fg="#4a90e2", bg="#f0f0f0", font=("Helvetica", 9))
        self.file_link_label.pack(pady=5)
        self.file_link_label.bind("<Button-1>", self.open_exported_file)
        
        # Initialize filter visibility
        self.on_filter_change()

    def create_tooltip(self, widget, text):
        tooltip = tk.Toplevel(widget)
        tooltip.wm_overrideredirect(True)
        tooltip.withdraw()
        label = tk.Label(tooltip, text=text, bg="yellow", fg="black", relief="solid", borderwidth=1, font=("Helvetica", 8))
        label.pack(ipadx=5, ipady=2)

        def enter(event):
            x, y, _, _ = widget.bbox("insert")
            x += widget.winfo_rootx() + 25
            y += widget.winfo_rooty() + 25
            tooltip.geometry(f"+{x}+{y}")
            tooltip.deiconify()

        def leave(event):
            tooltip.withdraw()

        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)

    def open_settings(self):
        settings_window = Toplevel(self.root)
        settings_window.title("Reference File Settings")
        settings_window.geometry("300x150")
        settings_window.configure(bg="#f0f0f0")
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        tk.Label(settings_window, text="Update Reference File:", font=("Helvetica", 11, "bold"), fg="#4a90e2", bg="#f0f0f0").pack(pady=10)
        
        btn_frame = tk.Frame(settings_window, bg="#f0f0f0")
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="Upload", command=lambda: self.upload_reference(settings_window), width=10, bg="#4a90e2", fg="#fff", relief="flat", bd=2).pack(side=tk.LEFT, padx=5)

    def upload_reference(self, settings_window):
        path = filedialog.askopenfilename(title="Select Reference CSV", filetypes=[("CSV files", "*.csv")])
        if path and os.path.exists(path):
            self.entryRef.config(state='normal')
            self.entryRef.delete(0, tk.END)
            self.entryRef.insert(0, path)
            self.entryRef.config(state='disabled')
            try:
                self.reference_data = pd.read_csv(path)
                self.reference_data.columns = self.reference_data.columns.str.strip().str.upper()
                save_last_reference_path(path)
                settings_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load reference file:\n{e}")
            finally:
                self.root.focus_force()

    def on_filter_change(self):
        opt = self.filter_option.get()
        
        # Disable all date/time widgets first
        for widget in self.date_widgets + self.datetime_widgets:
            widget.config(state='disabled')
        
        # Enable only the selected filter widgets
        if opt == "between_dates":
            for widget in self.date_widgets:
                widget.config(state='normal')
        elif opt == "between_datetime":
            for widget in self.datetime_widgets:
                widget.config(state='normal')

    def select_logger(self):
        path = filedialog.askopenfilename(title="Select Data Logger CSV", filetypes=[("CSV files", "*.csv")])
        if path:
            self.entryLogger.delete(0, tk.END)
            self.entryLogger.insert(0, path)

    def select_ei(self):
        path = filedialog.askopenfilename(title="Select EI CSV", filetypes=[("CSV files", "*.csv")])
        if path:
            self.entryEI.delete(0, tk.END)
            self.entryEI.insert(0, path)

    def normalize_signal(self, s):
        return str(s).strip().upper()

    def validate_inputs(self):
        if self.reference_data is None:
            messagebox.showerror("Error", "Please select a reference file.")
            return False
        
        logger_path = self.entryLogger.get().strip()
        ei_path = self.entryEI.get().strip()
        
        if not logger_path or not ei_path:
            messagebox.showerror("Error", "Please select both Data Logger and EI files.")
            return False
        
        return True

    def validate_time(self, time_str):
        pattern = r'^([0-1][0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9])\.(\d{3})$'
        if not re.match(pattern, time_str):
            return False
        hours, minutes, seconds, ms = map(int, time_str.replace(':', '.').split('.'))
        return 0 <= hours <= 23 and 0 <= minutes <= 59 and 0 <= seconds <= 59 and 0 <= ms <= 999

    def get_datetime_filter(self):
        filter_mode = self.filter_option.get()
        from_datetime = None
        to_datetime = None

        if filter_mode == "total":
            pass
        elif filter_mode == "between_dates":
            from_date = self.from_date_picker_dates.get_date()
            to_date = self.to_date_picker_dates.get_date()
            from_datetime = datetime.combine(from_date, datetime.min.time())
            to_datetime = datetime.combine(to_date, datetime.max.time())
        elif filter_mode == "between_datetime":
            from_date = self.from_date_picker_datetime.get_date()
            to_date = self.to_date_picker_datetime.get_date()
            from_time = self.from_time_entry.get().strip()
            to_time = self.to_time_entry.get().strip()
            if not from_time or not to_time:
                messagebox.showerror("Invalid Input", "Please enter both From Time and To Time.")
                return None, None
            if not (self.validate_time(from_time) and self.validate_time(to_time)):
                messagebox.showerror("Invalid Time Format", "Time must be in HH:MM:SS.mmm format (e.g., 14:30:45.123).")
                return None, None
            from_datetime_str = f"{from_date} {from_time}"
            to_datetime_str = f"{to_date} {to_time}"
            try:
                from_datetime = datetime.strptime(from_datetime_str, "%Y-%m-%d %H:%M:%S.%f")
                to_datetime = datetime.strptime(to_datetime_str, "%Y-%m-%d %H:%M:%S.%f")
                if from_datetime > to_datetime:
                    messagebox.showerror("Invalid Range", "From DateTime must be earlier than To DateTime.")
                    return None, None
            except ValueError as e:
                messagebox.showerror("Invalid Date/time", f"Error parsing date/time:\n{e}")
                return None, None

        return from_datetime, to_datetime

    def perform_comparison(self, category_name, signal_column):
        if not self.validate_inputs():
            return

        # Get selected signals
        if category_name == "ALL":
            track = self.reference_data.get('TRACK', pd.Series()).dropna().astype(str).str.strip().str.upper().tolist()
            points = self.reference_data.get('POINTS', pd.Series()).dropna().astype(str).str.strip().str.upper().tolist()
            signals = self.reference_data.get('SIGNALS', pd.Series()).dropna().astype(str).str.strip().str.upper().tolist()
            self.selected_signals = list(set(track + points + signals))
        else:
            if signal_column not in self.reference_data.columns:
                messagebox.showerror("Error", f"Column '{signal_column}' not found in reference file.")
                return
            self.selected_signals = self.reference_data[signal_column].dropna().astype(str).str.strip().str.upper().tolist()

        if not self.selected_signals:
            messagebox.showwarning("No Data", f"No {category_name.lower()} found in reference file.")
            return

        # Load data files
        logger_path = self.entryLogger.get().strip()
        ei_path = self.entryEI.get().strip()

        try:
            df_logger = pd.read_csv(logger_path)
            df_ei = pd.read_csv(ei_path)
            df_logger.columns = df_logger.columns.str.strip().str.upper()
            df_ei.columns = df_ei.columns.str.strip().str.upper()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read files:\n{e}")
            return

        # Check if DataFrames are empty or missing required columns
        if df_logger.empty or df_ei.empty:
            messagebox.showwarning("No Data", "One or both input files are empty.")
            return
        if "SIGNAL NAME" not in df_logger.columns or "SIGNAL NAME" not in df_ei.columns:
            messagebox.showerror("Error", "Missing 'SIGNAL NAME' column in one or both input files.")
            return
        if "SIGNAL STATUS" not in df_logger.columns or "SIGNAL STATUS" not in df_ei.columns:
            messagebox.showerror("Error", "Missing 'SIGNAL STATUS' column in one or both input files.")
            return
        if "SIGNAL TIME" not in df_logger.columns or "SIGNAL TIME" not in df_ei.columns:
            messagebox.showerror("Error", "Missing 'SIGNAL TIME' column in one or both input files.")
            return

        # Normalize signal names
        df_logger["SIGNAL NAME"] = df_logger["SIGNAL NAME"].apply(self.normalize_signal)
        df_ei["SIGNAL NAME"] = df_ei["SIGNAL NAME"].apply(self.normalize_signal)
        selected_normalized = [self.normalize_signal(s) for s in self.selected_signals]

        # Parse datetime for filtering and comparison
        try:
            df_logger["SIGNAL TIME"] = pd.to_datetime(
                df_logger["SIGNAL TIME"].str.replace(r":(\d{3})$", r".\1", regex=True),
                format="%d/%m/%Y %H:%M:%S.%f", errors='coerce'
            )
            df_ei["SIGNAL TIME"] = pd.to_datetime(
                df_ei["SIGNAL TIME"].str.replace(r":(\d{3})$", r".\1", regex=True),
                format="%d/%m/%Y %H:%M:%S.%f", errors='coerce'
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to parse datetime:\n{e}")
            return

        # Check for invalid datetime values
        if df_logger["SIGNAL TIME"].isna().any() or df_ei["SIGNAL TIME"].isna().any():
            messagebox.showwarning("Warning", "Some SIGNAL TIME values are invalid and will be excluded.")
            df_logger = df_logger[df_logger["SIGNAL TIME"].notna()]
            df_ei = df_ei[df_ei["SIGNAL TIME"].notna()]

        # Filter by selected signals
        df_logger = df_logger[df_logger["SIGNAL NAME"].isin(selected_normalized)]
        df_ei = df_ei[df_ei["SIGNAL NAME"].isin(selected_normalized)]

        # Apply datetime filter
        from_datetime, to_datetime = self.get_datetime_filter()
        if from_datetime is not None and to_datetime is not None:
            df_logger = df_logger[(df_logger["SIGNAL TIME"] >= from_datetime) & (df_logger["SIGNAL TIME"] <= to_datetime)]
            df_ei = df_ei[(df_ei["SIGNAL TIME"] >= from_datetime) & (df_ei["SIGNAL TIME"] <= to_datetime)]

        # Show buffer message
        self.file_link_label.config(text="Creating file, please wait...")
        self.root.update()

        # Perform comparison
        result_df, extra_ei_df, event_counts = self.compare_dataframes(df_logger, df_ei, category_name)
        
        # Export results
        self.auto_export_results(result_df, extra_ei_df, category_name, event_counts)

    def compare_dataframes(self, df_logger, df_ei, category_name):
        """Optimized comparison for large datasets using pandas merge and vectorized operations."""
        result_rows = []
        extra_ei_rows = []
        event_counts = {"Data logger": 0, "EI Log": 0, "Matched": 0, "Missmatch": 0, "Extra Events": 0}

        # Validate time tolerance
        try:
            tolerance_ms = float(self.tolerance_spinbox.get())
            tolerance = abs(tolerance_ms) / 1000.0
        except Exception:
            messagebox.showerror("Error", "Invalid time tolerance value.")
            return pd.DataFrame(), pd.DataFrame(), event_counts

        # Update event counts
        event_counts["Data logger"] = df_logger.shape[0]
        event_counts["EI Log"] = df_ei.shape[0]

        # Prepare for merge
        df_logger = df_logger.copy()
        df_ei = df_ei.copy()
        df_logger['DL_IDX'] = df_logger.index
        df_ei['EI_IDX'] = df_ei.index

        # Merge on SIGNAL NAME and SIGNAL STATUS
        merged = pd.merge(
            df_logger, df_ei,
            left_on=['SIGNAL NAME', 'SIGNAL STATUS'],
            right_on=['SIGNAL NAME', 'SIGNAL STATUS'],
            suffixes=('_DL', '_EI'),
            how='left'
        )

        # Calculate time difference
        merged['TIME_DIFF'] = (merged['SIGNAL TIME_EI'] - merged['SIGNAL TIME_DL']).dt.total_seconds()

        # Vectorized time match
        if tolerance_ms > 0:
            merged['TIME_MATCH'] = (merged['TIME_DIFF'] >= 0) & (merged['TIME_DIFF'] <= tolerance)
        elif tolerance_ms < 0:
            merged['TIME_MATCH'] = (merged['TIME_DIFF'] <= 0) & (merged['TIME_DIFF'] >= -tolerance)
        else:
            merged['TIME_MATCH'] = (merged['TIME_DIFF'] == 0)

        # Only keep first matching EI event for each DL event
        matched = merged[merged['TIME_MATCH']].sort_values('TIME_DIFF').drop_duplicates('DL_IDX', keep='first')
        matched_idx = set(matched['EI_IDX'].dropna().astype(int).tolist())

        # Build result rows (MATCHED and MISSED)
        for _, row in df_logger.iterrows():
            match_row = matched[matched['DL_IDX'] == row['DL_IDX']]
            if not match_row.empty:
                ei_row = match_row.iloc[0]
                result_rows.append([
                    row.get('SLNO', row['DL_IDX']+1),
                    row['SIGNAL NAME'],
                    row['SIGNAL STATUS'],
                    row['SIGNAL TIME'].strftime("%d/%m/%Y %H:%M:%S.%f")[:-3],
                    ei_row['SIGNAL NAME'],
                    ei_row['SIGNAL STATUS'],
                    ei_row['SIGNAL TIME_EI'].strftime("%d/%m/%Y %H:%M:%S.%f")[:-3],
                    "MATCHED"
                ])
                event_counts["Matched"] += 1
            else:
                result_rows.append([
                    row.get('SLNO', row['DL_IDX']+1),
                    row['SIGNAL NAME'],
                    row['SIGNAL STATUS'],
                    row['SIGNAL TIME'].strftime("%d/%m/%Y %H:%M:%S.%f")[:-3],
                    '-','-','-',"MISSED"
                ])
                event_counts["Missmatch"] += 1

        # Find unmatched EI events (Extra)
        unmatched_ei = df_ei[~df_ei['EI_IDX'].isin(matched_idx)]
        for _, ei_row in unmatched_ei.iterrows():
            extra_ei_rows.append([
                ei_row.get('SLNO', ei_row['EI_IDX']+1),
                ei_row['SIGNAL NAME'],
                ei_row['SIGNAL STATUS'],
                ei_row['SIGNAL TIME'].strftime("%d/%m/%Y %H:%M:%S.%f")[:-3],
                "EXTRA"
            ])
            event_counts["Extra Events"] += 1

        columns = [
            'SLNO', 'DL EVENT NAME', 'DL EVENT STATUS', 'DL EVENT TIME',
            'EI EVENT NAME', 'EI EVENT STATUS', 'EI EVENT TIME', 'RESULT'
        ]
        extra_columns = [
            'SLNO', 'EI EVENT NAME', 'EI EVENT STATUS', 'EI EVENT TIME', 'RESULT'
        ]

        return pd.DataFrame(result_rows, columns=columns), pd.DataFrame(extra_ei_rows, columns=extra_columns), event_counts

    def auto_export_results(self, result_df, extra_ei_df, category_name, event_counts):
        if result_df.empty and extra_ei_df.empty:
            self.file_link_label.config(text="")
            messagebox.showinfo("No Results", f"No {category_name.lower()} data found for comparison.")
            return
            
        save_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            title="Save Comparison Result"
        )
        
        if save_path:
            try:
                with pd.ExcelWriter(save_path, engine='xlsxwriter') as writer:
                    workbook = writer.book
                    worksheet = workbook.add_worksheet("Comparison")
                    writer.sheets['Comparison'] = worksheet

                    # --- Use correct date/time widgets based on filter ---
                    filter_mode = self.filter_option.get()
                    if filter_mode == "between_dates":
                        from_date_str = self.from_date_picker_dates.get_date().strftime("%Y-%m-%d")
                        from_time_str = "00:00:00.000"
                        to_date_str = self.to_date_picker_dates.get_date().strftime("%Y-%m-%d")
                        to_time_str = "23:59:59.999"
                    elif filter_mode == "between_datetime":
                        from_date_str = self.from_date_picker_datetime.get_date().strftime("%Y-%m-%d")
                        from_time_str = self.from_time_entry.get().strip() if self.from_time_entry.get().strip() else "00:00:00.000"
                        to_date_str = self.to_date_picker_datetime.get_date().strftime("%Y-%m-%d")
                        to_time_str = self.to_time_entry.get().strip() if self.to_time_entry.get().strip() else "23:59:59.999"
                    else:  # total
                        from_date_str = ""
                        from_time_str = ""
                        to_date_str = ""
                        to_time_str = ""

                    reporting_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    num_columns = len(result_df.columns)
                    start_col = 0
                    end_col = start_col + num_columns - 1

                    # Merge formats
                    merge_format = workbook.add_format({
                        'align': 'right',
                        'valign': 'vcenter',
                        'bold': True,
                        'bg_color': '#ddeeff'
                    })
                    merge_format_header = workbook.add_format({
                        'align': 'center',
                        'valign': 'vcenter',
                        'bold': True,
                        'bg_color': '#ddeeff'
                    })
                    merge_format_counts = workbook.add_format({
                        'align': 'left',
                        'valign': 'vcenter',
                        'bold': True,
                        'bg_color': '#ddeeff'
                    })

                    # Write merged header and metadata rows
                    worksheet.merge_range(0, start_col, 0, end_col, " COMPARISON REPORT ", merge_format_header)
                    worksheet.merge_range(1, start_col, 1, end_col, f"From Date :  {from_date_str} {from_time_str}", merge_format)
                    worksheet.merge_range(2, start_col, 2, end_col, f"To Date :  {to_date_str} {to_time_str}", merge_format)
                    worksheet.merge_range(3, start_col, 3, end_col, f"Reporting Date :  {reporting_datetime}", merge_format)
                    
                    worksheet.merge_range(4, start_col, 4, end_col, f"Data Logger Events :  {event_counts['Data logger']}", merge_format_counts)
                    worksheet.merge_range(5, start_col, 5, end_col, f"EI Events :  {event_counts['EI Log']}", merge_format_counts)
                    worksheet.merge_range(6, start_col, 6, end_col, f"Matched Events :  {event_counts['Matched']}", merge_format_counts)
                    worksheet.merge_range(7, start_col, 7, end_col, f"Mismatch Events :  {event_counts['Missmatch']}", merge_format_counts)
                    worksheet.merge_range(8, start_col, 8, end_col, f"Extra EI Events :  {event_counts['Extra Events']}", merge_format_counts)

                    # Write the main comparison DataFrame starting from row 11
                    worksheet.merge_range(10, start_col, 10, end_col, "Data Logger Comparison Results", merge_format_header)
                    result_df.to_excel(writer, sheet_name="Comparison", index=False, startrow=11)

                    # Auto-adjust column widths for main comparison
                    for idx, column in enumerate(result_df.columns):
                        max_length = max(result_df[column].astype(str).map(len).max(), len(column)) + 2
                        worksheet.set_column(idx, idx, min(max_length, 50))

                    # Write the extra EI events starting after the main comparison
                    if not extra_ei_df.empty:
                        start_row_extra = len(result_df) + 13  # Leave a gap after main results
                        worksheet.merge_range(start_row_extra, start_col, start_row_extra, len(extra_ei_df.columns) - 1,
                                             "Extra EI Events (Not in Data Logger)", merge_format_header)
                        extra_ei_df.to_excel(writer, sheet_name="Comparison", index=False, startrow=start_row_extra + 1)

                        # Auto-adjust column widths for extra EI events
                        for idx, column in enumerate(extra_ei_df.columns):
                            max_length = max(extra_ei_df[column].astype(str).map(len).max(), len(column)) + 2
                            worksheet.set_column(idx, idx, min(max_length, 50))

                self.last_export_path = save_path
                self.file_link_label.config(text=f"Results exported: {os.path.basename(save_path)} (Click to open)")
                messagebox.showinfo("Export Complete", f"Results exported to:\n{save_path}")

            except ModuleNotFoundError:
                self.file_link_label.config(text="")
                messagebox.showerror("Missing Dependency", "Please install 'xlsxwriter' to export results.")
            except Exception as e:
                self.file_link_label.config(text="")
                messagebox.showerror("Export Error", f"Failed to export results:\n{e}")
        else:
            self.file_link_label.config(text="")
            messagebox.showwarning("No File Saved", "Export cancelled or no file selected.")

    def open_exported_file(self, event):
        if self.last_export_path and os.path.exists(self.last_export_path):
            try:
                if os.name == 'nt':  # Windows
                    os.startfile(self.last_export_path)
                elif os.name == 'posix':  # macOS and Linux
                    subprocess.call(['open', self.last_export_path])
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file:\n{e}")
        else:
            messagebox.showwarning("File Not Found", "Exported file not found or has been moved.")

if __name__ == "__main__":
    root = tk.Tk()
    app = SignalComparator(root)
    root.mainloop()