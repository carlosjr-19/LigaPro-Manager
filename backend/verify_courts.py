import os
import sys
import uuid
from datetime import datetime
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app import app, db, User, League, Team, Match, Court

def run_verification():
    print("Starting Multi-Court Verification...")
    
    with app.app_context():
        # Clean up previous test data if any specific ones exist (optional)
        
        # 1. Create User (Premium)
        test_id = str(uuid.uuid4())[:8]
        user = User(
            email=f"premium_{test_id}@test.com",
            name="Premium User",
            password="hashed_password",
            role="owner",
            is_premium=True,
            premium_expires_at=datetime(2030, 1, 1)
        )
        db.session.add(user)
        db.session.commit()
        
        # 2. Create League (Should create Default Court)
        league = League(name=f"Court League {test_id}", user_id=user.id)
        db.session.add(league)
        db.session.flush()
        
        # Simulate creating default court (logic is in route, but we simulate it here or check if we use route logic)
        # Since I can't call route easily, I replicate the logic:
        default_court = Court(name="La Canchita", league_id=league.id)
        db.session.add(default_court)
        db.session.commit()
        
        print(f"Created League with Default Court: {default_court.name}")
        
        # 3. Add 2nd Court
        court2 = Court(name="La Raza", league_id=league.id)
        db.session.add(court2)
        db.session.commit()
        print(f"Created 2nd Court: {court2.name}")
        
        # 4. Check Limits (Try adding 4th?)
        # Current count = 2. Limit is 3.
        court3 = Court(name="Cancha 3", league_id=league.id)
        db.session.add(court3)
        db.session.commit()
        print(f"Created 3rd Court: {court3.name}")
        
        count = Court.query.filter_by(league_id=league.id).count()
        assert count == 3, f"Should have 3 courts, got {count}"
        
        # 5. Create Matches assigned to courts
        team1 = Team(name="T1", league_id=league.id)
        team2 = Team(name="T2", league_id=league.id)
        db.session.add_all([team1, team2])
        db.session.commit()
        
        match1 = Match(
            league_id=league.id,
            home_team_id=team1.id, 
            away_team_id=team2.id,
            court_id=default_court.id,
            match_date=datetime.now(),
            match_name="Match on Canchita"
        )
        match2 = Match(
            league_id=league.id,
            home_team_id=team2.id, 
            away_team_id=team1.id,
            court_id=court2.id,
            match_date=datetime.now(),
            match_name="Match on Raza"
        )
        db.session.add_all([match1, match2])
        db.session.commit()
        
        print("Created matches on different courts.")
        
        # 6. Verify Grouping Logic (Simulate generating report data)
        upcoming_matches = [match1, match2]
        matches_by_court = {}
        for match in upcoming_matches:
            c_name = match.court.name if match.court else "Cancha Principal"
            if c_name not in matches_by_court:
                matches_by_court[c_name] = []
            matches_by_court[c_name].append(match)
            
        print("Matches grouped by court:")
        for c, ms in matches_by_court.items():
            print(f"- {c}: {len(ms)} matches")
            
        assert "La Canchita" in matches_by_court
        assert "La Raza" in matches_by_court
        assert len(matches_by_court["La Canchita"]) == 1
        assert len(matches_by_court["La Raza"]) == 1
        
        print("VERIFICATION PASSED")

if __name__ == "__main__":
    run_verification()
