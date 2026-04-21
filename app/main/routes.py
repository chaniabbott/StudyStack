from flask import Blueprint, render_template
from app.models import Deck

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    public_decks = Deck.query.filter_by(is_public=True).limit(5).all()
    return render_template('main/index.html', decks=public_decks)