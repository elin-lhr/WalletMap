import pytest
import sqlalchemy as sa
from sqlalchemy.pool import StaticPool


@pytest.fixture
def app():
    from config import config_map
    from app import app, db
    app.config.from_object(config_map['testing'])

    # Flask-SQLAlchemy locks the engine at init_app time and re-calling init_app
    # is forbidden after the first request. Instead, replace the cached engine
    # directly. StaticPool makes every checkout reuse the same connection, which
    # is required for sqlite:///:memory: so that create_all and the session see
    # the same in-memory database.
    engine = sa.create_engine(
        'sqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )
    db._app_engines[app] = {None: engine}

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def test_user(app):
    from models import db, User
    with app.app_context():
        user = User(username='testuser', email='test@walletmap.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        return user
