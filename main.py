import multiprocessing
from ui.gui import App
import tkinter as tk

if __name__ == "__main__":
    multiprocessing.freeze_support()
    root = tk.Tk()
    app = App(root)
    root.mainloop()
