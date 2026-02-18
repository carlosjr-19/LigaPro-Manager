from routes.auth import auth_bp
from routes.main import main_bp
from routes.league import league_bp
from routes.team import team_bp
from routes.player import player_bp
from routes.match import match_bp
from routes.stats import stats_bp
from routes.premium import premium_bp
from routes.admin import admin_bp
from routes.match_matrix import match_matrix_bp
from routes.report import report_bp

def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(league_bp)
    app.register_blueprint(team_bp)
    app.register_blueprint(player_bp)
    app.register_blueprint(match_bp)
    app.register_blueprint(stats_bp)
    app.register_blueprint(premium_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(match_matrix_bp)
    app.register_blueprint(report_bp)
