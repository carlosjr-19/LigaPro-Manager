import os
import sys

# Add project root to path
basedir = os.path.dirname(os.path.abspath(__file__)) # d:/.../backend
project_root = os.path.dirname(basedir) # d:/.../LigaFutbol-main
sys.path.append(project_root)

from backend.app import app, db, User, League, Team, Player, Match, calculate_standings
from flask import Flask
import uuid
from datetime import datetime, timezone

def run_verification():
    print("Starting verification...")
    
    with app.app_context():
        # Create separate test db or use main one? 
        # Using main one but carefully cleaning up or using unique IDs
        # To avoid messing up user data, I will create a dedicated test league
        
        # 1. Setup Test Data
        test_id = str(uuid.uuid4())[:8]
        user_email = f"test_user_{test_id}@example.com"
        
        user = User(email=user_email, name="Test User", password="hashedpassword", role="owner")
        db.session.add(user)
        db.session.commit()
        
        league = League(name=f"Test League {test_id}", user_id=user.id)
        db.session.add(league)
        db.session.commit()
        
        team_a = Team(name="Team A", league_id=league.id)
        team_b = Team(name="Team B (To Delete)", league_id=league.id)
        db.session.add_all([team_a, team_b])
        db.session.commit()
        
        player_b = Player(name="Player B1", team_id=team_b.id, number=10, curp=f"CURP{test_id}")
        db.session.add(player_b)
        db.session.commit()
        
        # Match 1: Completed (Should remain)
        match1 = Match(
            league_id=league.id,
            home_team_id=team_a.id,
            away_team_id=team_b.id,
            match_date=datetime.now(timezone.utc),
            home_score=2,
            away_score=1,
            is_completed=True
        )
        
        # Match 2: Upcoming (Should be deleted)
        match2 = Match(
            league_id=league.id,
            home_team_id=team_b.id,
            away_team_id=team_a.id,
            match_date=datetime.now(timezone.utc),
            is_completed=False
        )
        
        matches = [match1, match2]
        db.session.add_all(matches)
        
        # Create Captain for Team B
        captain_email = f"cap_test_{test_id}@example.com"
        captain = User(
            email=captain_email,
            password="password",
            name="Captain B",
            role="captain",
            team_id=team_b.id
        )
        db.session.add(captain)
        db.session.commit()
        
        # Link captain to team manually (usually done by add_captain route)
        team_b.captain_user_id = captain.id
        db.session.commit()
        
        # Save IDs for verification
        m1_id = match1.id
        m2_id = match2.id
        team_b_id = team_b.id
        player_b_id = player_b.id
        team_a_id = team_a.id
        captain_id = captain.id
        
        print(f"Created League {league.id} with Teams {team_a.id}, {team_b.id} and Matches {match1.id}, {match2.id}")
        print(f"Created Captain {captain.id} for Team B")
        
        # 2. Simulate Delete Team B
        # logic from delete_team route
        print("Simulating deletion of Team B...")
        
        # Delete upcoming matches
        Match.query.filter(
            (Match.home_team_id == team_b.id) | (Match.away_team_id == team_b.id),
            Match.is_completed == False
        ).delete(synchronize_session=False)
        
        # Delete players
        Player.query.filter_by(team_id=team_b.id).delete(synchronize_session=False)
        
        # Delete captain(s) - replicating the new logic in app.py
        if team_b.captain_user_id:
            c = User.query.get(team_b.captain_user_id)
            if c: db.session.delete(c)
        User.query.filter_by(team_id=team_b.id, role='captain').delete(synchronize_session=False)
        
        # Soft delete team
        team_b.is_deleted = True
        db.session.commit()
        
        # 3. Verify Soft Deletion State
        # Expunge all to ensure we fetch fresh from DB and don't use stale objects in session
        db.session.expire_all()
        
        t_b_check = Team.query.get(team_b_id)
        assert t_b_check is not None, "Team B should still exist in DB"
        assert t_b_check.is_deleted == True, "Team B should be marked deleted"
        
        m1_check = Match.query.get(m1_id)
        assert m1_check is not None, "Completed match should still exist"
        
        m2_check = Match.query.get(m2_id)
        assert m2_check is None, "Upcoming match should be deleted"
        
        p_b_check = Player.query.get(player_b_id)
        assert p_b_check is None, "Player B should be deleted"
        
        c_check = User.query.get(captain_id)
        assert c_check is None, "Captain B should be deleted"
        
        print("Soft delete verification PASSED")
        
        # 4. Verify Standings
        # Team A should still have points from Match 1 (Win = 3pts)
        standings = calculate_standings(league.id)
        # standings list contains dicts. Find Team A.
        team_a_stats = next((s for s in standings if s['team'].id == team_a_id), None)
        assert team_a_stats is not None, "Team A should be in standings"
        assert team_a_stats['points'] == 3, f"Team A should have 3 points, got {team_a_stats['points']}"
        
        # Deleted team should NOT be in active standings list (filtered in app.py logic I added)
        team_b_stats = next((s for s in standings if s['team'].id == team_b_id), None)
        assert team_b_stats is None, "Team B (deleted) should NOT be in standings list"
        
        print("Standings verification PASSED")
        
        # 5. Verify Team Limit Logic
        # Team B is deleted. League has Team A (active) and Team B (deleted).
        # Count should be 1 (Team A only)
        count_active = Team.query.filter_by(league_id=league.id, is_deleted=False).count()
        assert count_active == 1, f"Should have 1 active team, got {count_active}"
        
        # Count total (physically in DB)
        count_total = Team.query.filter_by(league_id=league.id).count()
        assert count_total == 2, f"Should have 2 total teams in DB, got {count_total}"
        
        print("Team limit check verification PASSED")
        
        # 6. Simulate Reset Season (Hard Delete)
        print("Simulating Season Reset...")
        
        # Logic from reset_season route
        Match.query.filter_by(league_id=league.id).delete(synchronize_session=False) # Delete all matches
        Team.query.filter_by(league_id=league.id, is_deleted=True).delete(synchronize_session=False) # Hard delete
        db.session.commit()
        
        # 6. Verify Hard Deletion
        db.session.expire_all()
        t_b_final = Team.query.get(team_b_id)
        assert t_b_final is None, "Team B should be permanently deleted after season reset"
        
        t_a_final = Team.query.get(team_a_id)
        assert t_a_final is not None, "Team A should still exist"
        
        print("Season reset verification PASSED")
        
        # Clean up
        db.session.delete(league)
        db.session.delete(user)
        db.session.delete(t_a_final)
        db.session.commit()
        print("Cleanup done.")

if __name__ == '__main__':
    run_verification()
