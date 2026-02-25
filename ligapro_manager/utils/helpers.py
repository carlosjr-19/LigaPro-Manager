from models import League, Team, Match

def calculate_standings(league_id, include_playoffs=False):
    """Calculate standings for a league"""
    league = League.query.get_or_404(league_id)
    # Only show active teams in standings
    # Only show active (visible) teams in standings
    teams = Team.query.filter_by(league_id=league_id, is_deleted=False, is_hidden=False).all()
    
    # Get completed matches (only regular season by default)
    if include_playoffs:
        matches_query = Match.query.filter_by(league_id=league_id, is_completed=True)
    else:
        matches_query = Match.query.filter(
            Match.league_id == league_id,
            Match.is_completed == True,
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
            'points': 0
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
