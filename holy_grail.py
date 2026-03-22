#!/usr/bin/env python
# coding: utf-8

# In[26]:


import os
import json
import math
import tkinter as tk
from tkinter import ttk, messagebox
from itertools import product, combinations_with_replacement
import sys, subprocess

# Basis-Pfad für PDFs (funktioniert als Skript, Notebook oder exe)
try:
    base_path = os.path.dirname(os.path.abspath(__file__))  # Skript
except NameError:
    base_path = os.getcwd()  # Notebook / interaktiv

# Wenn als exe gepackt mit PyInstaller
if getattr(sys, 'frozen', False):
    base_path = os.path.dirname(sys.executable)

# ---------- Healfunktion ----------
def holy_light_hpms(bh, crit, haste, mana, mp5, int, min_h, max_h, spellh, spelllvl):

    mana_weight = get_mana_weight()
    mana_mode = mana_mode_var.get()
    spell_mult = min((spelllvl + 11) / 70, 1.0)
    cast_time = (spellh-0.5) / (1 + haste/1577)
    real_crit = crit + 0.06
    real_crit_int = real_crit + int * 0.000125 * 1.1**2

    if mana_mode == "capped":
        real_crit_int += 0.05
        crit_cap = float(crit_cap_var.get())
        effective_crit_for_mana = min(real_crit_int, crit_cap)
    else:
        effective_crit_for_mana = real_crit_int

    if libram_var.get() == "lightbringer":
        heal_nc = (min_h + max_h)/2 + (bh + int * 0.35 * 1.1**2 + 87) * (spellh/3.5) * spell_mult * 1.12
    else:
        heal_nc = (min_h + max_h)/2 + (bh + int * 0.35 * 1.1**2) * (spellh/3.5) * spell_mult * 1.12

    heal_c = heal_nc * 1.5
    heal_av = heal_nc * (1 - real_crit_int) + heal_c * real_crit_int

    if libram_var.get() == "mending":
        mana_mp5 = (mp5 + 22) * cast_time / 5
    else:
        mana_mp5 = mp5 * cast_time / 5

    mana_lib = mana - 34

    if libram_var.get() == "truth":
        mana_eff = mana_lib - mana_mp5
        mana_av = mana_eff * (1 - effective_crit_for_mana) + (mana_eff - mana_lib * 0.6) * effective_crit_for_mana
    else:
        mana_eff = mana - mana_mp5
        mana_av = mana_eff * (1 - effective_crit_for_mana) + (mana_eff - mana * 0.6) * effective_crit_for_mana

    hpm = heal_av / mana_av
    if hps_mode_var.get():
        hpms= heal_av / cast_time
    else:
        hpms = hpm / cast_time
    return hpms

# ---------- Setup ----------
rank9 = dict(min_h=1813, max_h=2015, mana=660, spellh=2.5, spelllvl=60)
rank11 = dict(min_h=2459, max_h=2740, mana=840, spellh=2.5, spelllvl=70)
share9_default = 0.8
share11 = 1-share9_default

try:
    base_path = os.path.dirname(os.path.abspath(__file__))
except NameError:
    base_path = os.getcwd()

json_path = os.path.join(base_path, "items.json")
with open("items.json", "r") as f:
    items = json.load(f)
    hidden_history = []

for slot_items in items.values():
    for itm in slot_items:
        itm["socket"] = int(itm.get("socket", 0))
        itm["meta"] = int(itm.get("meta", 0))

#-- Mana Weight Funktion----

def get_mana_weight():
    mode = mana_mode_var.get()

    if mode == "normal":
        return 0.0
    elif mode == "normal_25":
        return 0.25
    elif mode == "normal_50":
        return 0.5
    elif mode == "normal_75":
        return 0.75
    elif mode == "normal_100":
        return 1.0
    elif mode == "capped":
        return 0.0

# ---------- Helper ----------
def total_hpms(stats):
    share9 = float(share9_var.get())
    share11 = 1 - share9
    x9 = holy_light_hpms(**stats, **rank9)
    if share9 < 0 or share9 > 1: raise ValueError("HL9 Share must be between 0 and 1")
    x11 = holy_light_hpms(**stats, **rank11)
    mana_weight = get_mana_weight()
    return share9*x9 + share11*x11 + mana_weight * stats["int"] * 0.0025

def crit_to_chance(stats):
    base_crit = float(base_vars["crit"].get())
    rating = stats["crit"]
    return base_crit + rating / 2208

# ---------- Gems ----------
gems = [
    {"name":"Teardrop Crimson Spinel (22 heal)", "bh":22, "crit":0, "haste":0, "mp5":0, "int":0},
    {"name":"Quick Lionseye (10 haste)", "bh":0, "crit":0, "haste":10, "mp5":0, "int":0},
    {"name":"Luminous Pyrestone (11 heal 5 int)", "bh":11, "crit":0, "haste":0, "mp5":0, "int":5},
    {"name":"Royal Shadowsong Amethyst (11heal 2mp5)", "bh":11, "crit":0, "haste":0, "mp5":2, "int":0},
    {"name":"Gleaming Lionseye (10 crit)", "bh":0, "crit":10, "haste":0, "mp5":0, "int":0},
    {"name":"Brilliant Lionseye (10 int)", "bh":0, "crit":0, "haste":0, "mp5":0, "int":10},
]

blue_gems = [
    {"name":"Teardrop Living Ruby (18 heal)", "bh":18, "crit":0, "haste":0, "mp5":0, "int":0},
    {"name":"Quick Dawnstone (8 haste)", "bh":0, "crit":0, "haste":8, "mp5":0, "int":0},
    {"name":"Luminous Noble Topaz (9 heal 4 int)", "bh":9, "crit":0, "haste":0, "mp5":0, "int":4},
    {"name":"Royal Nightseye (9 heal 2 mp5)", "bh":9, "crit":0, "haste":0, "mp5":2, "int":0},
    {"name":"Gleaming Dawnstone (8 crit)", "bh":0, "crit":8, "haste":0, "mp5":0, "int":0},
    {"name":"Brilliant Dawnstone (8 int)", "bh":0, "crit":0, "haste":0, "mp5":0, "int":8},
]

#-------------Enchants----------------
enchant_options = {
    "head": [
        {"name": "Glyph of Renewal (35 bh, 7 mp5)", "bh": 35, "mp5": 7},
    ],
    "shoulder": [
        {"name": "Greater Inscription of Faith (33 bh, 4 mp5)", "bh": 33, "mp5": 4},
        {"name": "Greater Inscription of Discipline (18 bh, 10 crit)", "bh": 18, "crit": 10},
        {"name": "Greater Inscription of the Orb (12 bh, 15 crit)", "bh": 12, "crit": 15}
    ],
    "chest": [
        {"name": "Restore Mana prime (6 mp5)", "mp5": 6},
        {"name": "Exceptional Stats (6 int)", "int": 6}
    ],
    "wrist": [
        {"name": "Major Intellect (12 int)", "int": 12},
        {"name": "Superior Healing (30 bh)", "bh": 30}
    ],
    "gloves": [
        {"name": "Blasting (10 crit)", "crit": 10},
        {"name": "Minor Haste (10 haste)", "haste": 10},
        {"name": "Major Healing (35 bh)", "bh": 35}
    ],
    "weapon": [
        {"name": "Major Intellect (30 int)", "int": 30},
        {"name": "Major Healing (81 bh)", "bh": 81}
    ],
    "shield": [
        {"name": "Intellect (12 int)", "int": 12}
    ],
    "pants": [
        {"name": "Golden Spellthread (66 bh)", "bh": 66}
    ],
    "boots": [
        {"name": "Vitality (4 mp5)", "mp5": 4}
    ]
}

#-----------Consumables--------------
consumables_options = {
    "food": [
        {"name": "Golden Fish Sticks (44 bh)", "bh": 44},
        {"name": "Blackened Sporefish (8 mp5)", "mp5": 8},
        {"name": "Skullfish Soup (20 crit)", "crit": 20}
    ],
    "oil": [
        {"name": "Brilliant Wizard Oil (36 bh, 14 crit)", "bh": 36, "crit": 14},
        {"name": "Brilliant Mana Oil (25 bh, 12 mp5)", "bh": 25, "mp5": 12}
    ],
    "flask": [
        {"name": "Flask of Blinding Light (80 bh)", "bh": 80},
        {"name": "Flask of Distilled Wisdom (65 int)", "int": 65},
        {"name": "Flask of Mighty Restoration (25 mp5)", "mp5": 25},
    ],
    "battle_elixir": [
        {"name": "Elixir of Healing Power (50 bh)", "bh": 50},
        {"name": "Adept's Elixir (24 bh, 24 crit)", "bh": 24, "crit": 24}
    ],
    "guardian_elixir": [
        {"name": "Elixir of Major Mageblood (16 mp5)", "mp5": 16},
        {"name": "Elixir of Draenic Wisdom (30 int)", "int": 30}
    ]
}

def apply_meta(stats, meta_count):
    if meta_count == 0:
        return stats
    cast_time = (2.5-0.5) / (1 + stats["haste"]/1577)
    stats["int"] += 12 * meta_count
    stats["mp5"] += (1500/(cast_time * 20 + 15)) * meta_count
    return stats

# ---------- Gem Solver ----------
def optimize_gems(base_stats, num_sockets, meta_count, gem_list):
    best_hpms = 0
    best_combo = None
    for combo in combinations_with_replacement(gem_list, num_sockets):
        stats = base_stats.copy()
        for gem in combo:
            for stat in stats:
                stats[stat] += gem.get(stat,0)
        stats = apply_meta(stats, meta_count)
        calc_stats = stats.copy()
        calc_stats["crit"] = crit_to_chance(calc_stats)
        hpms = total_hpms(calc_stats)
        if hpms > best_hpms:
            best_hpms = hpms
            best_combo = combo
    return best_hpms, best_combo

# ---------- Build HPMS ---------- 

def build_hpms(items, enchants, base_stats, gem_bonus_socket):
    stats = base_stats.copy()
    sockets = 0
    meta_count = 0
    unique_items = set()

    for itm, ench in zip(items, enchants):

        if itm.get("unique", False):
            if itm["name"] in unique_items:
                return None
            unique_items.add(itm["name"])

        sockets += itm.get("socket", 0)
        meta_count += itm.get("meta", 0)

        # item stats
        for stat in stats:
            stats[stat] += itm.get(stat, 0)

        # enchant stats (WICHTIG NEU!)
        if ench is not None:
            for k, v in ench.items():
                if k != "name":
                    stats[k] += v

        # gems
        if gem_type_var.get() == "epic":
            gem_bonus_per_socket = 10
        else:
            gem_bonus_per_socket = 8

        mana_mode = mana_mode_var.get()
        mana_weight = get_mana_weight()

        if mana_weight >= 0.5:
            stats["int"] += itm.get("socket", 0) * gem_bonus_per_socket
        else:
            stats["crit"] += itm.get("socket", 0) * gem_bonus_per_socket

    stats = apply_meta(stats, meta_count)
    calc = stats.copy()
    calc["crit"] = crit_to_chance(calc)

    return total_hpms(calc)

# ---------- GUI Setup ----------
root = tk.Tk()
root.title("Holy Grail")

main_canvas = tk.Canvas(root)
scrollbar = tk.Scrollbar(root, orient="vertical", command=main_canvas.yview)
scrollable_frame = tk.Frame(main_canvas)

scrollable_frame.bind(
    "<Configure>",
    lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
)

main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
main_canvas.configure(yscrollcommand=scrollbar.set)
main_canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# ---------- Scrollen ----------
def bind_text_scroll(widget):
    widget.bind("<Enter>", lambda e: set_canvas_scroll(False))
    widget.bind("<Leave>", lambda e: set_canvas_scroll(True))
    widget.bind("<MouseWheel>", lambda ev: widget.yview_scroll(int(-1*(ev.delta/120)), "units"))
    widget.bind("<Button-4>", lambda ev: widget.yview_scroll(-1, "units"))
    widget.bind("<Button-5>", lambda ev: widget.yview_scroll(1, "units"))
    canvas_scroll_enabled = True

def on_mousewheel(event):
    if canvas_scroll_enabled:
        if event.num == 5 or event.delta < 0:
            main_canvas.yview_scroll(1, "units")
        elif event.num == 4 or event.delta > 0:
            main_canvas.yview_scroll(-1, "units")

root.bind_all("<MouseWheel>", on_mousewheel)
root.bind_all("<Button-4>", on_mousewheel)
root.bind_all("<Button-5>", on_mousewheel)

def set_canvas_scroll(enabled: bool):
    global canvas_scroll_enabled
    canvas_scroll_enabled = enabled

# ---------- Erklärung ----------
explanation_frame = tk.LabelFrame(scrollable_frame, text="Erklärung")
explanation_frame.pack(fill="x", padx=5, pady=5)

explanation = tk.Text(explanation_frame, height=18, wrap="word")
explanation.pack(fill="x", padx=5, pady=5)

# Basis-Pfad des Skripts oder der exe
import sys
import os
import subprocess
import tkinter.messagebox as messagebox
import webbrowser

try:
    exe_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    exe_dir = os.getcwd()

if getattr(sys, 'frozen', False):
    exe_dir = os.path.dirname(sys.executable)

# Funktion zum Öffnen der PDF "dieses Dokument"
def open_pdf(event=None):
    pdf_path = os.path.join(exe_dir, "Holy_Document.pdf")
    if not os.path.isfile(pdf_path):
        messagebox.showerror("Fehler", f"No document found:\n{pdf_path}")
        return
    if sys.platform == "win32":
        os.startfile(pdf_path)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", pdf_path])
    else:
        subprocess.Popen(["xdg-open", pdf_path])

# Funktion zum Öffnen des anderen PDFs "hier"
def open_other_pdf(event=None):
    pdf_path = os.path.join(exe_dir, "Holy_User_Guide.pdf")
    if not os.path.isfile(pdf_path):
        messagebox.showerror("Fehler", f"No document found:\n{pdf_path}")
        return
    if sys.platform == "win32":
        os.startfile(pdf_path)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", pdf_path])
    else:
        subprocess.Popen(["xdg-open", pdf_path])

# Funktion für die Webseite "dieses Tool"
def open_website(event=None):
    webbrowser.open("https://www.wowhead.com/tbc/gear-planner/paladin/blood-elf/A0YPBVAxIFIBMlMQUfBQJB9f")

# Hier kannst du deinen Text schreiben
intro_text = (
    "Welcome! This is the core of the Holy Grail for Holy Paladins made by Dedolox.\n"
    "This program optimizes for HPMS (heal per mana and second).\n"
    "For the exact calculations and the formulas behind it, "
    "you can read this document.\n"
    "A compact guide on how to use this optimizer can be found here.\n"
    "- Base stats must be determined after removing the items you want to optimize.\n"
    "- Crit must be entered as a decimal value (25.28% = 0.2528).\n"
    "- The crit value for holy spells must be entered.\n"
    "- Take the 49 MP5 from improved BoW into account\n"
    "- Sockets, meta sockets, and talents are taken into account.\n"
    "- Trinkets are not included.\n"
    "- To determine base stats with different trinkets, use this tool\n"
    "  (remember to include +5% crit from the talent Holy Power).\n"
    "- 2T6 bonus is not included in calculation. I just can't make it work,\n"
    "  but it's around 110 critrating so you definetly want it.\n" 
    "- HPS Mode completly ignores the mana regen of mp5 and crit - it just optimizes\n"
    "  for raw HPS. Only consider this for very short boss fights or giga endgame\n"
    "- Default values = naked stats (33 bh, 0.0952 crit, 49 mp5). Add trinket stats."
)

# Text zuerst editierbar machen
explanation.configure(state="normal")
explanation.insert(tk.END, intro_text)

# --- Tags setzen ---
# 1) "dieses Dokument"
pos_start = explanation.search("this document", "1.0", tk.END)
if pos_start:
    pos_end = f"{pos_start}+{len('this document')}c"
    explanation.tag_add("pdf_link", pos_start, pos_end)
    explanation.tag_config("pdf_link", foreground="blue", underline=True)
    explanation.tag_bind("pdf_link", "<Button-1>", open_pdf)
    explanation.tag_bind("pdf_link", "<Enter>", lambda e: explanation.config(cursor="hand2"))
    explanation.tag_bind("pdf_link", "<Leave>", lambda e: explanation.config(cursor=""))

# 2) "hier" für anderes PDF
# Suche ab Ende des ersten Vorkommens, um das zweite "hier" zu treffen
pos_start = explanation.search("here", pos_end, tk.END)
if pos_start:
    pos_end2 = f"{pos_start}+{len('here')}c"
    explanation.tag_add("other_pdf_link", pos_start, pos_end2)
    explanation.tag_config("other_pdf_link", foreground="blue", underline=True)
    explanation.tag_bind("other_pdf_link", "<Button-1>", open_other_pdf)
    explanation.tag_bind("other_pdf_link", "<Enter>", lambda e: explanation.config(cursor="hand2"))
    explanation.tag_bind("other_pdf_link", "<Leave>", lambda e: explanation.config(cursor=""))

# 3) "dieses Tool" für Webseite
pos_start = explanation.search("this tool", "1.0", tk.END)
if pos_start:
    pos_end = f"{pos_start}+{len('this tool')}c"
    explanation.tag_add("web_link", pos_start, pos_end)
    explanation.tag_config("web_link", foreground="blue", underline=True)
    explanation.tag_bind("web_link", "<Button-1>", open_website)
    explanation.tag_bind("web_link", "<Enter>", lambda e: explanation.config(cursor="hand2"))
    explanation.tag_bind("web_link", "<Leave>", lambda e: explanation.config(cursor=""))

# Text wieder schreibgeschützt machen
explanation.configure(state="disabled")

# Scrollverhalten wie bei anderen Textfeldern
bind_text_scroll(explanation)

# Tag für den klickbaren Link "dieses Dokument"
pos_start = explanation.search("dieses Dokument", "1.0", tk.END)
if pos_start:
    pos_end = f"{pos_start}+{len('dieses Dokument')}c"
    explanation.tag_add("pdf_link", pos_start, pos_end)
    explanation.tag_config("pdf_link", foreground="blue", underline=True)
    explanation.tag_bind("pdf_link", "<Button-1>", open_pdf)

    # 👆 Cursor auf Hand ändern, wenn man über den Text hovert
    explanation.tag_bind("pdf_link", "<Enter>", lambda e: explanation.config(cursor="hand2"))
    explanation.tag_bind("pdf_link", "<Leave>", lambda e: explanation.config(cursor=""))

# ---------- Options Row ----------
options_frame = tk.Frame(scrollable_frame)
options_frame.pack(anchor="w", padx=5, pady=5)


# Überschriften
tk.Label(options_frame, text="Content", font=("Arial",10,"bold")).grid(row=0, column=0, sticky="w", padx=15)
tk.Label(options_frame, text="Mana Weight", font=("Arial",10,"bold")).grid(row=0, column=1, sticky="w", padx=15)
tk.Label(options_frame, text="Libram", font=("Arial",10,"bold")).grid(row=0, column=2, sticky="w", padx=15)
tk.Label(options_frame, text="Gems", font=("Arial",10,"bold")).grid(row=0, column=3, sticky="w", padx=15)
tk.Label(options_frame, text="HPS Mode", font=("Arial",10,"bold")).grid(row=0, column=4, sticky="w", padx=15)

# ----- Content -----
content_vars = {}
contents = ["pre-raid","T4","T5","T6","ZA","SWP"]

for i, content in enumerate(contents):
    var = tk.BooleanVar(value=True)
    tk.Checkbutton(options_frame, text=content, variable=var)\
        .grid(row=i+1, column=0, sticky="w", padx=15)
    content_vars[content] = var

#--- Mana Weight ----
mana_weight_var = tk.DoubleVar(value=0.0)
mana_mode_var = tk.StringVar(value="normal")

tk.Radiobutton(options_frame, text="Off", value="normal", variable=mana_mode_var).grid(row=1, column=1, sticky="w", padx=15)
tk.Radiobutton(options_frame, text="Off - crit regen capped", value="capped", variable=mana_mode_var).grid(row=2, column=1, sticky="w", padx=15)
tk.Radiobutton(options_frame, text="25%", value="normal_25", variable=mana_mode_var).grid(row=3, column=1, sticky="w", padx=15)
tk.Radiobutton(options_frame, text="50%", value="normal_50", variable=mana_mode_var).grid(row=4, column=1, sticky="w", padx=15)
tk.Radiobutton(options_frame, text="75%", value="normal_75", variable=mana_mode_var).grid(row=5, column=1, sticky="w", padx=15)
tk.Radiobutton(options_frame, text="100%", value="normal_100", variable=mana_mode_var).grid(row=6, column=1, sticky="w", padx=15)

# ----- Libram -----
libram_var = tk.StringVar()
libram_var.set("none")   # Default

tk.Radiobutton(
    options_frame,
    text="None",
    variable=libram_var,
    value="none"
).grid(row=1, column=2, sticky="w", padx=15)

tk.Radiobutton(
    options_frame,
    text="Absolute Truth",
    variable=libram_var,
    value="truth"
).grid(row=2, column=2, sticky="w", padx=15)

tk.Radiobutton(
    options_frame,
    text="Lightbringer",
    variable=libram_var,
    value="lightbringer"
).grid(row=3, column=2, sticky="w", padx=15)

tk.Radiobutton(
    options_frame,
    text="Mending",
    variable=libram_var,
    value="mending"
).grid(row=4, column=2, sticky="w", padx=15)


# ----- Gem Type -----
gem_type_var = tk.StringVar(value="epic")

tk.Radiobutton(options_frame, text="Epic Gems", variable=gem_type_var, value="epic")\
    .grid(row=1, column=3, sticky="w", padx=15)

tk.Radiobutton(options_frame, text="Blue Gems", variable=gem_type_var, value="blue")\
    .grid(row=2, column=3, sticky="w", padx=15)

# ----- Haste Gems -----
consider_haste_var = tk.BooleanVar(value=True)

tk.Checkbutton(
    options_frame,
    text="Consider Haste Gems",
    variable=consider_haste_var
).grid(row=3, column=3, sticky="w", padx=15)


#----- HPS Mode -------
hps_mode_var = tk.BooleanVar(value=False)
tk.Checkbutton(
    options_frame,
    text="HPS Mode",
    variable=hps_mode_var
).grid(row=1, column=4, sticky="w", padx=15)


tk.Label(scrollable_frame, text="Basestats", font=("Arial",10,"bold")).pack(anchor="w", padx=5, pady=5)

stats_frame = tk.Frame(scrollable_frame)
stats_frame.pack(anchor="w")

base_vars = {}


stats = ["bh","crit","haste","mp5"]

stats = ["bh","crit","haste","mp5"]

for i, stat in enumerate(stats):
    tk.Label(stats_frame, text=f"{stat}:").grid(row=i, column=0, sticky="w")

    if stat == "bh":
        value = "33"
    elif stat == "crit":
        value = "0.0952"
    elif stat == "haste":
        value = "0"
    elif stat == "mp5":
        value = "49"

    var = tk.StringVar()
    var.set(value)  # 👉 nur fürs UI

    tk.Entry(stats_frame, textvariable=var, width=10).grid(row=i, column=1, padx=5)
    base_vars[stat] = var

# HL9 Share
tk.Label(stats_frame, text="HL9 Share:").grid(row=0, column=2, padx=(30,5), sticky="w")
share9_var = tk.StringVar(value=str(share9_default))
tk.Entry(stats_frame, textvariable=share9_var, width=10).grid(row=0, column=3)

# Crit Cap (NEU)
tk.Label(stats_frame, text="Crit Cap:").grid(row=1, column=2, padx=(30,5), sticky="w")
crit_cap_var = tk.StringVar(value="0.35")

crit_cap_entry = tk.Entry(
    stats_frame,
    textvariable=crit_cap_var,
    width=10,
    state="disabled"   
)
crit_cap_entry.grid(row=1, column=3)

def update_crit_cap_state(*args):
    if mana_mode_var.get() == "capped":
        crit_cap_entry.config(state="normal")
    else:
        crit_cap_entry.config(state="disabled")

mana_mode_var.trace_add("write", update_crit_cap_state)

# Initial
update_crit_cap_state()

# ---------- Mark Everything ----------
def mark_everything():
    for slot, lb in listboxes.items():
        lb.selection_clear(0, tk.END)
        lb.select_set(0, tk.END)

def unmark_everything():
    for slot, lb in listboxes.items():
        lb.selection_clear(0, tk.END)

mark_frame = tk.Frame(scrollable_frame)
mark_frame.pack(pady=5, anchor="w", padx=5)

tk.Button(mark_frame, text="Select All", command=mark_everything).pack(side="left", padx=5)
tk.Button(mark_frame, text="Unselect All", command=unmark_everything).pack(side="left", padx=5)

# ---------- Item Listboxes ----------
filtered_items_by_slot = {}
listboxes = {}
for slot, slot_items in items.items():
    frame = tk.LabelFrame(scrollable_frame, text=slot.capitalize())
    frame.pack(fill="x", padx=5, pady=5)
    lb = tk.Listbox(frame, selectmode=tk.MULTIPLE, height=5, exportselection=False)
    for itm in sorted(slot_items, key=lambda x: x["name"].lower()):
        lb.insert(tk.END, itm["name"])
    lb.pack(side="left", fill="x", expand=True)
    sb = tk.Scrollbar(frame, orient="vertical", command=lb.yview)
    lb.config(yscrollcommand=sb.set)
    sb.pack(side="right", fill="y")

    def bind_listbox_scroll(lb):
        lb.bind("<Enter>", lambda e: set_canvas_scroll(False))
        lb.bind("<Leave>", lambda e: set_canvas_scroll(True))
        lb.bind("<MouseWheel>", lambda ev: lb.yview_scroll(int(-1*(ev.delta/120)), "units"))
        lb.bind("<Button-4>", lambda ev: lb.yview_scroll(-1, "units"))
        lb.bind("<Button-5>", lambda ev: lb.yview_scroll(1, "units"))

    bind_listbox_scroll(lb)
    listboxes[slot] = lb

def update_listboxes():
    for slot, lb in listboxes.items():
        lb.delete(0, tk.END)
        filtered_items = [
            itm for itm in items[slot]
            if content_vars[itm["content"]].get() and not itm.get("hidden", False)
        ]
        filtered_items = sorted(filtered_items, key=lambda x: x["name"].lower())
        filtered_items_by_slot[slot] = filtered_items
        for itm in filtered_items:
            display_name = f'{itm["name"]} ({itm["dungeon"]} - {itm["boss"]})'
            lb.insert(tk.END, display_name)

for var in content_vars.values():
    var.trace_add("write", lambda *args: update_listboxes())

update_listboxes()

from tkinter import messagebox  # ganz oben im Importblock

def on_item_right_click(event, slot):
    lb = listboxes[slot]
    index = lb.nearest(event.y)
    if index < 0:
        return

    # **Markiere das angeklickte Item**
    lb.selection_clear(0, tk.END)  # vorherige Auswahl löschen
    lb.selection_set(index)        # nur das aktuelle markieren

    item = filtered_items_by_slot[slot][index]
    item = filtered_items_by_slot[slot][index]

    menu = tk.Menu(root, tearoff=0)

    def show_stats():
        stats_lines = []
        for k, v in item.items():
            if k in ["name", "content", "dungeon", "boss", "hidden"]:
                continue  # diese Felder überspringen
            stats_lines.append(f"{k}: {v}")  # einfach den gespeicherten Wert anzeigen

        stats_str = "\n".join(stats_lines)

        # Eigenes Fenster, kein nerviger Systemton
        win = tk.Toplevel(root)
        win.title(f"Stats: {item['name']}")
        tk.Label(win, text=stats_str, justify="left").pack(padx=10, pady=10)
        tk.Button(win, text="Schließen", command=win.destroy).pack(pady=5)

    def change_stats():
        change_win = tk.Toplevel(root)
        change_win.title(f"Ändere Stats: {item['name']}")
        fields = [k for k in item if k not in ["name","content","dungeon","boss","hidden"]]
        vars = {}
        for i, f in enumerate(fields):
            tk.Label(change_win, text=f).grid(row=i, column=0, sticky="w")
            v = tk.StringVar(value=str(item[f]))
            tk.Entry(change_win, textvariable=v).grid(row=i, column=1)
            vars[f] = v

        def save_changes():
            for f in vars:
                item[f] = int(vars[f].get())

            with open(json_path, "w") as fjson:
                json.dump(items, fjson, indent=4)

            update_listboxes()
            change_win.destroy()

        tk.Button(change_win, text="Speichern", command=save_changes).grid(row=len(fields), column=0, columnspan=2)

    def delete_item():
        if messagebox.askyesno("Löschen", f"Are you sure you want delete {item['name']}"):
            items[slot].remove(item)
            with open(json_path, "w") as fjson:
                json.dump(items, fjson, indent=4)
            update_listboxes()

    def hide_item():
        if messagebox.askyesno("Hide Item", f"Are you sure you want hide {item['name']}?"):
            item["hidden"] = True
            hidden_history.append(item)

            with open(json_path, "w") as fjson:
                json.dump(items, fjson, indent=4)

            update_listboxes()

    menu.add_command(label="Show Stats", command=show_stats)
    menu.add_command(label="Change Stats", command=change_stats)
    menu.add_command(label="Delete Item", command=delete_item)
    menu.add_command(label="Hide Item", command=hide_item)

    menu.tk_popup(event.x_root, event.y_root)

# Bind Rechtsklick auf alle Listboxes
for slot, lb in listboxes.items():
    lb.bind("<Button-3>", lambda e, s=slot: on_item_right_click(e, s))

# ---------- Button: Item hinzufügen ----------
def open_add_item_window():
    win = tk.Toplevel(root)
    win.title("Add Item")

    tk.Label(win, text="Slot").grid(row=0, column=0, sticky="w")
    slot_var = tk.StringVar(value=list(items.keys())[0])
    slot_menu = ttk.Combobox(win, textvariable=slot_var, values=list(items.keys()))
    slot_menu.grid(row=0, column=1, sticky="ew")

    tk.Label(win, text="Content").grid(row=1, column=0, sticky="w")
    content_var = tk.StringVar(value="pre-raid")
    content_menu = ttk.Combobox(
        win,
        textvariable=content_var,
        values=list(content_vars.keys()),
        state="readonly"
    )
    content_menu.grid(row=1, column=1, sticky="ew")

    fields = ["name","bh","crit","haste","mp5","int","socket","meta","dungeon","boss"]
    vars = {}

    for i, f in enumerate(fields):
        tk.Label(win, text=f).grid(row=i+2, column=0, sticky="w", padx=5, pady=2)
        if f in ["name","dungeon","boss"]:
            v = tk.StringVar()
        else:
            v = tk.StringVar(value="0")
        tk.Entry(win, textvariable=v).grid(row=i+2, column=1, sticky="ew", padx=5, pady=2)
        vars[f] = v

    # Buttons unter allen Feldern
    tk.Button(win, text="Add Item", command=lambda: add_manual(win, vars, slot_var, content_var)).grid(row=len(fields)+2, column=0, pady=5)
    tk.Button(win, text="Safe & Close", command=win.destroy).grid(row=len(fields)+2, column=1, pady=5)

    win.update_idletasks()
    win.minsize(win.winfo_reqwidth(), win.winfo_reqheight())

def add_manual(win, vars, slot_var, content_var):
    slot = slot_var.get()
    item = {}
    for f in vars:
        if f in ["name","dungeon","boss"]:
            item[f] = vars[f].get()
        item[f] = int(vars[f].get()) if f not in ["name","dungeon","boss"] else vars[f].get()
    item["content"] = content_var.get()
    items[slot].append(item)

    update_listboxes()  # Listboxen neu füllen

    # Optional: direkt speichern
    with open("items.json", "w") as f:
        json.dump(items, f, indent=4)

tk.Button(scrollable_frame, text="Add Item", command=open_add_item_window).pack(pady=5)

def revert_hiding():
    if messagebox.askyesno("Revert Hiding", "Are you sure you want to show every hidden item again?"):
        for slot_items in items.values():
            for itm in slot_items:
                if itm.get("hidden", False):
                    itm["hidden"] = False

        with open(json_path, "w") as fjson:
            json.dump(items, fjson, indent=4)
        update_listboxes()

def show_last_hidden():
    if not hidden_history:
        messagebox.showinfo("Info", "There is no hidden Item.")
        return

    item = hidden_history.pop()
    item["hidden"] = False

    with open(json_path, "w") as fjson:
        json.dump(items, fjson, indent=4)

    update_listboxes()

btn_frame = tk.Frame(scrollable_frame)
btn_frame.pack(pady=5)

tk.Button(btn_frame, text="Show Last Hidden", command=show_last_hidden).pack(side="left", padx=5)
tk.Button(btn_frame, text="Revert Hiding", command=revert_hiding).pack(side="left", padx=5)

# ---------- Output ----------
output_frame = tk.Frame(scrollable_frame)
output_frame.pack(padx=5, pady=5, fill="both", expand=True)

output_text = tk.Text(output_frame, height=15, width=80, wrap="word")
output_text.pack(side="left", fill="both", expand=True)

output_scrollbar = tk.Scrollbar(output_frame, command=output_text.yview)
output_scrollbar.pack(side="right", fill="y")

output_text.configure(yscrollcommand=output_scrollbar.set)

bind_text_scroll(output_text)
output_text.configure(state="disabled")

#---- Consumables-----
def eval_with_consumables(base_stats, consumables):
    stats = base_stats.copy()

    for c in consumables:
        for k, v in c.items():
            if k != "name":
                stats[k] = stats.get(k, 0) + v

    stats["crit"] = crit_to_chance(stats)
    return total_hpms(stats)

# ---------- Optimized Berechnen ----------

TOP_N = 2

def refine_build(build, enchants, selected_items, base_stats, gem_bonus_per_socket):
    slots = list(selected_items.keys())

    for i, slot in enumerate(slots):
        best_item = build[i]
        best_ench = enchants[i]

        best_hpms = build_hpms(build, enchants, base_stats, gem_bonus_per_socket)

        for itm in selected_items[slot]:

            # mögliche Enchants für diesen Slot
            possible_enchants = enchant_options.get(slot, [None])

            for ench in possible_enchants:
                candidate_build = build.copy()
                candidate_enchants = enchants.copy()

                candidate_build[i] = itm
                candidate_enchants[i] = ench

                hpms = build_hpms(candidate_build, candidate_enchants, base_stats, gem_bonus_per_socket)

                if hpms and hpms > best_hpms:
                    best_hpms = hpms
                    best_item = itm
                    best_ench = ench

        build[i] = best_item
        enchants[i] = best_ench

    return build, enchants

def berechnen():
    output_text.configure(state="normal")
    output_text.delete(1.0, tk.END)

    selected_items = {}
    for slot, lb in listboxes.items():
        indices = lb.curselection()
        if indices:
            selected_items[slot] = [filtered_items_by_slot[slot][i] for i in indices]

    if not selected_items:
        output_text.insert(tk.END,"There are no selected Items.\n")
        return

    best_enchants = []
    for slot in selected_items.keys():
        if slot in enchant_options:
            best_enchants.append(enchant_options[slot][0])  # default
        else:
            best_enchants.append(None)

    base_stats = {stat: float(base_vars[stat].get()) for stat in base_vars}
    base_stats["int"] = 0
    base_stats["crit"] = 0

    filtered_top = {}
    for slot, slot_items in selected_items.items():
        scored = []
        for itm in slot_items:
            tmp = base_stats.copy()
            for stat in tmp:
                tmp[stat] += itm.get(stat,0)
            if gem_type_var.get() == "epic":
                gem_bonus_per_socket = 10
            else:
                gem_bonus_per_socket = 8

            mana_weight = get_mana_weight()

            if mana_weight >= 0.5:
                tmp["int"] += itm.get("socket", 0) * gem_bonus_per_socket
            else:
                tmp["crit"] += itm.get("socket", 0) * gem_bonus_per_socket


            tmp = apply_meta(tmp, itm.get("meta",0))
            calc = tmp.copy()
            calc["crit"] = crit_to_chance(calc)
            best_local_hpms = -1
            best_local_ench = None

            possible_enchants = enchant_options.get(slot, [None])

            for ench in possible_enchants:
                tmp2 = tmp.copy()

                if ench is not None:
                    for k, v in ench.items():
                        if k != "name":
                            tmp2[k] += v

                calc = tmp2.copy()
                calc["crit"] = crit_to_chance(calc)

                hpms = total_hpms(calc)

                if hpms > best_local_hpms:
                    best_local_hpms = hpms
                    best_local_ench = ench

            scored.append((best_local_hpms, itm, best_local_ench))
        scored.sort(key=lambda x: x[0], reverse=True)
        filtered_top[slot] = [(itm, ench) for _, itm, ench in scored[:TOP_N]]

    best_hpms = 0
    best_hpms_gear = 0
    best_hpms_consumables = 0
    best_build = None
    best_combo = None
    for combo in product(*filtered_top.values()):
        hpms = build_hpms(
            [x[0] for x in combo],
            [x[1] for x in combo],
            base_stats,
            gem_bonus_per_socket
        )
        if hpms and hpms > best_hpms:
            best_hpms = hpms
            best_build = [x[0] for x in combo]
            best_enchants = [x[1] for x in combo]

    if best_build is None:
        output_text.insert(tk.END,"No Combination found\n")
        return

    max_iterations = 50
    min_iterations = 3
    iteration = 0


    while True:
        iteration += 1
        new_build, new_enchants = refine_build(
            best_build.copy(),
            best_enchants.copy(),
            selected_items,
            base_stats,
            gem_bonus_per_socket
        )

        if new_build == best_build and new_enchants == best_enchants:
            break

        best_build = new_build
        best_enchants = new_enchants


        if iteration >= max_iterations:
            break

    best_item_stats = base_stats.copy()
    best_sockets = 0
    best_meta = 0

    for itm, ench in zip(best_build, best_enchants):

        # items
        for stat in best_item_stats:
            best_item_stats[stat] += itm.get(stat, 0)

        # enchants
        if ench is not None:
            for k, v in ench.items():
                if k != "name":
                    best_item_stats[k] += v

        best_sockets += itm.get("socket", 0)
        best_meta += itm.get("meta", 0)


    gem_list = gems if gem_type_var.get() == "epic" else blue_gems

    # Haste Gems optional entfernen
    if not consider_haste_var.get():
        gem_list = [g for g in gem_list if g["haste"] == 0]

    best_hpms, best_gems = optimize_gems(best_item_stats, best_sockets, best_meta, gem_list)

    # Final stats inklusive Gems berechnen
    final_stats = best_item_stats.copy()

    for gem in best_gems:
        for stat in final_stats:
            final_stats[stat] += gem.get(stat, 0)

    final_stats = apply_meta(final_stats, best_meta)

    best_hpms_consumables = -1
    best_combo = None
    base_for_consumables = final_stats.copy()

    food_opts = consumables_options["food"]
    oil_opts = consumables_options["oil"]
    flasks = consumables_options["flask"]
    battle = consumables_options["battle_elixir"]
    guardian = consumables_options["guardian_elixir"]

    for food in food_opts:
        for oil in oil_opts:
            for flask in flasks:

                combo = [food, oil, flask]

                hpms = eval_with_consumables(base_for_consumables, combo)

                if hpms > best_hpms_consumables:
                    best_hpms_consumables = hpms
                    best_combo = combo

    for food in food_opts:
        for oil in oil_opts:
            for b in battle:
                for g in guardian:

                    combo = [food, oil, b, g]

                    hpms = eval_with_consumables(base_for_consumables, combo)

                    if hpms > best_hpms_consumables:
                        best_hpms_consumables = hpms
                        best_combo = combo


    for slot, itm in zip(selected_items.keys(), best_build):
        output_text.insert(tk.END, f"{slot}: {itm['name']} ({itm['dungeon']} - {itm['boss']})\n")

    output_text.insert(tk.END,f"\nTotal Sockets: {best_sockets}\n")
    output_text.insert(tk.END,"\nBest Gems:\n")

    gem_count = {}
    for g in best_gems:
        gem_count[g["name"]] = gem_count.get(g["name"],0)+1
    for name,count in gem_count.items():
        output_text.insert(tk.END,f"{count}x {name}\n")

    output_text.insert(tk.END,"\nBest Enchants:\n")

    for slot, ench in zip(selected_items.keys(), best_enchants):
        if ench is not None:
            output_text.insert(tk.END, f"{slot}: {ench['name']}\n")
    if hps_mode_var.get():
        output_text.insert(tk.END,f"\nHPS: {best_hpms}\n")
    else:
        output_text.insert(tk.END,f"\nHPMS: {best_hpms}\n")

    output_text.insert(tk.END,"\nFinal Stats:\n")

    base_crit = float(base_vars["crit"].get()) * 100

    eff_bh = final_stats["bh"] + final_stats["int"] * 0.35 * (1.1)

    eff_bh_bok = final_stats["bh"] + final_stats["int"] * 0.35 * (1.1**2)

    eff_crit = base_crit + final_stats["crit"]/22.08 + final_stats["int"] * 0.0125 * (1.1)

    eff_crit_bok = base_crit + final_stats["crit"]/22.08 + final_stats["int"] * 0.0125 * (1.1**2)

    cast_time = (2.5 - 0.5) / (1 + final_stats["haste"]/1577)



    output_text.insert(tk.END, f"bh: {round(eff_bh)}\n")
    if content_vars["T6"].get() or content_vars["SWP"].get():
        output_text.insert(tk.END, f"crit: {round(eff_crit,2)}% (that means {round(eff_crit+6,2)}% on Holy Light and {round(eff_crit+11,2)}% with 2T6)\n")
    else:
        output_text.insert(tk.END, f"crit: {round(eff_crit,2)}% (that means {round(eff_crit+6,2)}% on Holy Light)\n")
    output_text.insert(tk.END, f"haste: {round(final_stats['haste'])}\n")
    if best_meta >= 1:
        eff_mp5 = final_stats["mp5"] - (1500/(cast_time * 20 + 15))
        output_text.insert(tk.END, f"mp5: {round(eff_mp5)} ({round(final_stats["mp5"])} with meta socket)\n")
    else:
        eff_mp5 = final_stats["mp5"]
        output_text.insert(tk.END, f"mp5: {round(final_stats["mp5"])}\n")

    if best_combo is None:
        output_text.insert(tk.END, "\nConsumables: None found\n")
    else:
        output_text.insert(tk.END, "\nConsumables:\n")
        for c in best_combo:
            output_text.insert(tk.END, f"{c['name']}\n")

    output_text.configure(state="disabled")

# ---------- Button ----------


tk.Button(scrollable_frame,text="Calculate",command=berechnen).pack(pady=10)

root.mainloop()


# In[ ]:




