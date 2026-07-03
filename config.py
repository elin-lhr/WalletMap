import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI', 'sqlite:///walletmap.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {'pool_pre_ping': True}
    GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '')
    EXCHANGERATE_API_KEY = os.environ.get('EXCHANGERATE_API_KEY', '')

    # Sicurezza cookie di sessione
    SESSION_COOKIE_HTTPONLY = True   # il cookie non è leggibile via JavaScript
    SESSION_COOKIE_SAMESITE = 'Lax'  # mitigazione CSRF di base

    # Durata della sessione "Ricordami" (quando session.permanent = True)
    PERMANENT_SESSION_LIFETIME = timedelta(days=30)


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True  # cookie inviato solo su HTTPS (attivo solo in prod)
    _db_url = os.environ.get('DATABASE_URL', '')
    SQLALCHEMY_DATABASE_URI = (
        _db_url.replace('postgres://', 'postgresql://', 1)
        if _db_url else Config.SQLALCHEMY_DATABASE_URI
    )


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
}
