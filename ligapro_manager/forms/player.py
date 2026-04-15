from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DateField
from wtforms.validators import DataRequired, Length, Optional

class PlayerForm(FlaskForm):
    name = StringField('Nombre del Jugador', validators=[DataRequired(), Length(min=2, max=100)])
    number = IntegerField('Número (Dorsal)', validators=[Optional()])
    curp = StringField('CURP', validators=[Optional(), Length(max=20)])
    photo_url = StringField('URL de Foto', validators=[Optional()])
    registration_date = DateField('Fecha de registro', format='%Y-%m-%d', validators=[Optional()])
