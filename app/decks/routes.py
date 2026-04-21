from flask import Blueprint, Flask, render_template, redirect, url_for, flash, request, abort
from urllib.parse import urlsplit
from flask_login import login_required, current_user
from app import db
from app.models import User, Deck, Card
from app.decks.forms import DeckForm, CardForm
from wtforms.validators import DataRequired, length, Length, EqualTo, ValidationError
from wtforms import StringField, TextAreaField, SubmitField, BooleanField, PasswordField
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm

bp = Blueprint('decks', __name__)

@bp.route('/')
@login_required
def index():
    decks = Deck.query.filter_by(user_id=current_user.id).all()
    return render_template('decks/index.html', title='My Decks', decks=decks)

@bp.route('/decks/create', methods=['GET','POST'])
@login_required
def deck_create():
    form = DeckForm()
    if form.validate_on_submit():
        deck = Deck(
            title=form.title.data,
            description=form.description.data,
            is_public=form.is_public.data,
            owner=current_user
        )
        db.session.add(deck)
        db.session.commit()
        flash('Deck created successfully!', 'success')
        return redirect(url_for('decks.deck_detail', deck_id = deck.id))

    return render_template('decks/create.html', form=form)


@bp.route('/decks/<int:deck_id>')
def deck_detail(deck_id):
    deck = db.get_or_404(Deck, deck_id)
    #if deck is not public (is private) AND user is not authenticated or user does not match current user
    if not deck.is_public and (not current_user.is_authenticated or deck.owner != current_user):
        return redirect(url_for('main.index'))

    return render_template('decks/detail.html', deck=deck)


@bp.route('/decks')
@login_required
def deck_list():
    decks = Deck.query.filter_by(user_id=current_user.id).order_by(Deck.created_at.desc()).all()
    return render_template('decks/index.html', decks=decks)


@bp.route('/decks/<deck_id>/cards/new', methods=['GET','POST'])
@login_required
def card_create(deck_id):
    deck=db.get_or_404(Deck, deck_id)
    if deck.owner != current_user:
        abort(403)
    form = CardForm()
    if form.validate_on_submit():
        card = Card(
            question=form.question.data,
            answer=form.answer.data,
            deck_id=deck.id
        )
        db.session.add(card)
        db.session.commit()
        flash('Card added!', 'success')
        return redirect(url_for('decks.deck_detail', deck_id=deck.id))
    return render_template('decks/new_card.html', form=form, deck=deck)