"""Native controls for Wine testers; uses the ordinary updater without a web engine."""
import tkinter as tk
from tkinter import filedialog, messagebox

from .app import Application, ROOT


class CompatibilityWindow:
    def __init__(self, root, app):
        self.root, self.app = root, app
        root.title('The Bear Cave — PTR Compatibility Launcher')
        root.geometry('880x510')
        root.minsize(720, 460)
        root.configure(bg='#071422')
        try:
            root.iconbitmap(str(ROOT/'ui/assets/bear-cave-app-icon.ico'))
        except tk.TclError:
            pass
        panel = tk.Frame(root, bg='#071422', padx=24, pady=20)
        panel.pack(fill='both', expand=True)
        def label(text, **options):
            item = tk.Label(panel, text=text, bg='#071422', fg='#efd08b', anchor='w', **options)
            item.pack(fill='x', pady=(0, 12))
            return item
        label('THE BEAR CAVE — PUBLIC TEST REALM', font=('Arial', 19, 'bold'))
        label('Compatibility mode • Native controls • Linux/Wine testing pending', wraplength=660)
        label('Choose the PTR client folder containing Wow.exe.')
        self.path = tk.StringVar(value=app.client)
        row = tk.Frame(panel, bg='#071422')
        row.pack(fill='x', pady=(0, 16))
        self.entry = tk.Entry(row, textvariable=self.path, font=('Arial', 11))
        self.entry.pack(side='left', fill='x', expand=True, ipady=5)
        self.browse = tk.Button(row, text='Browse…', command=self.choose)
        self.browse.pack(side='left', padx=8)
        self.save = tk.Button(row, text='Save folder', command=self.select)
        self.save.pack(side='left')
        self.status = label('', wraplength=660, justify='left')
        self.error = label('', wraplength=660, justify='left')
        self.error.configure(fg='#ffab99')
        actions = tk.Frame(panel, bg='#071422')
        actions.pack(side='bottom', fill='x', pady=12)
        self.buttons = {}
        for action, title in [('check', 'Check / Repair'), ('recover', 'Recover'),
                              ('update', 'Update'), ('play', 'Play')]:
            button = tk.Button(actions, text=title, padx=14, pady=10,
                               command=lambda a=action: self.start(a))
            button.pack(side='left', padx=(0, 10))
            self.buttons[action] = button
        root.protocol('WM_DELETE_WINDOW', self.close)
        self.refresh()

    def choose(self):
        if self.app.busy:
            return
        # Tk dialogs and widgets must stay on the main thread.
        chosen = filedialog.askdirectory(parent=self.root, initialdir=self.app.client or None,
                                         title='Choose your PTR client folder', mustexist=True)
        if chosen:
            self.path.set(chosen)
            self.select()

    def select(self):
        try:
            self.app.select(self.path.get())
            self.start('check')
        except Exception as error:
            self.app.error = str(error)

    def start(self, action):
        try:
            self.app.start(action)
        except Exception as error:
            self.app.error = str(error)

    def refresh(self):
        state = self.app.status()
        self.status.configure(text=state['message'])
        self.error.configure(text=state['error'])
        for widget in (self.entry, self.browse, self.save):
            widget.configure(state='disabled' if state['busy'] else 'normal')
        for action, button in self.buttons.items():
            disabled = state['busy'] or not state['client']
            if action == 'update':
                disabled = disabled or not state['version'] or not state['changes']
            button.configure(state='disabled' if disabled else 'normal')
        self.root.after(200, self.refresh)

    def close(self):
        if self.app.busy:
            messagebox.showinfo('Operation in progress', 'Wait for the current operation to finish.', parent=self.root)
        else:
            self.root.destroy()


def main():
    root = tk.Tk()
    app = Application()
    CompatibilityWindow(root, app)
    root.mainloop()
