from datetime import date
from models import User, Spesa


def test_user_creation():
    user = User(username='mario', email='mario@test.com')
    assert user.username == 'mario'
    assert user.email == 'mario@test.com'


def test_password_hashing():
    user = User(username='mario', email='mario@test.com')
    user.set_password('password123')
    assert user.check_password('password123') is True


def test_password_not_in_plain():
    user = User(username='mario', email='mario@test.com')
    user.set_password('password123')
    assert 'password123' not in user.password_hash


def test_spesa_creation(app):
    from models import db, User, Spesa
    # Use the outer app context provided by the fixture — no nested context.
    # sqlite:///:memory: opens a fresh DB per connection; nesting would get a
    # second empty connection with no tables.
    user = User(username='mario', email='mario@test.com')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()

    spesa = Spesa(
        importo=50.0,
        categoria='Alimentari',
        tipo='uscita',
        data=date.today(),
        user_id=user.id,
    )
    db.session.add(spesa)
    db.session.commit()

    assert spesa.importo == 50.0
    assert spesa.categoria == 'Alimentari'
