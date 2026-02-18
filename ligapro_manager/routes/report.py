from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models import Match, League, Court, Team
from extensions import db
from sqlalchemy import func
from datetime import datetime
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.utils import get_column_letter
from io import BytesIO
from flask import send_file

report_bp = Blueprint('report', __name__)

@report_bp.route('/report')
@login_required
def index():
    # Ultra Premium Check
    if not getattr(current_user, 'is_ultra', False):
        flash('No tienes acceso a esta funcionalidad (Ultra Premium).', 'warning')
        return redirect(url_for('main.dashboard'))
        
    return render_template('report.html')

@report_bp.route('/global-schedule')
@login_required
def global_schedule():
    # Ultra Premium Check
    if not getattr(current_user, 'is_ultra', False):
        flash('No tienes acceso a esta funcionalidad (Ultra Premium).', 'warning')
        return redirect(url_for('main.dashboard'))

    # Date Parameter
    date_str = request.args.get('date')
    if date_str:
        try:
            selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            selected_date = datetime.now().date()
    else:
        selected_date = datetime.now().date()

    # Query Matches for ALL leagues owned by current_user on selected_date
    matches = Match.query.join(League).filter(
        League.user_id == current_user.id,
        func.date(Match.match_date) == selected_date
    ).order_by(Match.match_date).all()

    # Group by Court Name (String Select)
    grouped_schedule = {}
    
    for match in matches:
        # Determine Court Name
        if match.court:
            court_name = match.court.name
        else:
            court_name = "Sin Cancha Asignada"
            
        if court_name not in grouped_schedule:
            grouped_schedule[court_name] = {
                'matches': [],
                'matches': [],
                'total_cost_home': 0,
                'total_cost_away': 0,
                'total_referee': 0,
                'total_profit': 0
            }
        
        # Helper to convert to int safely
        def safe_int(val):
            try:
                return int(val)
            except (ValueError, TypeError):
                return 0

        grouped_schedule[court_name]['matches'].append(match)
        vis_home = safe_int(match.referee_cost_home)
        vis_away = safe_int(match.referee_cost_away)
        exp_ref = safe_int(match.referee_cost)
        
        grouped_schedule[court_name]['total_cost_home'] += vis_home
        grouped_schedule[court_name]['total_cost_away'] += vis_away
        grouped_schedule[court_name]['total_referee'] += exp_ref
        grouped_schedule[court_name]['total_profit'] += ((vis_home + vis_away) - exp_ref)

    # Sort groups by name (optional)
    sorted_schedule = dict(sorted(grouped_schedule.items()))

    return render_template('report/global_schedule.html', 
                         schedule=sorted_schedule, 
                         selected_date=selected_date)

@report_bp.route('/api/match/update_costs', methods=['POST'])
@login_required
def update_match_costs():
    if not getattr(current_user, 'is_ultra', False):
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    match_id = data.get('match_id')
    
    # Fields to update
    cost_home = data.get('referee_cost_home')
    cost_away = data.get('referee_cost_away')
    cost_referee = data.get('referee_cost')
    
    match = Match.query.get(match_id)
    if not match:
        return jsonify({'error': 'Match not found'}), 404
        
    # Update fields if provided
    if cost_home is not None:
        match.referee_cost_home = str(cost_home)
    if cost_away is not None:
        match.referee_cost_away = str(cost_away)
    if cost_referee is not None:
        match.referee_cost = str(cost_referee)
    
    db.session.commit()
    
    return jsonify({'success': True, 'match_id': match.id})

@report_bp.route('/global-schedule/config', methods=['GET', 'POST'])
@login_required
def global_schedule_config():
    if not getattr(current_user, 'is_ultra', False):
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('report.index'))
        
    if request.method == 'POST':
        # Update prices for leagues
        for key, value in request.form.items():
            if key.startswith('price_team_'):
                league_id = key.split('_')[2]
                league = League.query.get(league_id)
                if league and league.user_id == current_user.id:
                    try:
                        league.price_per_match = int(value)
                    except ValueError:
                        pass
            elif key.startswith('price_referee_'):
                league_id = key.split('_')[2]
                league = League.query.get(league_id)
                if league and league.user_id == current_user.id:
                    try:
                        league.price_referee = int(value)
                    except ValueError:
                        pass
        db.session.commit()
        flash('Precios actualizados correctamente.', 'success')
        return redirect(url_for('report.global_schedule_config'))

    leagues = League.query.filter_by(user_id=current_user.id).all()
    return render_template('report/config.html', leagues=leagues)

@report_bp.route('/global-schedule/history')
@login_required
def global_schedule_history():
    if not getattr(current_user, 'is_ultra', False):
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('report.index'))

    # Filters
    league_id = request.args.get('league_id')
    
    query = Match.query.join(League).filter(League.user_id == current_user.id)
    
    if league_id:
        query = query.filter(Match.league_id == league_id)
        
    matches = query.order_by(Match.match_date.desc()).all()
    
    history_events = []
    
    def parse_cost(val):
        if not val: return 0
        if isinstance(val, str) and not val.isdigit(): return 0 # NSP or text = 0 paid
        try: return int(val)
        except: return 0

    for match in matches:
        if not match.league: continue
        
        # Defaults
        default_team_price = match.league.price_per_match or 0
        default_ref_price = match.league.price_referee or 0
        
        # Check Home Team Debt
        paid_home = parse_cost(match.referee_cost_home)
        diff_home = paid_home - default_team_price
        if diff_home != 0:
            history_events.append({
                'date': match.match_date,
                'league': match.league.name,
                'match': f"{match.home_team.name} vs {match.away_team.name}",
                'entity': f"Local: {match.home_team.name}",
                'expected': default_team_price,
                'paid': paid_home,
                'balance': diff_home
            })
            
        # Check Away Team Debt
        paid_away = parse_cost(match.referee_cost_away)
        diff_away = paid_away - default_team_price
        if diff_away != 0:
            history_events.append({
                'date': match.match_date,
                'league': match.league.name,
                'match': f"{match.home_team.name} vs {match.away_team.name}",
                'entity': f"Visita: {match.away_team.name}",
                'expected': default_team_price,
                'paid': paid_away,
                'balance': diff_away
            })

        # Check Referee Balance
        paid_ref = parse_cost(match.referee_cost)
        diff_ref = paid_ref - default_ref_price
        if diff_ref != 0:
             history_events.append({
                'date': match.match_date,
                'league': match.league.name,
                'match': f"{match.home_team.name} vs {match.away_team.name}",
                'entity': "Arbitro",
                'expected': default_ref_price,
                'paid': paid_ref,
                'balance': diff_ref
            })

            
    # Sort events by date desc
    history_events.sort(key=lambda x: x['date'], reverse=True)
    
    leagues = League.query.filter_by(user_id=current_user.id).all()
    
    return render_template('report/history.html', 
                         events=history_events, 
                         leagues=leagues, 
                         selected_league=league_id)

@report_bp.route('/global-schedule/export')
@login_required
def export_global_schedule():
    if not getattr(current_user, 'is_ultra', False):
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('report.index'))

    # Date Parameter
    date_str = request.args.get('date')
    if date_str:
        try:
            selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            selected_date = datetime.now().date()
    else:
        selected_date = datetime.now().date()

    # Query Matches
    matches = Match.query.join(League).filter(
        League.user_id == current_user.id,
        func.date(Match.match_date) == selected_date
    ).order_by(Match.match_date).all()

    # Group by Court
    grouped_schedule = {}
    for match in matches:
        court_name = match.court.name if match.court else "Sin Cancha Asignada"
        if court_name not in grouped_schedule:
            grouped_schedule[court_name] = []
        grouped_schedule[court_name].append(match)
    
    sorted_schedule = dict(sorted(grouped_schedule.items()))

    # Create Excel
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Agenda Global"
    
    # Title
    ws['A1'] = f"AGENDA DE PARTIDOS - {selected_date.strftime('%d/%m/%Y')}"
    ws['A1'].font = Font(size=14, bold=True)
    ws.merge_cells('A1:H1')
    ws['A1'].alignment = Alignment(horizontal='center')
    
    current_row = 3
    
    # Styles
    header_fill = PatternFill(start_color="DDDDDD", end_color="DDDDDD", fill_type="solid")
    header_font = Font(bold=True)
    
    def parse_cost(val):
        if not val: return 0
        if isinstance(val, str) and not val.isdigit(): return 0
        try: return int(val)
        except: return 0

    for court_name, matches in sorted_schedule.items():
        # Court Header
        ws.cell(row=current_row, column=1, value=f"CANCHA: {court_name}")
        ws.cell(row=current_row, column=1).font = Font(bold=True, size=12, color="FFFFFF")
        ws.cell(row=current_row, column=1).fill = PatternFill(start_color="2F855A", end_color="2F855A", fill_type="solid") # Green
        ws.merge_cells(start_row=current_row, start_column=1, end_row=current_row, end_column=8)
        current_row += 1
        
        # Table Headers
        headers = ["Hora", "Categoría", "Local", "$ Local", "vs", "$ Visita", "Visitante", "$ Arbitro"]
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=current_row, column=col_num, value=header)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal='center')
        current_row += 1
        
        total_home = 0
        total_away = 0
        total_referee = 0
        
        for match in matches:
            ws.cell(row=current_row, column=1, value=match.match_date.strftime('%I:%M %p'))
            ws.cell(row=current_row, column=2, value=match.league.name)
            ws.cell(row=current_row, column=3, value=match.home_team.name).alignment = Alignment(horizontal='right')
            
            c_home = parse_cost(match.referee_cost_home)
            ws.cell(row=current_row, column=4, value=c_home)
            total_home += c_home
            
            ws.cell(row=current_row, column=5, value="-").alignment = Alignment(horizontal='center')
            
            c_away = parse_cost(match.referee_cost_away)
            ws.cell(row=current_row, column=6, value=c_away)
            total_away += c_away
            
            ws.cell(row=current_row, column=7, value=match.away_team.name)
            
            c_ref = parse_cost(match.referee_cost)
            ws.cell(row=current_row, column=8, value=c_ref)
            total_referee += c_ref
            
            current_row += 1
            
        # Totals Row
        ws.cell(row=current_row, column=3, value="TOTALES:").alignment = Alignment(horizontal='right')
        ws.cell(row=current_row, column=4, value=total_home).font = Font(bold=True)
        ws.cell(row=current_row, column=6, value=total_away).font = Font(bold=True)
        ws.cell(row=current_row, column=8, value=total_referee).font = Font(bold=True)
        current_row += 1
        
        # Profit Row
        profit = (total_home + total_away) - total_referee
        ws.cell(row=current_row, column=7, value="GANANCIA:").alignment = Alignment(horizontal='right')
        ws.cell(row=current_row, column=8, value=profit).font = Font(bold=True, color="008000" if profit >= 0 else "FF0000")
        current_row += 2 # Space between courts

    # Auto-adjust column widths
    for i, col in enumerate(ws.columns, 1):
        max_length = 0
        column = get_column_letter(i)
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2)
        ws.column_dimensions[column].width = adjusted_width

    output = BytesIO()
    wb.save(output)
    output.seek(0)
    
    filename = f"Agenda_Global_{selected_date.strftime('%Y-%m-%d')}.xlsx"
    return send_file(output, download_name=filename, as_attachment=True)

# Helper for calculating discrepancies
def calculate_discrepancies(matches):
    events = []
    
    def parse_cost(val):
        if not val: return 0
        if isinstance(val, str) and not val.isdigit(): return 0 
        try: return int(val)
        except: return 0

    for match in matches:
        if not match.league: continue
        
        # Defaults
        default_team_price = match.league.price_per_match or 0
        default_ref_price = match.league.price_referee or 0
        
        # Home
        paid_home = parse_cost(match.referee_cost_home)
        diff_home = paid_home - default_team_price
        if diff_home != 0:
            events.append({
                'league': match.league.name,
                'entity_type': 'Team',
                'entity_name': match.home_team.name,
                'balance': diff_home
            })
            
        # Away
        paid_away = parse_cost(match.referee_cost_away)
        diff_away = paid_away - default_team_price
        if diff_away != 0:
            events.append({
                'league': match.league.name,
                'entity_type': 'Team',
                'entity_name': match.away_team.name,
                'balance': diff_away
            })

        # Referee
        paid_ref = parse_cost(match.referee_cost)
        diff_ref = paid_ref - default_ref_price
        if diff_ref != 0:
             events.append({
                'league': match.league.name,
                'entity_type': 'Referee',
                'entity_name': 'Arbitro',
                'balance': diff_ref
            })
    return events

@report_bp.route('/global-schedule/summary')
@login_required
def global_schedule_summary():
    if not getattr(current_user, 'is_ultra', False):
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('report.index'))

    # Filters
    league_id = request.args.get('league_id')
    
    query = Match.query.join(League).filter(League.user_id == current_user.id)
    if league_id:
        query = query.filter(Match.league_id == league_id)
        
    matches = query.all()
    
    discrepancies = calculate_discrepancies(matches)
    
    # Aggregate
    teams_summary = {} # (league, team_name) -> total
    referee_summary = {} # (league) -> total
    
    for item in discrepancies:
        if item['entity_type'] == 'Team':
            key = (item['league'], item['entity_name'])
            teams_summary[key] = teams_summary.get(key, 0) + item['balance']
        elif item['entity_type'] == 'Referee':
            league_name = item['league']
            referee_summary[league_name] = referee_summary.get(league_name, 0) + item['balance']
            
    # Convert to list for display
    teams_list = [{'league': k[0], 'name': k[1], 'balance': v} for k, v in teams_summary.items()]
    teams_list.sort(key=lambda x: (x['league'], x['name']))
    
    referee_list = [{'league': k, 'balance': v} for k, v in referee_summary.items()]
    referee_list.sort(key=lambda x: x['league'])
    
    leagues = League.query.filter_by(user_id=current_user.id).all()
    
    return render_template('report/summary.html', 
                         teams_summary=teams_list,
                         referee_summary=referee_list,
                         leagues=leagues, 
                         selected_league=league_id)

@report_bp.route('/global-schedule/summary/export')
@login_required
def export_global_summary():
    if not getattr(current_user, 'is_ultra', False):
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('report.index'))

    # Filters
    league_id = request.args.get('league_id')
    query = Match.query.join(League).filter(League.user_id == current_user.id)
    if league_id:
        query = query.filter(Match.league_id == league_id)
        
    matches = query.all()
    discrepancies = calculate_discrepancies(matches)
    
    # Aggregate
    teams_summary = {}
    referee_summary = {}
    
    for item in discrepancies:
        if item['entity_type'] == 'Team':
            key = (item['league'], item['entity_name'])
            teams_summary[key] = teams_summary.get(key, 0) + item['balance']
        elif item['entity_type'] == 'Referee':
            league_name = item['league']
            referee_summary[league_name] = referee_summary.get(league_name, 0) + item['balance']
            
    teams_list = [{'league': k[0], 'name': k[1], 'balance': v} for k, v in teams_summary.items()]
    teams_list.sort(key=lambda x: (x['league'], x['name']))
    
    referee_list = [{'league': k, 'balance': v} for k, v in referee_summary.items()]
    referee_list.sort(key=lambda x: x['league'])

    # Excel
    wb = openpyxl.Workbook()
    # Sheet 1: Teams
    ws1 = wb.active
    ws1.title = "Balance Equipos"
    ws1.append(["Liga", "Equipo", "Balance Total"])
    for t in teams_list:
        ws1.append([t['league'], t['name'], t['balance']])
        
    # Sheet 2: Referees
    ws2 = wb.create_sheet("Balance Arbitraje")
    ws2.append(["Liga", "Balance Total"])
    for r in referee_list:
        ws2.append([r['league'], r['balance']])
        
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    
    filename = f"Resumen_Global_{datetime.now().strftime('%Y-%m-%d')}.xlsx"
    return send_file(output, download_name=filename, as_attachment=True)
