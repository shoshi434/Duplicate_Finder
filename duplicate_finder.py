"""
Duplicate File Finder - סקריפט לזיהוי ומחיקת קבצים כפולים
"""
import os
import hashlib
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from collections import defaultdict
from difflib import SequenceMatcher
import threading

class DuplicateFinderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("מזהה קבצים כפולים - Duplicate File Finder")
        self.root.geometry("1200x900")
        self.root.configure(bg="#f5f5f5")
        
        # משתנים
        self.selected_folder = tk.StringVar()
        self.duplicates = []
        self.file_checkboxes = {}
        self.max_display_groups = 100  # הגבלת תצוגה למניעת תקיעות
        self.scan_stopped = False  # דגל לעצירת סריקה
        
        self.setup_ui()
    
    def setup_ui(self):
        """יצירת הממשק"""
        # כותרת עם גרדיאנט מודרני
        title_frame = tk.Frame(self.root, bg="#1976D2", height=50)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        # תוכן הכותרת
        title_content = tk.Frame(title_frame, bg="#1976D2")
        title_content.pack(expand=True)
        
        tk.Label(title_content, text="🔍 מזהה קבצים כפולים", 
                bg="#1976D2", fg="white",
                font=("Segoe UI", 14, "bold")).pack(pady=(3, 0))
        tk.Label(title_content, text="SHOSHI ER | 2025", 
                bg="#1976D2", fg="#BBDEFB",
                font=("Segoe UI", 7)).pack(pady=(0, 3))
        
        # קו הפרדה צבעוני
        tk.Frame(self.root, bg="#64B5F6", height=3).pack(fill=tk.X)
        
        # שלב 1 - בחירת תיקייה
        folder_frame = tk.Frame(self.root, bg="white", relief=tk.FLAT, bd=0)
        folder_frame.pack(fill=tk.X, padx=20, pady=4)
        
        # כותרת שלב
        tk.Label(folder_frame, text="שלב 1: בחר תיקייה",
                font=("Segoe UI", 10, "bold"), bg="white", fg="#424242").pack(anchor="e", pady=(5, 3), padx=10)
        
        folder_row = tk.Frame(folder_frame, bg="white")
        folder_row.pack(fill=tk.X, padx=10, pady=(0, 5))
        
        # תיבת טקסט מעוצבת
        folder_entry = tk.Entry(folder_row, textvariable=self.selected_folder,
                               font=("Segoe UI", 9), relief=tk.SOLID, bd=1,
                               highlightthickness=1, highlightcolor="#2196F3",
                               highlightbackground="#E0E0E0")
        folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8), ipady=4)
        
        # כפתור גדול ומעוצב
        browse_btn = tk.Button(folder_row, text="📁 בחר תיקייה",
                              command=self.browse_folder,
                              font=("Segoe UI", 9, "bold"),
                              bg="#2196F3", fg="white",
                              activebackground="#1976D2", activeforeground="white",
                              relief=tk.FLAT, bd=0,
                              padx=18, pady=6, cursor="hand2")
        browse_btn.pack(side=tk.LEFT)
        
        # שלב 2 - אפשרויות
        options_frame = tk.Frame(self.root, bg="white", relief=tk.FLAT, bd=0)
        options_frame.pack(fill=tk.X, padx=20, pady=4)
        
        tk.Label(options_frame, text="שלב 2: אפשרויות סריקה",
                font=("Segoe UI", 10, "bold"), bg="white", fg="#424242").pack(anchor="e", pady=(5, 3), padx=10)
        
        self.scan_by_hash = tk.BooleanVar(value=True)
        self.scan_by_name = tk.BooleanVar(value=True)
        self.min_similarity = tk.IntVar(value=85)
        
        # שורת אפשרויות
        options_row = tk.Frame(options_frame, bg="white")
        options_row.pack(fill=tk.X, padx=10, pady=(0, 5))
        
        # Checkboxes מעוצבים
        check1 = tk.Checkbutton(options_row, text="זיהוי קבצים זהים",
                               variable=self.scan_by_hash,
                               font=("Segoe UI", 9), bg="white",
                               activebackground="white", selectcolor="#4CAF50",
                               cursor="hand2")
        check1.pack(side=tk.RIGHT, padx=10)
        
        check2 = tk.Checkbutton(options_row, text="זיהוי שמות דומים",
                               variable=self.scan_by_name,
                               font=("Segoe UI", 9), bg="white",
                               activebackground="white", selectcolor="#FF9800",
                               cursor="hand2")
        check2.pack(side=tk.RIGHT, padx=10)
        
        # בורר דמיון
        similarity_frame = tk.Frame(options_row, bg="white")
        similarity_frame.pack(side=tk.RIGHT, padx=10)
        
        tk.Label(similarity_frame, text="דמיון מינימלי:",
                font=("Segoe UI", 9), bg="white", fg="#616161").pack(side=tk.RIGHT, padx=3)
        
        spin = tk.Spinbox(similarity_frame, from_=50, to=100,
                         textvariable=self.min_similarity,
                         font=("Segoe UI", 9), width=5,
                         relief=tk.SOLID, bd=1)
        spin.pack(side=tk.RIGHT, padx=3)
        
        tk.Label(similarity_frame, text="%",
                font=("Segoe UI", 9), bg="white", fg="#616161").pack(side=tk.RIGHT)
        
        # שלב 3 - כפתורי פעולה גדולים
        button_frame = tk.Frame(self.root, bg="#f5f5f5", pady=4)
        button_frame.pack(fill=tk.X)
        
        # כפתור סריקה ראשי - ירוק וגדול
        self.scan_button = tk.Button(button_frame, text="🔍 התחל סריקה",
                                     command=self.start_scan,
                                     font=("Segoe UI", 9, "bold"),
                                     bg="#4CAF50", fg="white",
                                     activebackground="#388E3C", activeforeground="white",
                                     relief=tk.FLAT, bd=0,
                                     padx=20, pady=6, cursor="hand2")
        self.scan_button.pack(side=tk.RIGHT, padx=8)
        
        # אפקטי hover לכפתור סריקה
        def scan_enter(e):
            self.scan_button.config(bg="#66BB6A")
        def scan_leave(e):
            self.scan_button.config(bg="#4CAF50")
        self.scan_button.bind("<Enter>", scan_enter)
        self.scan_button.bind("<Leave>", scan_leave)
        
        # כפתור מחיקה - אדום
        self.delete_button = tk.Button(button_frame, text="🗑️ מחק מסומנים",
                                       command=self.delete_selected,
                                       font=("Segoe UI", 9, "bold"),
                                       bg="#9E9E9E", fg="white",
                                       activebackground="#d32f2f", activeforeground="white",
                                       relief=tk.FLAT, bd=0, state=tk.DISABLED,
                                       disabledforeground="#E0E0E0",
                                       padx=18, pady=6, cursor="hand2")
        self.delete_button.pack(side=tk.RIGHT, padx=8)
        
        # כפתור מחיקת כל הכפולים - אדום כהה
        self.delete_all_duplicates_button = tk.Button(button_frame, text="🗑️ מחק כל הכפולים",
                                                      command=self.delete_all_duplicates,
                                                      font=("Segoe UI", 9, "bold"),
                                                      bg="#9E9E9E", fg="white",
                                                      activebackground="#c62828", activeforeground="white",
                                                      relief=tk.FLAT, bd=0, state=tk.DISABLED,
                                                      disabledforeground="#E0E0E0",
                                                      padx=18, pady=6, cursor="hand2")
        self.delete_all_duplicates_button.pack(side=tk.RIGHT, padx=8)
        
        # אפקטי hover לכפתור מחיקה
        def delete_enter(e):
            if self.delete_button['state'] == tk.NORMAL:
                self.delete_button.config(bg="#EF5350")
        def delete_leave(e):
            if self.delete_button['state'] == tk.NORMAL:
                self.delete_button.config(bg="#f44336")
        self.delete_button.bind("<Enter>", delete_enter)
        self.delete_button.bind("<Leave>", delete_leave)
        
        # אפקטי hover לכפתור מחיקת כל הכפולים
        def delete_all_enter(e):
            if self.delete_all_duplicates_button['state'] == tk.NORMAL:
                self.delete_all_duplicates_button.config(bg="#D32F2F")
        def delete_all_leave(e):
            if self.delete_all_duplicates_button['state'] == tk.NORMAL:
                self.delete_all_duplicates_button.config(bg="#c62828")
        self.delete_all_duplicates_button.bind("<Enter>", delete_all_enter)
        self.delete_all_duplicates_button.bind("<Leave>", delete_all_leave)
        
        # כפתור עצירה - כתום (מוסתר בהתחלה)
        self.stop_button = tk.Button(button_frame, text="⏹ עצור",
                                     command=self.stop_scan,
                                     font=("Segoe UI", 9, "bold"),
                                     bg="#FF5722", fg="white",
                                     activebackground="#E64A19", activeforeground="white",
                                     relief=tk.FLAT, bd=0,
                                     padx=20, pady=6, cursor="hand2")
        # לא מציגים בהתחלה
        
        # אפקטי hover לכפתור עצירה
        def stop_enter(e):
            self.stop_button.config(bg="#FF7043")
        def stop_leave(e):
            self.stop_button.config(bg="#FF5722")
        self.stop_button.bind("<Enter>", stop_enter)
        self.stop_button.bind("<Leave>", stop_leave)
        
        # כפתור עזרה - כחול בהיר
        self.help_button = tk.Button(button_frame, text="❓ עזרה",
                                     command=self.show_help,
                                     font=("Segoe UI", 9, "bold"),
                                     bg="#03A9F4", fg="white",
                                     activebackground="#0288D1", activeforeground="white",
                                     relief=tk.FLAT, bd=0,
                                     padx=18, pady=6, cursor="hand2")
        self.help_button.pack(side=tk.LEFT, padx=8)
        
        # אפקטי hover לכפתור עזרה
        def help_enter(e):
            self.help_button.config(bg="#29B6F6")
        def help_leave(e):
            self.help_button.config(bg="#03A9F4")
        self.help_button.bind("<Enter>", help_enter)
        self.help_button.bind("<Leave>", help_leave)
        
        # סטטוס בולט
        status_frame = tk.Frame(self.root, bg="#E3F2FD", relief=tk.FLAT, bd=0)
        status_frame.pack(fill=tk.X, padx=20, pady=3)
        
        self.status_label = tk.Label(status_frame, text="✓ מוכן לסריקה",
                                     font=("Segoe UI", 8, "bold"),
                                     bg="#E3F2FD", fg="#1976D2",
                                     pady=3)
        self.status_label.pack()
        
        # פס התקדמות גדול יותר
        progress_container = tk.Frame(self.root, bg="#f5f5f5")
        progress_container.pack(fill=tk.X, padx=20, pady=(0, 5))
        
        self.progress = ttk.Progressbar(progress_container, mode='indeterminate', length=400)
        self.progress.pack(pady=5)
        
        # תוצאות
        results_frame = tk.Frame(self.root, bg="white", relief=tk.FLAT, bd=0)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=(0, 15))
        
        # כותרת תוצאות
        results_header = tk.Frame(results_frame, bg="#FAFAFA", height=45)
        results_header.pack(fill=tk.X)
        results_header.pack_propagate(False)
        
        tk.Label(results_header, text="תוצאות הסריקה",
                font=("Segoe UI", 13, "bold"), bg="#FAFAFA", fg="#424242").pack(anchor="e", padx=15, pady=10)
        
        # תוכן תוצאות עם Scrollbar
        results_content = tk.Frame(results_frame, bg="white")
        results_content.pack(fill=tk.BOTH, expand=True)
        
        # פס כלים לגלילה מהירה
        scroll_toolbar = tk.Frame(results_content, bg="#EEEEEE", height=35)
        scroll_toolbar.pack(fill=tk.X, side=tk.TOP)
        
        tk.Label(scroll_toolbar, text="⚡ גלילה מהירה:",
                font=("Segoe UI", 9, "bold"), bg="#EEEEEE", fg="#616161").pack(side=tk.RIGHT, padx=10)
        
        # כפתורי גלילה מהירה
        def scroll_to_top():
            self.results_canvas.yview_moveto(0)
        
        def scroll_to_bottom():
            self.results_canvas.yview_moveto(1)
        
        tk.Button(scroll_toolbar, text="⬆ תחילה",
                 command=scroll_to_top,
                 font=("Segoe UI", 9, "bold"),
                 bg="#90CAF9", fg="#0D47A1",
                 activebackground="#64B5F6",
                 relief=tk.FLAT, bd=0,
                 padx=15, pady=5, cursor="hand2").pack(side=tk.RIGHT, padx=5)
        
        tk.Button(scroll_toolbar, text="⬇ סוף",
                 command=scroll_to_bottom,
                 font=("Segoe UI", 9, "bold"),
                 bg="#90CAF9", fg="#0D47A1",
                 activebackground="#64B5F6",
                 relief=tk.FLAT, bd=0,
                 padx=15, pady=5, cursor="hand2").pack(side=tk.RIGHT, padx=5)
        
        tk.Label(scroll_toolbar, text="🎮 חיצים / Page Up/Down / Home/End",
                font=("Segoe UI", 8), bg="#EEEEEE", fg="#9E9E9E").pack(side=tk.LEFT, padx=15)
        
        # אינדיקטור מיקום גלילה
        self.scroll_position_label = tk.Label(scroll_toolbar, text="",
                font=("Segoe UI", 8, "bold"), bg="#EEEEEE", fg="#1976D2")
        self.scroll_position_label.pack(side=tk.LEFT, padx=10)
        
        # מיכל ה-Canvas
        canvas_container = tk.Frame(results_content, bg="white")
        canvas_container.pack(fill=tk.BOTH, expand=True)
        
        # מיכל ה-Canvas
        canvas_container = tk.Frame(results_content, bg="white")
        canvas_container.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar מעוצב
        scrollbar = ttk.Scrollbar(canvas_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Canvas עבור תוצאות
        self.results_canvas = tk.Canvas(canvas_container, yscrollcommand=scrollbar.set, 
                                       bg="#f0f0f0", highlightthickness=0)
        self.results_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.results_canvas.yview)
        
        # Frame פנימי לתוצאות עם רקע נקי
        self.results_inner_frame = tk.Frame(self.results_canvas, bg="#f0f0f0")
        self.canvas_frame = self.results_canvas.create_window((0, 0), 
                                                              window=self.results_inner_frame, 
                                                              anchor=tk.NW)
        
        # תיקון גלילה - עדכון גודל Canvas
        def configure_scroll(event=None):
            self.results_canvas.configure(scrollregion=self.results_canvas.bbox("all"))
            # התאמת רוחב הפריים לגודל Canvas
            canvas_width = self.results_canvas.winfo_width()
            if canvas_width > 1:
                self.results_canvas.itemconfig(self.canvas_frame, width=canvas_width)
            update_scroll_position()
        
        # עדכון אינדיקטור מיקום
        def update_scroll_position(*args):
            try:
                scroll_pos = self.results_canvas.yview()
                if scroll_pos[1] - scroll_pos[0] >= 1.0:
                    self.scroll_position_label.config(text="")
                else:
                    percentage = int(scroll_pos[0] * 100)
                    self.scroll_position_label.config(text=f"📍 {percentage}%")
            except:
                pass
        
        self.results_inner_frame.bind("<Configure>", configure_scroll)
        self.results_canvas.bind("<Configure>", configure_scroll)
        self.results_canvas.config(yscrollcommand=lambda *args: (scrollbar.set(*args), update_scroll_position()))
        
        # גלילה עם גלגלת העכבר - משופרת וחלקה יותר
        def on_mousewheel(event):
            # גלילה מהירה יותר - 3 יחידות במקום 1
            self.results_canvas.yview_scroll(int(-1*(event.delta/40)), "units")
        
        # גלילה עם חיצי מקלדת
        def on_key_scroll(event):
            if event.keysym == 'Up':
                self.results_canvas.yview_scroll(-1, "units")
            elif event.keysym == 'Down':
                self.results_canvas.yview_scroll(1, "units")
            elif event.keysym == 'Prior':  # Page Up
                self.results_canvas.yview_scroll(-1, "pages")
            elif event.keysym == 'Next':  # Page Down
                self.results_canvas.yview_scroll(1, "pages")
            elif event.keysym == 'Home':
                self.results_canvas.yview_moveto(0)
            elif event.keysym == 'End':
                self.results_canvas.yview_moveto(1)
        
        # קישור אירועי גלילה
        self.results_canvas.bind_all("<MouseWheel>", on_mousewheel)
        self.results_canvas.bind_all("<Up>", on_key_scroll)
        self.results_canvas.bind_all("<Down>", on_key_scroll)
        self.results_canvas.bind_all("<Prior>", on_key_scroll)  # Page Up
        self.results_canvas.bind_all("<Next>", on_key_scroll)   # Page Down
        self.results_canvas.bind_all("<Home>", on_key_scroll)
        self.results_canvas.bind_all("<End>", on_key_scroll)
        
        # הגדרת פוקוס כדי שהמקלדת תעבוד
        self.results_canvas.bind("<Button-1>", lambda e: self.results_canvas.focus_set())
    
    def browse_folder(self):
        """בחירת תיקייה"""
        folder = filedialog.askdirectory(title="בחר תיקייה לסריקה")
        if folder:
            self.selected_folder.set(folder)
    
    def stop_scan(self):
        """עצירת הסריקה"""
        self.scan_stopped = True
        self.update_status("⏹ הסריקה נעצרה על ידי המשתמש")
        self.stop_button.pack_forget()
        self.scan_button.config(state=tk.NORMAL)
        self.progress.stop()
    
    def start_scan(self):
        """התחלת סריקה בחוט נפרד"""
        folder = self.selected_folder.get()
        
        if not folder or not os.path.exists(folder):
            messagebox.showerror("שגיאה", "אנא בחר תיקייה תקינה")
            return
        
        # ניקוי תוצאות קודמות
        for widget in self.results_inner_frame.winfo_children():
            widget.destroy()
        
        self.duplicates = []
        self.file_checkboxes = {}
        
        # איפוס גלילה
        self.results_canvas.yview_moveto(0)
        
        # השבתת כפתורים והצגת כפתור עצירה
        self.scan_stopped = False
        self.scan_button.config(state=tk.DISABLED)
        self.delete_button.config(state=tk.DISABLED)
        self.stop_button.pack(side=tk.RIGHT, padx=15, after=self.scan_button)
        self.progress.start()
        
        # הרצה בחוט נפרד
        thread = threading.Thread(target=self.scan_files)
        thread.daemon = True
        thread.start()
    
    def scan_files(self):
        """סריקת קבצים וזיהוי כפילויות - מהירה ויעילה"""
        folder = self.selected_folder.get()
        
        self.update_status("סורק קבצים...")
        
        # איסוף כל הקבצים - עם דילוג על קבצים לא נגישים
        all_files = []
        skipped = 0
        
        for root, dirs, files in os.walk(folder):
            # בדיקה אם המשתמש עצר את הסריקה
            if self.scan_stopped:
                self.root.after(0, lambda: self.progress.stop())
                self.root.after(0, lambda: self.scan_button.config(state=tk.NORMAL))
                self.root.after(0, lambda: self.stop_button.pack_forget())
                return
            
            # דילוג על תיקיות מערכת
            dirs[:] = [d for d in dirs if not d.startswith('$') and d not in ['System Volume Information', 'Recycle.Bin']]
            
            for file in files:
                # בדיקה אם המשתמש עצר את הסריקה
                if self.scan_stopped:
                    self.root.after(0, lambda: self.progress.stop())
                    self.root.after(0, lambda: self.scan_button.config(state=tk.NORMAL))
                    self.root.after(0, lambda: self.stop_button.pack_forget())
                    return
                
                filepath = os.path.join(root, file)
                try:
                    # בדיקה שהקובץ נגיש
                    if os.path.exists(filepath) and os.path.getsize(filepath) >= 0:
                        all_files.append(filepath)
                    else:
                        skipped += 1
                except (OSError, PermissionError):
                    skipped += 1
                    continue
                
                # עדכון סטטוס כל 100 קבצים
                if len(all_files) % 100 == 0:
                    self.update_status(f"סורק... {len(all_files)} קבצים")
        
        status_msg = f"נמצאו {len(all_files)} קבצים"
        if skipped > 0:
            status_msg += f" ({skipped} דולגו)"
        self.update_status(status_msg + ", מחשב...")
        
        duplicates = []
        
        # זיהוי לפי Hash (קבצים זהים)
        if self.scan_by_hash.get():
            hash_duplicates = self.find_by_hash(all_files)
            duplicates.extend(hash_duplicates)
        
        # זיהוי לפי שם דומה
        if self.scan_by_name.get():
            name_duplicates = self.find_by_name(all_files)
            duplicates.extend(name_duplicates)
        
        self.duplicates = duplicates
        
        # עדכון ממשק
        self.root.after(0, self.display_results)
        self.root.after(0, lambda: self.progress.stop())
        self.root.after(0, lambda: self.scan_button.config(state=tk.NORMAL))
        self.root.after(0, lambda: self.stop_button.pack_forget())
        
        if duplicates:
            self.root.after(0, lambda: self.delete_button.config(state=tk.NORMAL, bg="#f44336"))
            # בדיקה אם יש קבוצות זהות (לא רק דומות)
            has_identical = any(d['type'] == 'identical' for d in duplicates)
            if has_identical:
                self.root.after(0, lambda: self.delete_all_duplicates_button.config(state=tk.NORMAL, bg="#c62828"))
    
    def find_by_hash(self, files):
        """מציאת קבצים זהים לפי Hash - מהיר ויעיל"""
        hash_map = defaultdict(list)
        total = len(files)
        
        for i, filepath in enumerate(files):
            # בדיקה אם המשתמש עצר את הסריקה
            if self.scan_stopped:
                return []
            
            try:
                # עדכון כל 50 קבצים או כל 2%
                if i % 50 == 0 or (i % max(1, total // 50) == 0):
                    progress = int((i / total) * 100)
                    self.update_status(f"מחשב Hash: {i}/{total} ({progress}%)")
                
                file_hash = self.get_file_hash(filepath)
                if not file_hash.startswith("error_"):
                    hash_map[file_hash].append(filepath)
            except Exception as e:
                continue
        
        # מציאת קבוצות כפולות
        duplicates = []
        for file_hash, file_list in hash_map.items():
            if len(file_list) > 1:
                duplicates.append({
                    'type': 'identical',
                    'similarity': 100,
                    'files': file_list
                })
        
        return duplicates
    
    def find_by_name(self, files):
        """מציאת קבצים עם שמות דומים - אופטימלי"""
        duplicates = []
        min_sim = self.min_similarity.get() / 100.0
        total = len(files)
        
        # דילוג אם יש יותר מדי קבצים (למנוע תקיעה)
        if total > 1000:
            self.update_status(f"דילוג על זיהוי שמות - {total} קבצים (מקסימום: 1000)")
            return duplicates
        
        # השוואת שמות קבצים
        filenames = [(Path(f).name.lower(), f) for f in files]
        
        checked_pairs = set()
        
        for i, (name1, path1) in enumerate(filenames):
            # בדיקה אם המשתמש עצר את הסריקה
            if self.scan_stopped:
                return []
            
            # עדכון כל 100 קבצים או כל 5%
            if i % 100 == 0 or (i % max(1, total // 20) == 0):
                progress = int((i / total) * 100)
                self.update_status(f"משווה שמות: {i}/{total} ({progress}%)")
            
            for j, (name2, path2) in enumerate(filenames[i+1:], i+1):
                if (i, j) in checked_pairs:
                    continue
                
                similarity = SequenceMatcher(None, name1.lower(), 
                                            name2.lower()).ratio()
                
                if similarity >= min_sim and path1 != path2:
                    # בדיקה אם כבר יש קבוצה עם אחד מהקבצים
                    found_group = None
                    for dup in duplicates:
                        if dup['type'] == 'similar' and (path1 in dup['files'] or 
                                                         path2 in dup['files']):
                            found_group = dup
                            break
                    
                    if found_group:
                        if path1 not in found_group['files']:
                            found_group['files'].append(path1)
                        if path2 not in found_group['files']:
                            found_group['files'].append(path2)
                    else:
                        duplicates.append({
                            'type': 'similar',
                            'similarity': int(similarity * 100),
                            'files': [path1, path2]
                        })
                    
                    checked_pairs.add((i, j))
        
        return duplicates
    
    def get_file_hash(self, filepath, block_size=1048576):
        """חישוב Hash של קובץ - מהיר ויעיל"""
        try:
            file_size = os.path.getsize(filepath)
            hasher = hashlib.md5()
            
            with open(filepath, 'rb') as f:
                # לקבצים קטנים - קרא הכל בבת אחת
                if file_size < 1048576:  # < 1MB
                    hasher.update(f.read())
                else:
                    # לקבצים גדולים - קרא בבלוקים של 1MB
                    while True:
                        data = f.read(block_size)
                        if not data:
                            break
                        hasher.update(data)
            
            return hasher.hexdigest()
        except (OSError, IOError) as e:
            # קובץ לא נגיש - החזר hash ייחודי
            return f"error_{filepath}_{e}"
    
    def display_results(self):
        """הצגת תוצאות - מהירה וללא תקיעות"""
        if not self.duplicates:
            self.update_status("לא נמצאו קבצים כפולים")
            
            ttk.Label(self.results_inner_frame, 
                     text="✓ לא נמצאו קבצים כפולים",
                     font=("Arial", 12, "bold")).pack(pady=20)
            return
        
        total_groups = len(self.duplicates)
        total_files = sum(len(g['files']) for g in self.duplicates)
        
        # הגבלת תצוגה למניעת תקיעות
        display_groups = self.duplicates[:self.max_display_groups]
        
        status = f"נמצאו {total_groups} קבוצות ({total_files} קבצים)"
        if total_groups > self.max_display_groups:
            status += f" - מציג {self.max_display_groups} ראשונות"
            
            warning = ttk.Label(self.results_inner_frame, 
                     text=f"⚠️ מוצגות {self.max_display_groups} קבוצות מתוך {total_groups}",
                     font=("Arial", 10, "bold"),
                     foreground="orange")
            warning.pack(pady=10)
        
        self.update_status(status)
        
        # הצגת התוצאות בעיצוב מעוגל ומסוגנן
        for i, dup_group in enumerate(display_groups):
            if i % 5 == 0 and i > 0:
                self.root.update_idletasks()
            
            # כרטיס מעוגל עם צל בולט
            card_container = tk.Frame(self.results_inner_frame, bg="#f0f0f0", relief=tk.FLAT, bd=0)
            card_container.pack(fill=tk.X, pady=15, padx=25)
            
            # צל תחתון
            shadow_bottom = tk.Frame(card_container, bg="#D0D0D0", height=4)
            shadow_bottom.pack(side=tk.BOTTOM, fill=tk.X)
            
            # הכרטיס עצמו
            card = tk.Frame(card_container, bg="white", relief=tk.RAISED, bd=1)
            card.pack(fill=tk.X)
            
            # כותרת מעוצבת עם צבעים בולטים
            if dup_group['type'] == 'identical':
                header_bg = "#C8E6C9"
                badge_bg = "#4CAF50"
                badge_text = "✓ קבצים זהים 100%"
                header_icon = "🟢"
            else:
                header_bg = "#FFE0B2"
                badge_bg = "#FF9800"
                similarity = dup_group['similarity']
                badge_text = f"≈ דומים {similarity}%"
                header_icon = "🟡"
            
            header = tk.Frame(card, bg=header_bg, height=60)
            header.pack(fill=tk.X)
            header.pack_propagate(False)
            
            # תוכן כותרת
            header_inner = tk.Frame(header, bg=header_bg)
            header_inner.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
            
            # אייקון בצד שמאל
            tk.Label(header_inner, text=header_icon,
                    bg=header_bg, font=("Segoe UI", 20)).pack(side=tk.LEFT, padx=(0, 10))
            
            # תג צבעוני מעוגל
            badge_frame = tk.Frame(header_inner, bg=badge_bg, bd=0, relief=tk.FLAT)
            badge_frame.pack(side=tk.RIGHT, padx=10)
            
            badge_label = tk.Label(badge_frame, text=badge_text,
                                  bg=badge_bg, fg="white",
                                  font=("Segoe UI", 11, "bold"),
                                  padx=20, pady=7)
            badge_label.pack()
            
            # מספר קבוצה
            group_label = tk.Label(header_inner, text=f"קבוצה #{i+1}",
                    bg=header_bg, fg="#212121",
                    font=("Segoe UI", 14, "bold"))
            group_label.pack(side=tk.RIGHT, padx=15)
            
            # מספר קבצים בקבוצה
            file_count = len(dup_group['files'])
            count_label = tk.Label(header_inner, text=f"({file_count} קבצים)",
                    bg=header_bg, fg="#616161",
                    font=("Segoe UI", 11))
            count_label.pack(side=tk.RIGHT, padx=(0, 5))
            
            # תוכן הקבוצה
            content = tk.Frame(card, bg="white")
            content.pack(fill=tk.X, padx=20, pady=15)
            
            for file_idx, filepath in enumerate(dup_group['files']):
                # שורת קובץ עם אפקט hover
                file_row = tk.Frame(content, bg="white", relief=tk.FLAT)
                file_row.pack(fill=tk.X, pady=8, padx=5)
                
                # אפקט hover לשורת קובץ
                def make_hover_effect(row):
                    def on_enter(e):
                        row.config(bg="#F5F5F5")
                        for child in row.winfo_children():
                            try:
                                if child.winfo_class() != 'Button':
                                    child.config(bg="#F5F5F5")
                                    if hasattr(child, 'winfo_children'):
                                        for subchild in child.winfo_children():
                                            try:
                                                if subchild.winfo_class() != 'Button':
                                                    subchild.config(bg="#F5F5F5")
                                            except:
                                                pass
                            except:
                                pass
                    def on_leave(e):
                        row.config(bg="white")
                        for child in row.winfo_children():
                            try:
                                if child.winfo_class() != 'Button':
                                    child.config(bg="white")
                                    if hasattr(child, 'winfo_children'):
                                        for subchild in child.winfo_children():
                                            try:
                                                if subchild.winfo_class() != 'Button':
                                                    subchild.config(bg="white")
                                            except:
                                                pass
                            except:
                                pass
                    row.bind("<Enter>", on_enter)
                    row.bind("<Leave>", on_leave)
                make_hover_effect(file_row)
                
                # Checkbox גדול ומעוצב בסגנון מודרני
                var = tk.IntVar(value=0)
                self.file_checkboxes[filepath] = var
                
                # יצירת checkbox גדול בעזרת Label
                checkbox_frame = tk.Frame(file_row, bg="white")
                checkbox_frame.pack(side=tk.LEFT, padx=(0, 15))
                
                checkbox_label = tk.Label(checkbox_frame, text="☐", 
                                         font=("Segoe UI", 28, "bold"),
                                         fg="#757575", bg="white",
                                         cursor="hand2")
                checkbox_label.pack()
                
                def toggle_checkbox(event, v=var, lbl=checkbox_label):
                    if v.get() == 0:
                        v.set(1)
                        lbl.config(text="☑", fg="#2196F3")
                    else:
                        v.set(0)
                        lbl.config(text="☐", fg="#757575")
                
                checkbox_label.bind("<Button-1>", toggle_checkbox)
                
                # אייקון קובץ גדול ומעוצב
                icon_label = tk.Label(file_row, text="📄", bg="white",
                                     font=("Segoe UI", 20))
                icon_label.pack(side=tk.LEFT, padx=(0, 12))
                
                # מידע קובץ
                info_frame = tk.Frame(file_row, bg="white")
                info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
                
                # שם קובץ - גדול ובולט
                filename = os.path.basename(filepath)
                name_label = tk.Label(info_frame, text=filename,
                                     bg="white", fg="#212121",
                                     font=("Segoe UI", 11, "bold"),
                                     anchor="w")
                name_label.pack(fill=tk.X)
                
                # פרטים - יותר קריא
                folder_path = os.path.dirname(filepath)
                size = os.path.getsize(filepath)
                size_str = self.format_size(size)
                
                details = f"📂 {folder_path}  •  📊 {size_str}"
                details_label = tk.Label(info_frame, text=details,
                                        bg="white", fg="#757575",
                                        font=("Segoe UI", 9),
                                        anchor="w")
                details_label.pack(fill=tk.X, pady=(4, 0))
                
                # כפתורים מעוגלים
                buttons_frame = tk.Frame(file_row, bg="white")
                buttons_frame.pack(side=tk.LEFT, padx=10)
                
                # כפתור פתח
                open_btn = tk.Button(buttons_frame, text="פתח",
                                   bg="#2196F3", fg="white",
                                   font=("Segoe UI", 10, "bold"),
                                   relief=tk.FLAT, bd=0,
                                   padx=22, pady=8,
                                   cursor="hand2",
                                   activebackground="#1976D2",
                                   command=lambda p=filepath: self.open_file(p))
                open_btn.pack(side=tk.LEFT, padx=3)
                
                # אפקט hover לכפתור פתח
                def make_open_hover(btn):
                    def on_enter(e):
                        btn.config(bg="#42A5F5")
                    def on_leave(e):
                        btn.config(bg="#2196F3")
                    btn.bind("<Enter>", on_enter)
                    btn.bind("<Leave>", on_leave)
                make_open_hover(open_btn)
                
                # כפתור תיקייה
                folder_btn = tk.Button(buttons_frame, text="תיקייה",
                                      bg="#757575", fg="white",
                                      font=("Segoe UI", 10, "bold"),
                                      relief=tk.FLAT, bd=0,
                                      padx=22, pady=8,
                                      cursor="hand2",
                                      activebackground="#616161",
                                      command=lambda p=filepath: self.open_folder(p))
                folder_btn.pack(side=tk.LEFT, padx=3)
                
                # אפקט hover לכפתור תיקייה
                def make_folder_hover(btn):
                    def on_enter(e):
                        btn.config(bg="#9E9E9E")
                    def on_leave(e):
                        btn.config(bg="#757575")
                    btn.bind("<Enter>", on_enter)
                    btn.bind("<Leave>", on_leave)
                make_folder_hover(folder_btn)
                
                # קו מפריד דק
                if file_idx < len(dup_group['files']) - 1:
                    separator = tk.Frame(content, bg="#eeeeee", height=1)
                    separator.pack(fill=tk.X, pady=5)
    
    def format_size(self, size):
        """פורמט גודל קובץ"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def open_file(self, filepath):
        """פתיחת קובץ"""
        try:
            os.startfile(filepath)
        except Exception as e:
            messagebox.showerror("שגיאה", f"לא ניתן לפתוח את הקובץ:\n{str(e)}")
    
    def open_folder(self, filepath):
        """פתיחת תיקיית הקובץ"""
        try:
            folder = os.path.dirname(filepath)
            os.startfile(folder)
        except Exception as e:
            messagebox.showerror("שגיאה", f"לא ניתן לפתוח את התיקיה:\n{str(e)}")
    
    def delete_all_duplicates(self):
        """מחיקת כל הקבצים הכפולים הזהים - משאיר קובץ אחד מכל קבוצה"""
        # איסוף כל הקבצים למחיקה מקבוצות זהות בלבד
        files_to_delete = []
        groups_count = 0
        
        for dup_group in self.duplicates:
            if dup_group['type'] == 'identical':  # רק קבצים זהים, לא דומים
                # משאיר את הקובץ הראשון, מוחק את כל השאר
                files = dup_group['files']
                if len(files) > 1:
                    files_to_delete.extend(files[1:])  # כל הקבצים מלבד הראשון
                    groups_count += 1
        
        if not files_to_delete:
            messagebox.showinfo("אין מה למחוק", "לא נמצאו קבצים כפולים זהים למחיקה")
            return
        
        # אישור מחיקה עם מידע מפורט
        result = messagebox.askyesno(
            "⚠️ אישור מחיקה המונית",
            f"פעולה זו תמחק {len(files_to_delete)} קבצים כפולים מתוך {groups_count} קבוצות זהות.\n\n"
            f"מכל קבוצה ישאר קובץ אחד (הראשון שנמצא).\n"
            f"קבוצות עם שמות דומים לא יימחקו.\n\n"
            f"⚠️ המחיקה סופית ולא ניתן לשחזר!\n\n"
            f"האם להמשיך?",
            icon='warning'
        )
        
        if not result:
            return
        
        # מחיקה
        deleted = 0
        errors = []
        
        for filepath in files_to_delete:
            try:
                os.remove(filepath)
                deleted += 1
            except Exception as e:
                errors.append(f"{os.path.basename(filepath)}: {str(e)}")
        
        # עדכון רשימת הכפילויות - הסרת קבוצות שנמחקו לגמרי
        files_to_delete_set = set(files_to_delete)
        updated_duplicates = []
        
        for dup_group in self.duplicates:
            remaining_files = [f for f in dup_group['files'] if f not in files_to_delete_set]
            
            # רק אם נשארו 2+ קבצים בקבוצה
            if len(remaining_files) > 1:
                dup_group['files'] = remaining_files
                updated_duplicates.append(dup_group)
        
        self.duplicates = updated_duplicates
        
        # הצגת תוצאות
        message = f"✓ נמחקו {deleted} קבצים בהצלחה!\n\nנשאר קובץ אחד מכל קבוצה."
        if errors:
            message += f"\n\n⚠️ שגיאות ({len(errors)}):\n" + "\n".join(errors[:5])
            if len(errors) > 5:
                message += f"\n... ועוד {len(errors) - 5}"
        
        messagebox.showinfo("סיום מחיקה", message)
        
        # עדכון התצוגה
        for widget in self.results_inner_frame.winfo_children():
            widget.destroy()
        
        self.file_checkboxes = {}
        self.display_results()
        
        # אם לא נשארו כפילויות, השבת את כפתורי המחיקה
        if not self.duplicates:
            self.delete_button.config(state=tk.DISABLED, bg="#9E9E9E")
            self.delete_all_duplicates_button.config(state=tk.DISABLED, bg="#9E9E9E")
        else:
            # בדיקה אם עדיין יש קבוצות זהות
            has_identical = any(d['type'] == 'identical' for d in self.duplicates)
            if not has_identical:
                self.delete_all_duplicates_button.config(state=tk.DISABLED, bg="#9E9E9E")
    
    def delete_selected(self):
        """מחיקת קבצים מסומנים"""
        files_to_delete = [path for path, var in self.file_checkboxes.items() 
                          if var.get() == 1]
        
        if not files_to_delete:
            messagebox.showwarning("אזהרה", "לא נבחרו קבצים למחיקה")
            return
        
        # אישור מחיקה
        result = messagebox.askyesno(
            "אישור מחיקה",
            f"האם אתה בטוח שברצונך למחוק {len(files_to_delete)} קבצים?\n"
            f"פעולה זו אינה הפיכה!"
        )
        
        if not result:
            return
        
        # מחיקה
        deleted = 0
        errors = []
        
        for filepath in files_to_delete:
            try:
                os.remove(filepath)
                deleted += 1
            except Exception as e:
                errors.append(f"{filepath}: {str(e)}")
        
        # עדכון רשימת הכפילויות - הסרת קבצים שנמחקו
        files_to_delete_set = set(files_to_delete)
        
        # מעבר על כל הקבוצות והסרת הקבצים שנמחקו
        updated_duplicates = []
        for dup_group in self.duplicates:
            # סינון קבצים שלא נמחקו
            remaining_files = [f for f in dup_group['files'] if f not in files_to_delete_set]
            
            # רק אם נשארו 2+ קבצים בקבוצה
            if len(remaining_files) > 1:
                dup_group['files'] = remaining_files
                updated_duplicates.append(dup_group)
        
        self.duplicates = updated_duplicates
        
        # הצגת תוצאות
        message = f"נמחקו {deleted} קבצים בהצלחה"
        if errors:
            message += f"\n\nשגיאות ({len(errors)}):\n" + "\n".join(errors[:5])
            if len(errors) > 5:
                message += f"\n... ועוד {len(errors) - 5}"
        
        messagebox.showinfo("סיום מחיקה", message)
        
        # עדכון התצוגה ללא סריקה מחדש
        for widget in self.results_inner_frame.winfo_children():
            widget.destroy()
        
        self.file_checkboxes = {}
        self.display_results()
        
        # אם לא נשארו כפילויות, השבת את כפתורי המחיקה
        if not self.duplicates:
            self.delete_button.config(state=tk.DISABLED, bg="#9E9E9E")
            self.delete_all_duplicates_button.config(state=tk.DISABLED, bg="#9E9E9E")
        else:
            # בדיקה אם עדיין יש קבוצות זהות
            has_identical = any(d['type'] == 'identical' for d in self.duplicates)
            if not has_identical:
                self.delete_all_duplicates_button.config(state=tk.DISABLED, bg="#9E9E9E")
    
    def update_status(self, text):
        """עדכון טקסט סטטוס"""
        self.root.after(0, lambda: self.status_label.config(text=text))
    
    def show_help(self):
        """הצגת חלון הוראות למשתמש"""
        help_window = tk.Toplevel(self.root)
        help_window.title("הוראות שימוש - SHOSHI Duplicate Finder")
        help_window.geometry("750x650")
        help_window.resizable(True, True)
        
        # צבע רקע
        help_window.configure(bg="#f8f9fa")
        
        # Scrollbar
        canvas = tk.Canvas(help_window, bg="#f8f9fa", highlightthickness=0)
        scrollbar = ttk.Scrollbar(help_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#f8f9fa")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # התאמת רוחב
        def configure_canvas(event):
            canvas.itemconfig(canvas_window, width=event.width)
        canvas.bind("<Configure>", configure_canvas)
        
        # תוכן ההוראות
        help_text = tk.Frame(scrollable_frame, bg="#f8f9fa", padx=20, pady=20)
        help_text.pack(fill=tk.BOTH, expand=True)
        
        # כותרת ראשית מודרנית
        title_frame = tk.Frame(help_text, bg="white", relief=tk.FLAT)
        title_frame.pack(fill=tk.X, pady=(0, 5))
        
        # כותרת עליונה
        header_top = tk.Frame(title_frame, bg="#6366f1", height=8)
        header_top.pack(fill=tk.X)
        
        # כותרת ראשית
        header_main = tk.Frame(title_frame, bg="#4f46e5")
        header_main.pack(fill=tk.X)
        tk.Label(header_main, text="📚 מדריך שימוש מהיר", 
                 font=("Segoe UI", 20, "bold"),
                 bg="#4f46e5", fg="white",
                 pady=20).pack()
        
        # כותרת משנה
        tk.Label(title_frame, text="כל מה שצריך לדעת בשביל להתחיל", 
                 font=("Segoe UI", 10),
                 bg="white", fg="#6b7280",
                 pady=10).pack()
        
        instructions = [
            {
                "number": "1",
                "title": "בחירת תיקייה",
                "icon": "📂",
                "content": "בחר את התיקייה שרוצה לסרוק\nעובד עם תיקיות מהמחשב או כונן חיצוני",
                "color": "#3b82f6",
                "bg": "#eff6ff"
            },
            {
                "number": "2", 
                "title": "הגדרות סריקה",
                "icon": "⚙️",
                "content": "זיהוי קבצים זהים - תוכן זהה לחלוטין (מומלץ)\n"
                         "זיהוי שמות דומים - שמות דומים כמו תמונה ותמונה 1\n"
                         "אחוז דמיון - 85% ברירת מחדל (גבוה יותר = יותר מדויק)",
                "color": "#8b5cf6",
                "bg": "#f5f3ff"
            },
            {
                "number": "3",
                "title": "הפעלת סריקה", 
                "icon": "🔍",
                "content": "לחץ 'התחל סריקה' והמתן\n"
                         "הזמן משתנה לפי כמות הקבצים\n"
                         "ניתן ללחוץ על '⏹ עצור' בכל רגע לעצירת הסריקה",
                "color": "#10b981",
                "bg": "#ecfdf5"
            },
            {
                "number": "4",
                "title": "בחירת קבצים",
                "icon": "✓",
                "content": "סמן את הקבצים שרוצה למחוק (תיבות סימון גדולות)\n"
                         "לחץ 'פתח' כדי לפתוח ולבדוק את הקובץ\n"
                         "לחץ 'תיקייה' כדי לראות את המיקום",
                "color": "#f59e0b",
                "bg": "#fffbeb"
            },
            {
                "number": "5",
                "title": "מחיקה ידנית",
                "icon": "🗑️",
                "content": "לחץ 'מחק מסומנים' למחיקת הקבצים שסימנת\n"
                         "המחיקה סופית - הקבצים לא עוברים לסל מיחזור\n"
                         "תקבל אישור לפני המחיקה",
                "color": "#ef4444",
                "bg": "#fef2f2"
            },
            {
                "number": "6",
                "title": "מחיקה אוטומטית",
                "icon": "⚡",
                "content": "לחץ 'מחק כל הכפולים' למחיקה אוטומטית\n"
                         "מוחק רק קבצים זהים 100% (לא דומים!)\n"
                         "משאיר קובץ אחד מכל קבוצה זהה\n"
                         "חוסך זמן במקרה של הרבה כפילויות",
                "color": "#9333ea",
                "bg": "#faf5ff"
            }
        ]
        
        for item in instructions:
            # מסגרת כרטיס מודרנית
            card = tk.Frame(help_text, bg=item["bg"], relief=tk.FLAT, bd=0)
            card.pack(fill=tk.X, pady=6, padx=10)
            
            # פס צבעוני בצד
            side_bar = tk.Frame(card, bg=item["color"], width=5)
            side_bar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 0))
            
            # תוכן הכרטיס
            content_frame = tk.Frame(card, bg=item["bg"])
            content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=15, pady=15)
            
            # שורה עליונה - מספר ואייקון
            top_row = tk.Frame(content_frame, bg=item["bg"])
            top_row.pack(fill=tk.X, anchor="e", pady=(0, 5))
            
            # אייקון
            tk.Label(top_row, text=item["icon"], 
                    font=("Segoe UI", 24),
                    bg=item["bg"]).pack(side=tk.RIGHT, padx=(10, 0))
            
            # מספר שלב
            num_frame = tk.Frame(top_row, bg=item["color"], 
                                width=35, height=35)
            num_frame.pack(side=tk.RIGHT, padx=5)
            num_frame.pack_propagate(False)
            tk.Label(num_frame, text=item["number"],
                    font=("Segoe UI", 16, "bold"),
                    bg=item["color"], fg="white").pack(expand=True)
            
            # כותרת - בשורה נפרדת תמיד
            tk.Label(content_frame, text=item["title"],
                    font=("Segoe UI", 14, "bold"),
                    bg=item["bg"], fg="#1f2937",
                    anchor="e", justify="right").pack(fill=tk.X, pady=(0, 8))
            
            # תוכן
            tk.Label(content_frame, text=item["content"],
                    font=("Segoe UI", 10),
                    bg=item["bg"], fg="#4b5563",
                    anchor="e", justify="right",
                    wraplength=600).pack(fill=tk.X, pady=(0, 5))
        
        # סעיף טיפים מיוחד
        tips_frame = tk.Frame(help_text, bg="#fef3c7", relief=tk.FLAT, bd=0)
        tips_frame.pack(fill=tk.X, pady=10, padx=10)
        
        tk.Frame(tips_frame, bg="#f59e0b", height=3).pack(fill=tk.X)
        
        tips_content = tk.Frame(tips_frame, bg="#fef3c7")
        tips_content.pack(fill=tk.BOTH, padx=15, pady=15)
        
        tk.Label(tips_content, text="💡 טיפים שימושיים",
                font=("Segoe UI", 13, "bold"),
                bg="#fef3c7", fg="#92400e",
                anchor="e").pack(fill=tk.X, pady=(0, 10))
        
        tips_text = (
            "מוצגות עד 100 קבוצות ראשונות בלבד •\n"
            "להעלות את אחוז הדמיון ל-90+ אם יש הרבה תוצאות •\n"
            "זיהוי שמות עובד עד 1000 קבצים •\n"
            "כפתור 'עצור' מופיע רק בזמן סריקה •\n"
            "'מחק כל הכפולים' מופיע רק אם יש קבצים זהים 100% •\n"
            "מומלץ לגבות קבצים חשובים לפני השימוש הראשון •\n"
            "אחרי מחיקה התוצאות מתעדכנות אוטומטית •"
        )
        
        tk.Label(tips_content, text=tips_text,
                font=("Segoe UI", 9),
                bg="#fef3c7", fg="#78350f",
                anchor="e", justify="right").pack(fill=tk.X)
        
        # סעיף זמנים
        time_frame = tk.Frame(help_text, bg="#e0f2fe", relief=tk.FLAT, bd=0)
        time_frame.pack(fill=tk.X, pady=10, padx=10)
        
        tk.Frame(time_frame, bg="#0284c7", height=3).pack(fill=tk.X)
        
        time_content = tk.Frame(time_frame, bg="#e0f2fe")
        time_content.pack(fill=tk.BOTH, padx=15, pady=15)
        
        tk.Label(time_content, text="⏱️ זמני סריקה משוערים",
                font=("Segoe UI", 13, "bold"),
                bg="#e0f2fe", fg="#075985",
                anchor="e").pack(fill=tk.X, pady=(0, 10))
        
        time_text = (
            "1,000 קבצים ← 10-30 שניות\n"
            "10,000 קבצים ← 2-5 דקות\n"
            "100,000 קבצים ← 30-60 דקות"
        )
        
        tk.Label(time_content, text=time_text,
                font=("Segoe UI", 9),
                bg="#e0f2fe", fg="#0c4a6e",
                anchor="e", justify="right").pack(fill=tk.X)
        
        # מידע על התוכנה - פוטר מודרני
        footer_frame = tk.Frame(help_text, bg="white")
        footer_frame.pack(fill=tk.X, pady=(20, 0))
        
        tk.Frame(footer_frame, bg="#e5e7eb", height=1).pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(footer_frame, text="SHOSHI ER | 2025", 
                 font=("Segoe UI", 9, "bold"),
                 bg="white",
                 fg="#9ca3af").pack(pady=5)
        
        tk.Label(footer_frame, text="נוצר במיוחד בשבילך ❤️", 
                 font=("Segoe UI", 8),
                 bg="white",
                 fg="#d1d5db").pack(pady=(0, 10))
        
        # כפתור סגירה מודרני
        close_btn_frame = tk.Frame(help_text, bg="white")
        close_btn_frame.pack(pady=20)
        
        def on_enter(e):
            close_button.config(bg="#2563eb")
        
        def on_leave(e):
            close_button.config(bg="#3b82f6")
        
        close_button = tk.Button(close_btn_frame, text="✓ הבנתי, בואו נתחיל", 
                                font=("Segoe UI", 11, "bold"),
                                bg="#3b82f6", fg="white",
                                activebackground="#1d4ed8",
                                activeforeground="white",
                                relief=tk.FLAT,
                                bd=0,
                                padx=50, pady=12,
                                cursor="hand2",
                                command=help_window.destroy)
        close_button.pack()
        close_button.bind("<Enter>", on_enter)
        close_button.bind("<Leave>", on_leave)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # גלילה עם גלגלת עכבר
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

def main():
    root = tk.Tk()
    app = DuplicateFinderApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
