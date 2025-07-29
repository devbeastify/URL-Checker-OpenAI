import re
def extract_domain_and_identifier(url):
    # Extract domain and last identifier from a URL, normalize www. and leading underscores
    match = re.match(r"https?://([^/]+)/.*?([\w\-]+)[/?]?$", url)
    if match:
        domain = match.group(1).lower().lstrip('_')
        if domain.startswith('www.'):
            domain = domain[4:]
        identifier = match.group(2).lower()
        return domain, identifier
    # fallback: try to get domain and last path segment
    try:
        domain = url.split('/')[2].lower().lstrip('_')
        if domain.startswith('www.'):
            domain = domain[4:]
        identifier = url.rstrip('/').split('/')[-1].lower()
        return domain, identifier
    except Exception:
        return url.lower(), url.lower()
def is_existing_url(url, clients):
    # Compare by domain and last identifier
    url_domain, url_id = extract_domain_and_identifier(url)
    for client in clients:
        c_domain, c_id = extract_domain_and_identifier(client)
        if url_domain == c_domain and url_id == c_id:
            return True, client
    # Fuzzy match with OpenAI on domain and identifier
    client_pairs = [extract_domain_and_identifier(c) for c in clients]
    prompt = (
        f"Given this found URL: {url}\n"
        f"Domain: {url_domain}\nIdentifier: {url_id}\n"
        f"Which of these client URLs is the closest match by domain and identifier?\n"
        + '\n'.join([f"{i+1}. {c} (Domain: {d}, Identifier: {idn})" for i, (c, (d, idn)) in enumerate(zip(clients, client_pairs))])
        + "\nAnswer with the full client URL or 'None'."
    )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for fuzzy URL matching. Focus on domain and last identifier."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100
        )
        answer = response.choices[0].message['content'].strip()
    except Exception:
        answer = None
    if answer and answer.lower() != 'none':
        for client in clients:
            if client.strip() == answer.strip():
                return True, client
    return False, None

import openai
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

from client_db import load_clients

def is_existing_client(profile_name, clients):
    for client in clients:
        if client.lower() == profile_name.lower():
            return True, client
    # Fuzzy match with OpenAI
    prompt = f"Is '{profile_name}' the same as any of these names? {', '.join(clients)}. Answer with the closest match or 'None'."
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for fuzzy name matching."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=10
        )
        answer = response.choices[0].message['content'].strip()
    except Exception:
        answer = None
    if answer and answer.lower() != 'none':
        for client in clients:
            if client.lower() == answer.lower():
                return True, client
    return False, None
