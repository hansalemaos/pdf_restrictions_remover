import tkinter as tk
from tkinter import filedialog
from os.path import join, normpath, exists
from os import walk
from os import remove as os_remove
from os import rename as os_rename
from tempfile import NamedTemporaryFile
from pikepdf import open as pikepdf_open
from contextlib import suppress
import tkinter.ttk as ttk
from textwrap import wrap
from time import sleep
import sys


def wrap_text(text, width):
    return "\n".join(wrap(text, width=width))


def get_display_size():
    root = tk.Tk()
    root.attributes("-alpha", 0)
    display_height = root.winfo_screenheight()
    display_width = root.winfo_screenwidth()
    root.destroy()
    return display_width, display_height


def get_set_with_all_pdf_endings():
    all_pdf_endings = set()
    for p in ["p", "P"]:
        for d in ["d", "D"]:
            for f in ["f", "F"]:
                all_pdf_endings.add("." + p + d + f)
    return all_pdf_endings


def bind_mousewheel(widget):
    # Windows and Linux
    widget.bind_all("<MouseWheel>", on_mousewheel)
    # macOS legacy
    widget.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
    widget.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))


def on_mousewheel(event):
    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


def get_all_files(dirName):
    all_files = []
    _ = [
        [
            file
            for file in filenames
            if len(file) > 4
            and file[-4:] in all_pdf_endings  # Path(file).suffix is too slow
            and all_files.append(normpath(join(dirpath, file)))
        ]
        for dirpath, dirnames, filenames in walk(dirName)
    ]
    return all_files


def select_file():
    filepath = filedialog.askopenfilename(title="Select a File")
    if filepath:
        pdf_files = [filepath]
        path_var.set("1 PDF found")
        show_checkboxes(pdf_files)


def select_folder():
    folderpath = filedialog.askdirectory(title="Select a Folder")
    if folderpath:
        pdf_files = get_all_files(folderpath)
        len_pdf_files = len(pdf_files)
        path_var.set(
            "1 PDF found" if len_pdf_files == 1 else f"{len_pdf_files} PDFs found"
        )
        show_checkboxes(pdf_files)


def show_checkboxes(pdf_files):
    # Clear old checkboxes
    for widget in checkbox_frame.winfo_children():
        widget.destroy()
    checkbox_vars.clear()

    for file in pdf_files:
        var = tk.BooleanVar(value=True)
        cb = ttk.Checkbutton(
            checkbox_frame,
            text=wrap_text(file, wraplength_file),
            variable=var,
        )
        cb.pack(fill="x", padx=5, pady=2)
        checkbox_vars[file] = var


def remove_pdf_restriction():
    selected_files = [file for file, var in checkbox_vars.items() if var.get()]
    new_tmp_file = NamedTemporaryFile(delete_on_close=False)
    outputfile = new_tmp_file.name
    new_tmp_file.close()
    bad_counter = 0
    good_counter = 0
    if not selected_files:
        tk.messagebox.showinfo("No files selected", "Please select at least one file.")
    else:
        for inputfile in selected_files:
            path_var.set(f"Converting {inputfile}")
            try:
                with pikepdf_open(inputfile) as pdf:
                    pdf.save(
                        outputfile,
                        encryption=False,
                    )

                os_remove(inputfile)
                os_rename(outputfile, inputfile)
                good_counter += 1
            except Exception as ex:
                exstr = str(ex).replace("\n", " ")
                path_var.set(f"ERROR: {exstr}")
                bad_counter += 1
                with suppress(Exception):
                    if exists(outputfile):
                        os_remove(outputfile)
                sleep(0.5)

        path_var.set(
            f"Conversion complete (success: {good_counter}, failed: {bad_counter})"
        )


display_width, display_height = get_display_size()

# sets are very fast
all_pdf_endings = get_set_with_all_pdf_endings()

# GUI setup
root = tk.Tk()
allpath = [
    g for x in sys.path if exists(g := join(x, "icon_remove_pdf_restrictions.png"))
]
if allpath:
    icon = tk.PhotoImage(file=allpath[0])
    root.iconphoto(False, icon)
root.title("PDF Restriction Remover")
root.geometry(f"{display_width}x{display_height}")
wraplength = int(display_width * 0.9)
wraplength_file = int(display_width * 0.8)
default_font = ("Segoe UI", 10)
style = ttk.Style()
path_var = tk.StringVar()
label = ttk.Label(root, textvariable=path_var, wraplength=wraplength, font=default_font)
label.pack(pady=10, padx=20)

# Buttons Frame
btn_frame = ttk.Frame(root)
btn_frame.pack(pady=5)

btn_file = ttk.Button(btn_frame, text="📄 Select single PDF File", command=select_file)
btn_file.pack(side="left", padx=10)

btn_folder = ttk.Button(
    btn_frame, text="📁 Select folder with PDFs", command=select_folder
)
btn_folder.pack(side="left", padx=10)

btn_convert = ttk.Button(
    root, text="🔓 Convert Selected PDFs", command=remove_pdf_restriction
)
btn_convert.pack(pady=15)

# Scrollable checkbox area
scroll_frame = ttk.Frame(root)
scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)

canvas = tk.Canvas(scroll_frame, bd=0, highlightthickness=0)
scrollbar = ttk.Scrollbar(scroll_frame, orient="vertical", command=canvas.yview)
checkbox_frame = ttk.Frame(canvas)

checkbox_frame.bind(
    "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=checkbox_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")
bind_mousewheel(canvas)

# Dictionary to hold checkbox states
checkbox_vars = {}
root.mainloop()
