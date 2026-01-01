#!/usr/bin/env python3
"""
Photo Organizer - GUI Version
Renomme photos par date EXIF avec interface graphique
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image
import os
import json
from datetime import datetime
import threading

class PhotoOrganizerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("📸 EXIF Batch Renamer - DigitalCraft")
        self.root.geometry("600x700")
        self.root.configure(bg='#2c3e50')
        
        self.dossier = None
        self.photos = []
        
        self.create_widgets()
    
    def create_widgets(self):
        # Header
        header = tk.Label(
            self.root,
            text="📸 EXIF Batch Renamer",
            font=("Arial", 20, "bold"),
            bg='#2c3e50',
            fg='white'
        )
        header.pack(pady=20)
        
        # Frame principal
        main_frame = tk.Frame(self.root, bg='#34495e', padx=20, pady=20)
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Sélection dossier
        tk.Label(
            main_frame,
            text="Dossier photos:",
            font=("Arial", 12),
            bg='#34495e',
            fg='white'
        ).pack(anchor='w', pady=(0,5))
        
        folder_frame = tk.Frame(main_frame, bg='#34495e')
        folder_frame.pack(fill='x', pady=(0,15))
        
        self.folder_entry = tk.Entry(
            folder_frame,
            font=("Arial", 10),
            bg='white',
            fg='black'
        )
        self.folder_entry.pack(side='left', fill='x', expand=True, padx=(0,10))
        
        tk.Button(
            folder_frame,
            text="📁 Parcourir",
            command=self.select_folder,
            bg='#3498db',
            fg='white',
            font=("Arial", 10, "bold"),
            padx=15,
            pady=5,
            cursor='hand2'
        ).pack(side='right')
        
        # Options
        tk.Label(
            main_frame,
            text="Format nom:",
            font=("Arial", 12),
            bg='#34495e',
            fg='white'
        ).pack(anchor='w', pady=(0,5))
        
        self.format_var = tk.StringVar(value="YYYY-MM-DD_HH-MM-SS")
        formats = [
            "YYYY-MM-DD_HH-MM-SS",
            "YYYYMMDD_HHMMSS",
            "YYYY-MM-DD"
        ]
        
        for fmt in formats:
            tk.Radiobutton(
                main_frame,
                text=fmt,
                variable=self.format_var,
                value=fmt,
                bg='#34495e',
                fg='white',
                selectcolor='#2c3e50',
                font=("Arial", 10)
            ).pack(anchor='w')
        
        # Préfixe
        prefix_frame = tk.Frame(main_frame, bg='#34495e')
        prefix_frame.pack(fill='x', pady=(15,0))
        
        tk.Label(
            prefix_frame,
            text="Préfixe (optionnel):",
            font=("Arial", 12),
            bg='#34495e',
            fg='white'
        ).pack(side='left')
        
        self.prefix_entry = tk.Entry(
            prefix_frame,
            font=("Arial", 10),
            bg='white',
            width=20
        )
        self.prefix_entry.pack(side='left', padx=(10,0))

        # SUFFIX :
        tk.Label(
            prefix_frame,
            text="Suffixe (optionnel):",
            font=("Arial", 12),
            bg='#34495e',
            fg='white'
        ).pack(side='left', padx=(20,0))
        
        self.suffix_entry = tk.Entry(
            prefix_frame,
            font=("Arial", 10),
            bg='white',
            width=20
        )
        self.suffix_entry.pack(side='left', padx=(10,0))
        
        # Checkboxes
        self.backup_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            main_frame,
            text="☑ Créer backup automatique",
            variable=self.backup_var,
            bg='#34495e',
            fg='white',
            selectcolor='#2c3e50',
            font=("Arial", 10)
        ).pack(anchor='w', pady=(15,5))
        
        
        
        # Progress bar
        self.progress = ttk.Progressbar(
            main_frame,
            mode='determinate',
            length=500
        )
        self.progress.pack(fill='x', pady=(20,5))
        
        self.progress_label = tk.Label(
            main_frame,
            text="0/0 photos traitées",
            font=("Arial", 10),
            bg='#34495e',
            fg='white'
        )
        self.progress_label.pack()
        
        # Bouton principal
        self.process_btn = tk.Button(
            self.root,
            text="🚀 RENOMMER LES PHOTOS",
            command=self.process_photos,
            bg='#27ae60',
            fg='white',
            font=("Arial", 14, "bold"),
            padx=30,
            pady=15,
            cursor='hand2'
        )
        self.process_btn.pack(pady=20)
        
        # Footer
        tk.Label(
            self.root,
            text="by DigitalCraft",
            font=("Arial", 8),
            bg='#2c3e50',
            fg='#7f8c8d'
        ).pack(side='bottom', pady=10)
    
    def select_folder(self):
        folder = filedialog.askdirectory(title="Sélectionner dossier photos")
        if folder:
            self.dossier = folder
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, folder)
            self.scan_photos()
    
    def scan_photos(self):
        if not self.dossier:
            return
        
        self.photos = []
        for f in os.listdir(self.dossier):
            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.heic', '.heif', '.webp')):
                self.photos.append(f)
        
        self.progress_label.config(text=f"0/{len(self.photos)} photos trouvées")
    
    def get_exif_date(self, filepath):
        try:
            img = Image.open(filepath)
            exif = img._getexif()
            if exif:
                date_str = exif.get(36867) or exif.get(306)
                if date_str:
                    return datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
        except:
            pass
        return None
    
    def format_filename(self, date, prefix="", suffix=""):
        fmt = self.format_var.get()
        
        if fmt == "YYYY-MM-DD_HH-MM-SS":
            name = date.strftime('%Y-%m-%d_%H-%M-%S')
        elif fmt == "YYYYMMDD_HHMMSS":
            name = date.strftime('%Y%m%d_%H%M%S')
        else:  # YYYY-MM-DD
            name = date.strftime('%Y-%m-%d')
        
        # Prefix et/ou suffix
        if prefix and suffix:
            name = f"{prefix}_{name}_{suffix}"
        elif prefix:
            name = f"{prefix}_{name}"
        elif suffix:
            name = f"{name}_{suffix}"
        
        return name
    
    def show_preview(self, changements):
        """Affiche fenêtre preview des changements"""
        preview_window = tk.Toplevel(self.root)
        preview_window.title("Preview Renommages")
        preview_window.geometry("500x600")
        preview_window.configure(bg='#2c3e50')
        
        # Header avec logo
        header_frame = tk.Frame(self.root, bg='#2c3e50')
        header_frame.pack(pady=15)
        
        try:
            from PIL import Image, ImageTk
            import os
            
            # Logo dans Téléchargements (permanent)
            logo_path = os.path.expanduser("~/Téléchargements/logo_dc_100.png")
            
            logo_img = Image.open(logo_path)
            logo_img = logo_img.resize((40, 40))
            logo_photo = ImageTk.PhotoImage(logo_img)
            
            logo_label = tk.Label(header_frame, image=logo_photo, bg='#2c3e50')
            logo_label.image = logo_photo
            logo_label.pack(side='left', padx=10)
        except Exception as e:
            print(f"⚠️ Logo non chargé: {e}")
        
        # Titre
        tk.Label(
            header_frame,
            text="EXIF Batch Renamer",
            font=("Arial", 18, "bold"),
            bg='#2c3e50',
            fg='white'
        ).pack(side='left', padx=5)
        
        # Badge DC
        tk.Label(
            header_frame,
            text="DC",
            font=("Arial", 10, "bold"),
            bg='#3498db',
            fg='white',
            padx=5,
            pady=2
        ).pack(side='left', padx=5)
        
        # Scrollbar + Text
        frame = tk.Frame(preview_window, bg='#34495e')
        frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side='right', fill='y')
        
        text = tk.Text(
            frame,
            font=("Courier", 9),
            bg='white',
            fg='black',
            yscrollcommand=scrollbar.set
        )
        text.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=text.yview)
        
        # Contenu
        for ancien, nouveau in changements:
            text.insert('end', f"✓ {ancien}\n", 'ancien')
            text.insert('end', f"  → {nouveau}\n\n", 'nouveau')
        
        text.tag_config('ancien', foreground='#e74c3c')
        text.tag_config('nouveau', foreground='#27ae60')
        text.config(state='disabled')
        
        # Frame boutons
        btn_frame = tk.Frame(preview_window, bg='#2c3e50')
        btn_frame.pack(pady=15)
        
        # Bouton Annuler
        tk.Button(
            btn_frame,
            text="❌ Annuler",
            command=preview_window.destroy,
            bg='#95a5a6',
            fg='white',
            font=("Arial", 11, "bold"),
            padx=25,
            pady=8
        ).pack(side='left', padx=10)
        
        # Bouton Renommer
        def confirm_rename():
            preview_window.destroy()
            self.execute_rename()
        
        tk.Button(
            btn_frame,
            text="🚀 Renommer maintenant",
            command=confirm_rename,
            bg='#27ae60',
            fg='white',
            font=("Arial", 11, "bold"),
            padx=25,
            pady=8
        ).pack(side='left', padx=10)

    def execute_rename(self):
        """Exécute renommage réel après confirmation preview"""
        # Change variable pour renommage réel
        self.preview_mode = False
        thread = threading.Thread(target=self.rename_photos_real)
        thread.start()

    def rename_photos_real(self):
        """Renommage réel sans preview"""
        self.process_btn.config(state='disabled')
        prefix = self.prefix_entry.get()
        suffix = self.suffix_entry.get()
        changements = []
        reussis = 0
    
        self.progress['maximum'] = len(self.photos)
    
        for i, photo in enumerate(self.photos):
            filepath = os.path.join(self.dossier, photo)
            date = self.get_exif_date(filepath)
        
            if date:
                ext = os.path.splitext(photo)[1]
                nouveau_nom = self.format_filename(date, prefix, suffix) + ext
                nouveau_path = os.path.join(self.dossier, nouveau_nom)
            
                # Éviter écrasement
                counter = 1
                while os.path.exists(nouveau_path) and nouveau_path != filepath:
                    nouveau_nom = self.format_filename(date, prefix, suffix) + f"_{counter}{ext}"
                    nouveau_path = os.path.join(self.dossier, nouveau_nom)
                    counter += 1
            
                # RENOMMAGE RÉEL
                if filepath != nouveau_path:
                    os.rename(filepath, nouveau_path)
                    changements.append([photo, nouveau_nom])
                    reussis += 1
        
            # Update progress
            self.progress['value'] = i + 1
            self.progress_label.config(text=f"{i+1}/{len(self.photos)} photos traitées")
            self.root.update_idletasks()
    
        # Backup
        if self.backup_var.get() and changements:
            backup_file = os.path.join(
                self.dossier,
                f".backup_renommage_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            with open(backup_file, 'w') as f:
                json.dump({
                    'date': datetime.now().isoformat(),
                    'changements': changements
                }, f, indent=2)
    
        # Résultat
        messagebox.showinfo(
            "Terminé!",
            f"{reussis}/{len(self.photos)} photos renommées avec succès!"
        )
    
        self.process_btn.config(state='normal')
        self.progress['value'] = 0
        self.scan_photos()
    
    def process_photos(self):
        if not self.dossier:
            messagebox.showerror("Erreur", "Sélectionnez un dossier d'abord!")
            return
        
        if not self.photos:
            messagebox.showwarning("Attention", "Aucune photo trouvée!")
            return
        
        
        # Lancer traitement dans thread séparé
        thread = threading.Thread(target=self.rename_photos)
        thread.start()
    
    def rename_photos(self):
        self.process_btn.config(state='disabled')
        prefix = self.prefix_entry.get()
        suffix = self.suffix_entry.get()
        changements = []
        reussis = 0

        # Force preview mode
        preview_mode = True  # AJOUTE CETTE LIGNE
        
        self.progress['maximum'] = len(self.photos)
        
        for i, photo in enumerate(self.photos):
            filepath = os.path.join(self.dossier, photo)
            date = self.get_exif_date(filepath)
            
            if date:
                ext = os.path.splitext(photo)[1]
                nouveau_nom = self.format_filename(date, prefix, suffix) + ext
                nouveau_path = os.path.join(self.dossier, nouveau_nom)
                
                # Éviter écrasement
                counter = 1
                while os.path.exists(nouveau_path) and nouveau_path != filepath:
                    nouveau_nom = self.format_filename(date, prefix, suffix) + f"_{counter}{ext}"
                    nouveau_path = os.path.join(self.dossier, nouveau_nom)
                    counter += 1
                
                if not preview_mode and filepath != nouveau_path:
                    os.rename(filepath, nouveau_path)
                    changements.append([photo, nouveau_nom])
                    reussis += 1
                elif preview_mode:
                    changements.append([photo, nouveau_nom])
                    reussis += 1
            
            # Update progress
            self.progress['value'] = i + 1
            self.progress_label.config(text=f"{i+1}/{len(self.photos)} photos traitées")
            self.root.update_idletasks()
        
        # Backup (TOUJOURS si checkbox cochée)
        if self.backup_var.get() and changements:
            backup_file = os.path.join(
                self.dossier,
                f".backup_renommage_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            with open(backup_file, 'w') as f:
                json.dump({
                    'date': datetime.now().isoformat(),
                    'changements': changements
                }, f, indent=2)
        
        # Résultat: TOUJOURS preview
        if changements:
            self.show_preview(changements)
        else:
            messagebox.showinfo("Information", "Aucune photo à renommer")
        
        self.process_btn.config(state='normal')
        self.progress['value'] = 0
        self.scan_photos()

if __name__ == "__main__":
    root = tk.Tk()
    app = PhotoOrganizerGUI(root)
    root.mainloop()