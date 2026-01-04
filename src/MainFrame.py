import tkinter as tk
from tkinter import ttk
from TimerFrame import TimerFrame
from InfoFrame import InfoFrame
from Record import Record

class MainFrame(ttk.Frame):
    def __init__(self, master, record: Record):
        super().__init__(master, style="MyMainFrame.TFrame")
        self.grid(column=0, row=0, sticky=tk.NSEW)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        
        self.timer_frame = TimerFrame(self)
        self.info_frame = InfoFrame(self, record)