from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional

class TeamForm(FlaskForm):
    name = StringField('Nombre del Equipo', validators=[DataRequired(), Length(min=2, max=100)])
    shield_url = StringField('URL del Escudo', validators=[Optional()])
    captain_name = StringField('Nombre del Capitán', validators=[Optional()])

class TeamNoteForm(FlaskForm):
    text = TextAreaField('Nota', validators=[DataRequired()])
