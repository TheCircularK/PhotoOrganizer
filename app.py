import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import os
from utils import *

def open_log_window():
    """
    Opens the log window if it doesn't exist yet.
    Returns the ScrolledText widget.
    """
    global log_window, log_text
    try:
        if log_window.winfo_exists():
            log_window.lift()
            return log_text
    except NameError:
        pass

    log_window = tk.Toplevel(window)
    log_window.title("Operation Log")
    log_window.geometry("800x600")

    log_text = scrolledtext.ScrolledText(log_window, wrap=tk.WORD)
    log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    log_text.insert(tk.END, "=== Log Started ===\n")
    log_text.focus()

    return log_text


def append_log(line: str):
    """
    Append a single line to the log window.
    """
    log_widget = open_log_window()

    def insert_line():
        log_widget.insert(tk.END, line + "\n")
        log_widget.see(tk.END)

    log_widget.after(0, insert_line)


def run_organizer():
    source = source_library_entry.get()
    destination = destination_path_input.get() or source

    append_log(f"Source: {source}")
    append_log(f"Destination: {destination}")
    append_log(f"Organize: {organize.get()}")
    append_log(f"Rename: {rename.get()}")
    append_log(f"Dry run: {dry_run.get()}")

    source_path = Path(source)
    destination_path = Path(destination)
    organize_enabled = organize.get()
    rename_enabled=rename.get()
    dry_run_enabled = dry_run.get()

    handle_files(source_folder=source_path, rename_enabled=rename_enabled, organize_enabled=organize_enabled, organize_dir=destination_path, dry_run=dry_run_enabled, logger=append_log)

    append_log("=== Finished ===")

def toggle_destination():
    state = "normal" if organize.get() else "disabled"
    destination_path_input.configure(state=state)
    dest_browse_button.configure(state=state)


def browse_source():
    folder = filedialog.askdirectory(title="Select Source Folder", initialdir=os.path.expanduser("~"))
    if folder:
        source_library_entry.delete(0, tk.END)
        source_library_entry.insert(0, folder)
        if not destination_path_input.get():
            destination_path_input.delete(0, tk.END)
            destination_path_input.insert(0, folder)


def browse_destination():
    folder = filedialog.askdirectory(title="Select Destination Folder", initialdir=os.path.expanduser("~"))
    if folder:
        destination_path_input.delete(0, tk.END)
        destination_path_input.insert(0, folder)


if __name__ == "__main__":
    window = tk.Tk()
    window.title("Photo Organizer")
    window.geometry("1500x850")

    # Main frame
    frame = ttk.Frame(window, padding=20)
    frame.pack(fill=tk.BOTH, expand=True)
    frame.columnconfigure(1, weight=1)

    # Title
    title_label = ttk.Label(
        frame,
        text="Organize / Rename Photos",
        font=("Segoe UI", 16, "bold")
    )
    title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

    # Source
    ttk.Label(frame, text="Source:").grid(row=1, column=0, sticky="w", pady=5)
    source_library_entry = ttk.Entry(frame)
    source_library_entry.grid(row=1, column=1, sticky="ew", pady=5)
    source_browse_button = ttk.Button(frame, text="Browse", command=browse_source)
    source_browse_button.grid(row=1, column=2, padx=(10, 0), pady=5)

    # Organize checkbox
    organize = tk.BooleanVar(value=True)
    organize_checkbox = ttk.Checkbutton(
        frame,
        text="Organize",
        variable=organize,
        command=toggle_destination
    )
    organize_checkbox.grid(row=2, column=0, sticky="w", pady=(10, 5))

    # Destination
    ttk.Label(frame, text="Destination Path:").grid(row=3, column=0, sticky="w", pady=5)
    destination_path_input = ttk.Entry(frame)
    destination_path_input.grid(row=3, column=1, sticky="ew", pady=5)
    dest_browse_button = ttk.Button(frame, text="Browse", command=browse_destination)
    dest_browse_button.grid(row=3, column=2, padx=(10, 0), pady=5)

    # Rename checkbox
    rename = tk.BooleanVar(value=True)
    rename_checkbox = ttk.Checkbutton(frame, text="Rename", variable=rename)
    rename_checkbox.grid(row=4, column=0, sticky="w", pady=(10, 5))

    # Dry run checkbox
    dry_run = tk.BooleanVar(value=True)
    dry_run_checkbox = ttk.Checkbutton(frame, text="Dry run", variable=dry_run)
    dry_run_checkbox.grid(row=5, column=0, sticky="w", pady=5)

    # Run button
    run_button = ttk.Button(frame, text="Run", command=run_organizer)
    run_button.grid(row=6, column=0, columnspan=3, pady=(20, 0))

    toggle_destination()
    window.mainloop()
