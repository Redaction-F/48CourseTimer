from __future__ import annotations
from typing import TYPE_CHECKING
import tkinter as tk
from tkinter import ttk
from LapTimer import Time
from Record import Record
from SettingRecordFrame import open_set_record
from Other import FortyEightCourseTimerError
if TYPE_CHECKING:
    from MainFrame import MainFrame

class InfoFrame(ttk.Frame):
    def __init__(self, master: MainFrame, record: Record):
        self.master: MainFrame = master
        self.__record: Record = record
        self.__new_record: list[Time] = []
        self.__total_new_record: Time = Time(0)
        self.__total_diff: Time = Time(0)

        super().__init__(master, padding=10, style="MyFrame.TFrame")
        self.grid(column=1, row=0, padx=10, pady=10, sticky=tk.NSEW)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.record_col: tuple[str, str, str, str, str] = ("", "Now Time", "Old Record", "Diff", "Total Diff")
        self.record_table: ttk.Treeview = ttk.Treeview(self, columns=self.record_col, style="MyTable.Treeview")
        self.record_table.column('#0', width=0, stretch='no')
        self.record_table.heading('#0', text='')
        for (i, width) in enumerate([60, 120, 120, 100, 100]):
            self.record_table.column(self.record_col[i], anchor=tk.E, width=width)
            self.record_table.heading(self.record_col[i], text=self.record_col[i], anchor=tk.W)
        for (i, v) in enumerate(self.record, start=1):
            self.record_table.insert("", i - 1, i, values=(
                "#{:2}".format(i), 
                "", 
                v.to_str(), 
                "", 
                ""
            ))
        self.record_table.insert("", len(self.record), "total", values=(
            "total", 
            "", 
            self.record.total.to_str(), 
            "", 
            ""
        ))
        self.record_table.grid(column=0, row=0, sticky=tk.NSEW)

        self.setting_button: ttk.Button = ttk.Button(self, text="Setting", command=lambda: open_set_record(self.record, self.set_old_record), style="MyButton.TButton")
        self.setting_button.grid(column=0, row=1, sticky=tk.E)
    
    def add_lap_display(self, value: int):
        if self.is_full_new_record():
            return
        
        value: Time = Time(value)
        old_record_time: Time = self.record[len(self.new_record)]

        self.__new_record.append(value)
        self.__total_new_record += value
        self.__total_diff += value - old_record_time

        values_list: list[str] = list(self.record_table.item(len(self.new_record), option="values"))
        values_list[1] = value.to_str()
        values_list[3] = (value - old_record_time).to_str(display_pm=True)
        values_list[4] = self.__total_diff.to_str(display_pm=True)
        self.record_table.item(len(self.new_record), values=tuple(values_list))

        values_list = list(self.record_table.item("total", option="values"))
        values_list[1] = self.__total_new_record.to_str()
        self.record_table.item("total", values=tuple(values_list))
    
    def reset_lap_display(self):
        self.__new_record.clear()
        self.__total_new_record = Time(0)
        self.__total_diff = Time(0)

        values_list: list[str]
        for i in range(1, len(self.record) + 1):
            values_list = list(self.record_table.item(i, option="values"))
            values_list[1] = ""
            values_list[3] = ""
            values_list[4] = ""
            self.record_table.item(i, values=tuple(values_list))
        
        values_list = list(self.record_table.item("total", option="values"))
        values_list[1] = self.__total_new_record.to_str()
        self.record_table.item("total", values=tuple(values_list))
    
    def set_old_record(self, record: Record):
        if len(self.record) != len(record):
            raise FortyEightCourseTimerError("Can't overwrite this value because this is too short or long")

        self.__record = record
        self.__total_diff = Time(0)

        values_list: list[str]
        new: Time
        for (i, old) in enumerate(self.record, start=1):
            if i - 1 < len(self.new_record):
                new = self.new_record[i - 1]
                self.__total_diff += new - old
                values_list = list(self.record_table.item(i, option="values"))
                values_list[2] = old.to_str()
                values_list[3] = (new - old).to_str(display_pm=True)
                values_list[4] = self.__total_diff.to_str(display_pm=True)
                self.record_table.item(i, values=tuple(values_list))
            else:
                values_list = list(self.record_table.item(i, option="values"))
                values_list[2] = old.to_str()
                values_list[3] = ""
                values_list[4] = ""
                self.record_table.item(i, values=tuple(values_list))
        
        values_list = list(self.record_table.item("total", option="values"))
        values_list[2] = self.record.total.to_str()
        self.record_table.item("total", values=tuple(values_list))
    
    def is_full_new_record(self) -> bool:
        return len(self.record) - len(self.new_record) == 1
    
    @property
    def record(self) -> Record:
        return self.__record
    
    @property
    def new_record(self) -> list[Time]:
        return self.__new_record