import os

from flask import Flask, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, BooleanField
from wtforms.validators import DataRequired, length, Length

app = Flask(__name__)
bootstrap = Bootstrap5(app)
app.config['SECRET_KEY'] = os.environ.get('CSRF_SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI','sqlite:///studystack.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Deck(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    is_public = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    cards = db.relationship('Card', backref='deck',lazy='select',
                            cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Deck {self.title}>'


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

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/decks')
def deck_list():
    decks = Deck.query.order_by(Deck.created_at.desc()).all()
    return render_template('index.html', decks=decks)

@app.route('/decks/create', methods=['GET','POST'])
def deck_create():
    form = DeckForm()
    if form.validate_on_submit():
        deck = Deck(
            title=form.title.data,
            description=form.description.data,
            is_public=form.is_public.data
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


if __name__ == '__main__':
    app.run(debug=True)
