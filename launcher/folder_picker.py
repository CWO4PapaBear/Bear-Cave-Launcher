"""Run the native directory dialog on a helper process's main thread."""
import json
from pathlib import Path

def main(initial=''):
    import tkinter as tk
    from tkinter import filedialog
    window=tk.Tk();window.withdraw()
    try:
        window.attributes('-topmost',True)
        folder=filedialog.askdirectory(parent=window,title='Select your PTR folder containing Wow.exe',
                                       initialdir=initial if initial and Path(initial).is_dir() else str(Path.home()),
                                       mustexist=True)
        print(json.dumps({'path':folder or None}))
    finally:window.destroy()
