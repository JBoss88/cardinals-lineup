import requests
import smtplib
from email.message import EmailMessage
from datetime import datetime
import time
import sys
import os

# --- CONFIGURATION ---
TEAM_ID = 138  # St. Louis Cardinals
SENDER_EMAIL = "jacksonboss88@gmail.com"
SENDER_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")
RECEIVER_EMAIL = ["jacksonboss88@gmail.com", 'jason.boss@fedex.com']

def get_todays_game():
    """Checks if the Cardinals play today and returns the game ID and details."""
    today = datetime.now().strftime("%Y-%m-%d")
    url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&teamId={TEAM_ID}&date={today}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if data['totalGames'] == 0:
            return None, "No game scheduled for today."
            
        game = data['dates'][0]['games'][0]
        game_pk = game['gamePk']
        
        # Get matchup details for the email subject line
        away_team = game['teams']['away']['team']['name']
        home_team = game['teams']['home']['team']['name']
        matchup = f"{away_team} @ {home_team}"
        
        return game_pk, matchup
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching schedule: {e}")
        return None, None

def get_lineup(game_pk):
    """Fetches the boxscore and parses the Cardinals' starting lineup."""
    url = f"https://statsapi.mlb.com/api/v1/game/{game_pk}/boxscore"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        teams = data['teams']
        
        # Determine if Cardinals are home or away
        if teams['home']['team']['id'] == TEAM_ID:
            cards_data = teams['home']
        else:
            cards_data = teams['away']
            
        players = cards_data['players']
        starting_lineup = []
        
        # Loop through all players on the roster for this game
        for player_key, player_info in players.items():
            # Starting players have a batting order ending in '00' (e.g., '100' for 1st)
            if 'battingOrder' in player_info and player_info['battingOrder'].endswith('00'):
                order_string = player_info['battingOrder']
                order_num = int(order_string[0]) # Extracts the 1 from '100'
                
                name = player_info['person']['fullName']
                position = player_info['position']['abbreviation']
                
                starting_lineup.append((order_num, f"{order_num}. {name} - {position}"))
        
        # Sort by batting order
        starting_lineup.sort()
        
        # If we found 9 players, the lineup is officially posted
        if len(starting_lineup) >= 9:
            # Extract just the formatted strings
            return "\n".join([player[1] for player in starting_lineup])
        else:
            return None # Lineup not posted yet
            
    except Exception as e:
        print(f"Error fetching lineup: {e}")
        return None

def send_email(subject, body):
    """Formats and sends the email via Gmail SMTP."""
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    
    # Change this line to join the list with a comma:
    msg['To'] = ", ".join(RECEIVER_EMAIL)

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        print("Lineup email sent successfully to everyone!")
    except Exception as e:
        print(f"Failed to send email: {e}")

def main():
    print("Starting Cardinals Lineup Bot...")
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 1. Check if we already sent the email today
    if os.path.exists("last_sent.txt"):
        with open("last_sent.txt", "r") as f:
            if f.read().strip() == today:
                print("We already sent today's lineup email. Shutting down.")
                return

    # 2. Check for a game today
    game_pk, matchup_info = get_todays_game()
    
    if not game_pk:
        print(matchup_info)
        return
        
    print(f"Game found: {matchup_info}")
    
    # 3. Check for the lineup (No more loops!)
    lineup_text = get_lineup(game_pk)
    
    if lineup_text:
        print("\nLineup secured!")
        print(lineup_text)
        
        # Send the email
        subject = f"⚾ Cardinals Lineup is Out: {matchup_info}"
        body = f"Here is your starting lineup for {matchup_info}:\n\n{lineup_text}\n\nGo Cards!"
        send_email(subject, body)
        
        # 4. Save today's date so we don't send it again
        with open("last_sent.txt", "w") as f:
            f.write(today)
            
    else:
        print("Lineup not posted yet. GitHub will try again next hour.")

if __name__ == "__main__":
    main()