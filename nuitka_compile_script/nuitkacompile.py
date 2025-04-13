from nutikacompile import compile_with_nuitka
import os
env_folder = r"C:\ProgramData\anaconda3\envs\pdfconverter"
outputdir = r"c:\remove_pdf_restrictions2"
command_used = compile_with_nuitka(
    pyfile=os.path.normpath(os.path.join(env_folder, "pdfconv.py")),
    icon=os.path.normpath(os.path.join(env_folder, "icon_remove_pdf_restrictions.png")),
    outputdir=outputdir,
    addfiles=[
        os.path.normpath(os.path.join(env_folder, "icon_remove_pdf_restrictions.png"))
    ],
    file_version="1.2",
    file_description="PDF restriction remover",
    product_name="PDF restriction remover",
    copyright="Copyright 2025",
    trademarks="Johannes Fischer",
    disable_console=True,
    onefile=True,
    needs_admin=False,
    arguments2add="--noinclude-numba-mode=nofollow --jobs=1 --enable-plugin=tk-inter",
)
