
import keyboard
import os

import re
import pyautogui
from notifier import notify
from client_matcher import is_existing_url
from client_db import load_clients, init_db, import_from_csv


CLIENTS_CSV = os.path.join(os.path.dirname(__file__), '..', 'clients.csv')
init_db()
# Import from CSV if DB is empty
if os.path.exists(CLIENTS_CSV) and not load_clients():
    import_from_csv(CLIENTS_CSV)



def get_url_from_address_bar():
    # Screenshot the full screen
    from screenshot_util import take_screenshot
    from ocr_util import extract_text_from_image
    screenshot_path = take_screenshot(region=None)
    text = extract_text_from_image(screenshot_path)
    print("\n--- OCR of full screen ---\n")
    print(text)
    print("\n----------------------\n")
    # Extract all LinkedIn profile URLs from the OCR text
    url_pattern = r"((https?://)?([\w\-\.]+\.)?linkedin\.com/in/[\w\-]+)"
    matches = re.findall(url_pattern, text, re.IGNORECASE)
    linkedin_urls = []
    for match in matches:
        url = match[0]
        if not url.startswith('http'):
            url = 'https://' + url.lstrip('/').replace(' ', '')
        linkedin_urls.append(url)
    # If none found, try OpenAI as fallback
    if not linkedin_urls:
        try:
            import openai
            import sys
            import os
            sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
            from config import OPENAI_API_KEY
            openai.api_key = OPENAI_API_KEY
            prompt = (
                "Extract all LinkedIn profile URLs from this browser address bar OCR text. "
                "If the protocol is missing, add https://. Return one URL per line. If there are no valid URLs, answer 'None'.\n\n" + text)
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that extracts all LinkedIn profile URLs from OCR text of browser address bars. Always return the full URL with https:// if missing, one per line."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200
            )
            answer = response.choices[0].message['content'].strip()
            if answer.lower() != 'none':
                for line in answer.splitlines():
                    line = line.strip()
                    if line and 'linkedin.com/in/' in line:
                        if not line.startswith('http'):
                            line = 'https://' + line.lstrip('/').replace(' ', '')
                        linkedin_urls.append(line)
        except Exception as e:
            print(f"OpenAI extraction failed: {e}")
    if not linkedin_urls:
        notify('No LinkedIn profile URL detected in screenshot. Please make sure the URL is visible.', success=None)
    return linkedin_urls

def check_address_bar_url():
    urls = get_url_from_address_bar()
    if not urls:
        return
    print(f"\n--- LinkedIn URLs from screenshot OCR ---\n" + '\n'.join(urls) + "\n----------------------\n")
    # Always reload the client database to reflect updates
    clients = load_clients(CLIENTS_CSV)
    results = []
    for url in urls:
        exists, client_val = is_existing_url(url, clients)
        if exists:
            results.append(f"{url}\n✔️ Already in your client list!\nMatched entry: {client_val}")
        else:
            results.append(f"{url}\n❌ NOT in your client list.")
    message = "LinkedIn URLs found:\n\n" + "\n\n".join(results)
    # Success if any found in client list
    success = any(is_existing_url(url, clients)[0] for url in urls)
    # Show summary in notification
    summary = f"{len(urls)} LinkedIn URL(s) found."
    if any('✔️' in r for r in results):
        summary += " Some are in your client list."
    else:
        summary += " None are in your client list."
    # Pass the full message to the notifier, so modal is shown only when notification is clicked
    notify(summary, success=success, message_for_modal=message)

if __name__ == "__main__":
    print("Press z+1 to screenshot the address bar, extract the URL, and check against your client list...")
    keyboard.add_hotkey('z+1', check_address_bar_url)
    keyboard.wait('esc')
