import tkinter as tk
import subprocess
import sys

BG = "#f5f5dc"
PRIMARY = "#98ff98"
DARK = "#2f4f4f"

def run_seq():
    subprocess.Popen([sys.executable, "sequential.py"])

def run_par():
    subprocess.Popen([sys.executable, "parallel.py"])

root = tk.Tk()
root.title("Log Analyzer")
root.geometry("420x320")
root.configure(bg=BG)

tk.Label(root, text="Log File Analyzer", font=("Segoe UI", 18, "bold"), bg=BG, fg=DARK).pack(pady=40)

tk.Button(root, text="Sequential Mode", bg=PRIMARY, width=22, height=2, command=run_seq).pack(pady=10)
tk.Button(root, text="Parallel Mode", bg=PRIMARY, width=22, height=2, command=run_par).pack(pady=10)

root.mainloop()