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

def notify(message, title="LinkedIn Checker", icon_path=None, duration=10, delay=0.5, success=None):
    time.sleep(delay)
    toaster = ToastNotifier()
    emoji = "✅" if success is True else ("❌" if success is False else "🔔")
    if icon_path is None:
        icon_path = os.path.join(os.path.dirname(__file__), "..", "icon.ico")
        if not os.path.exists(icon_path):
            icon_path = None
    formatted_title = f"{emoji} {title}"
    formatted_message = f"\n{message.strip()}\n"
    def on_click():
        threading.Thread(target=show_modal, args=(formatted_title, formatted_message)).start()
    toaster.show_toast(
        formatted_title,
        formatted_message,
        icon_path=icon_path,
        duration=duration,
        threaded=True,
        callback_on_click=on_click
    )
