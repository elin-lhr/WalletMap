import os
import json
from groq import Groq


def stima_prezzi(prodotti: list[str]) -> dict:
    api_key = os.environ.get('GROQ_API_KEY')
    client = Groq(api_key=api_key)

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
        return {'prodotti': [], 'totale': 0.0, 'errore': 'Stima non disponibile'}
