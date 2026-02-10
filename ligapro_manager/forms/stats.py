from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField
from wtforms.validators import DataRequired, Length, InputRequired, NumberRange, Optional

class StatForm(FlaskForm):
    player_name = StringField('Nombre del Jugador', validators=[DataRequired(), Length(max=100)])
    team_id = SelectField('Equipo', validators=[DataRequired()])
    photo_url = StringField('URL Foto (Opcional)', validators=[Optional()])
    value = IntegerField('Cantidad', validators=[InputRequired(), NumberRange(min=0)])
    stat_type = StringField('Tipo', validators=[DataRequired()])
