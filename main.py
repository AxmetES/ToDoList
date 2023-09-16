import logging
import os

import tkinter as tk
import tkinter.font as tkFont
from tkinter import messagebox
from sqlalchemy import desc

from marshmallow import ValidationError

from db import session
from models import Task
from schemas import TaskSchema

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


log_file_path = os.path.join(BASE_DIR, "myapp.log")
logging.basicConfig(
    filename=log_file_path,
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


window = tk.Tk()
window.title("To Do List")
window.resizable(width=False, height=False)

frame_main = tk.Frame(master=window, width=500, height=500, bg="red")
custom_font = tkFont.Font(size=20)


to_change_selected_index = None


def check_in_list(entry_val):
    num_items = listbox.size()
    for i in range(num_items):
        if entry_val == listbox.get(i):
            return True


def add_selected(db=session):
    entry_val = entry.get()
    if check_in_list(entry_val):
        entry.delete(0, tk.END)
        return
    task_data = {"task": entry_val}
    task_schema = TaskSchema()
    try:
        validated_data = task_schema.load(task_data)
    except ValidationError as e:
        logging.exception(e)
        task_errors = e.messages.get("task", [])

        if "Length must be between 1 and 255." in task_errors:
            messagebox.showerror(
                "Ошибка",
                "Текст слишком длинный. "
                "Максимум 255 символов или слишком короткий не меньше 1",
            )
            return
        else:
            messagebox.showerror("Ошибка", "Ошибка валидации данных.")
            return
    try:
        task = Task(**validated_data)
        db.add(task)
        db.commit()
    except Exception as e:
        logging.exception(e)
        db.rollback()
    finally:
        db.close()
    fill_text_box()
    entry.delete(0, tk.END)


def fill_text_box(db=session):
    listbox.delete(0, tk.END)
    all_tasks = db.query(Task).order_by(desc(Task.created_at)).all()
    for task in all_tasks:
        listbox.insert(tk.END, task.task)


def delete_selected(db=session):
    entry.delete(0, tk.END)
    selected_indices = listbox.curselection()
    if not selected_indices:
        return
    for index in selected_indices:
        list_val = listbox.get(index)
        record_to_delete = db.query(Task).filter(Task.task == list_val).first()
        if record_to_delete:
            try:
                db.delete(record_to_delete)
                session.commit()
                listbox.delete(index)
            except Exception as e:
                logging.exception(e)
            finally:
                db.close()
    fill_text_box()


def change_selected(db=session):
    global to_change_selected_index
    if to_change_selected_index is None:
        return
    entry_val = entry.get()
    if not entry_val:
        return
    list_val = listbox.get(to_change_selected_index)
    if check_in_list(entry_val):
        entry.delete(0, tk.END)
        return
    task = db.query(Task).filter_by(task=list_val).first()
    if not task:
        return
    task.task = entry_val
    to_change_selected_index = None
    try:
        db.commit()
        db.close()
        entry.delete(0, tk.END)
    except Exception as e:
        logging.exception(e)
    finally:
        db.close()

    fill_text_box()


def on_double_click(event):
    global to_change_selected_index
    entry.delete(0, tk.END)
    to_change_selected_index = listbox.nearest(event.y)
    text_to_insert = listbox.get(to_change_selected_index)
    entry.insert(0, text_to_insert)


label = tk.Label(
    master=frame_main,
    text="Daily Tasks",
    foreground="white",
    background="red",
    width=40,
    height=3,
    font=custom_font,
)
entry = tk.Entry(master=frame_main, width=60)
listbox = tk.Listbox(master=frame_main, width=60, height=30)
fill_text_box()
btn_add = tk.Button(master=frame_main, text="add", width=60, command=add_selected)
btn_del = tk.Button(master=frame_main, text="delete", width=60, command=delete_selected)
btn_chg = tk.Button(master=frame_main, text="change", width=60, command=change_selected)

label.pack()
tk.Label(master=frame_main, height=1, bg="red").pack()
entry.pack()
listbox.pack(pady=50)
btn_add.pack()
btn_del.pack(pady=50)
btn_chg.pack()
frame_main.pack()


listbox.bind("<Double-1>", on_double_click)
window.mainloop()
