import pytest
from datetime import datetime
from cards_lineup import get_todays_game, get_lineup, TEAM_ID

# --- FIXTURES ---
@pytest.fixture
def mock_no_game_data():
    return {"totalGames": 0, "dates": []}

@pytest.fixture
def mock_game_scheduled_data():
    return {
        "totalGames": 1,
        "dates": [{
            "games": [{
                "gamePk": 745612,
                "teams": {
                    "away": {"team": {"name": "Chicago Cubs"}},
                    "home": {"team": {"name": "St. Louis Cardinals"}}
                }
            }]
        }]
    }

# --- TESTS ---
def test_get_todays_game_returns_none_when_no_games(requests_mock, mock_no_game_data):
    # 1. Intercept the exact URL your script will try to call
    today = datetime.now().strftime("%Y-%m-%d")
    url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&teamId={TEAM_ID}&date={today}"
    
    # 2. Tell the mock to return our fake JSON instead of hitting the internet
    requests_mock.get(url, json=mock_no_game_data)
    
    game_pk, matchup = get_todays_game()
    
    # 4. Assert your logic handled the 0 games correctly
    assert game_pk is None
    assert matchup == "No game scheduled for today."

def test_get_todays_game_returns_correct_matchup(requests_mock, mock_game_scheduled_data):
    today = datetime.now().strftime("%Y-%m-%d")
    url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&teamId={TEAM_ID}&date={today}"
    
    requests_mock.get(url, json=mock_game_scheduled_data)
    
    game_pk, matchup = get_todays_game()
    
    assert game_pk == 745612
    assert matchup == "Chicago Cubs @ St. Louis Cardinals"


@pytest.fixture
def mock_boxscore_data():
    # A heavily simplified version of the MLB boxscore JSON
    return {
        "teams": {
            "away": {
                "team": {"id": 112}, # Cubs
                "players": {}
            },
            "home": {
                "team": {"id": 138}, # Cardinals
                "players": {
                    "ID1": {"person": {"fullName": "Masyn Winn"}, "position": {"abbreviation": "SS"}, "battingOrder": "100"},
                    "ID2": {"person": {"fullName": "Willson Contreras"}, "position": {"abbreviation": "C"}, "battingOrder": "200"},
                    # ... a bench player to ensure your filtering works
                    "ID3": {"person": {"fullName": "Bench Player"}, "position": {"abbreviation": "OF"}, "battingOrder": "101"} 
                }
            }
        }
    }

def test_get_lineup_parses_starters_correctly(requests_mock, mock_boxscore_data):
    game_pk = 745612
    url = f"https://statsapi.mlb.com/api/v1/game/{game_pk}/boxscore"
    
    requests_mock.get(url, json=mock_boxscore_data)
    
    lineup_text = get_lineup(game_pk)
    
    # Assert the bench player was ignored and formatting is correct
    assert "1. Masyn Winn - SS" in lineup_text
    assert "2. Willson Contreras - C" in lineup_text
    assert "Bench Player" not in lineup_text