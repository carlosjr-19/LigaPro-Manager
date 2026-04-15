from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, BooleanField
from wtforms.validators import DataRequired, Length, NumberRange, Optional

class LeagueForm(FlaskForm):
    name = StringField('Nombre de la Liga', validators=[DataRequired(), Length(min=2, max=100)])
    max_teams = IntegerField('Máximo de Equipos', validators=[DataRequired(), NumberRange(min=4, max=32)], default=10)
    num_vueltas = IntegerField('Número de Vueltas (Premium)', validators=[DataRequired(), NumberRange(min=1, max=5)], default=1)
    win_points = IntegerField('Puntos por Victoria', validators=[DataRequired()], default=3)
    draw_points = IntegerField('Puntos por Empate', validators=[DataRequired()], default=1)
    # Field handles by template conditional, but need it in form
    show_stats = BooleanField('Mostrar Estadísticas a Delegados', default=True)
    logo_url = StringField('URL del Logo (Premium)', validators=[Optional()])
    slogan = StringField('Slogan de la Liga (Premium)', validators=[Optional(), Length(max=255)])
    credential_color = StringField('Color de Credencial (Hex)', validators=[Optional(), Length(max=10)], default='#dc2626')
    credential_phrase = StringField('Frase para Registro (Opcional)', validators=[Optional(), Length(max=255)])
    show_team_logos = BooleanField('Mostrar Logos de Equipos en Reportes', default=False)
    
    # Premium Personalization Fields
    highlight_standings = BooleanField('Resaltar Posiciones en Tabla', default=False)
    highlight_start = IntegerField('Inicio Rango', validators=[Optional(), NumberRange(min=1)], default=1)
    highlight_end = IntegerField('Fin Rango', validators=[Optional(), NumberRange(min=1)], default=4)
    highlight_color = StringField('Color de Resaltado', validators=[Optional(), Length(max=10)], default='#4ade80')
    report_date_color = StringField('Color de Fecha en Reporte', validators=[Optional(), Length(max=10)], default='#ffffff99')
    report_date_size = IntegerField('Tamaño de Fecha (px)', validators=[Optional(), NumberRange(min=12, max=20)], default=14)
    custom_color_active = BooleanField('Color Personalizado para Nombre de Liga', default=False)
    custom_name_color = StringField('Color del Nombre de Liga', validators=[Optional(), Length(max=10)], default='#ffffff')
    custom_role_style = StringField('Diseño del Rol', validators=[Optional(), Length(max=50)])
    enable_shutdown_tiebreaker = BooleanField('Habilitar desempate de partidos en shutdown', default=False)
    show_matchday_in_report = BooleanField('Mostrar Jornada en Rol', default=False)
    allow_captains_add_players = BooleanField('Permitir añadir jugadores', default=True)
    show_player_registration_date = BooleanField('Mostrar fecha de registro de los jugadores', default=False)
