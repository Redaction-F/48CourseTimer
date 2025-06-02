import sys
import os
import re
from typing import Callable, Self, Optional
import tkinter as tk
from tkinter import ttk, messagebox
from LapTimer import Time
from Other import FortyEightCourseTimerError

BACKUP_DIR_NAME = "backup"

class OptionRecord:
    RECORD_LEN: int = 48

    def __init__(self, value: Optional[list[Time]]=None):
        if value is not None and len(value) != OptionRecord.RECORD_LEN:
            raise FortyEightCourseTimerError("The len of this record is not {}".format(OptionRecord.RECORD_LEN))
        self.__value: Optional[list[Time]] = value
    
    @property
    def value(self) -> list[Time]:
        if self.__value is None:
            return [Time(12000) for _ in range(1, 49)]
        else:
            return self.__value
    
    def is_none(self) -> bool:
        return self.__value is None
    
    def set_value(self, value: list[Time]):
        self.__value = value

class Record(OptionRecord):
    def __init__(self, value: list[Time]):
        super().__init__(value)
        self.__value: list[Time] = value
        self.__total: Time = sum(self.__value, start=Time(0))

    def __getitem__(self, item: int) -> Time:
        return self.__value[item]
    
    def __len__(self) -> int:
        return len(self.__value)
    
    def __iter__(self):
        return self.__value.__iter__()
    
    @property
    def total(self) -> Time:
        return self.__total
    
    @classmethod
    def unwrap(cls, option_record: OptionRecord) -> Self:
        if option_record.is_none():
            raise FortyEightCourseTimerError("This value is none.")
        else:
            return Record(option_record.value)
    
    @classmethod
    def unwrap_or_defualt(cls,option_record: OptionRecord) -> Self:
        return Record(option_record.value)

def join_path(path_1: str, path_2: Optional[str]) -> str:
    if path_2 is None:
        return path_1
    else:
        return os.path.join(path_1, path_2)

def resource_path(path: Optional[str]=None, is_backup: bool=False) -> str:
    if is_backup:
        return resource_path(join_path(BACKUP_DIR_NAME, path))
    else:
        dir_path: str
        if hasattr(sys, '_MEIPASS'):
            dir_path = sys._MEIPASS
        else:
            dir_path = os.path.abspath('.')
        return join_path(os.path.join(dir_path, "resource"), path)

def read_record(file_name: str, is_backup: bool=False) -> Record:
    file_path: str = resource_path(file_name, is_backup=is_backup)
    
    record_list: list[Time] = []
    with open(file_path, "r") as file:
        for line in file.readlines():
            line = line.strip()
            if not(line.isdecimal()):
                raise FortyEightCourseTimerError("Invalid value in \"{}\"".format(file_name))
            record_list.append(Time(int(line)))
    
    if len(record_list) != Record.RECORD_LEN:
        raise FortyEightCourseTimerError("Number of record in \"{}\" is not {}".format(file_name, Record.RECORD_LEN))
    
    return Record(record_list)

def read_top_record() -> Record:
    option_record: OptionRecord = OptionRecord()
    try:
        option_record.set_value(read_record("record.txt"))
        record: Record = Record.unwrap(option_record)
        return record
    except FortyEightCourseTimerError as e:
        messagebox.showwarning("Warning", "Python Error\n{}".format(e))

    yn: bool = messagebox.askyesno("Record", "Fail to read old record.\nDo you want to read other record?")
    if yn:
        open_read_record(option_record.set_value)
        if option_record.is_none():
            messagebox.showwarning("Warning", "There is no record because the file was not selected or can't be read.\nThis app will start with defult record.")
    return Record.unwrap_or_defualt(option_record)

def delete_record(file_name: str):
    try:
        os.remove(resource_path(file_name, is_backup=True))
    except Exception as e:
        messagebox.showwarning("Warning", "Python Error.\n{}".format(e))
        messagebox.showwarning("Warning", "Fail to delete the file.")

def open_read_record(set_record: Callable[[Record], None]):
    def __close():
        rr_root.quit()
        rr_root.destroy()

    rr_root: tk.Tk = tk.Tk()
    rr_root.title("Setting Record")
    rr_root.geometry("640x360")
    rr_root.protocol("WM_DELETE_WINDOW", __close)
    rr_root.rowconfigure(0, weight=1)
    rr_root.columnconfigure(0, weight=1)
    rr_style: ttk.Style = ttk.Style(rr_root)
    rr_style.configure("MyLabel.TLabel", anchor=tk.CENTER, font=("HG丸ｺﾞｼｯｸM-PRO", 12))
    rr_style.configure("MyButton.TButton", background="#8F8F8F", width=8, font=("HG丸ｺﾞｼｯｸM-PRO", 18))

    read_record_frame: ReadRecordFrame = ReadRecordFrame(rr_root, set_record)
    
    rr_root.mainloop()

class ReadRecordFrame(ttk.Frame):
    def __init__(self, master: tk.Tk, set_record: Callable[[Record], None]):
        self.__file_list: list[str] = []
        self.__set_record: Callable[[Record], None] = set_record

        super().__init__(master)
        self.grid(column=0, row=0, sticky=tk.NSEW)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        self.message: ttk.Label = ttk.Label(self, text="Select record", style="MyLabel.TLabel")
        self.message.grid(column=0, row=0, columnspan=3, sticky=tk.EW)

        self.list_strvar: tk.StringVar = tk.StringVar(self, self.__file_list)
        self.list_box: tk.Listbox = tk.Listbox(self, listvariable=self.list_strvar)
        self.list_box.grid(column=0, row=1, columnspan=3, sticky=tk.NSEW)

        self.button_delete: ttk.Button = ttk.Button(self, text="Delete", style="MyButton.TButton", command=self.delete_record_wrapper)
        self.button_delete.grid(column=1, row=2,  sticky=tk.E)
        self.button_ok: ttk.Button = ttk.Button(self, text="OK", style="MyButton.TButton", command=self.set_record_wrapper)
        self.button_ok.grid(column=2, row=2,  sticky=tk.E)
        
        self.update_file_list()
    
    def update_file_list(self):
        self.__file_list.clear()
        re_patter: re.Pattern = re.compile("(.+)\.txt")
        match: Optional[re.Match]
        for file_name in sorted(os.listdir(resource_path(is_backup=True))):
            match = re_patter.match(file_name)
            if match is not None:
                self.__file_list.append(match.groups()[0])
        self.list_strvar.set(self.__file_list)
    
    def selected_file_name(self) -> Optional[str]:
        selected_index: tuple = self.list_box.curselection()
        if len(selected_index) != 0:
            return "{}.txt".format(self.__file_list[self.list_box.curselection()[0]])
        else:
            return None
    
    def set_record_wrapper(self):
        file_name: Optional[str] = self.selected_file_name()
        if file_name is None:
            pass
        else:
            try:
                record: Record = read_record(file_name, is_backup=True)
                self.__set_record(record)
            except FortyEightCourseTimerError as e:
                messagebox.showwarning("Warning", "Python Error\n{}".format(e))
        self.master.quit()
        self.master.destroy()
    
    def delete_record_wrapper(self):
        file_name: Optional[str] = self.selected_file_name()
        if file_name is None:
            messagebox.showwarning("Warning", "Select a record.")
        else:
            delete_record(file_name)
            self.update_file_list()