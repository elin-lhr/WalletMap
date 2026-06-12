# 💸 WalletMap

[![Live on Render](https://img.shields.io/badge/Live%20App-Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)](https://walletmap.onrender.com)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)

> WalletMap è un'app web di **finanza personale** che ti aiuta a tenere traccia di entrate, uscite, budget mensili e abbonamenti — con una lista della spesa intelligente che stima i prezzi in tempo reale grazie all'AI di Groq.

---

## ✨ Features

| Feature | Descrizione |
|---|---|
| 🔐 **Autenticazione** | Registrazione, login e logout con password hashate sicure |
| 📊 **Dashboard** | Panoramica mensile con saldo, grafici per categoria e andamento degli ultimi 6 mesi |
| 📝 **Registro spese** | Aggiungi e cancella entrate/uscite con data, categoria e nota |
| 💰 **Budget mensile** | Imposta un limite di spesa per categoria e monitora l'avanzamento con barre di progresso |
| 🔄 **Abbonamenti** | Tieni traccia dei rinnovi (mensile/trimestrale/annuale) con alert automatici a 7 giorni |
| 🛒 **Lista della spesa AI** | Inserisci i prodotti e ottieni una stima dei prezzi al supermercato grazie a Groq + Llama 3 |
| 📤 **Export dati** | Scarica tutte le tue spese in formato **CSV** o **Excel (.xlsx)** con un click |
| 👤 **Profilo utente** | Statistiche personali: spese registrate, budget attivi, abbonamenti in corso |
| 🛡️ **Pagine di errore** | Gestione personalizzata degli errori 404 e 500 |

---

## 🛠️ Tech Stack

| Tecnologia | Ruolo |
|---|---|
| **Python 3.11** | Linguaggio principale |
| **Flask 3.1** | Web framework |
| **SQLAlchemy / Flask-SQLAlchemy** | ORM e gestione database (SQLite in dev, PostgreSQL in prod) |
| **Flask-WTF / WTForms** | Gestione form e protezione CSRF |
| **Groq API** (Llama 3.1) | Stima AI dei prezzi nella lista della spesa |
| **openpyxl** | Generazione file Excel per l'export |
| **psycopg2-binary** | Driver PostgreSQL per la produzione |
| **Werkzeug** | Hashing sicuro delle password |
| **Gunicorn** | WSGI server per la produzione |
| **Render** | Piattaforma di deploy cloud |
| **python-dotenv** | Gestione variabili d'ambiente |

---

## 🚀 Installazione locale

### 1. Clona il repository

```bash
git clone https://github.com/elin-lhr/WalletMap.git
cd WalletMap
```

### 2. Crea e attiva il virtual environment

```bash
python -m venv venv
```

**macOS / Linux:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

### 3. Installa le dipendenze

```bash
pip install -r requirements.txt
```

### 4. Configura le variabili d'ambiente

```bash
cp .env.example .env
```

Apri `.env` e compila i valori richiesti (vedi sezione [Variabili d'ambiente](#️-variabili-dambiente)).

### 5. Avvia l'applicazione

```bash
flask run --debug
```

L'app sarà disponibile su [http://localhost:5000](http://localhost:5000) 🎉

---

## ⚙️ Variabili d'ambiente

Crea un file `.env` nella root del progetto partendo da `.env.example` e compila le seguenti variabili:

```env
SECRET_KEY=          # Chiave segreta Flask — genera con: python3 -c "import secrets; print(secrets.token_hex(32))"
DATABASE_URI=        # URI del database (es. sqlite:///walletmap.db oppure postgres://...)
GROQ_API_KEY=        # API key di Groq (https://console.groq.com) — usata per la lista della spesa AI
FLASK_ENV=           # "development" in locale, "production" su Render
```

> ⚠️ **Non committare mai il file `.env` su Git.** È già incluso nel `.gitignore`.

---

## ☁️ Deploy

L'app è deployata su **Render** con Gunicorn come server WSGI.

🔗 **App live:** [https://walletmap.onrender.com](https://walletmap.onrender.com)

Il file `Procfile` contiene il comando di avvio:

```
web: gunicorn app:app
```

Per deployare la tua versione su Render:
1. Crea un nuovo **Web Service** su [render.com](https://render.com)
2. Collega il repository GitHub `elin-lhr/WalletMap`
3. Imposta le variabili d'ambiente nella dashboard di Render
4. Render rileva automaticamente il `Procfile` e avvia l'app

---

## 📁 Struttura del progetto

```
WalletMap/
├── app.py              # Entry point e definizione di tutte le route
├── models.py           # Modelli DB: User, Spesa, Budget, Abbonamento, ListaSpesa
├── forms.py            # Form Flask-WTF (Login, Register, Spesa, Budget, Abbonamento, ListaSpesa)
├── services.py         # Integrazione Groq API per la stima prezzi
├── config.py           # Configurazioni per dev/prod/test
├── requirements.txt    # Dipendenze Python
├── Procfile            # Comando di avvio per Render
├── runtime.txt         # Versione Python per Render
├── .env.example        # Template variabili d'ambiente
├── static/
│   └── css/            # Fogli di stile
└── templates/          # Template Jinja2 (dashboard, registro, budget, abbonamenti…)
```

---

## 👤 Autore

**elin-lhr** — [GitHub](https://github.com/elin-lhr)
