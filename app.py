import os
from functools import wraps
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session
from models import db, User, Spesa, Budget, Abbonamento, ListaSpesa
from forms import LoginForm, RegisterForm, SpesaForm, BudgetForm, AbbonamentoForm, ListaSpesaForm
from config import config_map

app = Flask(__name__)
env = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config_map.get(env, config_map['development']))

db.init_app(app)


# ========== Auth Decorators ==========

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            flash('Devi effettuare il login', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper


@app.context_processor
def inject_globals():
    user_id = session.get('user_id')
    current_user = User.query.get(user_id) if user_id else None
    return {'current_user': current_user, 'current_year': datetime.utcnow().year}


# ========== Public Routes ==========

@app.route('/')
def index():
    return render_template('index.html')


# ========== Auth Routes ==========

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data.strip()
        password = form.password.data

        user = User.query.filter_by(username=username).first()
        if user is None or not user.check_password(password):
            flash('Username o password errati', 'error')
            return render_template('login.html', form=form)

        session['user_id'] = user.id
        flash('Login effettuato!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    session.clear()
    flash('Logout effettuato', 'success')
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data.strip()
        email = form.email.data.strip().lower()
        password = form.password.data

        if User.query.filter_by(username=username).first():
            flash('Username già in uso.', 'error')
            return render_template('register.html', form=form)

        if User.query.filter_by(email=email).first():
            flash('Email già registrata.', 'error')
            return render_template('register.html', form=form)

        user = User(username=username, email=email)
        user.set_password(password)

        try:
            db.session.add(user)
            db.session.commit()
        except Exception:
            db.session.rollback()
            flash('Errore durante la creazione dell\'account. Riprova.', 'error')
            return render_template('register.html', form=form)

        flash('Account creato! Ora puoi fare login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)


@app.route('/profile')
@login_required
def profile():
    user = User.query.get(session['user_id'])
    spese_count = Spesa.query.filter_by(user_id=user.id).count()
    budget_count = Budget.query.filter_by(user_id=user.id).count()
    abbonamenti_count = Abbonamento.query.filter_by(user_id=user.id, attivo=True).count()

    return render_template(
        'profile.html',
        user=user,
        spese_count=spese_count,
        budget_count=budget_count,
        abbonamenti_count=abbonamenti_count,
    )


# ========== WalletMap Routes ==========

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template('dashboard.html')


@app.route('/registro', methods=['GET', 'POST'])
@login_required
def registro():
    form = SpesaForm()
    if form.validate_on_submit():
        spesa = Spesa(
            importo=form.importo.data,
            categoria=form.categoria.data,
            data=form.data.data,
            nota=form.nota.data,
            tipo=form.tipo.data,
            user_id=session['user_id'],
        )
        db.session.add(spesa)
        db.session.commit()
        flash('Spesa aggiunta!', 'success')
        return redirect(url_for('registro'))

    spese = (
        Spesa.query
        .filter_by(user_id=session['user_id'])
        .order_by(Spesa.data.desc())
        .all()
    )
    totale_entrate = sum(s.importo for s in spese if s.tipo == 'entrata')
    totale_uscite = sum(s.importo for s in spese if s.tipo == 'uscita')
    saldo = totale_entrate - totale_uscite

    return render_template(
        'registro.html',
        form=form,
        spese=spese,
        totale_entrate=totale_entrate,
        totale_uscite=totale_uscite,
        saldo=saldo,
    )


@app.route('/registro/elimina/<int:id>', methods=['POST'])
@login_required
def elimina_spesa(id):
    spesa = Spesa.query.get_or_404(id)
    if spesa.user_id != session['user_id']:
        flash('Non autorizzato', 'error')
        return redirect(url_for('registro'))
    db.session.delete(spesa)
    db.session.commit()
    flash('Spesa eliminata', 'success')
    return redirect(url_for('registro'))


@app.route('/budget', methods=['GET', 'POST'])
@login_required
def budget():
    form = BudgetForm()
    return render_template('budget.html', form=form)


@app.route('/abbonamenti', methods=['GET', 'POST'])
@login_required
def abbonamenti():
    form = AbbonamentoForm()
    return render_template('abbonamenti.html', form=form)


@app.route('/lista-spesa', methods=['GET', 'POST'])
@login_required
def lista_spesa():
    form = ListaSpesaForm()
    return render_template('lista_spesa.html', form=form)


@app.route('/export/csv')
@login_required
def export_csv():
    return 'coming soon'


with app.app_context():
    db.create_all()


# ========== Error Handlers ==========

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    db.session.rollback()
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run(debug=True, port=5001)
