import pyautogui
import os
import time

def take_screenshot(save_dir="screenshots", region=None):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    file_path = os.path.join(save_dir, f"screenshot_{timestamp}.png")
    screenshot = pyautogui.screenshot(region=region)
    screenshot.save(file_path)
    return file_path
