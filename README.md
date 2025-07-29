# LinkedIn Screenshot OCR Client Checker

A modular Python project inspired by ScreenOCR-PythonIA. Take screenshots, extract text with Tesseract OCR, compare names to a client list (CSV), and show Windows notifications.

## Features
- Take screenshots of LinkedIn profiles or My Network page
- Extract text using Tesseract OCR
- Compare extracted names to your client list (CSV)
- Show clear Windows notifications for matches
- Modular and easy to extend

## Setup
1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
2. Install Tesseract OCR and add it to your PATH
3. Add your OpenAI API key to `config.py` (for fuzzy matching)
4. Add your client names (one per line) to `clients.csv`

## Usage
- Run `python main.py` and follow the prompts
- Press the hotkey to take a screenshot and check the profile
- For batch analysis, place screenshots in the `screenshots/` folder and run `python main.py analyze_network`

## Notes
- Screenshots are saved in the `screenshots/` folder
- OCR accuracy depends on screenshot quality and LinkedIn UI
- This project does not use browser automation and is compliant with LinkedIn's terms
