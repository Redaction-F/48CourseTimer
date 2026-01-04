import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Literal, TypeGuard, Optional
from LapTimer import Time
from Record import OptionRecord, Record, open_read_record

def open_set_record(record: Record, set_record: Callable[[Record], None]):
    def __close():
        sr_root.quit()
        sr_root.destroy()

    sr_root: tk.Tk = tk.Tk()
    sr_root.title("Setting Record")
    sr_root.geometry("1280x720")
    sr_root.protocol("WM_DELETE_WINDOW", __close)
    sr_root.rowconfigure(0, weight=1)
    sr_root.columnconfigure(0, weight=1)
    style_record_window: ttk.Style = ttk.Style(sr_root)
    style_record_window.configure("MyFrame.TFrame", background="#CFCFCF")
    style_record_window.configure("MyRecordFrame.TFrame", background="#AFAFAF")
    style_record_window.configure("MyLabel.TLabel", background="#AFAFAF", anchor=tk.CENTER, font=("HG丸ｺﾞｼｯｸM-PRO", 12))
    style_record_window.configure("MyButton.TButton", background="#8F8F8F", width=8, font=("HG丸ｺﾞｼｯｸM-PRO", 18))

    setting_record_frame: SetRecordFrame = SetRecordFrame(sr_root, record, set_record)

    sr_root.mainloop()

class SetRecordFrame(ttk.Frame):
    def __init__(self, master: tk.Tk, record: Record, set_record: Callable[[Record], None]):
        self.__master: tk.Tk = master
        self.__set_record: Callable[[Record], None] = set_record

        super().__init__(master, padding=10, style="MyFrame.TFrame")
        self.grid(column=0, row=0, sticky=tk.NSEW)
        for i in range(4):
            self.columnconfigure(i, weight=1)
        for i in range(13):
            self.rowconfigure(i, weight=1)

        self.record_entry: list[OneCourseRecord] = []
        for i in range(1, Record.RECORD_LEN + 1):
            self.record_entry.append(OneCourseRecord(self, i, record[i - 1]))
            if i >= 2:
                self.record_entry[i - 2].set_focus_next(self.record_entry[i - 1].focus_entry)
        
        self.other_button: ttk.Button = ttk.Button(self, text="Other", style="MyButton.TButton", command=self.read_record_wrapper)
        self.other_button.grid(column=2, row=12, sticky=tk.E)
        self.ok_button: ttk.Button = ttk.Button(self, text="OK", style="MyButton.TButton", command=self.set_old_record_wrapper)
        self.ok_button.grid(column=3, row=12, sticky=tk.E)
    
    def set_old_record_wrapper(self):
        def __is_record_list(record_list: list[Optional[Time]]) -> TypeGuard[list[Time]]:
            return all(map(lambda x: x is not None, record_list))

        record_list: list[Optional[Time]] = [Time.from_input(v.hour_str, v.minute_str, v.sec_str, v.csec_str) for v in self.record_entry]
        if __is_record_list(record_list):
            self.__set_record(Record(record_list))
            self.__master.quit()
            self.__master.destroy()
        else:
            none_iter = filter(lambda x: x[1] is None, enumerate(record_list, start=1))
            none_index: list[int] = list(map(lambda x: x[0], none_iter))
            messagebox.showerror("Invalid Input", "Your input is not numeric.\nindex: {}".format(", ".join(map(lambda x: str(x), none_index))))
    
    def read_record_wrapper(self):
        option_record: OptionRecord = OptionRecord()
        open_read_record(option_record.set_value)
        record: Record = Record.unwrap_or_defualt(option_record)
        self.__set_record(record)
        self.__master.quit()
        self.__master.destroy()

class OneCourseRecord(ttk.Frame):
    def __init__(self, master, i: int, one_record: Time):
        self.__focus_next: Optional[Callable[[any], None]] =  None

        super().__init__(master, relief=tk.RAISED, borderwidth=2, style="MyRecordFrame.TFrame")
        self.grid(column=(i - 1) // 12, row=(i - 1) % 12, sticky=tk.NSEW)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(4, weight=1)
        self.columnconfigure(6, weight=1)

        self.entry_label: ttk.Label = ttk.Label(self, text="Course: {}".format(i), style="MyLabel.TLabel")
        self.entry_label.grid(column=0, columnspan=7, row=0, sticky=tk.W)
        self.format_label_1: ttk.Label = ttk.Label(self, text=":", style="MyLabel.TLabel")
        self.format_label_1.grid(column=1, row=1)
        self.format_label_2: ttk.Label = ttk.Label(self, text=":", style="MyLabel.TLabel")
        self.format_label_2.grid(column=3, row=1)
        self.format_label_3: ttk.Label = ttk.Label(self, text=".", style="MyLabel.TLabel")
        self.format_label_3.grid(column=5, row=1)

        self.entry_hour_str: tk.StringVar = tk.StringVar(self, str(one_record.hour))
        self.entry_hour: tk.Entry = tk.Entry(self, textvariable=self.entry_hour_str, justify="right", width=6, font=("HG丸ｺﾞｼｯｸM-PRO", 10))
        self.entry_hour.grid(column=0, row=1)

        self.entry_minute_str: tk.StringVar = tk.StringVar(self, str(one_record.minute))
        self.entry_minute: tk.Entry = tk.Entry(self, textvariable=self.entry_minute_str, justify="right", width=6, font=("HG丸ｺﾞｼｯｸM-PRO", 10))
        self.entry_minute.grid(column=2, row=1)

        self.entry_sec_str: tk.StringVar = tk.StringVar(self, str(one_record.sec))
        self.entry_sec: tk.Entry = tk.Entry(self, textvariable=self.entry_sec_str, justify="right", width=6, font=("HG丸ｺﾞｼｯｸM-PRO", 10))
        self.entry_sec.grid(column=4, row=1)

        self.entry_csec_str: tk.StringVar = tk.StringVar(self, str(one_record.csec))
        self.entry_csec: tk.Entry = tk.Entry(self, textvariable=self.entry_csec_str, justify="right", width=6, font=("HG丸ｺﾞｼｯｸM-PRO", 10))
        self.entry_csec.grid(column=6, row=1)
        
        self.entry_hour.bind("<Return>", lambda _: self.focus_entry("minute"))
        self.entry_minute.bind("<Return>", lambda _: self.focus_entry("sec"))
        self.entry_sec.bind("<Return>", lambda _: self.focus_entry("csec"))
        self.entry_csec.bind("<Return>", self.focus_next)
    
    def focus_entry(self, value: Literal["hour", "minute", "sec", "csec"]):
        target_obj: tk.Entry
        if value == "hour":
            target_obj = self.entry_hour
        elif value == "minute":
            target_obj = self.entry_minute
        elif value == "sec":
            target_obj = self.entry_sec
        else:
            target_obj = self.entry_csec
        target_obj.focus_set()
        target_obj.icursor("end")

    def set_focus_next(self, foucus_next: Callable[[any], None]):
        self.__focus_next = foucus_next
    
    def focus_next(self, _):
        if self.__focus_next is not None:
            self.__focus_next("hour")
    
    @property
    def hour_str(self) -> str:
        return self.entry_hour_str.get()
    
    @property
    def minute_str(self) -> str:
        return self.entry_minute_str.get()
    
    @property
    def sec_str(self) -> str:
        return self.entry_sec_str.get()
    
    @property
    def csec_str(self) -> str:
        return self.entry_csec_str.get()