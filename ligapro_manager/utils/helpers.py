from models import League, Team, Match
import unicodedata

def normalize_name(name):
    """Normalize name by removing accents and converting to lowercase."""
    if not name:
        return ""
    return ''.join(c for c in unicodedata.normalize('NFD', name)
                  if unicodedata.category(c) != 'Mn').lower().strip()

def calculate_standings(league_id, include_playoffs=False):
    """Calculate standings for a league"""
    league = League.query.get_or_404(league_id)
    # Only show active teams in standings
    # Only show active (visible) teams in standings
    teams = Team.query.filter_by(league_id=league_id, is_deleted=False, is_hidden=False).all()
    
    # Get completed matches (only regular season by default, never practice matches)
    if include_playoffs:
        matches_query = Match.query.filter(
            Match.league_id == league_id,
            Match.is_completed == True,
            Match.is_practice == False
        )
    else:
        matches_query = Match.query.filter(
            Match.league_id == league_id,
            Match.is_completed == True,
            Match.is_practice == False,
            Match.stage.in_(['regular', None, ''])
        )
    
    all_matches = matches_query.all()
    
    # If not premium, only count the first match between any pair (Round 1)
    if not league.owner.is_active_premium:
        filtered_matches = []
        pairs_seen = set()
        # Sort matches by date to ensure we pick the first one chronologically
        sorted_matches = sorted(all_matches, key=lambda x: x.match_date)
        for m in sorted_matches:
            pair = tuple(sorted([m.home_team_id, m.away_team_id]))
            if pair not in pairs_seen:
                filtered_matches.append(m)
                pairs_seen.add(pair)
        matches = filtered_matches
    else:
        matches = all_matches
    
    standings = []
    
    # Points configuration (Enforce defaults for non-premium)
    is_premium = league.owner.is_active_premium
    win_points = league.win_points if is_premium else 3
    draw_points = league.draw_points if is_premium else 1
    for team in teams:
        stats = {
            'team': team,
            'played': 0,
            'won': 0,
            'drawn': 0,
            'lost': 0,
            'goals_for': 0,
            'goals_against': 0,
            'goal_difference': 0,
            'points': (team.manual_points_modifier or 0)
        }
        
        for match in matches:
            if match.home_team_id == team.id:
                stats['played'] += 1
                stats['goals_for'] += match.home_score or 0
                stats['goals_against'] += match.away_score or 0
                
                if match.home_score > match.away_score:
                    stats['won'] += 1
                    stats['points'] += win_points
                elif match.home_score == match.away_score:
                    stats['drawn'] += 1
                    if league.enable_shutdown_tiebreaker and getattr(match, 'shutdown_winner_id', None):
                        if match.shutdown_winner_id == team.id:
                            stats['points'] += 2
                        else:
                            stats['points'] += 1
                    else:
                        stats['points'] += draw_points
                else:
                    stats['lost'] += 1
                    
            elif match.away_team_id == team.id:
                stats['played'] += 1
                stats['goals_for'] += match.away_score or 0
                stats['goals_against'] += match.home_score or 0
                
                if match.away_score > match.home_score:
                    stats['won'] += 1
                    stats['points'] += win_points
                elif match.away_score == match.home_score:
                    stats['drawn'] += 1
                    if league.enable_shutdown_tiebreaker and getattr(match, 'shutdown_winner_id', None):
                        if match.shutdown_winner_id == team.id:
                            stats['points'] += 2
                        else:
                            stats['points'] += 1
                    else:
                        stats['points'] += draw_points
                else:
                    stats['lost'] += 1
        
        stats['goal_difference'] = stats['goals_for'] - stats['goals_against']
        standings.append(stats)
    
    # Sort by points, goal difference, goals for
    standings.sort(key=lambda x: (x['points'], x['goal_difference'], x['goals_for']), reverse=True)
    return standings

def is_league_accessible(user_id, league_id):
    """
    Check if a user can access a specific league based on their plan limits.
    Free plan: Max 3 leagues (oldest 3).
    Premium: Unlimited.
    """
    from models import User
    
    user = User.query.get(user_id)
    if not user:
        return False
        
    if user.is_active_premium:
        return True
        
    # Get all leagues for user sorted by creation date
    leagues = League.query.filter_by(user_id=user_id).order_by(League.created_at.asc()).all()
    
    if len(leagues) <= 3:
        return True
        
    # Get IDs of the first 3 leagues
    allowed_ids = [l.id for l in leagues[:3]]
    
    return league_id in allowed_ids

def archive_league_finances(league):
    """
    Archives the financial data for a league before it gets deleted or reset.
    Groups by Match Date and Court, then inserts into ArchivedFinance.
    Saves match-level breakdown in details_json only if the owner is Ultra.
    """
    from extensions import db
    from models import ArchivedFinance
    import json
    
    matches = Match.query.filter_by(league_id=league.id).all()
    if not matches:
        return
        
    def parse_cost(val):
        if not val: return 0
        if isinstance(val, str) and not val.isdigit(): return 0 
        try: return int(val)
        except: return 0
        
    def is_waived(val):
        if isinstance(val, str) and val.upper() in ['NSP', 'GIFT']: 
            return True
        return False
        
    archives = {}
    is_ultra = getattr(league.owner, 'is_ultra', False)
    
    for match in matches:
        # Respect Charge Start Date
        if not league.charge_from_start and league.charge_start_date:
            if match.match_date.date() < league.charge_start_date:
                continue
                
        date_key = match.match_date.date()
        court_name = match.court.name if match.court else "Sin Cancha"
        key = (date_key, court_name)
        
        if key not in archives:
            archives[key] = {'income': 0, 'expense': 0, 'matches': []}
            
        income_home = parse_cost(match.referee_cost_home) if not is_waived(match.referee_cost_home) else 0
        income_away = parse_cost(match.referee_cost_away) if not is_waived(match.referee_cost_away) else 0
        expense_ref = parse_cost(match.referee_cost) if not is_waived(match.referee_cost) else 0
            
        archives[key]['income'] += (income_home + income_away)
        archives[key]['expense'] += expense_ref
        
        if is_ultra:
            archives[key]['matches'].append({
                'home': match.home_team.name if match.home_team else 'Local',
                'away': match.away_team.name if match.away_team else 'Visita',
                'home_paid': income_home,
                'away_paid': income_away,
                'ref_paid': expense_ref,
                'time': match.match_date.strftime('%H:%M') if match.match_date else ''
            })
        
    for (date_key, court_name), totals in archives.items():
        if totals['income'] == 0 and totals['expense'] == 0:
            continue
            
        details_val = json.dumps(totals['matches']) if is_ultra and totals['matches'] else None
            
        archive = ArchivedFinance(
            user_id=league.user_id,
            league_name=league.name,
            court_name=court_name,
            date=date_key,
            income=totals['income'],
            expense=totals['expense'],
            profit=totals['income'] - totals['expense'],
            details_json=details_val
        )
        db.session.add(archive)

