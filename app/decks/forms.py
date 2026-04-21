from wtforms import StringField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length
from flask_wtf import FlaskForm

class DeckForm(FlaskForm):
    title = StringField('Deck Title', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description')
    is_public = BooleanField('Make this deck public', default=True)
    submit = SubmitField('Create Deck')

class CardForm(FlaskForm):
    question = TextAreaField('Question', validators=[DataRequired()])
    answer = TextAreaField('Answer', validators=[DataRequired()])
    submit = SubmitField('Add Card')