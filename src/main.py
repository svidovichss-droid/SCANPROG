#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Точка входа для Data Matrix Quality Scanner
"""

import sys
import os

# Добавляем путь к DLL для PyInstaller
if getattr(sys, 'frozen', False):
    # Запущено из EXE
    bundle_dir = sys._MEIPASS
    dll_path = os.path.join(bundle_dir, 'libdmtx.dll')
    if os.path.exists(dll_path):
        os.environ['PATH'] = bundle_dir + os.pathsep + os.environ.get('PATH', '')

import tkinter as tk
from gui import DataMatrixGUI


def main():
    """Главная функция"""
    root = tk.Tk()
    
    # Установка иконки если доступна
    try:
        if getattr(sys, 'frozen', False):
            icon_path = os.path.join(sys._MEIPASS, 'resources', 'icon.ico')
        else:
            icon_path = os.path.join(os.path.dirname(__file__), '..', 'resources', 'icon.ico')
            
        if os.path.exists(icon_path):
            root.iconbitmap(icon_path)
    except Exception:
        pass
    
    app = DataMatrixGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()