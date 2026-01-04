import os
import sys
import shutil
import tkinter as tk
from tkinter import ttk, messagebox
from src.MainFrame import MainFrame
from src.Record import read_top_record, resource_path, BACKUP_DIR_NAME
from src.LapTimer import Time

def close_with_save():
    try:
        record_str = list(map(lambda x: str(x.total_csec), main_frame.info_frame.record))
        with open(resource_path("record.txt"), "w") as file:
            file.writelines("\n".join(record_str))
        exe_backup_path: str = os.path.join(os.path.dirname(sys.argv[0]), BACKUP_DIR_NAME)
        if not(os.path.isdir(exe_backup_path)):
            os.mkdir(exe_backup_path)
        for file_name in os.listdir(resource_path(is_backup=True)):
            shutil.copy(resource_path(file_name, is_backup=True), exe_backup_path)
    except Exception as e:
        messagebox.showerror("Error", "Python Error\n{}".format(e))
    root.quit()
    root.destroy()

def loop():
    main_frame.timer_frame.update()
    root.after(10, loop)

record: list[Time] = read_top_record()
root: tk.Tk = tk.Tk()
root.title("48CourseTimer")
root.geometry("1280x720")
root.protocol("WM_DELETE_WINDOW", close_with_save)
root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)

style: ttk.Style = ttk.Style(root)
style.configure("MyMainFrame.TFrame", background="#8F8F8F")
style.configure("MyFrame.TFrame", background="#CFCFCF")
style.configure("MyLabel.TLabel", anchor=tk.CENTER, font=("HG丸ｺﾞｼｯｸM-PRO", 12))
style.configure("MyNameLabel.TLabel", background="#CFCFCF", anchor=tk.CENTER, font=("HG丸ｺﾞｼｯｸM-PRO", 24))
style.configure("MyTimer.TLabel", background="#AFAFAF", anchor=tk.CENTER, width=15, font=("Consolas", 50))
style.configure("MyEmpty.TLabel", background="#CFCFCF")
style.configure("MyButton.TButton", background="#8F8F8F", width=8, font=("HG丸ｺﾞｼｯｸM-PRO", 18))
style.configure("MyTable.Treeview", background="#AFAFAF", font=("Consolas", 12), rowheight=15)

main_frame: MainFrame = MainFrame(root, record)

root.bind("<Key-Return>", lambda _: main_frame.timer_frame.start_restart_stop())
root.bind("<Key-space>", lambda _: main_frame.timer_frame.lap())

root.after(10, loop)
root.mainloop()