from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, EmailField, SubmitField,
    FloatField, SelectField, DateField, TextAreaField, IntegerField
)
from wtforms.validators import DataRequired, Length, Email, EqualTo, Optional


CATEGORIE = [
    ('Alimentari', 'Alimentari'),
    ('Trasporti', 'Trasporti'),
    ('Casa', 'Casa'),
    ('Salute', 'Salute'),
    ('Svago', 'Svago'),
    ('Altro', 'Altro'),
]


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Accedi')


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField(
        'Conferma password',
        validators=[DataRequired(), EqualTo('password', message='Le password non corrispondono')]
    )
    submit = SubmitField('Registrati')


class CambioPasswordForm(FlaskForm):
    password_attuale = PasswordField('Password attuale', validators=[DataRequired()])
    nuova_password = PasswordField('Nuova password', validators=[DataRequired(), Length(min=6)])
    conferma_password = PasswordField(
        'Conferma nuova password',
        validators=[DataRequired(), EqualTo('nuova_password', message='Le password non corrispondono')]
    )
    submit = SubmitField('Cambia password')


class SpesaForm(FlaskForm):
    importo = FloatField('Importo (€)', validators=[DataRequired()])
    categoria = SelectField('Categoria', choices=CATEGORIE, validators=[DataRequired()])
    data = DateField('Data', validators=[DataRequired()])
    nota = StringField('Nota', validators=[Optional()])
    tipo = SelectField(
        'Tipo',
        choices=[('uscita', 'Uscita'), ('entrata', 'Entrata')],
        validators=[DataRequired()]
    )
    valuta = SelectField('Valuta', choices=[
        ('EUR', '€ Euro'),
        ('USD', '$ Dollaro USA'),
        ('GBP', '£ Sterlina'),
        ('CNY', '¥ Yuan cinese'),
        ('AUD', 'A$ Dollaro australiano'),
        ('KRW', '₩ Won coreano'),
    ], default='EUR')
    submit = SubmitField('Salva')


class BudgetForm(FlaskForm):
    categoria = SelectField('Categoria', choices=CATEGORIE, validators=[DataRequired()])
    limite_mensile = FloatField('Limite mensile (€)', validators=[DataRequired()])
    mese = StringField('Mese (YYYY-MM)', validators=[DataRequired()])
    submit = SubmitField('Salva')


class AbbonamentoForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired()])
    importo = FloatField('Importo (€)', validators=[DataRequired()])
    ciclo = SelectField(
        'Ciclo',
        choices=[
            ('mensile', 'Mensile'),
            ('trimestrale', 'Trimestrale'),
            ('annuale', 'Annuale'),
        ],
        validators=[DataRequired()]
    )
    prossimo_rinnovo = DateField('Prossimo rinnovo', validators=[DataRequired()])
    giorni_preavviso = IntegerField('Giorni di preavviso', default=3)
    submit = SubmitField('Salva')


class ListaSpesaForm(FlaskForm):
    prodotti = TextAreaField('Prodotti (uno per riga)', validators=[DataRequired()])
    submit = SubmitField('Salva')
