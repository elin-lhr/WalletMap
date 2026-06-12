from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    cookie_consent = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    spese = db.relationship('Spesa', backref='user', lazy=True)
    budgets = db.relationship('Budget', backref='user', lazy=True)
    abbonamenti = db.relationship('Abbonamento', backref='user', lazy=True)
    liste_spesa = db.relationship('ListaSpesa', backref='user', lazy=True)

    def set_password(self, password):
        # pbkdf2:sha256 — werkzeug's default (scrypt) needs OpenSSL, not LibreSSL on macOS Python builds
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Spesa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    importo = db.Column(db.Float, nullable=False)
    categoria = db.Column(db.String(50), nullable=False)
    data = db.Column(db.Date, nullable=False)
    nota = db.Column(db.String(200))
    tipo = db.Column(db.String(10), nullable=False)  # 'entrata' o 'uscita'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    categoria = db.Column(db.String(50), nullable=False)
    limite_mensile = db.Column(db.Float, nullable=False)
    mese = db.Column(db.String(7), nullable=False)  # formato 'YYYY-MM'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class Abbonamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    importo = db.Column(db.Float, nullable=False)
    ciclo = db.Column(db.String(20), nullable=False)  # 'mensile'/'trimestrale'/'annuale'
    prossimo_rinnovo = db.Column(db.Date, nullable=False)
    giorni_preavviso = db.Column(db.Integer, default=3)
    attivo = db.Column(db.Boolean, default=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class ListaSpesa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    data = db.Column(db.Date, nullable=False)
    prodotti = db.Column(db.Text)  # JSON string
    totale_stimato = db.Column(db.Float, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
