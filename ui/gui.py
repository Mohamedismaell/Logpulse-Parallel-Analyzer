import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from engines.sequential_engine import SequentialEngine
from engines.parallel_engine import ParallelEngine

BACKGROUND = "#282828"
SURFACE = "#353535"
SURFACE_ALT = "#404040"
BORDER = "#4A4A4A"

ACCENT = "#FFFFFF"
ACCENT_HOVER = "#E0E0E0"
SECONDARY = "#3A3A3A"
SECONDARY_HOVER = "#4A4A4A"

TEXT = "#E8E8E8"
MUTED_TEXT = "#B0B0B0"
ACCENT_TEXT = "#000000"

SUCCESS = "#55FF55"
ERROR = "#FF5555"

WINDOW_PADDING = 12
SECTION_PADDING = 10
FIELD_PADDING_X = 12
FIELD_PADDING_Y = 6

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Logpulse Analyzer Dashboard")
        self.root.geometry("1000x800") 
        self.root.configure(bg=BACKGROUND)

        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('TFrame', background=BACKGROUND)
        style.configure('Surface.TFrame', background=SURFACE)
        
        style.configure('TLabelframe', background=BACKGROUND, foreground=ACCENT, bordercolor=BORDER)
        style.configure('TLabelframe.Label', background=BACKGROUND, font=("Segoe UI", 11, "bold"), foreground=ACCENT)
        style.configure('TLabel', background=BACKGROUND, foreground=TEXT, font=("Segoe UI", 11))
        style.configure('Surface.TLabel', background=SURFACE, foreground=TEXT, font=("Segoe UI", 11))
        style.configure('Header.TLabel', font=("Segoe UI", 26, "bold"), foreground=TEXT, background=BACKGROUND)
        style.configure("Horizontal.TProgressbar", background=ACCENT, troughcolor=SURFACE_ALT, bordercolor=BACKGROUND)
        style.configure("Vertical.TScrollbar", background=SURFACE_ALT, troughcolor=BACKGROUND, bordercolor=BORDER, arrowcolor=TEXT)

        self.container = tk.Frame(self.root, bg=BACKGROUND)
        self.container.pack(fill="both", expand=True)

        self.files = []
        self.is_running = False
        self.stop_flag = False
        self.keyword = ""
        
        self.create_main_screen()
        self.create_comparison_screen()
        self.show_main_screen()

    def create_main_screen(self):
        self.frame_main = tk.Frame(self.container, bg=BACKGROUND)
        
        lbl_title = ttk.Label(self.frame_main, text="Logpulse Analyzer", style="Header.TLabel")
        lbl_title.pack(pady=(200, 40))
        
        self.btn_start = tk.Button(self.frame_main, text="Launch Application", bg=ACCENT, fg=ACCENT_TEXT, font=("Segoe UI", 16, "bold"), width=25, height=2, borderwidth=0, cursor="hand2", command=self.show_comp_screen)
        self.btn_start.pack()

        self.btn_start.bind("<Enter>", lambda e: self.btn_start.config(bg=ACCENT_HOVER))
        self.btn_start.bind("<Leave>", lambda e: self.btn_start.config(bg=ACCENT))
        
    def create_comparison_screen(self):
        self.frame_comp_base = tk.Frame(self.container, bg=BACKGROUND)
        
        self.canvas = tk.Canvas(self.frame_comp_base, bg=BACKGROUND, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.frame_comp_base, orient="vertical", command=self.canvas.yview)
        
        self.frame_comp = tk.Frame(self.canvas, bg=BACKGROUND)
        
        self.frame_comp.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas_window = self.canvas.create_window((0, 0), window=self.frame_comp, anchor="nw")
        
        def _on_canvas_configure(event):
            self.canvas.itemconfig(self.canvas_window, width=event.width)
            
        self.canvas.bind("<Configure>", _on_canvas_configure)
        
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120) * 3), "units")
            
        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        self.canvas.configure(yscrollcommand=self.scrollbar.set, yscrollincrement="15")
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        top_bar = tk.Frame(self.frame_comp, bg=BACKGROUND)
        top_bar.pack(fill="x", pady=(WINDOW_PADDING, 0), padx=WINDOW_PADDING)
        
        self.btn_back = tk.Button(top_bar, text="← Return", bg=SECONDARY, fg=TEXT, font=("Segoe UI", 10, "bold"), borderwidth=0, cursor="hand2", command=self.show_main_screen)
        self.btn_back.pack(side="left")
        self.btn_back.bind("<Enter>", lambda e: self.btn_back.config(bg=SECONDARY_HOVER))
        self.btn_back.bind("<Leave>", lambda e: self.btn_back.config(bg=SECONDARY))
        
        self.lbl_status = ttk.Label(top_bar, text="Status: Ready", font=("Segoe UI", 11, "italic"), foreground=MUTED_TEXT)
        self.lbl_status.pack(side="right")
        
        control_bar = tk.Frame(self.frame_comp, bg=SURFACE)
        control_bar.pack(fill="x", pady=SECTION_PADDING, padx=WINDOW_PADDING)
        
        self.btn_upload = tk.Button(control_bar, text="Upload Logs", bg=SECONDARY, fg=TEXT, font=("Segoe UI", 11, "bold"), borderwidth=0, width=15, cursor="hand2", command=self.upload_logs)
        self.btn_upload.pack(side="left", padx=10, pady=10)
        self.btn_upload.bind("<Enter>", lambda e: self.btn_upload.config(bg=SECONDARY_HOVER) if self.btn_upload['state'] == tk.NORMAL else None)
        self.btn_upload.bind("<Leave>", lambda e: self.btn_upload.config(bg=SECONDARY) if self.btn_upload['state'] == tk.NORMAL else None)

        self.btn_reset = tk.Button(control_bar, text="Reset", bg=SECONDARY, fg=TEXT, font=("Segoe UI", 11, "bold"), borderwidth=0, width=10, cursor="hand2", command=self.reset_all)
        self.btn_reset.pack(side="left", padx=5, pady=10)
        self.btn_reset.bind("<Enter>", lambda e: self.btn_reset.config(bg=SECONDARY_HOVER) if self.btn_reset['state'] == tk.NORMAL else None)
        self.btn_reset.bind("<Leave>", lambda e: self.btn_reset.config(bg=SECONDARY) if self.btn_reset['state'] == tk.NORMAL else None)

        self.lbl_files = ttk.Label(control_bar, text="0 files selected", style="Surface.TLabel")
        self.lbl_files.pack(side="left", padx=10)
        
        # New Dropdown Menu removing typeable state
        self.kw_var = tk.StringVar(value="Filter: ALL")
        self.combo_kw = tk.OptionMenu(control_bar, self.kw_var, "Filter: ALL", "Filter: Timeout", "Filter: Deadlock")
        self.combo_kw.config(bg=BACKGROUND, fg=TEXT, font=("Segoe UI", 10, "bold"), borderwidth=0, highlightthickness=0, activebackground=SECONDARY_HOVER, activeforeground=TEXT, cursor="hand2")
        self.combo_kw["menu"].config(bg=SURFACE, fg=TEXT, font=("Segoe UI", 10), activebackground=SECONDARY_HOVER, activeforeground=TEXT)
        self.combo_kw.pack(side="left", padx=(15,0), pady=10)

        self.btn_run = tk.Button(control_bar, text="Start Analysis", bg=ACCENT, fg=ACCENT_TEXT, font=("Segoe UI", 11, "bold"), borderwidth=0, width=15, cursor="hand2", command=self.run_comparisons)
        self.btn_run.pack(side="right", padx=(10, 10), pady=10)
        
        self.btn_stop = tk.Button(control_bar, text="Halt", bg=ERROR, fg=ACCENT_TEXT, font=("Segoe UI", 11, "bold"), borderwidth=0, width=10, cursor="hand2", state=tk.DISABLED, command=self.stop_processing)
        self.btn_stop.pack(side="right")
        
        content_frame = ttk.Frame(self.frame_comp)
        content_frame.pack(fill="both", expand=True, padx=WINDOW_PADDING, pady=(0, SECTION_PADDING))
        
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=1)
        content_frame.rowconfigure(0, weight=1)
        
        frame_seq = ttk.Labelframe(content_frame, text="Sequential System Results")
        frame_seq.grid(row=0, column=0, sticky="nsew", padx=SECTION_PADDING)
        
        frame_par = ttk.Labelframe(content_frame, text="Parallel System Results")
        frame_par.grid(row=0, column=1, sticky="nsew", padx=SECTION_PADDING)
        
        self.seq_fields = self.build_four_fields(frame_seq)
        self.par_fields = self.build_four_fields(frame_par)
        
        summary_frame = ttk.Labelframe(self.frame_comp, text="Performance Conclusion")
        summary_frame.pack(fill="x", padx=WINDOW_PADDING + SECTION_PADDING, pady=(0, WINDOW_PADDING))
        
        self.lbl_speed_seq = ttk.Label(summary_frame, text="Sequential Time: --", font=("Segoe UI", 12))
        self.lbl_speed_seq.pack(side="left", padx=FIELD_PADDING_X, pady=SECTION_PADDING)
        self.lbl_speed_par = ttk.Label(summary_frame, text="Parallel Time: --", font=("Segoe UI", 12))
        self.lbl_speed_par.pack(side="left", padx=FIELD_PADDING_X, pady=SECTION_PADDING)
        self.lbl_diff = ttk.Label(summary_frame, text="Difference: --", font=("Segoe UI", 12, "bold"))
        self.lbl_diff.pack(side="left", padx=FIELD_PADDING_X*2, pady=SECTION_PADDING)
        self.lbl_conclusion = ttk.Label(summary_frame, text="", font=("Segoe UI", 13, "bold"), foreground=SUCCESS)
        self.lbl_conclusion.pack(side="right", padx=FIELD_PADDING_X, pady=SECTION_PADDING)

        padding_frame = tk.Frame(self.frame_comp, bg=BACKGROUND, height=50)
        padding_frame.pack(fill="x")

    def build_four_fields(self, parent):
        parent.columnconfigure(0, weight=1)
        parent.columnconfigure(1, weight=1)
        parent.rowconfigure(0, weight=0) 
        parent.rowconfigure(1, weight=1) 
        parent.rowconfigure(2, weight=4)
        
        fields = {}
        prog_frame = ttk.Frame(parent)
        prog_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=FIELD_PADDING_X, pady=FIELD_PADDING_Y)
        
        prog = ttk.Progressbar(prog_frame, orient="horizontal", mode="determinate", style="Horizontal.TProgressbar")
        prog.pack(fill="x", expand=True)
        fields["prog"] = prog
        
        f1 = ttk.Labelframe(parent, text="Total Time")
        f1.grid(row=1, column=0, sticky="nsew", padx=FIELD_PADDING_Y, pady=FIELD_PADDING_Y)
        fields["time"] = ttk.Label(f1, text="0.0 sec", font=("Segoe UI", 20, "bold"), foreground=SUCCESS)
        fields["time"].pack(expand=True, pady=FIELD_PADDING_Y*2)
        
        f2 = ttk.Labelframe(parent, text="Total Errors")
        f2.grid(row=1, column=1, sticky="nsew", padx=FIELD_PADDING_Y, pady=FIELD_PADDING_Y)
        fields["err"] = ttk.Label(f2, text="0", font=("Segoe UI", 20, "bold"), foreground=ERROR)
        fields["err"].pack(expand=True, pady=FIELD_PADDING_Y*2)
        
        f3 = ttk.Labelframe(parent, text="Most Common Anomalies")
        f3.grid(row=2, column=0, sticky="nsew", padx=FIELD_PADDING_Y, pady=FIELD_PADDING_Y)
        fields["common"] = tk.Text(f3, bg=SURFACE, fg=TEXT, insertbackground=TEXT, borderwidth=0, font=("Consolas", 10), wrap="word", height=22)
        fields["common"].pack(fill="both", expand=True, padx=FIELD_PADDING_Y, pady=FIELD_PADDING_Y)
        
        f4 = ttk.Labelframe(parent, text="Anomalies Per Minute")
        f4.grid(row=2, column=1, sticky="nsew", padx=FIELD_PADDING_Y, pady=FIELD_PADDING_Y)
        fields["freq"] = tk.Text(f4, bg=SURFACE, fg=TEXT, insertbackground=TEXT, borderwidth=0, font=("Consolas", 10), wrap="word", height=22)
        fields["freq"].pack(fill="both", expand=True, padx=FIELD_PADDING_Y, pady=FIELD_PADDING_Y)
        
        return fields

    def show_main_screen(self):
        self.reset_all()
        self.frame_comp_base.pack_forget()
        self.frame_main.pack(fill="both", expand=True)
        
    def show_comp_screen(self):
        self.frame_main.pack_forget()
        self.frame_comp_base.pack(fill="both", expand=True)

    def upload_logs(self):
        if self.is_running: return
        filepaths = filedialog.askopenfilenames(filetypes=[("Log Files", "*.log"), ("All files", "*.*")])
        if filepaths:
            self.files = list(filepaths)
            self.lbl_files.config(text=f"{len(self.files)} logs staged")

    def run_comparisons(self):
        if not self.files:
            messagebox.showwarning("No Files", "Please stage log files first.")
            return

        # Fetch strict selection
        kw = self.kw_var.get()
        if kw == "Filter: ALL": kw = ""
        else: kw = kw.replace("Filter: ", "")
        
        self.keyword = kw
            
        self.is_running = True
        self.stop_flag = False
        self.btn_run.config(bg=SECONDARY, fg=MUTED_TEXT, state=tk.DISABLED) 
        self.btn_upload.config(bg=SECONDARY, fg=MUTED_TEXT, state=tk.DISABLED)
        self.btn_stop.config(bg=ERROR, fg=ACCENT_TEXT, state=tk.NORMAL)
        self.btn_reset.config(state=tk.DISABLED)
        self.combo_kw.config(state=tk.DISABLED)
        
        self.update_fields_blank(self.seq_fields)
        self.update_fields_blank(self.par_fields)
        self._set_progress(self.seq_fields["prog"], 0, len(self.files))
        self._set_progress(self.par_fields["prog"], 0, len(self.files))
        
        self._reset_speed_summary()
        self.lbl_status.config(text="Status: Evaluating Sequential Engine...")
        
        t = threading.Thread(target=self._process_data)
        t.daemon = True
        t.start()

    def stop_processing(self):
        if self.is_running:
            self.stop_flag = True
            self.lbl_status.config(text="Status: Initiating Halt...", foreground=ERROR)
            self.btn_stop.config(bg=SECONDARY, fg=MUTED_TEXT, state=tk.DISABLED)

    def reset_all(self):
        if self.is_running: self.stop_processing()
        self.files = []
        self.lbl_files.config(text="0 files selected")
        self.lbl_status.config(text="Status: Ready", foreground=MUTED_TEXT)
        self.update_fields_blank(self.seq_fields)
        self.update_fields_blank(self.par_fields)
        self._set_progress(self.seq_fields["prog"], 0, 100)
        self._set_progress(self.par_fields["prog"], 0, 100)
        self._reset_speed_summary()
        self.kw_var.set("Filter: ALL")
        if hasattr(self, 'combo_kw'): self.combo_kw.config(state=tk.NORMAL)

    def update_fields_blank(self, field_dict):
        field_dict["time"].config(text="0.0 sec")
        field_dict["err"].config(text="0")
        field_dict["common"].delete("1.0", tk.END)
        field_dict["freq"].delete("1.0", tk.END)

    def _set_progress(self, prog_widget, current, total):
        prog_widget["maximum"] = total
        prog_widget["value"] = current

    def _process_data(self):
        def check_cancel(): return self.stop_flag
        def seq_progress(current, total): self.root.after(0, lambda: self._set_progress(self.seq_fields["prog"], current, total))
        def par_progress(current, total): self.root.after(0, lambda: self._set_progress(self.par_fields["prog"], current, total))
            
        try:
            seq_res = SequentialEngine.run_analysis(self.files, keyword=self.keyword, check_cancel=check_cancel, progress_cb=seq_progress)
            if self.stop_flag:
                self.root.after(0, self._finalize_cancel)
                return
            self.root.after(0, lambda: self.update_fields(self.seq_fields, seq_res))
            self.root.after(0, lambda: self.lbl_status.config(text="Status: Evaluating Parallel Engine..."))
            
            par_res = ParallelEngine.run_analysis(self.files, keyword=self.keyword, check_cancel=check_cancel, progress_cb=par_progress)
            if self.stop_flag:
                self.root.after(0, self._finalize_cancel)
                return
            self.root.after(0, lambda: self.update_fields(self.par_fields, par_res))
            self.root.after(0, lambda: self._update_speed_summary(seq_res.time_taken, par_res.time_taken))
            self.root.after(0, self._finalize_success)
            
        except Exception as e:
            self.root.after(0, lambda: self.lbl_status.config(text=f"Error evaluating metrics! Check console.", foreground=ERROR))
            self.root.after(0, self._finalize_error)
            print(f"Error during analysis thread task -> {e}")

    def _update_speed_summary(self, seq_time, par_time):
        self.lbl_speed_seq.config(text=f"Sequential Time: {seq_time} s")
        self.lbl_speed_par.config(text=f"Parallel Time: {par_time} s")
        
        if seq_time == 0 or par_time == 0:
            self.lbl_diff.config(text="Difference: N/A")
            self.lbl_conclusion.config(text="")
            return
            
        diff_sec = round(abs(seq_time - par_time), 2)
        self.lbl_diff.config(text=f"Difference: {diff_sec} s")
        
        if seq_time > par_time:
            percent = round(((seq_time - par_time) / seq_time) * 100, 1)
            self.lbl_conclusion.config(text=f"Parallel engine is {percent}% faster! ✓", foreground=SUCCESS)
        elif par_time > seq_time:
            percent = round(((par_time - seq_time) / par_time) * 100, 1)
            self.lbl_conclusion.config(text=f"Sequential engine is {percent}% faster! ✓", foreground=SUCCESS)
        else:
            self.lbl_conclusion.config(text="Both systems took identical times.", foreground=ACCENT)

    def _reset_speed_summary(self):
        self.lbl_speed_seq.config(text="Sequential Time: --")
        self.lbl_speed_par.config(text="Parallel Time: --")
        self.lbl_diff.config(text="Difference: --")
        self.lbl_conclusion.config(text="")

    def _finalize_success(self):
        self.lbl_status.config(text="Status: Analysis Complete!", foreground=SUCCESS)
        self._reset_buttons()
    def _finalize_cancel(self):
        self.lbl_status.config(text="Status: Process Halted.", foreground=ERROR)
        self._reset_buttons()
    def _finalize_error(self):
        self._reset_buttons()

    def _reset_buttons(self):
        self.is_running = False
        self.btn_run.config(bg=ACCENT, fg=ACCENT_TEXT, state=tk.NORMAL)
        self.btn_upload.config(bg=SECONDARY, fg=TEXT, state=tk.NORMAL)
        self.btn_reset.config(bg=SECONDARY, fg=TEXT, state=tk.NORMAL)
        self.btn_stop.config(bg=SECONDARY, fg=MUTED_TEXT, state=tk.DISABLED)
        if hasattr(self, 'combo_kw'): self.combo_kw.config(state=tk.NORMAL)

    def update_fields(self, field_dict, analysis_result):
        field_dict["time"].config(text=f"{analysis_result.time_taken} sec")
        field_dict["err"].config(text=str(analysis_result.total_errors))
        
        field_dict["common"].delete("1.0", tk.END)
        for msg, count in analysis_result.most_common:
            field_dict["common"].insert(tk.END, f"► {msg}\n   Frequency: {count}\n\n")
            
        field_dict["freq"].delete("1.0", tk.END)
        for minute in sorted(analysis_result.freq_per_minute.keys()):
            field_dict["freq"].insert(tk.END, f"[{minute}]: {analysis_result.freq_per_minute[minute]} anomalies.\n")


if __name__ == "__main__":
    multiprocessing.freeze_support()
    root = tk.Tk()
    app = App(root)
    root.mainloop()
