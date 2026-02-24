from flask_wtf import FlaskForm
from wtforms import SelectField, IntegerField, DateTimeField
from wtforms.validators import DataRequired, InputRequired, NumberRange, Optional

class MatchForm(FlaskForm):
    home_team_id = SelectField('Equipo Local', validators=[DataRequired()])
    away_team_id = SelectField('Equipo Visitante', validators=[DataRequired()])
    court_id = SelectField('Cancha', validators=[DataRequired()])
    match_date = DateTimeField('Fecha y Hora', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])

class MatchResultForm(MatchForm):
    home_score = IntegerField('Goles Local', validators=[Optional(), NumberRange(min=0)])
    away_score = IntegerField('Goles Visitante', validators=[Optional(), NumberRange(min=0)])
