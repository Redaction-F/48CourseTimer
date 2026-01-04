from __future__ import annotations
import datetime
from typing import Optional, TYPE_CHECKING
import tkinter as tk
from tkinter import ttk, messagebox
from src.LapTimer import Timer, Time
from src.Record import Record, resource_path
if TYPE_CHECKING:
    from MainFrame import MainFrame

class TimerFrame(ttk.Frame):

    def __init__(self, master: MainFrame):
        self.master: MainFrame = master
        self.__timer: Timer = Timer()

        super().__init__(master, style="MyFrame.TFrame")
        self.grid(column=0, row=0, padx=10, pady=10, sticky=tk.NSEW)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

        self.empty_1: ttk.Label = ttk.Label(self, style="MyEmpty.TLabel")
        self.empty_1.grid(column=0, columnspan=3, row=0, pady=40)

        self.timer_label_str: tk.StringVar = tk.StringVar(self)
        self.timer_label_str.set(str(self.__timer))
        self.timer_label: ttk.Label = ttk.Label(self, textvariable=self.timer_label_str, style="MyTimer.TLabel")
        self.timer_label.grid(column=0, columnspan=3, row=1, ipady=30)

        self.empty_2: ttk.Label = ttk.Label(self, style="MyEmpty.TLabel")
        self.empty_2.grid(column=0, columnspan=3, row=2, pady=40)

        self.reset_button_str: tk.StringVar = tk.StringVar(self)
        self.reset_button: ttk.Button = ttk.Button(self, textvariable=self.reset_button_str, command=self.reset, style="MyButton.TButton")
        self.reset_button.grid(column=0, row=3, ipady=10)

        self.main_button_str: tk.StringVar = tk.StringVar(self)
        self.main_button: ttk.Button = ttk.Button(self, textvariable=self.main_button_str, command=self.start_restart_stop, style="MyButton.TButton")
        self.main_button.grid(column=1, row=3, ipady=15)

        self.lap_button_str: tk.StringVar = tk.StringVar(self)
        self.lap_button: ttk.Button = ttk.Button(self, textvariable=self.lap_button_str, command=self.lap, style="MyButton.TButton")
        self.lap_button.grid(column=2, row=3, ipady=10)

        self.empty_2: ttk.Label = ttk.Label(self, style="MyEmpty.TLabel")
        self.empty_2.grid(column=0, columnspan=3, row=4, pady=40)

        self.name_label: ttk.Label = ttk.Label(self, text="Record name:", style="MyNameLabel.TLabel")
        self.name_label.grid(column=1, row=5, sticky=tk.E)
        self.name_entry_str: tk.StringVar = tk.StringVar()
        self.name_entry: tk.Entry = tk.Entry(self, textvariable=self.name_entry_str, justify="left", width=20, font=("Consolas", 12))
        self.name_entry.grid(column=2, row=5, ipady=5, sticky=tk.W)
        
        self.update_button_labels()
    
    def update_button_labels(self):
        button_labels: tuple[Optional[str], Optional[str], Optional[str]] = self.__timer.button_labels()
        buttons: list[tuple[ttk.Button, tk.StringVar]] = [(self.reset_button, self.reset_button_str), (self.main_button, self.main_button_str), (self.lap_button, self.lap_button_str)]
        for (button_label, (button, button_str)) in zip(button_labels, buttons):
            if button_label is None:
                button_str.set("")
                button.configure(state=tk.DISABLED)
            else:
                button_str.set(button_label)
                button.configure(state=tk.NORMAL)

    def start_restart_stop(self):
        self.__timer.start_restart_stop()
        self.focus_set()
        self.update_button_labels()

    def reset(self):
        if self.master.info_frame.is_full_new_record():
            self.save_old_record()

        is_ok: bool = messagebox.askokcancel("Reset timer", "Are you sure you want to reset timer?")
        if not(is_ok):
            return
        self.__timer.reset()
        self.update_button_labels()
        self.master.info_frame.reset_lap_display()
    
    def lap(self):
        if self.master.info_frame.is_full_new_record():
            self.__timer.stop()
            self.focus_set()
            self.update_button_labels()
        else:
            lap: int | None = self.__timer.lap()
            self.update_button_labels()
            if lap is not None:
                self.master.info_frame.add_lap_display(lap)
    
    def update(self):
        self.timer_label_str.set(str(self.__timer))
    
    def save_old_record(self):
        record_list: list[Time] = self.master.info_frame.new_record.copy()
        record_list.append(self.__timer.time - sum(record_list, start=Time(0)))
        record: Record = Record(record_list)
        save_yn: bool = messagebox.askyesno("Save?", "Save?\nThe old record will not be lost.")
        if save_yn:
            file_name: str = self.name_entry_str.get()
            if file_name == "":
                file_name = "record_{}".format(datetime.datetime.now().strftime("%Y_%m%d_%H%M%S"))
            with open(resource_path("{}.txt".format(file_name), is_backup=True), "w") as file:
                file.writelines("\n".join(map(lambda x: str(x.total_csec), record)))
        else:
            return

        is_ok_overwite: bool = messagebox.askokcancel("Overwrite old record?", "Are you sure you want to overwrite the old record with the new record?\nThe old record will be lost.")
        if is_ok_overwite:
            self.master.info_frame.set_old_record(record)