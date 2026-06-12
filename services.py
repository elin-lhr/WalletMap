from __future__ import annotations  # consente 'dict | None' anche su Python 3.9

import os
import json
import requests
from flask import current_app
from groq import Groq


def stima_prezzi(prodotti: list[str]) -> dict | None:
    api_key = os.environ.get('GROQ_API_KEY')
    client = Groq(api_key=api_key, timeout=5)

    lista = '\n'.join(f'- {p}' for p in prodotti)
    prompt = (
        'Stima il prezzo medio in euro per ciascuno dei seguenti prodotti '
        'in un supermercato italiano.\n'
        'Rispondi SOLO con un oggetto JSON valido, senza testo aggiuntivo, '
        'senza markdown, senza backtick.\n'
        'Formato: {"prodotto": prezzo_float, "prodotto2": prezzo_float}\n'
        'Esempio: {"latte": 1.30, "pane": 2.50, "pasta": 1.20}\n\n'
        f'Prodotti:\n{lista}'
    )

    try:
        result = client.chat.completions.create(
            model='llama-3.1-8b-instant',
            max_tokens=500,
            messages=[{'role': 'user', 'content': prompt}],
        )
        raw = result.choices[0].message.content.strip()
        prezzi = json.loads(raw)
        prodotti_out = [
            {'nome': nome, 'prezzo_stimato': float(prezzo)}
            for nome, prezzo in prezzi.items()
        ]
        totale = round(sum(p['prezzo_stimato'] for p in prodotti_out), 2)
        return {'prodotti': prodotti_out, 'totale': totale}
    except Exception:
        # Errore di rete/timeout/risposta non valida: il chiamante gestisce None.
        return None


def get_tasso_cambio(valuta: str) -> float | None:
    # EUR è la valuta base: nessuna chiamata API necessaria.
    if valuta == 'EUR':
        return 1.0

    api_key = current_app.config.get('EXCHANGERATE_API_KEY', '')
    url = f'https://v6.exchangerate-api.com/v6/{api_key}/latest/EUR'

    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        # Tasso EUR -> valuta richiesta (es. 1 EUR = 1.08 USD).
        return float(data['conversion_rates'][valuta])
    except Exception:
        # Timeout/ConnectionError/HTTPError/KeyError: il chiamante gestisce None.
        return None
