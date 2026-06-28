import customtkinter as ctk
import json
import os
import requests
from tkinter import messagebox
import webbrowser

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class LawsMemoApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("EasyNPA - Province RP")
        self.root.geometry("1520x900")
        self.root.minsize(1400, 800)
        self.root.attributes('-topmost', True)
        
        self.github_base = "https://raw.githubusercontent.com/ynikum228/easynpa/refs/heads/main/laws/"
        
        self.laws_data = {}
        self.current_main_tab = "Законы"
        self.current_sub_tab = "УК"
        self.notes_visible = {}
        
        self.create_ui()
        
        self.root.bind("<Alt_L>", self.toggle_main_window)
        self.open_settings()  # Настройки при запуске
    
    def try_load_from_github(self, category):
        """Загружает кодекс только когда нужно"""
        if category in self.laws_data:
            return True
        
        try:
            url = f"{self.github_base}{category}.json"
            response = requests.get(url, timeout=8)
            if response.status_code == 200:
                self.laws_data[category] = response.json()
                os.makedirs("laws", exist_ok=True)
                with open(f"laws/{category}.json", "w", encoding="utf-8") as f:
                    json.dump(self.laws_data[category], f, ensure_ascii=False, indent=2)
                return True
        except:
            pass
        return False
    
    def create_ui(self):
        top = ctk.CTkFrame(self.root, height=80, fg_color="#0a0a0a")
        top.pack(fill="x")
        top.pack_propagate(False)
        
        ctk.CTkLabel(top, text="EasyNPA", font=ctk.CTkFont(size=28, weight="bold")).pack(side="left", padx=30, pady=20)
        ctk.CTkLabel(top, text="Province RP", font=ctk.CTkFont(size=18), text_color="#94a3b8").pack(side="left", pady=20)
        
        self.search_var = ctk.StringVar()
        search = ctk.CTkEntry(top, placeholder_text="🔍 Поиск по законам...", 
                            textvariable=self.search_var, width=580, height=48, font=ctk.CTkFont(size=15))
        search.pack(side="left", padx=40)
        search.bind("<KeyRelease>", self.on_search)
        
        ctk.CTkButton(top, text="⚙ Настройки", width=130, height=48,
                     command=self.open_settings).pack(side="right", padx=8)
        
        ctk.CTkButton(top, text="🔄 Обновить", width=130, height=48,
                     command=self.update_all_from_github).pack(side="right", padx=8)
        
        # Главные вкладки
        main_tabs = ctk.CTkFrame(self.root, height=60, fg_color="#111111")
        main_tabs.pack(fill="x", pady=(5, 0))
        
        for text, tab in [("Законы", "Законы"), ("Док. МВД", "Док. МВД"), ("Правила", "Правила")]:
            btn = ctk.CTkButton(main_tabs, text=text, width=220, height=50,
                              fg_color="#3b82f6" if self.current_main_tab == tab else "#1f1f1f",
                              hover_color="#1e40af", font=ctk.CTkFont(size=16, weight="bold"),
                              command=lambda t=tab: self.switch_main_tab(t))
            btn.pack(side="left", padx=12, pady=8)
        
        self.sub_tab_frame = ctk.CTkFrame(self.root, height=55, fg_color="#161616")
        self.sub_tab_frame.pack(fill="x", pady=(0, 8))
        
        self.refresh_sub_tabs()
        
        self.scroll_frame = ctk.CTkScrollableFrame(self.root, fg_color="#0c0c0c")
        self.scroll_frame.pack(fill="both", expand=True, padx=15, pady=10)
        
        self.refresh_articles()
    
    def open_settings(self):
        win = ctk.CTkToplevel(self.root)
        win.title("Настройки EasyNPA")
        win.geometry("460x400")
        win.attributes('-topmost', True)
        
        ctk.CTkLabel(win, text="EasyNPA", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=15)
        ctk.CTkLabel(win, text="Настройки", font=ctk.CTkFont(size=18)).pack(pady=5)
        
        ctk.CTkLabel(win, text="Горячая клавиша:", font=ctk.CTkFont(size=14)).pack(pady=(20,5))
        ctk.CTkLabel(win, text="Alt + L", font=ctk.CTkFont(size=20, weight="bold"), text_color="#60a5fa").pack()
        
        ctk.CTkButton(win, text="Открыть мой VK", height=45,
                     command=lambda: webbrowser.open("https://vk.com/goidagirlz")).pack(pady=25)
        
        ctk.CTkButton(win, text="Закрыть", command=win.destroy).pack(pady=10)
    
    def toggle_main_window(self, event=None):
        if self.root.state() == "withdrawn":
            self.root.deiconify()
            self.root.lift()
        else:
            self.root.withdraw()
    
    def switch_main_tab(self, tab):
        self.current_main_tab = tab
        if tab == "Законы":
            self.current_sub_tab = "УК"
        elif tab == "Док. МВД":
            self.current_sub_tab = "ФЗоП"
        else:
            self.current_sub_tab = "ОПГО"
        self.refresh_sub_tabs()
        self.refresh_articles()
        self.scroll_to_top()
    
    def refresh_sub_tabs(self):
        for widget in self.sub_tab_frame.winfo_children():
            widget.destroy()
        
        if self.current_main_tab == "Законы":
            sub_tabs = ["УК", "КоАП", "ПДД"]
        elif self.current_main_tab == "Док. МВД":
            sub_tabs = ["ФЗоП", "Устав росгвардии", "Регламент УСБ"]
        else:
            sub_tabs = ["ОПГО", "ВПС"]
        
        for tab in sub_tabs:
            btn = ctk.CTkButton(self.sub_tab_frame, text=tab, width=170, height=40,
                              fg_color="#3b82f6" if tab == self.current_sub_tab else "#1f1f1f",
                              hover_color="#2563eb",
                              command=lambda t=tab: self.switch_sub_tab(t))
            btn.pack(side="left", padx=5, pady=8)
    
    def switch_sub_tab(self, tab):
        self.current_sub_tab = tab
        self.try_load_from_github(tab)
        self.refresh_sub_tabs()
        self.refresh_articles()
        self.scroll_to_top()
    
    def scroll_to_top(self):
        try:
            self.scroll_frame._parent_canvas.yview_moveto(0)
        except:
            pass
    
    def refresh_articles(self, query=""):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        
        query = query.lower()
        
        if self.current_sub_tab not in self.laws_data:
            ctk.CTkLabel(self.scroll_frame, text="Загрузка раздела...", 
                        font=ctk.CTkFont(size=16)).pack(pady=120)
            return
        
        for code, data in self.laws_data[self.current_sub_tab].items():
            full_text = f"{code} {data.get('title','')} {data.get('text','')}".lower()
            if query and query not in full_text:
                continue
            
            card = ctk.CTkFrame(self.scroll_frame, fg_color="#1a1a1a", corner_radius=10)
            card.pack(fill="x", pady=8, padx=12)
            
            code_frame = ctk.CTkFrame(card, fg_color="#252525", corner_radius=8)
            code_frame.pack(anchor="w", padx=20, pady=(16,8))
            ctk.CTkLabel(code_frame, text=code, font=ctk.CTkFont(size=16, weight="bold"), text_color="#e0f2fe").pack(padx=16, pady=8)
            
            ctk.CTkLabel(card, text=data.get('title', ''), font=ctk.CTkFont(size=17, weight="bold")).pack(anchor="w", padx=20, pady=(0,10))
            
            ctk.CTkLabel(card, text=data.get("text", ""), font=ctk.CTkFont(size=14), text_color="#cbd5e1", wraplength=1350, justify="left").pack(anchor="w", padx=20, pady=(0,16))
            
            if data.get("punishment"):
                pf = ctk.CTkFrame(card, fg_color="#450a0a", border_width=1, border_color="#f87171", corner_radius=8)
                pf.pack(fill="x", padx=20, pady=(0,16))
                ctk.CTkLabel(pf, text="⚠ Наказание", text_color="#fda4af", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=16, pady=(12,4))
                ctk.CTkLabel(pf, text=data["punishment"], text_color="#fecaca", font=ctk.CTkFont(size=14)).pack(anchor="w", padx=16, pady=(0,12))
            
            notes = data.get("notes", [])
            if notes:
                key = f"{self.current_sub_tab}_{code}"
                is_visible = self.notes_visible.get(key, False)
                btn_text = "▲ Скрыть примечания" if is_visible else "▼ Показать примечания"
                
                note_btn = ctk.CTkButton(card, text=btn_text, width=240, height=36, fg_color="#334155")
                note_btn.pack(anchor="w", padx=20, pady=(0,16))
                note_btn.configure(command=lambda k=key, b=note_btn, n=notes: self.toggle_notes(k, b, n))
                
                if is_visible:
                    nf = ctk.CTkFrame(card, fg_color="#1e2937", corner_radius=8)
                    nf.pack(fill="x", padx=20, pady=(0,16))
                    ctk.CTkLabel(nf, text="📝 Примечания", text_color="#bae6fd", font=ctk.CTkFont(size=13.5, weight="bold")).pack(anchor="w", padx=16, pady=(12,6))
                    for note in notes:
                        ctk.CTkLabel(nf, text=f"• {note}", text_color="#bae6fd", font=ctk.CTkFont(size=13.5), wraplength=1350, justify="left").pack(anchor="w", padx=16, pady=1)
    
    def toggle_notes(self, key, button, notes):
        self.notes_visible[key] = not self.notes_visible.get(key, False)
        self.refresh_articles(self.search_var.get())
    
    def on_search(self, event=None):
        self.refresh_articles(self.search_var.get())
        self.scroll_to_top()
    
    def copy_to_clipboard(self, text):
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        messagebox.showinfo("Готово", "Текст скопирован")
    
    def update_all_from_github(self):
        self.laws_data = {}  # Сброс кэша
        messagebox.showinfo("Обновление", "Обновляем все разделы...")
        # Перезагружаем все
        categories = ["УК", "КоАП", "ПДД", "ФЗоП", "Устав росгвардии", "Регламент УСБ", "ОПГО", "ВПС"]
        for cat in categories:
            self.try_load_from_github(cat)
        messagebox.showinfo("Готово", "База обновлена!")
        self.refresh_articles()
    
    def scroll_to_top(self):
        try:
            self.scroll_frame._parent_canvas.yview_moveto(0)
        except:
            pass

if __name__ == "__main__":
    app = LawsMemoApp()
    app.root.mainloop()