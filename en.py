import customtkinter as ctk
from tkinter import filedialog, simpledialog, messagebox
import json
import os
import requests
import locale  # Import du module locale

# Initialisation de CustomTkinter
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Dictionnaires de traductions
translations = {
    "en": {
        "title": "JSON Waypoints Extractor",
        "select_folder": "Select Folder:",
        "extract_waypoints": "Extract Waypoints",
        "download_zip": "Need a zip file?",
        "discord": "Discord - Reimu",
        "waypoint_extraction": "Extracting waypoints...",
        "waypoints_saved": "Waypoints saved at:",
        "error_reading": "Error reading:",
        "download_complete": "ZIP file downloaded successfully.",
        "file_not_accessible": "The file is not accessible at the provided URL.",
        "warning": "Warning",
        "enter_github_url": "Enter the URL of the ZIP file on GitHub:",
        "invalid_folder": "Invalid folder. Please select a valid folder.",
        "download": "Download",
        "success": "Download completed",
        "select_save_location": "Choose where to save the ZIP file"
    },
}

# Langue par défaut
current_language = "en"

# Fonction pour détecter la langue de l'ordinateur
def detect_language():
    lang, _ = locale.getdefaultlocale()  # Récupère la locale par défaut
    if lang is not None:
        lang_code = lang.split('_')[0]  # Extrait le code de langue
        if lang_code in translations:
            return lang_code
    return "en"  # Retourne "fr" par défaut si la langue n'est pas supportée

# Détection de la langue de l'ordinateur à l'initialisation
current_language = detect_language()

# Fonction pour changer la langue
def change_language(lang):
    global current_language
    current_language = lang
    update_ui_text()

# Fonction pour mettre à jour le texte de l'interface
def update_ui_text():
    app.title(translations[current_language]["title"])
    folder_label.configure(text=translations[current_language]["select_folder"])
    extract_button.configure(text=translations[current_language]["extract_waypoints"])
    btn_download_zip.configure(text=translations[current_language]["download_zip"])
    btn_discord.configure(text=translations[current_language]["discord"])
    
    # Mise à jour du texte dans la zone de logs
    log_textbox.configure(state="normal")
    log_textbox.delete(1.0, "end")
    log_textbox.insert("end", translations[current_language]["waypoint_extraction"] + "\n")
    log_textbox.configure(state="disabled")

    # Mise à jour du label titre
    label_title.configure(text=translations[current_language]["title"])

# Fonction pour ouvrir un dialogue de sélection de dossier
def select_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        folder_entry.configure(state="normal")
        folder_entry.delete(0, "end")
        folder_entry.insert(0, folder_path)
        folder_entry.configure(state="disabled")

# Fonction pour extraire les waypoints et les sauvegarder dans waypoints.json
def extract_waypoints():
    folder_path = folder_entry.get()
    waypoints = []

    if not os.path.isdir(folder_path):
        log_textbox.insert("end", translations[current_language]["invalid_folder"] + "\n")
        return

    log_textbox.insert("end", translations[current_language]["waypoint_extraction"] + "\n")

    # Parcours de tous les fichiers .json dans le dossier
    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            file_path = os.path.join(folder_path, filename)
            try:
                with open(file_path, 'r') as file:
                    data = json.load(file)

                    # Vérification et extraction des données si elles existent
                    if "position" in data and "name" in data:
                        waypoint = {
                            "color": 4294967295,
                            "name": f"Waypoints {data['name']}",
                            "x": data["position"][0],
                            "y": data["position"][1],
                            "z": data["position"][2]
                        }
                        waypoints.append(waypoint)
                        log_textbox.insert("end", f"Extracted waypoint from: {filename}\n")
                    else:
                        log_textbox.insert("end", f"{translations[current_language]['error_reading']} {filename}\n")
            except Exception as e:
                log_textbox.insert("end", f"{translations[current_language]['error_reading']} {filename}: {e}\n")

    # Sauvegarde des waypoints dans un fichier
    output_path = os.path.join(folder_path, "waypoints.json")
    try:
        with open(output_path, 'w') as output_file:
            json.dump(waypoints, output_file, indent=4)
        log_textbox.insert("end", f"{translations[current_language]['waypoints_saved']} {output_path}\n")
    except Exception as e:
        log_textbox.insert("end", f"{translations[current_language]['error_reading']} waypoints.json: {e}\n")

# Fonction pour vérifier si le fichier est accessible
def check_file_accessible(github_link):
    try:
        response = requests.head(github_link)
        return response.status_code == 200
    except requests.RequestException:
        return False

# Fonction pour télécharger le fichier ZIP
def download_zip(github_link):
    if not check_file_accessible(github_link):
        messagebox.showerror(translations[current_language]["warning"], translations[current_language]["file_not_accessible"])
        return

    # Demande à l'utilisateur où sauvegarder le fichier
    save_path = filedialog.asksaveasfilename(defaultextension=".zip", 
                                               filetypes=[("Fichiers ZIP", "*.zip"), ("Tous les fichiers", "*.*")],
                                               title=translations[current_language]["select_save_location"])
    if not save_path:
        return  # L'utilisateur a annulé la sélection du fichier

    response = requests.get(github_link, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    if total_size == 0:
        messagebox.showerror(translations[current_language]["warning"], "Impossible de récupérer la taille du fichier.")
        return

    with open(save_path, 'wb') as f:
        for data in response.iter_content(chunk_size=1024):
            f.write(data)

    messagebox.showinfo(translations[current_language]["success"], translations[current_language]["download_complete"])

# Fonction pour ouvrir la nouvelle interface GUI
def open_new_gui():
    new_gui = ctk.CTkToplevel(app)
    new_gui.title(translations[current_language]["title"])
    new_gui.geometry("400x200")

    label = ctk.CTkLabel(master=new_gui, text=translations[current_language]["enter_github_url"])
    label.pack(pady=10)

    entry_url = ctk.CTkEntry(master=new_gui, width=300)
    entry_url.pack(pady=5)

    button_download = ctk.CTkButton(master=new_gui, text=translations[current_language]["download"], command=lambda: download_file(entry_url.get(), new_gui))
    button_download.pack(pady=10)

# Fonction pour télécharger un fichier
def download_file(url, gui):
    if not url:
        messagebox.showwarning(translations[current_language]["warning"], "Veuillez entrer une URL valide.")
        return
    
    if not check_file_accessible(url):
        messagebox.showerror(translations[current_language]["warning"], translations[current_language]["file_not_accessible"])
        return

    # Demande à l'utilisateur où sauvegarder le fichier
    save_path = filedialog.asksaveasfilename(defaultextension=".zip", 
                                               filetypes=[("Fichiers ZIP", "*.zip"), ("Tous les fichiers", "*.*")],
                                               title=translations[current_language]["select_save_location"])
    if not save_path:
        return  # L'utilisateur a annulé la sélection du fichier

    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    if total_size == 0:
        messagebox.showerror(translations[current_language]["warning"], "Impossible de récupérer la taille du fichier.")
        return

    with open(save_path, 'wb') as f:
        for data in response.iter_content(chunk_size=1024):
            f.write(data)

    messagebox.showinfo(translations[current_language]["success"], translations[current_language]["download_complete"])
    gui.destroy()  # Ferme la nouvelle interface après le téléchargement
    
# Création de la fenêtre principale
app = ctk.CTk()
app.geometry("700x500")
app.title(translations[current_language]["title"])

# Cadre gauche pour les boutons
frame_left = ctk.CTkFrame(master=app, width=150)
frame_left.grid(row=0, column=0, padx=10, pady=10, sticky="ns")

# Ajout du menu déroulant pour changer la langue
language_options = ["fr", "ru", "jp", "id", "cn","en"]
language_var = ctk.StringVar(value=current_language)
language_dropdown = ctk.CTkOptionMenu(master=frame_left, variable=language_var, values=language_options, command=change_language, fg_color="red")  # Couleur rouge
language_dropdown.pack(pady=10)

btn_extract = ctk.CTkButton(master=frame_left, text=translations[current_language]["extract_waypoints"], width=140, command=extract_waypoints, fg_color="lightblue", text_color="black")
btn_extract.pack(pady=10)

btn_download_zip = ctk.CTkButton(master=frame_left, text=translations[current_language]["download_zip"], width=140, command=open_new_gui, fg_color="lightgreen", text_color="black")
btn_download_zip.pack(pady=10)

btn_discord = ctk.CTkButton(master=frame_left, text=translations[current_language]["discord"], width=140, fg_color="white", text_color="black")
btn_discord.pack(pady=10)

# Cadre principal pour les éléments d'extraction
frame_main = ctk.CTkFrame(master=app)
frame_main.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

# Label principal
label_title = ctk.CTkLabel(master=frame_main, text=translations[current_language]["title"], font=("Arial", 16))
label_title.pack(pady=10)

# Sélecteur de dossier
folder_label = ctk.CTkLabel(master=frame_main, text=translations[current_language]["select_folder"])
folder_label.pack(pady=(10, 0))

folder_entry = ctk.CTkEntry(master=frame_main, width=400)
folder_entry.pack(pady=5)
folder_entry.insert(0, "Select folder containing JSON files")
folder_entry.configure(state="disabled")

browse_button = ctk.CTkButton(master=frame_main, text="Browse", command=select_folder, fg_color="lightgreen", text_color="black")
browse_button.pack(pady=5)

# Bouton d'extraction
extract_button = ctk.CTkButton(master=frame_main, text=translations[current_language]["extract_waypoints"], command=extract_waypoints, fg_color="lightgreen", text_color="black")
extract_button.pack(pady=20)

# Zone de texte pour les logs
log_textbox = ctk.CTkTextbox(master=frame_main, width=500, height=200)
log_textbox.pack(pady=10)
log_textbox.configure(state="normal")

# Ajustement des proportions pour les colonnes
app.grid_columnconfigure(0, weight=1)
app.grid_columnconfigure(1, weight=3)

# Lancer l'application
app.mainloop()