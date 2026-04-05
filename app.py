import os
from urllib.parse import urlsplit

from flask import Flask, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager, UserMixin, login_required, current_user,login_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import StringField, TextAreaField, SubmitField, BooleanField, PasswordField
from wtforms.validators import DataRequired, length, Length, EqualTo, ValidationError

app = Flask(__name__)
bootstrap = Bootstrap5(app)
app.config['SECRET_KEY'] = os.environ.get('CSRF_SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI','sqlite:///studystack.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


class Deck(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    is_public = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    cards = db.relationship('Card', backref='deck',lazy='select',
                            cascade='all, delete-orphan')

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Deck {self.title}>'


class User(UserMixin, db.Model):
    id=db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(50), unique=True, nullable=False)
    email=db.Column(db.String(120), unique=True, nullable=False)
    password=db.Column(db.String(255), nullable=False)
    created_at=db.Column(db.DateTime, server_default=db.func.now())
    decks=db.relationship('Deck', backref='owner', lazy='dynamic')


    def set_password(self, password):
        self.password=generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question=db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)

    deck_id = db.Column(db.Integer, db.ForeignKey('deck.id'), nullable=False)

    def __repr__(self):
        return f'<Card{self.question[:30]}>'



class DeckForm(FlaskForm):
    title = StringField('Deck Title', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description')
    is_public = BooleanField('Make this deck public', default=True)
    submit = SubmitField('Create Deck')

class CardForm(FlaskForm):
    question = TextAreaField('Question', validators=[DataRequired()])
    answer = TextAreaField('Answer', validators=[DataRequired()])
    submit = SubmitField('Add Card')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('',validators=[DataRequired(), Length(min=8,max=50)])
    submit = SubmitField('Login')

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/decks')
@login_required
def deck_list():
    decks = Deck.query.filter_by(user_id=current_user.id).order_by(Deck.created_at.desc()).all()
    return render_template('decks/index.html', decks=decks)

@app.route('/decks/create', methods=['GET','POST'])
@login_required
def deck_create():
    form = DeckForm()
    if form.validate_on_submit():
        deck = Deck(
            title=form.title.data,
            description=form.description.data,
            is_public=form.is_public.data,
            user_id=current_user.id
        )
        db.session.add(deck)
        db.session.commit()
        flash('Deck created successfully!', 'success')
        return redirect(url_for('deck_detail', deck_id = deck.id))

    return render_template('decks/create.html', form=form)

@app.route('/decks/<int:deck_id>')
def deck_detail(deck_id):
    deck = db.get_or_404(Deck, deck_id)
    return render_template('decks/detail.html', deck=deck)

@app.route('/decks/<deck_id>/cards/new', methods=['GET','POST'])
def card_create(deck_id):
    form=CardForm()
    deck=db.get_or_404(Deck, deck_id)
    if form.validate_on_submit():
        card = Card(
            question=form.question.data,
            answer=form.answer.data,
            deck_id=deck.id
        )
        db.session.add(card)
        db.session.commit()
        flash('Card added!', 'success')
        return redirect(url_for('deck_detail', deck_id=deck.id))
    return render_template('decks/new_card.html', form=form, deck=deck)

@app.route('/register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('deck_list'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email = form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('auth/register.html', form=form)

@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('deck_list'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('deck_list')
        return redirect(next_page)
    return render_template('auth/login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


if __name__ == '__main__':
    app.run(debug=True)
