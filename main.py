import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import multiprocessing
import sequential
import parallel

BG = "#f5f5dc"
PRIMARY = "#98ff98"
DARK = "#2f4f4f"

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Logpulse Analyzer Dashboard")
        self.root.geometry("1000x700") 
        self.root.configure(bg=BG)

        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background=BG)
        style.configure('TLabelframe', background=BG, foreground=DARK)
        style.configure('TLabelframe.Label', background=BG, font=("Segoe UI", 10, "bold"), foreground=DARK)
        style.configure('TLabel', background=BG, foreground=DARK, font=("Segoe UI", 11))
        style.configure('Header.TLabel', font=("Segoe UI", 24, "bold"), foreground=DARK)

        self.container = tk.Frame(self.root, bg=BG)
        self.container.pack(fill="both", expand=True)

        self.files = []
        self.is_running = False
        self.stop_flag = False
        
        self.create_main_screen()
        self.create_comparison_screen()
        
        self.show_main_screen()

    def create_main_screen(self):
        self.frame_main = tk.Frame(self.container, bg=BG)
        
        lbl_title = ttk.Label(self.frame_main, text="Logpulse Analyzer", style="Header.TLabel")
        lbl_title.pack(pady=(200, 30))
        
        btn_start = tk.Button(self.frame_main, text="Start Application", bg=PRIMARY, fg=DARK, font=("Segoe UI", 16, "bold"), width=20, height=2, command=self.show_comp_screen)
        btn_start.pack()
        
    def create_comparison_screen(self):
        self.frame_comp = tk.Frame(self.container, bg=BG)
        
        top_bar = tk.Frame(self.frame_comp, bg=BG)
        top_bar.pack(fill="x", pady=(10, 0), padx=10)
        
        btn_back = tk.Button(top_bar, text="← Back to Start", bg="#ffd1dc", fg=DARK, font=("Segoe UI", 10, "bold"), cursor="hand2", command=self.show_main_screen)
        btn_back.pack(side="left")
        
        self.lbl_status = ttk.Label(top_bar, text="Status: Ready", font=("Segoe UI", 11, "italic"), foreground="#4a4a4a")
        self.lbl_status.pack(side="right")
        
        control_bar = tk.Frame(self.frame_comp, bg=BG)
        control_bar.pack(fill="x", pady=15, padx=15)
        
        self.btn_upload = tk.Button(control_bar, text="Upload Logs", bg="#b3e0ff", fg=DARK, font=("Segoe UI", 11, "bold"), width=15, command=self.upload_logs)
        self.btn_upload.pack(side="left")
        
        self.lbl_files = ttk.Label(control_bar, text="0 files selected")
        self.lbl_files.pack(side="left", padx=15)
        
        self.btn_run = tk.Button(control_bar, text="Start Processing", bg=PRIMARY, fg=DARK, font=("Segoe UI", 11, "bold"), width=15, command=self.run_comparisons)
        self.btn_run.pack(side="right", padx=(10, 0))
        
        self.btn_stop = tk.Button(control_bar, text="Stop", bg="#ff9999", fg=DARK, font=("Segoe UI", 11, "bold"), width=10, state=tk.DISABLED, command=self.stop_processing)
        self.btn_stop.pack(side="right")
        
        content_frame = ttk.Frame(self.frame_comp)
        content_frame.pack(fill="both", expand=True, padx=15, pady=(0, 10))
        
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=1)
        content_frame.rowconfigure(0, weight=1)
        
        frame_seq = ttk.Labelframe(content_frame, text="Sequential System Results")
        frame_seq.grid(row=0, column=0, sticky="nsew", padx=10)
        
        frame_par = ttk.Labelframe(content_frame, text="Parallel System Results")
        frame_par.grid(row=0, column=1, sticky="nsew", padx=10)
        
        self.seq_fields = self.build_four_fields(frame_seq)
        self.par_fields = self.build_four_fields(frame_par)
        
        summary_frame = ttk.Labelframe(self.frame_comp, text="Performance Comparison")
        summary_frame.pack(fill="x", padx=25, pady=(0, 15))
        
        self.lbl_speed_seq = ttk.Label(summary_frame, text="Sequential Time: --", font=("Segoe UI", 12))
        self.lbl_speed_seq.pack(side="left", padx=15, pady=10)
        
        self.lbl_speed_par = ttk.Label(summary_frame, text="Parallel Time: --", font=("Segoe UI", 12))
        self.lbl_speed_par.pack(side="left", padx=15, pady=10)
        
        self.lbl_diff = ttk.Label(summary_frame, text="Difference: --", font=("Segoe UI", 12, "bold"))
        self.lbl_diff.pack(side="left", padx=25, pady=10)
        
        self.lbl_conclusion = ttk.Label(summary_frame, text="", font=("Segoe UI", 13, "bold"))
        self.lbl_conclusion.pack(side="right", padx=15, pady=10)

    def build_four_fields(self, parent):
        parent.columnconfigure(0, weight=1)
        parent.columnconfigure(1, weight=1)
        
        # Row 0 handles the loading bar.
        parent.rowconfigure(0, weight=0)
        parent.rowconfigure(1, weight=1) 
        parent.rowconfigure(2, weight=4)
        
        fields = {}
        
        # New Progress Bar integrated clearly at the top of the quadrant
        prog_frame = ttk.Frame(parent)
        prog_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        prog = ttk.Progressbar(prog_frame, orient="horizontal", mode="determinate")
        prog.pack(fill="x", expand=True)
        fields["prog"] = prog
        
        f1 = ttk.Labelframe(parent, text="Total Time")
        f1.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        fields["time"] = ttk.Label(f1, text="0.0 sec", font=("Segoe UI", 18, "bold"), foreground="#007acc")
        fields["time"].pack(expand=True)
        
        f2 = ttk.Labelframe(parent, text="Total Errors")
        f2.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
        fields["err"] = ttk.Label(f2, text="0", font=("Segoe UI", 18, "bold"), foreground="#d9534f")
        fields["err"].pack(expand=True)
        
        f3 = ttk.Labelframe(parent, text="Most Common Errors")
        f3.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
        fields["common"] = tk.Text(f3, bg="white", font=("Consolas", 9), wrap="word")
        fields["common"].pack(fill="both", expand=True, padx=3, pady=3)
        
        f4 = ttk.Labelframe(parent, text="Errors Per Minute")
        f4.grid(row=2, column=1, sticky="nsew", padx=5, pady=5)
        fields["freq"] = tk.Text(f4, bg="white", font=("Consolas", 9), wrap="word")
        fields["freq"].pack(fill="both", expand=True, padx=3, pady=3)
        
        return fields

    def show_main_screen(self):
        self.frame_comp.pack_forget()
        self.frame_main.pack(fill="both", expand=True)
        
    def show_comp_screen(self):
        self.frame_main.pack_forget()
        self.frame_comp.pack(fill="both", expand=True)

    def upload_logs(self):
        if self.is_running:
            return
        filepaths = filedialog.askopenfilenames(filetypes=[("Log Files", "*.log"), ("All files", "*.*")])
        if filepaths:
            self.files = list(filepaths)
            self.lbl_files.config(text=f"{len(self.files)} files selected")

    def run_comparisons(self):
        if not self.files:
            messagebox.showwarning("No Files", "Please upload log files first.")
            return
            
        self.is_running = True
        self.stop_flag = False
        self.btn_run.config(state=tk.DISABLED)
        self.btn_upload.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        
        self.update_fields(self.seq_fields, "0.0", "0", [], {})
        self.update_fields(self.par_fields, "0.0", "0", [], {})
        self._set_progress(self.seq_fields["prog"], 0, len(self.files))
        self._set_progress(self.par_fields["prog"], 0, len(self.files))
        
        self._reset_speed_summary()
        self.lbl_status.config(text="Status: Evaluating Sequential Model...")
        
        t = threading.Thread(target=self._process_data)
        t.daemon = True
        t.start()

    def stop_processing(self):
        if self.is_running:
            self.stop_flag = True
            self.lbl_status.config(text="Status: Canceling...")
            self.btn_stop.config(state=tk.DISABLED)

    def _set_progress(self, prog_widget, current, total):
        prog_widget["maximum"] = total
        prog_widget["value"] = current

    def _process_data(self):
        def check_cancel():
            return self.stop_flag
            
        def seq_progress(current, total):
            self.root.after(0, lambda: self._set_progress(self.seq_fields["prog"], current, total))
            
        def par_progress(current, total):
            self.root.after(0, lambda: self._set_progress(self.par_fields["prog"], current, total))
            
        try:
            # 1. Processing Sequential System
            seq_res = sequential.run_analysis(self.files, check_cancel=check_cancel, progress_cb=seq_progress)
            if self.stop_flag:
                self.root.after(0, self._finalize_cancel)
                return
                
            self.root.after(0, lambda: self.update_fields(self.seq_fields, *seq_res))
            self.root.after(0, lambda: self.lbl_status.config(text="Status: Evaluating Parallel Model..."))
            
            # 2. Processing Parallel System
            par_res = parallel.run_analysis(self.files, check_cancel=check_cancel, progress_cb=par_progress)
            if self.stop_flag:
                self.root.after(0, self._finalize_cancel)
                return
                
            self.root.after(0, lambda: self.update_fields(self.par_fields, *par_res))
            self.root.after(0, lambda: self._update_speed_summary(seq_res[0], par_res[0]))
            self.root.after(0, self._finalize_success)
            
        except Exception as e:
            self.root.after(0, lambda: self.lbl_status.config(text=f"Error evaluating metrics! Check console."))
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
            self.lbl_conclusion.config(text=f"Parallel is {percent}% faster! ✓", foreground="#2ca02c")
        elif par_time > seq_time:
            percent = round(((par_time - seq_time) / par_time) * 100, 1)
            self.lbl_conclusion.config(text=f"Sequential is {percent}% faster! ✓", foreground="#2ca02c")
        else:
            self.lbl_conclusion.config(text="Both systems took equal time.", foreground="#007acc")

    def _reset_speed_summary(self):
        self.lbl_speed_seq.config(text="Sequential Time: --")
        self.lbl_speed_par.config(text="Parallel Time: --")
        self.lbl_diff.config(text="Difference: --")
        self.lbl_conclusion.config(text="")

    def _finalize_success(self):
        self.lbl_status.config(text="Status: Analysis Complete!")
        self._reset_buttons()
        
    def _finalize_cancel(self):
        self.lbl_status.config(text="Status: Process Canceled.")
        self._reset_buttons()
        
    def _finalize_error(self):
        self._reset_buttons()

    def _reset_buttons(self):
        self.is_running = False
        self.btn_run.config(state=tk.NORMAL)
        self.btn_upload.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)

    def update_fields(self, field_dict, t, errs, common, freq):
        field_dict["time"].config(text=f"{t} sec" if t != "0.0" else "0.0 sec")
        field_dict["err"].config(text=str(errs))
        
        field_dict["common"].delete("1.0", tk.END)
        for msg, count in common:
            field_dict["common"].insert(tk.END, f"► {msg}\n   Count: {count}\n\n")
            
        field_dict["freq"].delete("1.0", tk.END)
        for minute in sorted(freq.keys()):
            field_dict["freq"].insert(tk.END, f"[{minute}]: {freq[minute]} errors\n")


if __name__ == "__main__":
    multiprocessing.freeze_support()
    root = tk.Tk()
    app = App(root)
    root.mainloop()