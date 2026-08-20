import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
import shutil
import os
import json
import sys
import math

try:
    from PIL import Image, ImageTk, ImageDraw, ImageOps
except ImportError:
    import tkinter.messagebox as messagebox
    messagebox.showerror("Errore", "Manca la libreria Pillow.")
    sys.exit()

# --- PALETTE COLORI LMU ---
BG_MAIN = "#191C21"
BG_HEADER = "#0A111A"
BG_CARD = "#212732"
ACCENT_GOLD = "#F5A623"
ACCENT_RED = "#E60028"
ACCENT_CYAN = "#00C3E3"
TEXT_WHITE = "#FFFFFF"
TEXT_GREY = "#9CA3AF"

# --- LOGICA DI ESTRAZIONE AL PRIMO AVVIO ---
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
    BUNDLE_DIR = sys._MEIPASS 
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    BUNDLE_DIR = BASE_DIR

CONFIG_FILE = os.path.join(BASE_DIR, "lmu_config.json")
DB_IMG_DIR = os.path.join(BASE_DIR, "database_volanti")
DEFAULT_IMG_NAME = os.path.join(DB_IMG_DIR, "Logo_QuickSwitch.png")

def estrai_risorse_iniziali():
    internal_db = os.path.join(BUNDLE_DIR, "database_volanti")
    if os.path.exists(internal_db) and not os.path.exists(DB_IMG_DIR):
        try:
            shutil.copytree(internal_db, DB_IMG_DIR)
        except Exception:
            pass

if getattr(sys, 'frozen', False):
    estrai_risorse_iniziali()

selected_preset_file = None  
cards_frames = []
current_page = 0  # Variabile globale per l'impaginazione

# --- NUOVA GESTIONE METADATI ---
def sanitize_name(name):
    return "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).strip()

def get_meta_path(cartella_preset):
    return os.path.join(cartella_preset, "quickswitch_meta.json")

def load_meta(cartella_preset):
    p = get_meta_path(cartella_preset)
    if os.path.exists(p):
        try:
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_meta(cartella_preset, data):
    p = get_meta_path(cartella_preset)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# --- POP-UP SEMPLIFICATO PER L'IMPORTAZIONE ---
def ask_preset_data(parent):
    dialog = tk.Toplevel(parent)
    dialog.title("Nuovo Preset")
    dialog.geometry("400x260")
    dialog.configure(bg=BG_CARD)
    dialog.resizable(False, False)
    
    dialog.transient(parent)
    dialog.grab_set()
    
    dialog.update_idletasks()
    x = parent.winfo_x() + (parent.winfo_width() // 2) - 200
    y = parent.winfo_y() + (parent.winfo_height() // 2) - 130
    dialog.geometry(f"+{x}+{y}")

    result = {"preset": None, "immagine": None}

    tk.Label(dialog, text="Nome del preset (es. Setup Endurance):", bg=BG_CARD, fg=TEXT_GREY, font=("Segoe UI", 9, "bold")).pack(pady=(20, 5), anchor="w", padx=30)
    entry_preset = tk.Entry(dialog, width=40, bg=BG_MAIN, fg=TEXT_WHITE, insertbackground=TEXT_WHITE, relief="flat", font=("Segoe UI", 10))
    entry_preset.pack(padx=30, ipady=5)

    def scegli_immagine():
        file_img = filedialog.askopenfilename(title="Seleziona immagine", filetypes=[("Immagini", "*.png;*.jpg;*.jpeg")], initialdir=DB_IMG_DIR, parent=dialog)
        if file_img:
            result["immagine"] = file_img
            btn_img.config(text="✅ IMMAGINE PRONTA", bg="#28A745", fg=TEXT_WHITE)

    btn_img = tk.Button(dialog, text="🖼️ ASSOCIA IMMAGINE (Opzionale)", bg="#404040", fg=TEXT_WHITE, command=scegli_immagine, relief="flat", font=("Segoe UI", 9, "bold"))
    btn_img.pack(pady=20, fill="x", padx=30, ipady=5)

    def on_ok():
        result["preset"] = entry_preset.get().strip()
        dialog.destroy()

    btn_frame = tk.Frame(dialog, bg=BG_CARD)
    btn_frame.pack(pady=5)
    
    tk.Button(btn_frame, text="SALVA", bg=ACCENT_CYAN, fg=TEXT_WHITE, command=on_ok, relief="flat", width=12, font=("Segoe UI", 9, "bold")).pack(side="left", padx=10)
    tk.Button(btn_frame, text="ANNULLA", bg="#555555", fg=TEXT_WHITE, command=dialog.destroy, relief="flat", width=12, font=("Segoe UI", 9, "bold")).pack(side="left", padx=10)

    dialog.wait_window(dialog)
    return result["preset"], result["immagine"]

# --- FUNZIONI CORE ---
def carica_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f).get("lmu_path", "")
        except Exception:
            pass
    return ""

def salva_config(path):
    data = {}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
        except Exception:
            pass
    data["lmu_path"] = path
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f)

def carica_ultimo_caricato():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f).get("last_loaded", "")
        except Exception:
            pass
    return ""

def salva_ultimo_caricato(nome_preset):
    data = {}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
        except Exception:
            pass
    data["last_loaded"] = nome_preset
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f)

def imposta_cartella():
    cartella_radice = filedialog.askdirectory(title="Seleziona la cartella principale di Le Mans Ultimate", parent=app)
    if cartella_radice:
        cartella_player = os.path.join(cartella_radice, "UserData", "player")
        if not os.path.exists(cartella_player):
            lbl_stato.config(text="Cartella errata!", fg=ACCENT_RED)
            return
            
        salva_config(cartella_radice)
        lbl_percorso.config(text=f"...\\UserData\\player")
        os.makedirs(os.path.join(cartella_player, "preset_volanti"), exist_ok=True)
        aggiorna_griglia()
        lbl_stato.config(text="PERCORSO CONFIGURATO", fg=ACCENT_CYAN)

def importa_preset():
    cartella_radice = carica_config()
    if not cartella_radice:
        lbl_stato.config(text="IMPOSTA LA CARTELLA LMU!", fg=ACCENT_RED)
        return
        
    cartella_player = os.path.join(cartella_radice, "UserData", "player")
    cartella_preset = os.path.join(cartella_player, "preset_volanti")
    os.makedirs(cartella_preset, exist_ok=True)
    
    file_esterno = filedialog.askopenfilename(title="Seleziona JSON", filetypes=[("JSON", "*.json")], parent=app)
    if file_esterno:
        nome_preset, percorso_immagine = ask_preset_data(app)
        
        if not nome_preset: 
            return
        
        if not nome_preset.endswith(".json"):
            nome_preset += ".json"
            
        destinazione = os.path.join(cartella_preset, nome_preset)
        shutil.copy2(file_esterno, destinazione)
        
        nome_base = nome_preset.replace(".json", "")
        
        if percorso_immagine:
            nome_file_img = f"{nome_base}.png"
            destinazione_preset_img = os.path.join(cartella_preset, nome_file_img)
            destinazione_db_img = os.path.join(DB_IMG_DIR, nome_file_img)
            
            try:
                img = Image.open(percorso_immagine).convert("RGBA")
                # Forza rapporto 16:9
                img_16_9 = ImageOps.fit(img, (256, 144), method=Image.Resampling.LANCZOS)
                img_16_9.save(destinazione_preset_img, format="PNG")
                
                os.makedirs(DB_IMG_DIR, exist_ok=True)
                img_16_9.save(destinazione_db_img, format="PNG")
            except Exception:
                pass

        meta = load_meta(cartella_preset)
        meta[nome_preset] = "Preset Personalizzato"
        save_meta(cartella_preset, meta)
        
        aggiorna_griglia()
        lbl_stato.config(text=f"PRESET IMPORTATO!", fg=ACCENT_GOLD)

def applica_preset():
    global selected_preset_file
    cartella_radice = carica_config()
    if not cartella_radice:
        lbl_stato.config(text="ERRORE CARTELLA LMU", fg=ACCENT_RED)
        return
        
    if not selected_preset_file:
        lbl_stato.config(text="SELEZIONA UN PRESET", fg=ACCENT_RED)
        return
    
    cartella_player = os.path.join(cartella_radice, "UserData", "player")
    origine = os.path.join(cartella_player, "preset_volanti", selected_preset_file)
    destinazione = os.path.join(cartella_player, "direct input.json")
    
    try:
        if os.path.exists(destinazione):
            os.remove(destinazione)
        shutil.copyfile(origine, destinazione)
        salva_ultimo_caricato(selected_preset_file)
        lbl_stato.config(text=f"SETUP VOLANTE ATTIVO IN LMU!", fg="#28A745")
        aggiorna_griglia()
    except Exception as e:
        lbl_stato.config(text="ERRORE SOSTITUZIONE.", fg=ACCENT_RED)

def cambia_immagine_da_icona(nome_json):
    cartella_radice = carica_config()
    cartella_preset = os.path.join(cartella_radice, "UserData", "player", "preset_volanti")
    file_immagine = filedialog.askopenfilename(title="Seleziona immagine", filetypes=[("Immagini", "*.png;*.jpg;*.jpeg")], initialdir=DB_IMG_DIR, parent=app)
    
    if file_immagine:
        nome_base = nome_json.replace(".json", "")
        nome_file_img = f"{nome_base}.png"
        destinazione_preset = os.path.join(cartella_preset, nome_file_img)
        destinazione_db = os.path.join(DB_IMG_DIR, nome_file_img)
        
        try:
            img = Image.open(file_immagine).convert("RGBA")
            # Forza rapporto 16:9
            img_16_9 = ImageOps.fit(img, (256, 144), method=Image.Resampling.LANCZOS)
            img_16_9.save(destinazione_preset, format="PNG")
            
            os.makedirs(DB_IMG_DIR, exist_ok=True)
            img_16_9.save(destinazione_db, format="PNG")
            
            aggiorna_griglia() 
        except Exception:
            pass

def rinomina_preset(nome_json):
    cartella_radice = carica_config()
    cartella_preset = os.path.join(cartella_radice, "UserData", "player", "preset_volanti")
    vecchio_nome_base = nome_json.replace(".json", "")
    
    nuovo_nome = simpledialog.askstring("Rinomina Preset", f"Inserisci il nuovo nome:", initialvalue=vecchio_nome_base, parent=app)
    
    if nuovo_nome and nuovo_nome != vecchio_nome_base:
        if not nuovo_nome.endswith(".json"): nuovo_nome += ".json"
        vecchio_percorso = os.path.join(cartella_preset, nome_json)
        nuovo_percorso = os.path.join(cartella_preset, nuovo_nome)
        
        if os.path.exists(nuovo_percorso):
            messagebox.showerror("Errore", "Nome già in uso!", parent=app)
            return
            
        os.rename(vecchio_percorso, nuovo_percorso)
        
        img_vecchia = os.path.join(cartella_preset, f"{vecchio_nome_base}.png")
        if os.path.exists(img_vecchia):
            os.rename(img_vecchia, os.path.join(cartella_preset, f"{nuovo_nome.replace('.json', '')}.png"))
            
        meta = load_meta(cartella_preset)
        if nome_json in meta:
            meta[nuovo_nome] = meta.pop(nome_json)
            save_meta(cartella_preset, meta)
            
        aggiorna_griglia()

def elimina_preset(nome_json):
    cartella_radice = carica_config()
    cartella_preset = os.path.join(cartella_radice, "UserData", "player", "preset_volanti")
    
    risposta = messagebox.askyesno("Conferma", f"Eliminare '{nome_json}'?", parent=app)
    if risposta:
        os.remove(os.path.join(cartella_preset, nome_json))
        img_preset = os.path.join(cartella_preset, f"{nome_json.replace('.json', '')}.png")
        if os.path.exists(img_preset): os.remove(img_preset)
            
        meta = load_meta(cartella_preset)
        if nome_json in meta:
            del meta[nome_json]
            save_meta(cartella_preset, meta)
            
        global selected_preset_file
        if selected_preset_file == nome_json: selected_preset_file = None
        aggiorna_griglia()

def seleziona_card(nome_json, frame_selezionato):
    global selected_preset_file
    selected_preset_file = nome_json
    for f in cards_frames:
        f.config(highlightbackground=BG_CARD)
    frame_selezionato.config(highlightbackground=ACCENT_CYAN)
    lbl_stato.config(text=f"PRONTO: {nome_json}", fg=ACCENT_CYAN)

def genera_immagine_default(size=(256, 144)):
    if os.path.exists(DEFAULT_IMG_NAME):
        try: 
            img = Image.open(DEFAULT_IMG_NAME).convert("RGBA")
            return ImageOps.fit(img, size, method=Image.Resampling.LANCZOS)
        except Exception: pass
    img = Image.new('RGB', size, color='#333333')
    draw = ImageDraw.Draw(img)
    draw.text((105, 65), "NO IMG", fill="#777777")
    return img

def cambia_pagina(delta):
    global current_page
    current_page += delta
    aggiorna_griglia()

def aggiorna_griglia():
    global selected_preset_file, cards_frames, current_page
    selected_preset_file = None
    cards_frames.clear()
    
    ultimo_caricato = carica_ultimo_caricato()
    
    # Svuota i contenitori centrali
    for widget in grid_container.winfo_children(): widget.destroy()
    for widget in pagination_frame.winfo_children(): widget.destroy()
        
    cartella_radice = carica_config()
    if not cartella_radice: return
    cartella_preset = os.path.join(cartella_radice, "UserData", "player", "preset_volanti")
    if not os.path.exists(cartella_preset): return
        
    file_list = [f for f in os.listdir(cartella_preset) if f.endswith(".json") and f != "quickswitch_meta.json"]
    
    # Calcolo Impaginazione
    total_pages = math.ceil(len(file_list) / 6) if file_list else 1
    if current_page >= total_pages: current_page = total_pages - 1
    if current_page < 0: current_page = 0
    
    page_files = file_list[current_page*6 : (current_page+1)*6]
    
    colonne = 3 
    for i, nome_json in enumerate(page_files):
        riga = i // colonne
        col = i % colonne
        
        card = tk.Frame(grid_container, bg=BG_CARD, highlightbackground=BG_CARD, highlightthickness=3, padx=5, pady=5)
        card.grid(row=riga, column=col, padx=15, pady=15)
        cards_frames.append(card)
        
        frame_header = tk.Frame(card, bg=BG_CARD)
        frame_header.pack(fill="x")
        
        menu_opzioni = tk.Menu(card, tearoff=0, bg="#404040", fg="white", font=("Segoe UI", 9))
        menu_opzioni.add_command(label="🖼️ Cambia Foto", command=lambda n=nome_json: cambia_immagine_da_icona(n))
        menu_opzioni.add_command(label="✏️ Rinomina", command=lambda n=nome_json: rinomina_preset(n))
        menu_opzioni.add_separator()
        menu_opzioni.add_command(label="🗑️ Elimina", command=lambda n=nome_json: elimina_preset(n))
        
        btn_menu = tk.Label(frame_header, text="⋮", font=("Arial", 16, "bold"), bg=BG_CARD, fg=TEXT_GREY, cursor="hand2")
        btn_menu.pack(side="right")
        btn_menu.bind("<Button-1>", lambda e, m=menu_opzioni: m.post(e.x_root, e.y_root))
        
        nome_base = nome_json.replace(".json", "")
        img_custom_pr = os.path.join(cartella_preset, f"{nome_base}.png")
        
        if os.path.exists(img_custom_pr): img_path = img_custom_pr
        else: img_path = None
        
        if img_path:
            try:
                img = Image.open(img_path)
            except Exception:
                img = genera_immagine_default()
        else:
            img = genera_immagine_default()
            
        img.thumbnail((256, 144), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        lbl_img = tk.Label(card, image=photo, bg=BG_CARD, cursor="hand2")
        lbl_img.image = photo 
        lbl_img.pack(pady=5)
        
        frame_testi = tk.Frame(card, bg=BG_CARD)
        frame_testi.pack(fill="x")
        
        lbl_titolo = tk.Label(frame_testi, text=nome_base[:18].upper(), font=("Impact", 14), bg=BG_CARD, fg=TEXT_WHITE, cursor="hand2")
        lbl_titolo.pack(anchor="center", padx=5, pady=(0, 5))

        colore_accento = "#28A745" if nome_json == ultimo_caricato else ACCENT_RED
        accent = tk.Frame(card, bg=colore_accento, height=4)
        accent.pack(fill="x", side="bottom")
        
        elementi_card = [card, frame_header, lbl_img, frame_testi, lbl_titolo]
        for elemento in elementi_card:
            elemento.bind("<Button-1>", lambda e, n=nome_json, f=card: seleziona_card(n, f))

    # Renderizzazione Pulsanti Paginazione
    if total_pages > 1:
        tk.Button(pagination_frame, text="◀ PREC", bg=BG_CARD, fg=TEXT_WHITE, command=lambda: cambia_pagina(-1), state="normal" if current_page > 0 else "disabled", relief="flat").pack(side="left", padx=10)
        tk.Label(pagination_frame, text=f"Pagina {current_page+1} di {total_pages}", bg=BG_MAIN, fg=TEXT_GREY).pack(side="left", padx=10)
        tk.Button(pagination_frame, text="SUCC ▶", bg=BG_CARD, fg=TEXT_WHITE, command=lambda: cambia_pagina(1), state="normal" if current_page < total_pages - 1 else "disabled", relief="flat").pack(side="left", padx=10)

# --- GESTIONE FINESTRE MENU SISTEMA ---
def mostra_guida():
    guida_path = os.path.join(BASE_DIR, "guidauso.txt")
    if not os.path.exists(guida_path):
        testo_base = """=== GUIDA ALL'USO DI QUICK SWITCH ===

1. Prima Configurazione (Collegamento a LMU)
- Clicca sui tre puntini in alto a destra e seleziona 'Imposta cartella LMU'.
- Seleziona la cartella principale dove hai installato Le Mans Ultimate.

2. Aggiungere un Setup
- Clicca su 'ADD PRESET' e seleziona il tuo file .json.
- Scegli un nome e, se vuoi, associa un'immagine.
- Clicca su SALVA.

3. Modifica e Organizzazione
- Clicca sui tre puntini sopra l'immagine di un volante per Cambiare Foto, Rinominare o Eliminare il preset.

4. Attivare il Setup nel Gioco
- Clicca sul preset che vuoi usare (si illuminerà di azzurro).
- Premi il bottone 'SWITCH' in basso.
- Ora puoi avviare Le Mans Ultimate e scendere in pista!
"""
        try:
            with open(guida_path, "w", encoding="utf-8") as f:
                f.write(testo_base)
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile creare il file guidauso.txt:\n{e}", parent=app)
            return
            
    try:
        if os.name == 'nt':
            os.startfile(guida_path)
        else:
            import subprocess
            subprocess.call(('open' if sys.platform == 'darwin' else 'xdg-open', guida_path))
    except Exception as e:
        messagebox.showerror("Errore", f"Impossibile aprire il file guidauso.txt:\n{e}", parent=app)

def mostra_info():
    messagebox.showinfo("Info", "Quick Switch v0.1.6\nSviluppato per Le Mans Ultimate.", parent=app)


# --- APP SETUP ---
app = tk.Tk()
app.title("Quick Switch")
app.geometry("1050x700") 
app.configure(bg=BG_MAIN)
app.resizable(False, False)

# Applica Favicon all'applicazione
try:
    icon_img = ImageTk.PhotoImage(Image.open(DEFAULT_IMG_NAME))
    app.wm_iconphoto(False, icon_img)
except Exception:
    pass 

header_frame = tk.Frame(app, bg=BG_HEADER)
header_frame.pack(fill="x", padx=20, pady=(20, 10))

gold_line = tk.Frame(header_frame, bg=ACCENT_GOLD, height=3)
gold_line.pack(side="bottom", fill="x")

content_header = tk.Frame(header_frame, bg=BG_HEADER)
content_header.pack(fill="both", expand=True, padx=15, pady=10)

try:
    if os.path.exists(DEFAULT_IMG_NAME):
        header_img = Image.open(DEFAULT_IMG_NAME).convert("RGBA")
        header_img = ImageOps.fit(header_img, (40, 40), method=Image.Resampling.LANCZOS)
        header_photo = ImageTk.PhotoImage(header_img)
        lbl_header_logo = tk.Label(content_header, image=header_photo, bg=BG_HEADER)
        lbl_header_logo.image = header_photo
        lbl_header_logo.pack(side="left", padx=(0, 10))
except Exception:
    pass 

tk.Label(content_header, text="QUICK SWITCH", font=("Impact", 22), bg=BG_HEADER, fg=TEXT_WHITE).pack(side="left")

lbl_percorso = tk.Label(content_header, text="...\\UserData\\player" if carica_config() else "LMU Folder Missing", font=("Segoe UI", 8), bg=BG_HEADER, fg=TEXT_GREY)
lbl_percorso.pack(side="left", padx=20)

right_frame = tk.Frame(content_header, bg=BG_HEADER)
right_frame.pack(side="right", fill="y")

lbl_stato = tk.Label(right_frame, text="SISTEMA PRONTO", font=("Segoe UI", 9, "bold"), bg=BG_HEADER, fg=ACCENT_CYAN)
lbl_stato.pack(side="left", padx=(0, 20))

# Pulsante inibito ("AGGIUNGI PRESET") eliminato
# Pulsante rimanente modificato in "ADD PRESET"
tk.Button(right_frame, text="ADD\nPRESET", font=("Segoe UI", 8, "bold"), bg=BG_MAIN, fg=TEXT_WHITE, relief="ridge", borderwidth=1, width=12, height=2, command=importa_preset).pack(side="left", padx=5)

menu_sistema = tk.Menu(right_frame, tearoff=0, bg="#404040", fg="white", font=("Segoe UI", 9))
menu_sistema.add_command(label="⚙️ Imposta cartella LMU", command=imposta_cartella)
menu_sistema.add_command(label="📖 Guida di utilizzo", command=mostra_guida)
menu_sistema.add_command(label="ℹ️ Info e Ringraziamenti", command=mostra_info)

btn_sistema = tk.Label(right_frame, text="⋮", font=("Arial", 22, "bold"), bg=BG_HEADER, fg=TEXT_GREY, cursor="hand2")
btn_sistema.pack(side="left", padx=(10, 0))
btn_sistema.bind("<Button-1>", lambda e: menu_sistema.post(e.x_root, e.y_root))

# --- AREA CENTRALE CON IMPAGINAZIONE ---
center_area = tk.Frame(app, bg=BG_MAIN)
center_area.pack(fill="both", expand=True, padx=20, pady=5)

grid_container = tk.Frame(center_area, bg=BG_MAIN)
grid_container.pack(expand=True)  

pagination_frame = tk.Frame(center_area, bg=BG_MAIN)
pagination_frame.pack(side="bottom", pady=5)

frame_bottom = tk.Frame(app, bg=BG_MAIN)
frame_bottom.pack(fill="x", padx=20, pady=15)

tk.Button(frame_bottom, text="SWITCH", font=("Impact", 16), bg=ACCENT_RED, fg=TEXT_WHITE, activebackground="#A3001C", activeforeground="white", relief="flat", command=applica_preset, width=20, pady=8).pack(pady=10)

aggiorna_griglia()
app.mainloop()