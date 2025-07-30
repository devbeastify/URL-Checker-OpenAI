import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
import importlib
client_db = importlib.import_module('client_db')
import threading

class Dashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Client Checker Dashboard")
        self.geometry("700x400")
        self.resizable(False, False)
        self.create_widgets()
        self.refresh_client_list()

    def create_widgets(self):
        # Client List
        self.client_list = ttk.Treeview(self, columns=("URL",), show="headings")
        self.client_list.heading("URL", text="Client URL")
        self.client_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Buttons
        btn_frame = tk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Button(btn_frame, text="Add Client", command=self.add_client).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Remove Selected", command=self.remove_selected).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Refresh", command=self.refresh_client_list).pack(side=tk.LEFT, padx=5)
        self.checker_btn = tk.Button(btn_frame, text="Start Checker", command=self.toggle_checker)
        self.checker_btn.pack(side=tk.RIGHT, padx=5)
        self.checker_process = None

        # Status
        self.status = tk.StringVar()
        self.status.set("Ready.")
        tk.Label(self, textvariable=self.status, anchor="w").pack(fill=tk.X, padx=10, pady=(0,10))

    def refresh_client_list(self):
        for row in self.client_list.get_children():
            self.client_list.delete(row)
        clients = client_db.get_all_clients()
        for url in clients:
            self.client_list.insert('', 'end', values=(url,))
        self.status.set(f"Loaded {len(clients)} clients.")

    def add_client(self):
        url = simpledialog.askstring("Add Client", "Enter client URL:")
        if url:
            if client_db.add_client(url):
                self.status.set("Client added.")
                self.refresh_client_list()
            else:
                messagebox.showerror("Error", "Client already exists or invalid.")

    def remove_selected(self):
        selected = self.client_list.selection()
        if not selected:
            messagebox.showinfo("Remove Client", "No client selected.")
            return
        for item in selected:
            url = self.client_list.item(item, 'values')[0]
            client_db.remove_client(url)
        self.status.set("Client(s) removed.")
        self.refresh_client_list()


    def toggle_checker(self):
        if self.checker_process is None:
            self.start_checker()
        else:
            self.stop_checker()

    def start_checker(self):
        self.status.set("Running checker...")
        self.checker_btn.config(text="Stop Checker")
        threading.Thread(target=self.run_main, daemon=True).start()

    def stop_checker(self):
        if self.checker_process is not None:
            try:
                self.checker_process.terminate()
                self.status.set("Checker stopped.")
            except Exception as e:
                self.status.set(f"Error stopping: {e}")
            self.checker_process = None
            self.checker_btn.config(text="Start Checker")

    def run_main(self):
        import subprocess
        try:
            self.checker_process = subprocess.Popen([sys.executable, os.path.join('src', 'main.py')], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = self.checker_process.communicate()
            if self.checker_process.returncode == 0:
                self.status.set("Checker finished.")
                output = stdout.strip()
                if output:
                    messagebox.showinfo("Checker Output", output)
            else:
                self.status.set("Checker error.")
                messagebox.showerror("Error", stderr.strip() or "Unknown error.")
        except Exception as e:
            self.status.set(f"Error: {e}")
            messagebox.showerror("Error", str(e))
        finally:
            self.checker_process = None
            self.checker_btn.config(text="Start Checker")

if __name__ == "__main__":
    Dashboard().mainloop()
