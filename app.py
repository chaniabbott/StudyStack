from app import create_app, db
from app.models import User, Deck, Card

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db':db, 'User':User, 'Deck':Deck, 'Card':Card}

if __name__ == '__main__':
    app.run(debug=True)
