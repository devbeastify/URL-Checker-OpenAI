
import keyboard
import os

import re
import pyautogui
from notifier import notify
from client_matcher import load_clients, is_existing_url

CLIENTS_CSV = os.path.join(os.path.dirname(__file__), '..', 'clients.csv')



def get_url_from_address_bar():
    # Screenshot the top portion of the screen (address bar area)
    screen_width, screen_height = pyautogui.size()
    # Adjust these values as needed for your browser UI
    region = (0, 0, screen_width, 120)  # x, y, width, height
    from screenshot_util import take_screenshot
    from ocr_util import extract_text_from_image
    screenshot_path = take_screenshot(region=region)
    text = extract_text_from_image(screenshot_path)
    print("\n--- OCR of address bar area ---\n")
    print(text)
    print("\n----------------------\n")
    # Match URLs with or without protocol
    url_pattern = r"(https?://)?([\w\-\.]+\.[a-z]{2,})(/[\w\-\._~:/?#\[\]@!$&'()*+,;=%]*)?"
    matches = re.findall(url_pattern, text, re.IGNORECASE)
    urls = []
    for match in matches:
        proto, domain, path = match
        if domain:
            url = (proto if proto else 'https://') + domain + (path if path else '')
            urls.append(url)
    if urls:
        return urls[0]
    # If regex fails, use OpenAI to extract the URL
    try:
        import openai
        import sys
        import os
        sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
        from config import OPENAI_API_KEY
        openai.api_key = OPENAI_API_KEY
        prompt = f"Extract the full URL (with https:// if missing) from this browser address bar OCR text. If no valid URL, answer 'None'.\n\n{text}"
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts URLs from OCR text of browser address bars. Always return the full URL with https:// if missing."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100
        )
        answer = response.choices[0].message['content'].strip()
        if answer.lower() != 'none':
            # Prepend https:// if missing
            if not answer.startswith('http'):
                answer = 'https://' + answer
            return answer
    except Exception as e:
        print(f"OpenAI extraction failed: {e}")
    notify('No URL detected in address bar screenshot. Please make sure the URL is visible.', success=None)
    return None

def check_address_bar_url():
    url = get_url_from_address_bar()
    if not url:
        return
    print(f"\n--- URL from address bar OCR ---\n{url}\n----------------------\n")
    # Always reload the client database to reflect updates
    clients = load_clients(CLIENTS_CSV)
    exists, client_val = is_existing_url(url, clients)
    if exists:
        message = f"Found URL:\n{url}\n\nResult: This URL is already in your client list!\n\nMatched entry:\n{client_val}"
        notify(message, success=True)
    else:
        message = f"Found URL:\n{url}\n\nResult: This URL is NOT in your client list."
        notify(message, success=False)

if __name__ == "__main__":
    print("Press z+1 to screenshot the address bar, extract the URL, and check against your client list...")
    keyboard.add_hotkey('z+1', check_address_bar_url)
    keyboard.wait('esc')
