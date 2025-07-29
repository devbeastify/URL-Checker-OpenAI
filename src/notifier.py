import time
from win10toast_click import ToastNotifier
import os
import threading

def show_modal(title, message):
    import tkinter as tk
    from tkinter import messagebox
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo(title, message)
    root.destroy()

def notify(message, title="LinkedIn Checker", icon_path=None, duration=10, delay=0.5, success=None, message_for_modal=None):
    time.sleep(delay)
    toaster = ToastNotifier()
    emoji = "✅" if success is True else ("❌" if success is False else "🔔")
    if icon_path is None:
        icon_path = os.path.join(os.path.dirname(__file__), "..", "icon.ico")
        if not os.path.exists(icon_path):
            icon_path = None
    formatted_title = f"{emoji} {title}"
    formatted_message = f"\n{message.strip()}\n"
    # Use message_for_modal if provided, else use notification message
    modal_message = message_for_modal if message_for_modal else formatted_message
    def on_click():
        import tkinter as tk
        from tkinter import scrolledtext
        root = tk.Tk()
        root.title("LinkedIn URL Results")
        root.geometry("600x400")
        txt = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Segoe UI", 11))
        txt.insert(tk.END, modal_message)
        txt.configure(state='disabled')
        txt.pack(expand=True, fill='both', padx=10, pady=10)
        btn = tk.Button(root, text="Close", command=root.destroy)
        btn.pack(pady=10)
        root.mainloop()
    toaster.show_toast(
        formatted_title,
        formatted_message,
        icon_path=icon_path,
        duration=duration,
        threaded=True,
        callback_on_click=on_click
    )
