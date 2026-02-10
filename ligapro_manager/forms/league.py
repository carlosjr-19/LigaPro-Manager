from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, BooleanField
from wtforms.validators import DataRequired, Length, NumberRange, Optional

class LeagueForm(FlaskForm):
    name = StringField('Nombre de la Liga', validators=[DataRequired(), Length(min=2, max=100)])
    max_teams = IntegerField('Máximo de Equipos', validators=[DataRequired(), NumberRange(min=4, max=32)], default=10)
    win_points = IntegerField('Puntos por Victoria', validators=[DataRequired()], default=3)
    draw_points = IntegerField('Puntos por Empate', validators=[DataRequired()], default=1)
    # Field handles by template conditional, but need it in form
    show_stats = BooleanField('Mostrar Estadísticas a Capitanes', default=True)
    logo_url = StringField('URL del Logo (Premium)', validators=[Optional()])
    slogan = StringField('Slogan de la Liga (Premium)', validators=[Optional(), Length(max=255)])
