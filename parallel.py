import tkinter as tk
from tkinter import filedialog
import multiprocessing
import time
import re
from collections import Counter, defaultdict

BG = "#f5f5dc"
PRIMARY = "#98ff98"
DARK = "#2f4f4f"

def parse_log(path):
    pattern = r"\[(.*?)\] (\w+): (.*)"
    errors = []
    with open(path, encoding="utf-8", errors="ignore") as f:
        for line in f:
            m = re.match(pattern, line)
            if m:
                t, lvl, msg = m.groups()
                if lvl == "ERROR":
                    errors.append((t, msg))
                    for _ in range(15000):
                        x = hash(msg)
                        x = x * x
    return errors

def analyze(errors):
    msgs = [m for _, m in errors]
    c = Counter(msgs)
    freq = defaultdict(int)
    for t, _ in errors:
        minute = t[:16]
        freq[minute] += 1
    return len(errors), c.most_common(3), dict(freq)

def worker(path):
    return parse_log(path)

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Parallel Analyzer")
        self.root.geometry("650x500")
        self.root.configure(bg=BG)
        self.files = []

        tk.Label(root, text="Parallel Log Analyzer", font=("Segoe UI", 16, "bold"), bg=BG, fg=DARK).pack(pady=10)

        tk.Button(root, text="Upload Logs", bg=PRIMARY, command=self.upload).pack(pady=5)

        self.label = tk.Label(root, text="No files selected", bg=BG)
        self.label.pack()

        tk.Button(root, text="Run", bg=PRIMARY, command=self.run).pack(pady=10)

        self.output = tk.Text(root, bg="white")
        self.output.pack(fill="both", expand=True, padx=10, pady=10)

    def upload(self):
        files = filedialog.askopenfilenames(filetypes=[("Log Files", "*.log")])
        self.files = list(files)
        self.label.config(text=f"{len(self.files)} files selected")

    def run(self):
        if not self.files:
            return

        self.output.delete(1.0, tk.END)
        start = time.perf_counter()

        with multiprocessing.Pool() as pool:
            results = pool.map(worker, self.files)

        all_errors = []
        for r in results:
            all_errors.extend(r)

        total, common, freq = analyze(all_errors)
        t = time.perf_counter() - start

        self.output.insert(tk.END, f"Total Time: {round(t,2)} sec\n\n")
        self.output.insert(tk.END, f"Total Errors: {total}\n\n")

        self.output.insert(tk.END, "Most Common Errors:\n")
        for m, c in common:
            self.output.insert(tk.END, f"{m} → {c}\n")

        self.output.insert(tk.END, "\nErrors Per Minute:\n")
        for k, v in freq.items():
            self.output.insert(tk.END, f"{k} → {v}\n")

if __name__ == "__main__":
    import multiprocessing
    multiprocessing.freeze_support()

    root = tk.Tk()
    App(root)
    root.mainloop()