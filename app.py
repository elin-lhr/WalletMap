import os
import io
import csv
import json
import calendar
from functools import wraps
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import openpyxl
from openpyxl.styles import Font
from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import inspect, text
from models import db, User, Spesa, Budget, Abbonamento, ListaSpesa
from forms import LoginForm, RegisterForm, SpesaForm, BudgetForm, AbbonamentoForm, ListaSpesaForm, CambioPasswordForm
from config import config_map
from services import stima_prezzi, get_tasso_cambio

app = Flask(__name__)
env = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config_map.get(env, config_map['development']))

# SECRET_KEY: obbligatoria in produzione, fallback insicuro solo in sviluppo.
if not app.config.get('SECRET_KEY'):
    if env == 'production':
        raise RuntimeError(
            'SECRET_KEY non impostata: è obbligatoria in produzione. '
            'Configurala nelle variabili d\'ambiente.'
        )
    app.config['SECRET_KEY'] = 'dev-insecure-key-not-for-production'

csrf = CSRFProtect(app)
db.init_app(app)


@app.template_filter('from_json')
def from_json_filter(value):
    try:
        return json.loads(value)
    except Exception:
        return {'prodotti': [], 'totale': 0.0}


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
    current_user = db.session.get(User, user_id) if user_id else None
    return {'current_user': current_user, 'current_year': datetime.utcnow().year}


# ========== Public Routes ==========

@app.route('/')
def index():
    # Se già loggato, la home porta dritto in dashboard (niente landing "Accedi").
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/cookie-consent', methods=['POST'])
def cookie_consent():
    # Funziona anche per utenti anonimi: nessun @login_required.
    user_id = session.get('user_id')
    if user_id:
        user = db.session.get(User, user_id)
        if user:
            user.cookie_consent = True
            db.session.commit()
    # Salva sempre il consenso in sessione: copre anche gli utenti non loggati.
    session['cookie_consent'] = True
    return redirect(request.referrer or url_for('index'))


@app.route('/privacy')
def privacy():
    return render_template('privacy.html')


@app.route('/cookie-policy')
def cookie_policy():
    return render_template('cookie_policy.html')


# ========== Auth Routes ==========

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data.strip()
        password = form.password.data

        user = User.query.filter_by(username=username).first()
        if user is None or not user.check_password(password):
            flash('Username o password errati', 'error')
            return render_template('login.html', form=form)

        session['user_id'] = user.id
        # "Ricordami": sessione persistente (PERMANENT_SESSION_LIFETIME) vs
        # cookie di sessione che scade alla chiusura del browser.
        session.permanent = bool(form.ricordami.data)
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
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
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
    user = db.session.get(User, session['user_id'])
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


@app.route('/delete-account', methods=['POST'])
@login_required
def delete_account():
    user = db.session.get(User, session['user_id'])

    # Elimina prima tutti i dati associati all'utente.
    Spesa.query.filter_by(user_id=user.id).delete()
    Budget.query.filter_by(user_id=user.id).delete()
    Abbonamento.query.filter_by(user_id=user.id).delete()
    ListaSpesa.query.filter_by(user_id=user.id).delete()

    # Poi elimina l'utente.
    db.session.delete(user)
    db.session.commit()
    session.clear()
    flash('Account eliminato con successo', 'success')
    return redirect(url_for('index'))


@app.route('/cambia-password', methods=['GET', 'POST'])
@login_required
def cambia_password():
    form = CambioPasswordForm()
    if form.validate_on_submit():
        user = db.session.get(User, session['user_id'])
        if not user.check_password(form.password_attuale.data):
            flash('Password attuale errata', 'error')
            return render_template('cambia_password.html', form=form)

        user.set_password(form.nuova_password.data)
        db.session.commit()
        flash('Password cambiata con successo!', 'success')
        return redirect(url_for('profile'))

    return render_template('cambia_password.html', form=form)


# ========== WalletMap Routes ==========

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    today = date.today()
    MESI_IT = {1:'Gen',2:'Feb',3:'Mar',4:'Apr',5:'Mag',6:'Giu',
               7:'Lug',8:'Ago',9:'Set',10:'Ott',11:'Nov',12:'Dic'}

    tutte_spese = Spesa.query.filter_by(user_id=session['user_id']).all()
    spese_mese = [s for s in tutte_spese
                  if s.data.month == today.month and s.data.year == today.year]

    totale_entrate = round(sum(s.importo for s in spese_mese if s.tipo == 'entrata'), 2)
    totale_uscite  = round(sum(s.importo for s in spese_mese if s.tipo == 'uscita'),  2)
    saldo = round(totale_entrate - totale_uscite, 2)

    spese_per_categoria: dict = {}
    for s in spese_mese:
        if s.tipo == 'uscita':
            spese_per_categoria[s.categoria] = round(
                spese_per_categoria.get(s.categoria, 0) + s.importo, 2)
    spese_per_categoria = dict(
        sorted(spese_per_categoria.items(), key=lambda x: x[1], reverse=True))

    def _dettaglio(items):
        # Serializza le transazioni per il pop-up di dettaglio (più recenti prima).
        return [
            {
                'data': s.data.strftime('%d/%m/%Y'),
                'categoria': s.categoria,
                'importo': s.importo,
                'nota': s.nota or '',
            }
            for s in sorted(items, key=lambda x: x.data, reverse=True)
        ]

    andamento = []
    for i in range(5, -1, -1):
        mese_dt = today - relativedelta(months=i)
        entrate_items = [s for s in tutte_spese
                         if s.tipo == 'entrata'
                         and s.data.month == mese_dt.month
                         and s.data.year == mese_dt.year]
        uscite_items = [s for s in tutte_spese
                        if s.tipo == 'uscita'
                        and s.data.month == mese_dt.month
                        and s.data.year == mese_dt.year]
        andamento.append({
            'mese': MESI_IT[mese_dt.month],
            'entrate': round(sum(s.importo for s in entrate_items), 2),
            'uscite': round(sum(s.importo for s in uscite_items), 2),
            'entrate_dettaglio': _dettaglio(entrate_items),
            'uscite_dettaglio': _dettaglio(uscite_items),
        })

    vals = [m['entrate'] for m in andamento] + [m['uscite'] for m in andamento]
    max_val = max(vals) if any(v > 0 for v in vals) else 1
    for m in andamento:
        m['h_entrate'] = int((m['entrate'] / max_val) * 160)
        m['h_uscite']  = int((m['uscite']  / max_val) * 160)

    abb_raw = (
        Abbonamento.query
        .filter_by(user_id=session['user_id'], attivo=True)
        .order_by(Abbonamento.prossimo_rinnovo.asc())
        .all()
    )
    # Mostra ogni abbonamento entro la sua finestra di preavviso personale
    # (giorni_preavviso), non un fisso di 7 giorni uguale per tutti.
    abbonamenti_scadenza = [
        {
            'nome': a.nome,
            'importo': a.importo,
            'prossimo_rinnovo': a.prossimo_rinnovo,
            'giorni_rimanenti': (a.prossimo_rinnovo - today).days,
        }
        for a in abb_raw
        if (a.prossimo_rinnovo - today).days <= (a.giorni_preavviso or 0)
    ]

    return render_template(
        'dashboard.html',
        totale_entrate=totale_entrate,
        totale_uscite=totale_uscite,
        saldo=saldo,
        spese_per_categoria=spese_per_categoria,
        andamento=andamento,
        abbonamenti_scadenza=abbonamenti_scadenza,
    )


@app.route('/registro', methods=['GET', 'POST'])
@login_required
def registro():
    form = SpesaForm()
    if form.validate_on_submit():
        valuta = form.valuta.data
        if valuta != 'EUR':
            tasso = get_tasso_cambio(valuta)
            if tasso is None:
                flash('Tasso di cambio non disponibile. Spesa salvata in EUR.', 'error')
                importo_eur = form.importo.data
                importo_originale = None
                valuta = 'EUR'
            else:
                importo_originale = form.importo.data
                importo_eur = round(form.importo.data / tasso, 2)
        else:
            importo_eur = form.importo.data
            importo_originale = None

        spesa = Spesa(
            importo=importo_eur,
            categoria=form.categoria.data,
            data=form.data.data,
            nota=form.nota.data,
            tipo=form.tipo.data,
            valuta=valuta,
            importo_originale=importo_originale,
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

    if request.method == 'GET':
        form.mese.data = datetime.utcnow().strftime('%Y-%m')

    if form.validate_on_submit():
        esistente = Budget.query.filter_by(
            categoria=form.categoria.data,
            mese=form.mese.data,
            user_id=session['user_id'],
        ).first()
        if esistente:
            flash('Budget già impostato per questa categoria e mese', 'error')
        else:
            nuovo = Budget(
                categoria=form.categoria.data,
                limite_mensile=form.limite_mensile.data,
                mese=form.mese.data,
                user_id=session['user_id'],
            )
            db.session.add(nuovo)
            db.session.commit()
            flash('Budget impostato!', 'success')
        return redirect(url_for('budget'))

    budgets_raw = (
        Budget.query
        .filter_by(user_id=session['user_id'])
        .order_by(Budget.mese.desc(), Budget.categoria)
        .all()
    )

    budgets = []
    for b in budgets_raw:
        spese_del_mese = [
            s.importo for s in Spesa.query.filter_by(
                user_id=session['user_id'],
                categoria=b.categoria,
                tipo='uscita',
            ).all()
            if s.data.strftime('%Y-%m') == b.mese
        ]
        spese_usate = sum(spese_del_mese)
        percentuale = round(min((spese_usate / b.limite_mensile) * 100, 100), 1) if b.limite_mensile else 0
        budgets.append({
            'id': b.id,
            'categoria': b.categoria,
            'limite_mensile': b.limite_mensile,
            'mese': b.mese,
            'spese_usate': spese_usate,
            'percentuale': percentuale,
            'rimanente': b.limite_mensile - spese_usate,
        })

    return render_template('budget.html', form=form, budgets=budgets)


@app.route('/budget/elimina/<int:id>', methods=['POST'])
@login_required
def elimina_budget(id):
    b = Budget.query.get_or_404(id)
    if b.user_id != session['user_id']:
        flash('Non autorizzato', 'error')
        return redirect(url_for('budget'))
    db.session.delete(b)
    db.session.commit()
    flash('Budget eliminato', 'success')
    return redirect(url_for('budget'))


@app.route('/abbonamenti', methods=['GET', 'POST'])
@login_required
def abbonamenti():
    form = AbbonamentoForm()

    if form.validate_on_submit():
        nuovo = Abbonamento(
            nome=form.nome.data,
            importo=form.importo.data,
            ciclo=form.ciclo.data,
            prossimo_rinnovo=form.prossimo_rinnovo.data,
            giorni_preavviso=form.giorni_preavviso.data,
            user_id=session['user_id'],
        )
        db.session.add(nuovo)
        db.session.commit()
        flash('Abbonamento aggiunto!', 'success')
        return redirect(url_for('abbonamenti'))

    abbonamenti_raw = (
        Abbonamento.query
        .filter_by(user_id=session['user_id'], attivo=True)
        .order_by(Abbonamento.prossimo_rinnovo.asc())
        .all()
    )
    lista_abbonamenti = [
        {
            'id': a.id,
            'nome': a.nome,
            'importo': a.importo,
            'ciclo': a.ciclo,
            'prossimo_rinnovo': a.prossimo_rinnovo,
            'giorni_preavviso': a.giorni_preavviso,
            'giorni_al_rinnovo': (a.prossimo_rinnovo - date.today()).days,
        }
        for a in abbonamenti_raw
    ]

    return render_template('abbonamenti.html', form=form, abbonamenti=lista_abbonamenti)


@app.route('/abbonamenti/elimina/<int:id>', methods=['POST'])
@login_required
def disattiva_abbonamento(id):
    a = Abbonamento.query.get_or_404(id)
    if a.user_id != session['user_id']:
        flash('Non autorizzato', 'error')
        return redirect(url_for('abbonamenti'))
    a.attivo = False
    db.session.commit()
    flash('Abbonamento disattivato', 'success')
    return redirect(url_for('abbonamenti'))


@app.route('/abbonamenti/rinnova/<int:id>', methods=['POST'])
@login_required
def rinnova_abbonamento(id):
    a = Abbonamento.query.get_or_404(id)
    if a.user_id != session['user_id']:
        flash('Non autorizzato', 'error')
        return redirect(url_for('abbonamenti'))

    mesi_map = {'mensile': 1, 'trimestrale': 3, 'annuale': 12}
    mesi = mesi_map.get(a.ciclo, 1)
    a.prossimo_rinnovo = a.prossimo_rinnovo + relativedelta(months=mesi)

    spesa = Spesa(
        importo=a.importo,
        categoria='Abbonamenti',
        data=date.today(),
        nota='Rinnovo automatico: ' + a.nome,
        tipo='uscita',
        user_id=session['user_id'],
    )
    db.session.add(spesa)
    db.session.commit()
    flash('Abbonamento rinnovato e spesa registrata!', 'success')
    return redirect(url_for('abbonamenti'))


@app.route('/lista-spesa', methods=['GET', 'POST'])
@login_required
def lista_spesa():
    form = ListaSpesaForm()

    if form.validate_on_submit():
        prodotti_list = [
            riga.strip()
            for riga in form.prodotti.data.splitlines()
            if riga.strip()
        ]
        stima = stima_prezzi(prodotti_list)

        # L'API esterna ha fallito (timeout/rete/risposta non valida).
        if stima is None:
            flash('Servizio di stima non disponibile. Riprova tra qualche minuto.', 'error')
            return redirect(url_for('lista_spesa'))

        nuova = ListaSpesa(
            nome='Lista del ' + date.today().strftime('%d/%m/%Y'),
            data=date.today(),
            prodotti=json.dumps(stima, ensure_ascii=False),
            totale_stimato=stima['totale'],
            user_id=session['user_id'],
        )
        db.session.add(nuova)
        db.session.commit()
        flash('Lista salvata!', 'success')
        return redirect(url_for('lista_spesa'))

    liste = (
        ListaSpesa.query
        .filter_by(user_id=session['user_id'])
        .order_by(ListaSpesa.data.desc())
        .all()
    )
    return render_template('lista_spesa.html', form=form, liste=liste)


@app.route('/lista-spesa/modifica/<int:id>', methods=['POST'])
@login_required
def modifica_lista(id):
    lista = ListaSpesa.query.get_or_404(id)
    if lista.user_id != session['user_id']:
        flash('Non autorizzato', 'error')
        return redirect(url_for('lista_spesa'))

    nome = (request.form.get('nome') or '').strip() or lista.nome
    nomi = request.form.getlist('nome_prodotto')
    prezzi = request.form.getlist('prezzo_prodotto')
    azione = request.form.get('azione', 'salva')

    # Tiene solo le righe con un nome non vuoto; il prezzo diventa 0 se assente/non valido.
    prodotti = []
    for i, n in enumerate(nomi):
        n = n.strip()
        if not n:
            continue
        prezzo = 0.0
        if i < len(prezzi):
            try:
                prezzo = float((prezzi[i] or '0').replace(',', '.'))
            except ValueError:
                prezzo = 0.0
        prodotti.append({'nome': n, 'prezzo_stimato': round(prezzo, 2)})

    # "Ristima con AI": ricalcola i prezzi sui nomi correnti tramite Groq.
    if azione == 'ristima' and prodotti:
        stima = stima_prezzi([p['nome'] for p in prodotti])
        if stima is None:
            flash('Servizio di stima non disponibile. Modifiche non applicate.', 'error')
            return redirect(url_for('lista_spesa'))
        prodotti = stima['prodotti']

    totale = round(sum(p['prezzo_stimato'] for p in prodotti), 2)
    lista.nome = nome
    lista.prodotti = json.dumps({'prodotti': prodotti, 'totale': totale}, ensure_ascii=False)
    lista.totale_stimato = totale
    db.session.commit()
    flash('Lista aggiornata!', 'success')
    return redirect(url_for('lista_spesa'))


@app.route('/lista-spesa/elimina/<int:id>', methods=['POST'])
@login_required
def elimina_lista(id):
    lista = ListaSpesa.query.get_or_404(id)
    if lista.user_id != session['user_id']:
        flash('Non autorizzato', 'error')
        return redirect(url_for('lista_spesa'))
    db.session.delete(lista)
    db.session.commit()
    flash('Lista eliminata', 'success')
    return redirect(url_for('lista_spesa'))


@app.route('/export/csv')
@login_required
def export_csv():
    spese = (
        Spesa.query
        .filter_by(user_id=session['user_id'])
        .order_by(Spesa.data.desc())
        .all()
    )
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(['Data', 'Categoria', 'Nota', 'Importo', 'Tipo'])
    for s in spese:
        writer.writerow([
            s.data.strftime('%d/%m/%Y'),
            s.categoria,
            s.nota or '',
            f'{s.importo:.2f}',
            s.tipo,
        ])
    response = make_response(buf.getvalue())
    response.mimetype = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment; filename=walletmap_spese.csv'
    return response


@app.route('/export/excel')
@login_required
def export_excel():
    spese = (
        Spesa.query
        .filter_by(user_id=session['user_id'])
        .order_by(Spesa.data.desc())
        .all()
    )
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Spese'

    headers = ['Data', 'Categoria', 'Nota', 'Importo', 'Tipo']
    ws.append(headers)
    bold = Font(bold=True)
    for cell in ws[1]:
        cell.font = bold

    for s in spese:
        ws.append([
            s.data.strftime('%d/%m/%Y'),
            s.categoria,
            s.nota or '',
            s.importo,
            s.tipo,
        ])

    ws.column_dimensions['A'].width = 15
    ws.column_dimensions['B'].width = 15
    ws.column_dimensions['C'].width = 30
    ws.column_dimensions['D'].width = 12
    ws.column_dimensions['E'].width = 12

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    response = make_response(buf.read())
    response.mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response.headers['Content-Disposition'] = 'attachment; filename=walletmap_spese.xlsx'
    return response


def ensure_schema():
    """Aggiunge colonne mancanti a tabelle già esistenti: db.create_all() crea
    solo le tabelle nuove, non fa ALTER. Necessario su DB creati prima delle
    colonne multi-valuta (es. il Postgres di Render aveva 'spesa' senza
    'valuta'/'importo_originale', causando errori su ogni query)."""
    inspector = inspect(db.engine)
    if 'spesa' not in inspector.get_table_names():
        return
    cols = {c['name'] for c in inspector.get_columns('spesa')}
    migrazioni = []
    if 'valuta' not in cols:
        migrazioni.append("ALTER TABLE spesa ADD COLUMN valuta VARCHAR(3) DEFAULT 'EUR' NOT NULL")
    if 'importo_originale' not in cols:
        migrazioni.append("ALTER TABLE spesa ADD COLUMN importo_originale FLOAT")
    if not migrazioni:
        return
    try:
        for stmt in migrazioni:
            db.session.execute(text(stmt))
        db.session.commit()
        print('ensure_schema: colonne aggiunte ->', migrazioni)
    except Exception as e:
        db.session.rollback()
        print('ensure_schema: migrazione fallita:', e)


with app.app_context():
    db.create_all()
    ensure_schema()


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
