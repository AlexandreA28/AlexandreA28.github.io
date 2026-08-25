import os
import re
import base64
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk, filedialog, messagebox
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# ==============
# CRYPTOGRAPHIE
# ==============

def get_key_from_password(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=600_000,
    )
    return kdf.derive(password.encode('utf-8'))

def extract_flag(file_path: str):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        return None, f"\nErreur de lecture : {e}"

    if not lines:
        return None, "\nLe fichier est vide."

    for line in reversed(lines):
        line = line.strip()
        if not line:
            continue
        match = re.search(r'Flag\s*final[e]?\s*:\s*(.+)', line, re.IGNORECASE)
        if match:
            return match.group(1).strip(), None
    
    return None, ""

def encrypt_wu(file_path: str, flag: str):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().encode('utf-8')
    except Exception as e:
        return False, f"Erreur de lecture : {e}"

    salt = os.urandom(16)
    nonce = os.urandom(12)
    key = get_key_from_password(flag, salt)
    
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, content, None)

    out_file = file_path + ".enc"
    try:
        final_bytes = salt + nonce + ciphertext
        b64_data = base64.b64encode(final_bytes).decode('utf-8')

        with open(out_file, 'w') as f:
            f.write(b64_data)
        return True, f"Fichier chiffré avec succès !\nClé utilisée : {flag}"
    except Exception as e:
        return False, f"Erreur lors de la sauvegarde : {e}"

def decrypt_wu(file_path: str, flag: str):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            b64_data = f.read().strip()
        data = base64.b64decode(b64_data)
    except Exception as e:
        return False, f"Erreur de lecture ou de décodage Base64 : {e}"

    if len(data) < 28:
        return False, "Fichier corrompu ou invalide."

    salt = data[:16]
    nonce = data[16:28]
    ciphertext = data[28:]

    key = get_key_from_password(flag, salt)
    aesgcm = AESGCM(key)

    try:
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        
        # Logique de nommage
        if file_path.endswith('.enc'):
            base_path = file_path[:-4]
        else:
            base_path = file_path
            
        root, ext = os.path.splitext(base_path)
        out_file = f"{root}_DECRYPT{ext}"

        with open(out_file, 'wb') as f:
            f.write(plaintext)

        try:
            os.remove(file_path)
            msg_supp = ""
        except Exception as e:
            msg_supp = f"\n(Suppression du .enc impossible : {e})"

        return True, f"Déchiffrement réussi !\nSauvegardé sous : {os.path.basename(out_file)}{msg_supp}"
        
    except Exception:
        return False, "Échec du déchiffrement : Flag incorrect ou fichier corrompu."

def format_size(size_in_bytes):
    """Convertit la taille en octets vers un format lisible (Ko, Mo)."""
    if size_in_bytes < 1024:
        return f"1 Ko"
    elif size_in_bytes < 1024 ** 2:
        return f"{size_in_bytes / 1024:.1f} Ko"
    elif size_in_bytes < 1024 ** 3:
        return f"{size_in_bytes / (1024 ** 2):.1f} Mo"
    else:
        return f"{size_in_bytes / (1024 ** 3):.1f} Go"

# ====================
# INTERFACE GRAPHIQUE
# ====================

class WUApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Write-Up Encryptor")
        
        try:
            self.state('zoomed')
        except tk.TclError:
            self.attributes('-zoomed', True)

        self.current_dir = os.path.abspath(os.path.dirname(__file__))

        default_font = tkfont.nametofont("TkDefaultFont")
        default_font.configure(size=14)
        
        text_font = tkfont.nametofont("TkTextFont")
        text_font.configure(size=14)
        
        heading_font = tkfont.nametofont("TkHeadingFont")
        heading_font.configure(size=16, weight="bold")

        style = ttk.Style(self)
        style.theme_use('clam')
        
        style.configure("Treeview", font=("TkDefaultFont", 14), rowheight=30)
        style.configure("Treeview.Heading", font=("TkHeadingFont", 16, "bold"))

        top_frame = ttk.Frame(self, padding=10)
        top_frame.pack(fill=tk.X)

        self.btn_browse = ttk.Button(top_frame, text="Choisir le dossier racine", command=self.browse_folder)
        self.btn_browse.pack(side=tk.LEFT, padx=5)

        self.btn_up = ttk.Button(top_frame, text="↑ Dossier parent", command=self.go_up)
        self.btn_up.pack(side=tk.LEFT, padx=5)

        self.lbl_dir = ttk.Label(top_frame, text=self.current_dir, foreground="gray")
        self.lbl_dir.pack(side=tk.LEFT, padx=10)

        mode_frame = ttk.Frame(self, padding=10)
        mode_frame.pack(fill=tk.X)
        
        self.mode_var = tk.StringVar(value="enc")
        
        self.btn_mode_enc = tk.Button(mode_frame, text="▶ Chiffrement", 
                                      font=("TkDefaultFont", 14, "bold"), bg="#4CAF50", fg="white", 
                                      command=lambda: self.change_mode("enc"), relief=tk.FLAT, cursor="hand2", 
                                      width=42)
        self.btn_mode_enc.pack(side=tk.LEFT, padx=10, ipady=8)

        self.btn_mode_dec = tk.Button(mode_frame, text="Déchiffrement (.enc)", 
                                      font=("TkDefaultFont", 14, "bold"), bg="#e0e0e0", fg="black", 
                                      command=lambda: self.change_mode("dec"), relief=tk.FLAT, cursor="hand2", 
                                      width=42)
        self.btn_mode_dec.pack(side=tk.LEFT, padx=10, ipady=8)

        list_frame = ttk.Frame(self, padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("Nom", "Type", "Taille")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        self.tree.heading("Nom", text="Nom du fichier / dossier")
        self.tree.heading("Type", text="Type")
        self.tree.heading("Taille", text="Taille")
        
        self.tree.column("Nom", width=850)
        self.tree.column("Type", width=120, anchor=tk.CENTER)
        self.tree.column("Taille", width=120, anchor=tk.E)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.tag_configure("folder", background="lightyellow")
        self.tree.bind("<Double-1>", self.on_double_click)

        bottom_frame = ttk.Frame(self, padding=10)
        bottom_frame.pack(fill=tk.X)

        self.btn_action = ttk.Button(bottom_frame, text="Traiter le fichier sélectionné")
        self.btn_action.configure(command=self.process_file)
        self.btn_action.pack(pady=10, ipadx=20, ipady=5)

        self.refresh_list()
    
    def change_mode(self, mode):
        self.mode_var.set(mode)
        
        if mode == "enc":
            self.btn_mode_enc.config(bg="#4CAF50", fg="white", text="▶ Chiffrement")
            self.btn_mode_dec.config(bg="#e0e0e0", fg="black", text="Déchiffrement (.enc)")
        else:
            # Le bouton chiffrement devient inactif (Gris)
            self.btn_mode_enc.config(bg="#e0e0e0", fg="black", text="Chiffrement")
            # Le bouton déchiffrement devient actif (Bleu)
            self.btn_mode_dec.config(bg="#2196F3", fg="white", text="▶ Déchiffrement (.enc)")
        # On met à jour l'affichage des fichiers
        self.refresh_list()

    def browse_folder(self):
        folder = filedialog.askdirectory(title="Sélectionner le dossier racine")
        if folder:
            self.current_dir = folder
            self.refresh_list()

    def go_up(self):
        if not self.current_dir:
            return
        parent = os.path.dirname(self.current_dir)
        if parent and parent != self.current_dir:
            self.current_dir = parent
            self.refresh_list()

    def refresh_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        if not self.current_dir or not os.path.isdir(self.current_dir):
            return

        self.lbl_dir.config(text=self.current_dir)
        mode = self.mode_var.get()
        
        try:
            entries = list(os.scandir(self.current_dir))
        except PermissionError:
            self.ask_custom_dialog("Erreur", f"Accès refusé au dossier :\n{self.current_dir}", show_entry=False)
            self.go_up()
            return

        entries.sort(key=lambda e: (not e.is_dir(), e.name.lower()))

        for entry in entries:
            if entry.is_dir():
                self.tree.insert("", tk.END, values=(f"📁 {entry.name}", "FILE", "-"), tags=("folder", entry.path))
            elif entry.is_file():
                if mode == "enc":
                    if entry.name.endswith(".enc") or "_DECRYPT" in entry.name:
                        continue
                elif mode == "dec":
                    if not entry.name.endswith(".enc"):
                        continue
                
                stat = entry.stat()
                size_str = format_size(stat.st_size)
                
                _, ext = os.path.splitext(entry.name)
                if ext:
                    ext = ext.lstrip('.').upper()
                else:
                    ext = "-"
                self.tree.insert("", tk.END, values=(f"📄 {entry.name}", ext, size_str), tags=("file", entry.path))

    def on_double_click(self, event):
        selected = self.tree.selection()
        if not selected:
            return
            
        item = selected[0]
        tags = self.tree.item(item, "tags")
        
        if tags:
            if tags[0] == "folder":
                self.current_dir = tags[1]
                self.refresh_list()
            elif tags[0] == "file":
                self.process_file()
    
    def ask_custom_dialog(self, title, message, initial_value="", show_cancel=False, show_entry=True):
        top = tk.Toplevel(self)
        top.title(title)
        top.transient(self)
        top.grab_set()
        top.focus_force()

        result = [None] 

        frame = ttk.Frame(top, padding=15)
        frame.pack(fill=tk.BOTH, expand=True)

        alignement = tk.CENTER if not show_entry else tk.W
        ttk.Label(frame, text=message, justify=tk.CENTER if not show_entry else tk.LEFT).pack(anchor=alignement, pady=(0, 5))
        
        if show_entry:
            entry = ttk.Entry(frame, width=50)
            entry.insert(0, initial_value)
            entry.pack(fill=tk.X, pady=5)
            entry.focus_set()
            entry.select_range(0, tk.END)

        def on_ok(event=None):
            if show_entry:
                result[0] = entry.get()
            else:
                result[0] = True
            top.destroy()
            
        def on_cancel(event=None):
            result[0] = None
            top.destroy()

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=(15, 0))

        btn_ok = ttk.Button(btn_frame, text="OK", command=on_ok)
        btn_ok.pack(side=tk.LEFT, padx=5)
        
        if not show_entry:
            btn_ok.focus_set()

        if show_cancel:
            btn_cancel = ttk.Button(btn_frame, text="Annuler", command=on_cancel)
            btn_cancel.pack(side=tk.LEFT, padx=5)
            top.bind('<Escape>', on_cancel)

        top.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - (top.winfo_reqwidth() // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (top.winfo_reqheight() // 2)
        top.geometry(f"+{x}+{y}")
        top.resizable(False, False)
        
        top.bind('<Return>', on_ok)
        
        self.wait_window(top)
        return result[0]

    def process_file(self):
        selected_item = self.tree.selection()
        if not selected_item:
            self.ask_custom_dialog("Attention", "Veuillez sélectionner un fichier.", show_entry=False)
            return

        tags = self.tree.item(selected_item[0], "tags")
        
        if tags and tags[0] == "folder":
            self.ask_custom_dialog("Information", "Ceci est un dossier.\nDouble-cliquez dessus pour l'ouvrir.", show_entry=False)
            return

        full_path = tags[1]
        mode = self.mode_var.get()

        if mode == "enc":
            extracted_flag, error_msg = extract_flag(full_path)
            
            if extracted_flag:
                prompt_text = "Flag détecté automatiquement !\nValidez ou modifiez la clé de chiffrement :"
                initial_val = extracted_flag
            else:
                prompt_text = f"Aucun flag trouvé automatiquement.{error_msg}\nVeuillez entrer la clé de chiffrement :"
                initial_val = ""

            final_flag = self.ask_custom_dialog("Clé de chiffrement", prompt_text, initial_value=initial_val, show_cancel=True)
            
            if final_flag:
                clean_flag = final_flag.strip()
                success, msg = encrypt_wu(full_path, clean_flag)
                if success:
                    # Ici on garde show_entry=True pour pouvoir copier la clé
                    self.ask_custom_dialog("Succès", "Fichier chiffré avec succès !\nClé utilisée :", initial_value=clean_flag)
                    self.refresh_list()
                else:
                    self.ask_custom_dialog("Erreur de chiffrement", msg, show_entry=False)
                
        elif mode == "dec":
            flag = self.ask_custom_dialog("Mot de passe", "Entrez le flag pour déchiffrer ce Write-Up :", show_cancel=True)
            if flag:
                success, msg = decrypt_wu(full_path, flag.strip())
                if success:
                    self.ask_custom_dialog("Succès", msg, show_entry=False)
                    self.refresh_list()
                else:
                    self.ask_custom_dialog("Erreur de déchiffrement", msg, show_entry=False)

if __name__ == "__main__":
    app = WUApp()
    app.mainloop()