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
        self.root.geometry("1000x700")
        
        # משתנים
        self.selected_folder = tk.StringVar()
        self.duplicates = []
        self.file_checkboxes = {}
        self.max_display_groups = 100  # הגבלת תצוגה למניעת תקיעות
        
        self.setup_ui()
    
    def setup_ui(self):
        """יצירת הממשק"""
        # כותרת
        title_frame = ttk.Frame(self.root, padding="10")
        title_frame.pack(fill=tk.X)
        
        ttk.Label(title_frame, text="🔍 מזהה קבצים כפולים", 
                 font=("Arial", 18, "bold")).pack()
        ttk.Label(title_frame, text="SHOSHI ER | 2025", 
                 font=("Arial", 9), foreground="gray").pack(pady=2)
        
        ttk.Separator(self.root, orient="horizontal").pack(fill=tk.X, pady=10)
        
        # שלב 1 - בחירת תיקייה
        folder_frame = ttk.LabelFrame(self.root, text="שלב 1: בחר תיקייה", padding="15")
        folder_frame.pack(fill=tk.X, padx=20, pady=10)
        
        folder_row = ttk.Frame(folder_frame)
        folder_row.pack(fill=tk.X)
        
        ttk.Entry(folder_row, textvariable=self.selected_folder, 
                 font=("Arial", 10)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        ttk.Button(folder_row, text="📁 בחר תיקייה", 
                  command=self.browse_folder).pack(side=tk.LEFT)
        
        # שלב 2 - אפשרויות
        options_frame = ttk.LabelFrame(self.root, text="שלב 2: אפשרויות סריקה", padding="15")
        options_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.scan_by_hash = tk.BooleanVar(value=True)
        self.scan_by_name = tk.BooleanVar(value=True)
        self.min_similarity = tk.IntVar(value=85)
        
        # שורת אפשרויות
        options_row = ttk.Frame(options_frame)
        options_row.pack(fill=tk.X)
        
        ttk.Checkbutton(options_row, text="זיהוי קבצים זהים", 
                       variable=self.scan_by_hash).pack(side=tk.LEFT, padx=10)
        
        ttk.Checkbutton(options_row, text="זיהוי שמות דומים", 
                       variable=self.scan_by_name).pack(side=tk.LEFT, padx=10)
        
        ttk.Label(options_row, text="דמיון מינימלי:").pack(side=tk.LEFT, padx=(20, 5))
        ttk.Spinbox(options_row, from_=50, to=100, textvariable=self.min_similarity, 
                   width=6).pack(side=tk.LEFT)
        ttk.Label(options_row, text="%").pack(side=tk.LEFT, padx=(2, 0))
        
        ttk.Label(options_row, text="%").pack(side=tk.LEFT, padx=(2, 0))
        
        ttk.Separator(self.root, orient="horizontal").pack(fill=tk.X, pady=10)
        
        # שלב 3 - כפתורי פעולה
        button_frame = ttk.Frame(self.root, padding="10")
        button_frame.pack(fill=tk.X)
        
        self.scan_button = ttk.Button(button_frame, text="🔍 סרוק תיקייה", 
                                     command=self.start_scan)
        self.scan_button.pack(side=tk.LEFT, padx=10)
        
        self.delete_button = ttk.Button(button_frame, text="🗑️ מחק מסומנים", 
                                       command=self.delete_selected, state=tk.DISABLED)
        self.delete_button.pack(side=tk.LEFT, padx=10)
        
        self.help_button = ttk.Button(button_frame, text="❓ עזרה", 
                                     command=self.show_help)
        self.help_button.pack(side=tk.RIGHT, padx=10)
        
        ttk.Separator(self.root, orient="horizontal").pack(fill=tk.X, pady=5)
        
        # סטטוס
        status_frame = ttk.Frame(self.root, padding="5")
        status_frame.pack(fill=tk.X)
        
        self.status_label = ttk.Label(status_frame, text="מוכן לסריקה", 
                                     font=("Arial", 10))
        self.status_label.pack()
        
        # פס התקדמות
        self.progress = ttk.Progressbar(self.root, mode='indeterminate')
        self.progress.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        # תוצאות
        results_frame = ttk.LabelFrame(self.root, text="תוצאות", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(results_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Canvas עבור תוצאות
        self.results_canvas = tk.Canvas(results_frame, yscrollcommand=scrollbar.set, 
                                       highlightthickness=0)
        self.results_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.results_canvas.yview)
        
        # Frame פנימי לתוצאות
        self.results_inner_frame = ttk.Frame(self.results_canvas)
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
        
        self.results_inner_frame.bind("<Configure>", configure_scroll)
        self.results_canvas.bind("<Configure>", configure_scroll)
        
        # גלילה עם גלגלת העכבר
        def on_mousewheel(event):
            self.results_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        self.results_canvas.bind_all("<MouseWheel>", on_mousewheel)
    
    def browse_folder(self):
        """בחירת תיקייה"""
        folder = filedialog.askdirectory(title="בחר תיקייה לסריקה")
        if folder:
            self.selected_folder.set(folder)
    
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
        
        # השבתת כפתורים
        self.scan_button.config(state=tk.DISABLED)
        self.delete_button.config(state=tk.DISABLED)
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
            # דילוג על תיקיות מערכת
            dirs[:] = [d for d in dirs if not d.startswith('$') and d not in ['System Volume Information', 'Recycle.Bin']]
            
            for file in files:
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
        
        if duplicates:
            self.root.after(0, lambda: self.delete_button.config(state=tk.NORMAL))
    
    def find_by_hash(self, files):
        """מציאת קבצים זהים לפי Hash - מהיר ויעיל"""
        hash_map = defaultdict(list)
        total = len(files)
        
        for i, filepath in enumerate(files):
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
        
        # הצגת התוצאות
        for i, dup_group in enumerate(display_groups):
            if i % 5 == 0 and i > 0:
                self.root.update_idletasks()
            
            # כותרת קבוצה
            if dup_group['type'] == 'identical':
                group_title = f"קבוצה {i+1}: זהים"
            else:
                group_title = f"קבוצה {i+1}: דומים {dup_group['similarity']}%"
            
            group_frame = ttk.LabelFrame(self.results_inner_frame, 
                                        text=group_title, 
                                        padding="10")
            group_frame.pack(fill=tk.X, pady=5, padx=5)
            
            for filepath in dup_group['files']:
                file_frame = ttk.Frame(group_frame)
                file_frame.pack(fill=tk.X, pady=2)
                
                # Checkbox
                var = tk.IntVar(value=0)
                self.file_checkboxes[filepath] = var
                
                cb = ttk.Checkbutton(file_frame, variable=var, 
                                    onvalue=1, offvalue=0)
                cb.pack(side=tk.LEFT, padx=5)
                
                # מידע על הקובץ
                size = os.path.getsize(filepath)
                size_str = self.format_size(size)
                
                file_info = f"{filepath} ({size_str})"
                label = ttk.Label(file_frame, text=file_info, wraplength=650)
                label.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
                
                # כפתורים
                ttk.Button(file_frame, text="📄", width=3,
                          command=lambda p=filepath: self.open_file(p)).pack(side=tk.LEFT, padx=2)
                
                ttk.Button(file_frame, text="📁", width=3,
                          command=lambda p=filepath: self.open_folder(p)).pack(side=tk.LEFT, padx=2)
    
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
        
        # אם לא נשארו כפילויות, השבת את כפתור המחיקה
        if not self.duplicates:
            self.delete_button.config(state=tk.DISABLED)
    
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
                "content": "לחץ סרוק קבצים והמתן\n"
                         "הזמן משתנה לפי כמות הקבצים\n"
                         "תיקיות גדולות יכולות לקחת מספר דקות",
                "color": "#10b981",
                "bg": "#ecfdf5"
            },
            {
                "number": "4",
                "title": "בחירת קבצים",
                "icon": "✓",
                "content": "סמן את הקבצים שרוצה למחוק\n"
                         "לחץ 📄 כדי לפתוח ולבדוק את הקובץ\n"
                         "לחץ 📁 כדי לראות את המיקום",
                "color": "#f59e0b",
                "bg": "#fffbeb"
            },
            {
                "number": "5",
                "title": "מחיקה סופית",
                "icon": "🗑️",
                "content": "לחץ מחק קבצים מסומנים\n"
                         "המחיקה סופית - הקבצים לא עוברים לסל מיחזור\n"
                         "תקבל אישור לפני המחיקה",
                "color": "#ef4444",
                "bg": "#fef2f2"
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
