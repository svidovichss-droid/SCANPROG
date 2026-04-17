#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUI для Data Matrix Quality Scanner
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk
import cv2
import threading
import os
from typing import Optional

from scanner import DataMatrixQualityScanner


class ModernButton(ttk.Button):
    """Современная кнопка со стилем"""
    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)
        self.configure(style='Modern.TButton')


class DataMatrixGUI:
    """Графический интерфейс сканера"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Data Matrix Quality Scanner - ГОСТ Р 57302-2016")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)
        
        # Цветовая схема
        self.colors = {
            'bg': '#f5f5f5',
            'primary': '#2196F3',
            'secondary': '#757575',
            'success': '#4CAF50',
            'warning': '#FF9800',
            'error': '#f44336',
            'card': '#ffffff',
            'text': '#212121'
        }
        
        self.scanner = DataMatrixQualityScanner()
        self.current_image_path: Optional[str] = None
        self.video_capture: Optional[cv2.VideoCapture] = None
        self.is_camera_active = False
        
        self.setup_styles()
        self.setup_ui()
        
    def setup_styles(self):
        """Настройка стилей ttk"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Основные цвета
        style.configure('Modern.TButton', 
                       font=('Segoe UI', 10, 'bold'),
                       padding=10,
                       background=self.colors['primary'],
                       foreground='white')
        
        style.configure('Card.TFrame', background=self.colors['card'])
        style.configure('Header.TLabel', 
                       font=('Segoe UI', 24, 'bold'),
                       background=self.colors['bg'],
                       foreground=self.colors['text'])
        
        style.configure('Subheader.TLabel',
                       font=('Segoe UI', 12),
                       background=self.colors['bg'],
                       foreground=self.colors['secondary'])
        
        style.configure('Grade.TLabel',
                       font=('Segoe UI', 48, 'bold'))
        
        style.configure('Param.TLabel',
                       font=('Segoe UI', 11),
                       background=self.colors['card'])
        
        style.configure('Value.TLabel',
                       font=('Segoe UI', 11, 'bold'),
                       background=self.colors['card'])
        
    def setup_ui(self):
        """Создание интерфейса"""
        self.root.configure(bg=self.colors['bg'])
        
        # Главный контейнер
        main_container = ttk.Frame(self.root, style='Card.TFrame')
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Заголовок
        header_frame = ttk.Frame(main_container, style='Card.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(header_frame, 
                 text="Data Matrix Quality Scanner",
                 style='Header.TLabel').pack(anchor=tk.W)
        
        ttk.Label(header_frame,
                 text="Оценка качества печати по ГОСТ Р 57302-2016 / ISO/IEC 15415",
                 style='Subheader.TLabel').pack(anchor=tk.W)
        
        # Контент
        content_frame = ttk.Frame(main_container, style='Card.TFrame')
        content_frame.pack(fill=tk.BOTH, expand=True)
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=2)
        content_frame.rowconfigure(0, weight=1)
        
        # Левая панель - изображение и управление
        left_panel = ttk.Frame(content_frame, style='Card.TFrame')
        left_panel.grid(row=0, column=0, sticky='nsew', padx=(0, 10))
        left_panel.rowconfigure(1, weight=1)
        
        # Кнопки загрузки
        btn_frame = ttk.Frame(left_panel, style='Card.TFrame')
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="📁 Загрузить файл", 
                  command=self.load_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="📷 Камера", 
                  command=self.toggle_camera).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🔍 Анализ", 
                  command=self.analyze).pack(side=tk.LEFT, padx=5)
        
        # Область изображения
        self.image_frame = ttk.LabelFrame(left_panel, text="Изображение", padding=10)
        self.image_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.image_label = ttk.Label(self.image_frame, text="Загрузите изображение...")
        self.image_label.pack(expand=True)
        
        # Правая панель - результаты
        right_panel = ttk.Frame(content_frame, style='Card.TFrame')
        right_panel.grid(row=0, column=1, sticky='nsew', padx=(10, 0))
        
        # Общая оценка
        self.grade_card = ttk.LabelFrame(right_panel, text="Общая оценка качества", padding=20)
        self.grade_card.pack(fill=tk.X, pady=(0, 10))
        
        self.grade_label = ttk.Label(self.grade_card, text="--", 
                                    style='Grade.TLabel',
                                    foreground=self.colors['secondary'])
        self.grade_label.pack()
        
        self.grade_desc_label = ttk.Label(self.grade_card, text="Ожидание анализа",
                                         font=('Segoe UI', 14))
        self.grade_desc_label.pack()
        
        # Таблица параметров
        params_frame = ttk.LabelFrame(right_panel, text="Детальные параметры", padding=10)
        params_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Создаем таблицу
        columns = ('param', 'value', 'grade', 'status')
        self.tree = ttk.Treeview(params_frame, columns=columns, 
                                show='headings', height=8)
        
        self.tree.heading('param', text='Параметр')
        self.tree.heading('value', text='Значение')
        self.tree.heading('grade', text='Оценка')
        self.tree.heading('status', text='Статус')
        
        self.tree.column('param', width=300)
        self.tree.column('value', width=100, anchor='center')
        self.tree.column('grade', width=80, anchor='center')
        self.tree.column('status', width=150, anchor='center')
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(params_frame, orient=tk.VERTICAL, 
                                 command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Декодированные данные
        data_frame = ttk.LabelFrame(right_panel, text="Декодированные данные", padding=10)
        data_frame.pack(fill=tk.X, pady=10)
        
        self.data_text = scrolledtext.ScrolledText(data_frame, height=4, 
                                                  font=('Consolas', 11),
                                                  wrap=tk.WORD)
        self.data_text.pack(fill=tk.X)
        
        # Кнопки действий
        action_frame = ttk.Frame(right_panel, style='Card.TFrame')
        action_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(action_frame, text="💾 Сохранить отчет", 
                  command=self.save_report).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="📋 Экспорт JSON", 
                  command=self.export_json).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="ℹ️ О программе", 
                  command=self.show_about).pack(side=tk.RIGHT, padx=5)
        
        # Статусная строка
        self.status_var = tk.StringVar(value="Готов к работе")
        self.status_bar = ttk.Label(main_container, 
                                   textvariable=self.status_var,
                                   relief=tk.SUNKEN,
                                   anchor=tk.W,
                                   font=('Segoe UI', 9))
        self.status_bar.pack(fill=tk.X, pady=(10, 0))
        
    def load_file(self):
        """Загрузка файла изображения"""
        file_path = filedialog.askopenfilename(
            title="Выберите изображение Data Matrix",
            filetypes=[
                ("Изображения", "*.png *.jpg *.jpeg *.bmp *.tiff *.gif *.tif"),
                ("Все файлы", "*.*")
            ]
        )
        
        if file_path:
            self.stop_camera()
            self.current_image_path = file_path
            self.display_image(file_path)
            self.status_var.set(f"Загружено: {os.path.basename(file_path)}")
            
    def display_image(self, source):
        """Отображение изображения"""
        try:
            if isinstance(source, str):
                img = Image.open(source)
            else:
                # OpenCV array
                img = Image.fromarray(cv2.cvtColor(source, cv2.COLOR_BGR2RGB))
            
            # Масштабирование
            max_size = (500, 500)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            photo = ImageTk.PhotoImage(img)
            self.image_label.configure(image=photo, text="")
            self.image_label.image = photo
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось отобразить изображение: {e}")
            
    def toggle_camera(self):
        """Включение/выключение камеры"""
        if self.is_camera_active:
            self.stop_camera()
        else:
            self.start_camera()
            
    def start_camera(self):
        """Запуск камеры"""
        self.video_capture = cv2.VideoCapture(0)
        if not self.video_capture.isOpened():
            messagebox.showerror("Ошибка", "Не удалось открыть камеру")
            return
            
        self.is_camera_active = True
        self.update_camera()
        self.status_var.set("Камера активна")
        
    def stop_camera(self):
        """Остановка камеры"""
        self.is_camera_active = False
        if self.video_capture:
            self.video_capture.release()
            self.video_capture = None
            
    def update_camera(self):
        """Обновление кадра с камеры"""
        if self.is_camera_active and self.video_capture:
            ret, frame = self.video_capture.read()
            if ret:
                self.current_frame = frame
                self.display_image(frame)
                
            self.root.after(30, self.update_camera)
            
    def analyze(self):
        """Запуск анализа"""
        if not hasattr(self, 'current_image_path') and not hasattr(self, 'current_frame'):
            if self.is_camera_active:
                # Анализ текущего кадра
                self.run_analysis(self.current_frame)
            else:
                messagebox.showwarning("Предупреждение", "Сначала загрузите изображение")
            return
            
        source = self.current_image_path if hasattr(self, 'current_image_path') else self.current_frame
        self.run_analysis(source)
        
    def run_analysis(self, source):
        """Выполнение анализа в потоке"""
        self.status_var.set("Анализ...")
        self.root.update()
        
        thread = threading.Thread(target=self._analysis_worker, args=(source,))
        thread.start()
        
    def _analysis_worker(self, source):
        """Рабочий поток анализа"""
        try:
            results = self.scanner.perform_full_analysis(source)
            self.root.after(0, lambda: self._update_ui(results))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Ошибка", str(e)))
            
    def _update_ui(self, results: dict):
        """Обновление интерфейса результатами"""
        # Общая оценка
        grade = results['overall_grade']
        grade_text = results['overall_grade_text']
        grade_color = results['overall_color']
        
        self.grade_label.configure(
            text=f"{grade}",
            foreground=grade_color
        )
        self.grade_desc_label.configure(text=grade_text)
        
        # Таблица параметров
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        params_data = [
            ("Декодирование", results['decode']['status'], 
             results['decode']['grade'], results['decode']['grade_text']),
            ("Контраст символа (SC)", f"{results['symbol_contrast']['value']:.1f}%",
             results['symbol_contrast']['grade'], results['symbol_contrast']['grade_text']),
            ("Модуляция (MOD)", f"{results['modulation']['value']:.1f}%",
             results['modulation']['grade'], results['modulation']['grade_text']),
            ("Запас по отражению (RM)", f"{results['reflectance_margin']['value']:.1f}%",
             results['reflectance_margin']['grade'], results['reflectance_margin']['grade_text']),
            ("Повреждение шаблона (FPD)", f"{results['fixed_pattern_damage']['value']:.1f}%",
             results['fixed_pattern_damage']['grade'], results['fixed_pattern_damage']['grade_text']),
            ("Осевая неоднородность (AN)", f"{results['axial_nonuniformity']['value']:.1f}%",
             results['axial_nonuniformity']['grade'], results['axial_nonuniformity']['grade_text']),
            ("Неоднородность сетки (GN)", f"{results['grid_nonuniformity']['value']:.1f}%",
             results['grid_nonuniformity']['grade'], results['grid_nonuniformity']['grade_text']),
            ("Неисп. коррекция ошибок (UEC)", f"{results['unused_error_correction']['value']:.1f}%",
             results['unused_error_correction']['grade'], results['unused_error_correction']['grade_text']),
        ]
        
        for param, value, grade, status in params_data:
            self.tree.insert('', tk.END, values=(param, value, f"{grade:.1f}", status))
            
        # Декодированные данные
        self.data_text.delete(1.0, tk.END)
        self.data_text.insert(tk.END, results['decode']['data'])
        
        self.status_var.set(f"Анализ завершен. Общая оценка: {grade} ({grade_text})")
        
    def save_report(self):
        """Сохранение отчета"""
        if not self.scanner.results:
            messagebox.showwarning("Предупреждение", "Сначала выполните анализ")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[
                ("Текстовый отчет", "*.txt"),
                ("JSON", "*.json"),
                ("Все файлы", "*.*")
            ]
        )
        
        if file_path:
            try:
                if file_path.endswith('.json'):
                    self.scanner.export_json(file_path)
                else:
                    self.scanner.generate_report(file_path)
                messagebox.showinfo("Успех", f"Отчет сохранен:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))
                
    def export_json(self):
        """Экспорт в JSON"""
        if not self.scanner.results:
            messagebox.showwarning("Предупреждение", "Сначала выполните анализ")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON", "*.json")]
        )
        
        if file_path:
            try:
                self.scanner.export_json(file_path)
                messagebox.showinfo("Успех", f"JSON сохранен:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))
                
    def show_about(self):
        """Окно о программе"""
        about_window = tk.Toplevel(self.root)
        about_window.title("О программе")
        about_window.geometry("500x400")
        about_window.resizable(False, False)
        about_window.transient(self.root)
        about_window.grab_set()
        
        # Содержимое
        ttk.Label(about_window, 
                 text="Data Matrix Quality Scanner",
                 font=('Segoe UI', 16, 'bold')).pack(pady=20)
        
        ttk.Label(about_window,
                 text="Версия 1.0.0",
                 font=('Segoe UI', 10)).pack()
        
        info_text = """
Оценка качества печати двумерных штриховых кодов 
Data Matrix по стандарту:

• ГОСТ Р 57302-2016
• ISO/IEC 15415:2011

Параметры оценки:
• Декодирование (Decode)
• Контраст символа (Symbol Contrast)
• Модуляция (Modulation)  
• Запас по отражению (Reflectance Margin)
• Повреждение фиксированного шаблона (FPD)
• Осевая неоднородность (AN)
• Неоднородность сетки (GN)
• Неиспользованная коррекция ошибок (UEC)

© 2024
        """
        
        ttk.Label(about_window,
                 text=info_text,
                 font=('Segoe UI', 10),
                 justify=tk.CENTER).pack(pady=20)
        
        ttk.Button(about_window, text="Закрыть", 
                  command=about_window.destroy).pack(pady=10)