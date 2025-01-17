import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
from datetime import datetime

def download_tiktok_user():
    def set_language(language):
        if language == "Français":
            label_username.config(text="Nom d'utilisateur TikTok :")
            label_folder.config(text="Dossier de téléchargement :")
            button_choose_folder.config(text="Choisir un dossier")
            check_date.config(text="Ajouter la date de création au nom du fichier")
            button_start.config(text="Commencer le téléchargement")
            button_cancel.config(text="Annuler")
            log_text.delete(1.0, tk.END)
            log_text.insert(tk.END, "Bienvenue! Entrez le nom d'utilisateur TikTok et choisissez un dossier.\n")
        else:
            label_username.config(text="TikTok Username:")
            label_folder.config(text="Download folder:")
            button_choose_folder.config(text="Choose folder")
            check_date.config(text="Add creation date to filename")
            button_start.config(text="Start download")
            button_cancel.config(text="Cancel")
            log_text.delete(1.0, tk.END)
            log_text.insert(tk.END, "Welcome! Enter TikTok username and choose a folder.\n")

    root = tk.Tk()
    root.title("TikTok Account Downloader")
    root.geometry("600x500")
    root.resizable(False, False)

    root.config(bg="#f7f7f7")

    language = tk.StringVar(value="English")
    language_menu = tk.OptionMenu(root, language, "English", "Français", command=set_language)
    language_menu.pack(pady=10)

    frame_inputs = tk.Frame(root, bg="#f7f7f7")
    frame_inputs.pack(pady=10)

    label_username = tk.Label(frame_inputs, text="TikTok Username:", bg="#f7f7f7", font=('Arial', 10))
    label_username.grid(row=0, column=0, sticky="e", padx=5, pady=5)
    username = tk.StringVar()
    tk.Entry(frame_inputs, textvariable=username, width=40).grid(row=0, column=1, padx=5, pady=5)

    label_folder = tk.Label(frame_inputs, text="Download folder:", bg="#f7f7f7", font=('Arial', 10))
    label_folder.grid(row=1, column=0, sticky="e", padx=5, pady=5)
    folder_selected = tk.StringVar()
    tk.Entry(frame_inputs, textvariable=folder_selected, width=40).grid(row=1, column=1, padx=5, pady=5)
    button_choose_folder = tk.Button(frame_inputs, text="Choose folder", command=lambda: folder_selected.set(filedialog.askdirectory()))
    button_choose_folder.grid(row=1, column=2, padx=5, pady=5)

    add_date_var = tk.BooleanVar()
    check_date = tk.Checkbutton(root, text="Add creation date to filename", variable=add_date_var, bg="#f7f7f7", font=('Arial', 10))
    check_date.pack(pady=10)

    progress_bar = tk.Label(root, text="Progress:", bg="#f7f7f7", font=('Arial', 10))
    progress_bar.pack(pady=5)

    progress = tk.Label(root, text="Waiting...", bg="#f7f7f7", font=('Arial', 10), fg="blue")
    progress.pack(pady=5)

    log_text = tk.Text(root, wrap=tk.WORD, height=10, width=70)
    log_text.pack(pady=10)
    log_text.insert(tk.END, "Welcome! Enter TikTok username and choose a folder.\n")

    def start_download():
        username_val = username.get().strip()
        folder_val = folder_selected.get().strip()
        if not username_val or not folder_val:
            log_text.insert(tk.END, "Error: Username and download folder are required.\n")
            return

        yt_dlp_exe = os.path.join(os.path.dirname(__file__), 'yt-dlp_x86.exe')

        if not os.path.isfile(yt_dlp_exe):
            log_text.insert(tk.END, f"Error: {yt_dlp_exe} not found in the folder.\n")
            return

        def format_date(upload_date):
            try:
                return datetime.strptime(upload_date, "%Y%m%d").strftime("%Y/%m/%d")
            except ValueError:
                return upload_date

        output_template = os.path.join(folder_val, "%(uploader)s_%(title)s.%(ext)s")

        if add_date_var.get():
            output_template = os.path.join(
                folder_val,
                "%(upload_date)s_%(uploader)s_%(title)s.%(ext)s"
            )

        command = [
            yt_dlp_exe,
            "-o", output_template,
            f"https://www.tiktok.com/@{username_val}"
        ]

        def download_thread():
            try:
                process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

                for line in process.stdout:
                    if "date:" in line:
                        date_str = line.split("date:")[1].strip()
                        formatted_date = format_date(date_str)
                        line = line.replace(date_str, formatted_date)
                    log_text.insert(tk.END, line)
                    log_text.yview(tk.END)
                    root.update_idletasks()

                for line in process.stderr:
                    log_text.insert(tk.END, line)
                    log_text.yview(tk.END)
                    root.update_idletasks()

                process.wait()

                log_text.insert(tk.END, f"Download completed. Videos are in: {folder_val}\n")
                progress.config(text="Download completed", fg="green")

            except subprocess.CalledProcessError as e:
                log_text.insert(tk.END, f"Download error: {e}\n")
                progress.config(text="Download failed", fg="red")
                root.update_idletasks()

        threading.Thread(target=download_thread, daemon=True).start()
        progress.config(text="Downloading...", fg="blue")

    button_start = tk.Button(root, text="Start download", command=start_download, bg="#4CAF50", fg="white", font=('Arial', 12))
    button_start.pack(pady=10)

    button_cancel = tk.Button(root, text="Cancel", command=root.quit, bg="#f44336", fg="white", font=('Arial', 12))
    button_cancel.pack(pady=10)

    set_language(language.get())
    root.mainloop()

if __name__ == "__main__":
    download_tiktok_user()
