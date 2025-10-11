import streamlit as st
import pandas as pd
from PIL import Image
import numpy as np
import os
import json
from players_page import show_players_page
from matches_page import show_matches_page

# File paths for data persistence
PLAYERS_DATA_FILE = "players_data.json"
PHOTOS_DIR = "player_photos"

def save_players_data(players_data):
    """Save players data to JSON file."""
    try:
        with open(PLAYERS_DATA_FILE, 'w') as f:
            json.dump(players_data, f, indent=2)
    except Exception as e:
        st.error(f"Error saving player data: {e}")

def load_players_data():
    """Load players data from JSON file or return sample data if file doesn't exist."""
    try:
        if os.path.exists(PLAYERS_DATA_FILE):
            with open(PLAYERS_DATA_FILE, 'r') as f:
                players_data = json.load(f)
                # Ensure all players have required fields
                for player in players_data:
                    if 'photo_path' not in player:
                        player['photo_path'] = None
                    if 'status' not in player:
                        player['status'] = 'active'  # Default status for existing players
                    if 'fatigue_prediction' not in player:
                        player['fatigue_prediction'] = calculate_fatigue_prediction(
                            player['avg_bpm'], player['rr_ms'], 
                            player['avg_speed'], player['acceleration']
                        )
                return players_data
        else:
            # First time running - create sample data and save it
            sample_data = initialize_sample_players()
            save_players_data(sample_data)
            return sample_data
    except Exception as e:
        st.error(f"Error loading player data: {e}")
        # Return sample data as fallback
        return initialize_sample_players()

def clear_all_photos():
    """Clear all player photos from storage and update player data."""
    try:
        # Clear photo paths from all players
        for player in st.session_state.players_data:
            if player.get('photo_path'):
                # Try to delete the physical file
                try:
                    if os.path.exists(player['photo_path']):
                        os.remove(player['photo_path'])
                except:
                    pass  # Continue even if file deletion fails
                
                # Remove photo path from player data
                player['photo_path'] = None
        
        # Save updated data
        save_players_data(st.session_state.players_data)
        
        # Optionally remove the entire photos directory if empty
        try:
            if os.path.exists(PHOTOS_DIR):
                # Check if directory is empty
                if not os.listdir(PHOTOS_DIR):
                    os.rmdir(PHOTOS_DIR)
        except:
            pass  # Continue even if directory removal fails
        
        return True
    except Exception as e:
        st.error(f"Error clearing photos: {e}")
        return False

def clear_all_players():
    """Clear all players from the platform and reset to empty state."""
    try:
        # First clear all photos
        clear_all_photos()
        
        # Clear all player data
        st.session_state.players_data = []
        
        # Save empty data to file
        save_players_data(st.session_state.players_data)
        
        # Try to remove the entire photos directory
        try:
            if os.path.exists(PHOTOS_DIR):
                import shutil
                shutil.rmtree(PHOTOS_DIR)
        except:
            pass  # Continue even if directory removal fails
        
        # Try to remove the entire matches history directory
        try:
            if os.path.exists("matches_history"):
                import shutil
                shutil.rmtree("matches_history")
        except:
            pass  # Continue even if directory removal fails
        
        return True
    except Exception as e:
        st.error(f"Error clearing all players: {e}")
        return False

def main():
    """Main function to run the NFL fatigue tracking platform."""
    st.set_page_config(
        page_title="NFL Fatigue Tracker",
        page_icon="⚫",
        layout="wide"
    )
    
    # Sidebar navigation
    st.sidebar.title("🏈 NFL Fatigue Tracker")
    page = st.sidebar.selectbox(
        "🧭 Navigate to:",
        ["🏠 Main Dashboard", "👥 Players", "🏟️ Matches"]
    )
    
    # Page routing
    if page == "🏠 Main Dashboard":
        show_main_dashboard()
    elif page == "👥 Players":
        show_players_page()
    elif page == "🏟️ Matches":
        show_matches_page()

def show_main_dashboard():
    """Display the main dashboard page."""
    st.title("🏈 NFL Player Fatigue Tracking Platform ⚡")
    st.markdown("---")
    
    # Initialize session state for players data
    if 'players_data' not in st.session_state:
        st.session_state.players_data = load_players_data()
    
    # Sidebar sections
    st.sidebar.header("➕ Add New Player")
    with st.sidebar.expander("👤 Add Player", expanded=False):
        add_new_player_form()
    
    st.sidebar.header("🎲 Generate Random Players")
    with st.sidebar.expander("🎯 Generate Players", expanded=False):
        generate_random_players_form()
    
    st.sidebar.header("📊 Manual Metric Entry")
    selected_player = st.sidebar.selectbox(
        "Select Player:",
        options=[f"{p['name']} (#{p['number']})" for p in st.session_state.players_data]
    )
    
    if selected_player:
        player_index = next(i for i, p in enumerate(st.session_state.players_data) 
                          if f"{p['name']} (#{p['number']})" == selected_player)
        
        st.sidebar.subheader(f"Update {selected_player}")
        new_bpm = st.sidebar.number_input("Average BPM", 
                                        value=float(st.session_state.players_data[player_index]['avg_bpm']),
                                        min_value=40.0, max_value=200.0, step=0.1)
        new_rr_ms = st.sidebar.number_input("RR_MS", 
                                          value=float(st.session_state.players_data[player_index]['rr_ms']),
                                          min_value=200.0, max_value=2000.0, step=1.0)
        new_speed = st.sidebar.number_input("Avg Speed (yards/sec)", 
                                          value=st.session_state.players_data[player_index]['avg_speed'],
                                          min_value=0.0, max_value=15.0, step=0.1)
        new_acceleration = st.sidebar.number_input("Acceleration (yards/sec²)", 
                                                 value=st.session_state.players_data[player_index]['acceleration'],
                                                 min_value=0.0, max_value=10.0, step=0.1)
        new_status = st.sidebar.selectbox("Player Status", 
                                        options=["active", "benched", "practice squad", "injured"],
                                        index=["active", "benched", "practice squad", "injured"].index(st.session_state.players_data[player_index].get('status', 'active')))
        
        if st.sidebar.button("📊 Update Metrics"):
            st.session_state.players_data[player_index]['avg_bpm'] = new_bpm
            st.session_state.players_data[player_index]['rr_ms'] = new_rr_ms
            st.session_state.players_data[player_index]['avg_speed'] = new_speed
            st.session_state.players_data[player_index]['acceleration'] = new_acceleration
            st.session_state.players_data[player_index]['status'] = new_status
            # Recalculate fatigue prediction
            st.session_state.players_data[player_index]['fatigue_prediction'] = calculate_fatigue_prediction(
                new_bpm, new_rr_ms, new_speed, new_acceleration
            )
            save_players_data(st.session_state.players_data)  # Save to file
            st.sidebar.success("✅ Metrics updated!")
            st.rerun()
    
    # Photo update section
    st.sidebar.header("📸 Update Player Photo")
    photo_player = st.sidebar.selectbox(
        "📋 Select Player for Photo Update:",
        options=[f"{p['name']} (#{p['number']})" for p in st.session_state.players_data],
        key="photo_player_select"
    )
    
    if photo_player:
        photo_player_index = next(i for i, p in enumerate(st.session_state.players_data) 
                                if f"{p['name']} (#{p['number']})" == photo_player)
        
        uploaded_file = st.sidebar.file_uploader(
            f"Upload photo for {photo_player}",
            type=['png', 'jpg', 'jpeg'],
            key=f"photo_upload_{photo_player_index}"
        )
        
        if uploaded_file is not None:
            # Save the uploaded file
            photos_dir = "player_photos"
            if not os.path.exists(photos_dir):
                os.makedirs(photos_dir)
            
            photo_path = os.path.join(photos_dir, f"player_{photo_player_index}_{uploaded_file.name}")
            with open(photo_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Update player data with photo path
            st.session_state.players_data[photo_player_index]['photo_path'] = photo_path
            save_players_data(st.session_state.players_data)  # Save to file
            st.sidebar.success(f"Photo updated for {photo_player}!")
            st.rerun()
    
    # Player removal section
    st.sidebar.header("🗑️ Remove Player")
    if len(st.session_state.players_data) > 0:
        remove_player = st.sidebar.selectbox(
            "⚠️ Select Player to Remove:",
            options=[f"{p['name']} (#{p['number']})" for p in st.session_state.players_data],
            key="remove_player_select"
        )
        
        if remove_player:
            remove_player_index = next(i for i, p in enumerate(st.session_state.players_data) 
                                     if f"{p['name']} (#{p['number']})" == remove_player)
            
            # Show player details for confirmation
            player_to_remove = st.session_state.players_data[remove_player_index]
            st.sidebar.write(f"**Player:** {player_to_remove['name']}")
            st.sidebar.write(f"**Team:** {player_to_remove['team']}")
            st.sidebar.write(f"**Position:** {player_to_remove['position']}")
            
            # Confirmation checkbox
            confirm_removal = st.sidebar.checkbox(
                f"I confirm I want to remove {player_to_remove['name']}",
                key="confirm_removal"
            )
            
            # Remove button with confirmation
            if st.sidebar.button("Remove Player", type="secondary"):
                if confirm_removal:
                    # Remove player photo if it exists
                    if player_to_remove.get('photo_path') and os.path.exists(player_to_remove['photo_path']):
                        try:
                            os.remove(player_to_remove['photo_path'])
                        except:
                            pass  # If file deletion fails, continue anyway
                    
                    # Remove player matches history file if it exists
                    removed_player_name = st.session_state.players_data[remove_player_index]['name']
                    safe_player_name = removed_player_name.replace(" ", "_").replace("/", "_").replace("\\", "_")
                    matches_file = f"matches_history/{safe_player_name}_matches.json"
                    if os.path.exists(matches_file):
                        try:
                            os.remove(matches_file)
                        except:
                            pass  # If file deletion fails, continue anyway
                    
                    # Remove player from data
                    st.session_state.players_data.pop(remove_player_index)
                    save_players_data(st.session_state.players_data)  # Save to file
                    st.sidebar.success(f"✅ Player {removed_player_name} removed successfully!")
                    st.rerun()
                else:
                    st.sidebar.error("❌ Please confirm the removal by checking the checkbox above.")
    else:
        st.sidebar.info("No players available to remove.")
    
    # Clear all photos section
    st.sidebar.header("🗂️ Clear All Photos")
    if st.sidebar.button("🖼️ Clear All Player Photos", type="secondary"):
        if clear_all_photos():
            st.sidebar.success("✅ All player photos cleared successfully!")
            st.rerun()
        else:
            st.sidebar.error("❌ Error clearing photos.")
    
    # Clear all players section
    st.sidebar.header("🚨 Clear All Players")
    st.sidebar.warning("⚠️ This will remove ALL players and their data!")
    confirm_clear_all = st.sidebar.checkbox("☑️ I confirm I want to clear ALL players", key="confirm_clear_all")
    if st.sidebar.button("🗑️ Clear All Players", type="secondary"):
        if confirm_clear_all:
            if clear_all_players():
                st.sidebar.success("✅ All players cleared successfully!")
                st.rerun()
            else:
                st.sidebar.error("❌ Error clearing players.")
        else:
            st.sidebar.error("⚠️ Please confirm by checking the checkbox above.")
    
    # Main dashboard content
    st.header("🏆 Player Fatigue Dashboard")
    st.write("Real-time monitoring of NFL player fatigue levels and performance metrics.")
    
    # Display players in grid (4 per row)
    display_players_grid(st.session_state.players_data)

def add_new_player_form():
    """Display form to add a new player."""
    with st.form("add_player_form"):
        st.subheader("Player Information")
        
        col1, col2 = st.columns(2)
        with col1:
            new_name = st.text_input("👤 Player Name*", placeholder="e.g., Tom Brady")
            new_number = st.number_input("🔢 Jersey Number*", min_value=1, max_value=99, value=1)
        
        with col2:
            new_position = st.selectbox("🏈 Position*", 
                                      ["QB", "RB", "WR", "TE", "OL", "DL", "LB", "CB", "S", "K", "P"])
            new_team = st.text_input("🏟️ Team*", placeholder="e.g., Tampa Bay Buccaneers")
        
        st.subheader("📊 Player Status")
        new_status = st.selectbox("⚡ Status*", ["active", "benched", "practice squad", "injured"])
        
        st.subheader("📈 Performance Metrics")
        col3, col4 = st.columns(2)
        with col3:
            new_bpm = st.number_input("❤️ Average BPM", min_value=40.0, max_value=200.0, value=75.0, step=0.1)
            new_rr_ms = st.number_input("💓 RR_MS", min_value=200.0, max_value=2000.0, value=800.0, step=1.0)
        
        with col4:
            new_speed = st.number_input("🏃 Avg Speed (yards/sec)", min_value=0.0, max_value=15.0, 
                                      value=5.0, step=0.1)
            new_acceleration = st.number_input("⚡ Acceleration (yards/sec²)", min_value=0.0, 
                                             max_value=10.0, value=3.5, step=0.1)
        
        # Photo upload
        st.subheader("📸 Player Photo (Optional)")
        uploaded_photo = st.file_uploader("🖼️ Upload player photo", type=['png', 'jpg', 'jpeg'])
        
        submitted = st.form_submit_button("➕ Add Player")
        
        if submitted:
            if new_name and new_team:
                # Check if player number already exists
                existing_numbers = [p['number'] for p in st.session_state.players_data]
                if new_number in existing_numbers:
                    st.error(f"❌ Jersey number {new_number} is already taken!")
                    return
                
                # Create new player
                new_player = {
                    "name": new_name,
                    "number": new_number,
                    "position": new_position,
                    "team": new_team,
                    "avg_bpm": new_bpm,
                    "rr_ms": new_rr_ms,
                    "avg_speed": new_speed,
                    "acceleration": new_acceleration,
                    "status": new_status,
                    "photo_path": None
                }
                
                # Calculate fatigue prediction
                new_player['fatigue_prediction'] = calculate_fatigue_prediction(
                    new_bpm, new_rr_ms, new_speed, new_acceleration
                )
                
                # Handle photo upload
                if uploaded_photo is not None:
                    photos_dir = "player_photos"
                    if not os.path.exists(photos_dir):
                        os.makedirs(photos_dir)
                    
                    photo_path = os.path.join(photos_dir, f"player_{len(st.session_state.players_data)}_{uploaded_photo.name}")
                    with open(photo_path, "wb") as f:
                        f.write(uploaded_photo.getbuffer())
                    new_player['photo_path'] = photo_path
                
                # Add to players data
                st.session_state.players_data.append(new_player)
                save_players_data(st.session_state.players_data)  # Save to file
                st.success(f"✅ Player {new_name} added successfully!")
                st.rerun()
            else:
                st.error("❌ Please fill in all required fields (marked with *)")

def generate_random_players_form():
    """Display form to generate random players."""
    import random
    
    with st.form("generate_random_players_form"):
        st.subheader("🎲 Generate Random Players")
        
        # Configuration options
        col1, col2 = st.columns(2)
        
        with col1:
            num_players = st.number_input("👥 Number of Players", min_value=1, max_value=50, value=5)
            team_name = st.text_input("🏆 Team Name", placeholder="e.g., Random Eagles", value="Random Team")
        
        with col2:
            position_distribution = st.selectbox(
                "⚽ Position Distribution",
                ["Balanced NFL Roster", "Defensive Focus", "Offensive Focus", "Random Mix"]
            )
        
        # Player quality settings
        st.subheader("⭐ Player Quality Settings")
        quality_level = st.selectbox(
            "💪 Overall Team Quality",
            ["Elite Team", "Good Team", "Average Team", "Mixed Quality", "Random"]
        )
        
        submitted = st.form_submit_button("🎲 Generate Random Players")
        
        if submitted:
            # Generate random players
            new_players = create_random_players(num_players, team_name, position_distribution, quality_level)
            
            # Check for jersey number conflicts
            existing_numbers = [p['number'] for p in st.session_state.players_data]
            
            players_added = 0
            for player in new_players:
                # Find available jersey number
                original_number = player['number']
                attempts = 0
                while player['number'] in existing_numbers and attempts < 99:
                    player['number'] = random.randint(1, 99)
                    attempts += 1
                
                if player['number'] not in existing_numbers:
                    st.session_state.players_data.append(player)
                    existing_numbers.append(player['number'])
                    players_added += 1
            
            # Save and update
            if players_added > 0:
                save_players_data(st.session_state.players_data)
                st.success(f"✅ Generated and added {players_added} random players!")
                st.rerun()
            else:
                st.error("❌ Could not add players - too many jersey number conflicts!")

def create_random_players(num_players, team_name, position_distribution, quality_level):
    """Create a list of random players with realistic stats."""
    import random
    
    # NFL Positions with realistic distributions
    if position_distribution == "Balanced NFL Roster":
        positions = (["QB"] * 2 + ["RB"] * 3 + ["WR"] * 5 + ["TE"] * 2 + ["OL"] * 8 +
                    ["DL"] * 6 + ["LB"] * 6 + ["CB"] * 4 + ["S"] * 3 + ["K", "P"])
    elif position_distribution == "Defensive Focus":
        positions = ["DL"] * 8 + ["LB"] * 8 + ["CB"] * 6 + ["S"] * 4 + ["QB", "RB", "WR"]
    elif position_distribution == "Offensive Focus":
        positions = ["QB"] * 3 + ["RB"] * 5 + ["WR"] * 8 + ["TE"] * 3 + ["OL"] * 6
    else:  # Random Mix
        all_positions = ["QB", "RB", "WR", "TE", "OL", "DL", "LB", "CB", "S", "K", "P"]
        positions = [random.choice(all_positions) for _ in range(num_players)]
    
    # Realistic NFL player names
    first_names = [
        "Aaron", "Adrian", "Antonio", "Brandon", "Calvin", "Dak", "Deion", "Derek", "Deshaun",
        "Ezekiel", "Frank", "George", "Jarvis", "Josh", "Julian", "Julio", "Lamar", "Mac",
        "Michael", "Mike", "Nick", "Odell", "Patrick", "Rob", "Russell", "Stefon", "Tom",
        "Travis", "Tyreek", "Von", "Zach", "DeAndre", "Khalil", "Alvin", "Chris", "Cooper",
        "Davante", "DeVonta", "Jalen", "Justin", "Kyler", "Najee", "Saquon", "Tua"
    ]
    
    last_names = [
        "Adams", "Allen", "Brady", "Brown", "Cook", "Cooper", "Davis", "Evans", "Green",
        "Hill", "Hopkins", "Jackson", "Johnson", "Jones", "Kelce", "Lewis", "Mack", "Miller",
        "Murray", "Newton", "Robinson", "Rogers", "Smith", "Taylor", "Thomas", "Watson",
        "White", "Williams", "Wilson", "Young", "Beckham", "Bell", "Bosa", "Donald", "Elliott",
        "Garrett", "Gronkowski", "Henry", "Kamara", "Mahomes", "McCaffrey", "Ramsey", "Watt"
    ]
    
    # Quality-based stat ranges
    if quality_level == "Elite Team":
        bpm_range = (65, 85)
        rr_range = (700, 900)
        speed_range = (6.0, 9.0)
        accel_range = (4.0, 6.5)
    elif quality_level == "Good Team":
        bpm_range = (70, 90)
        rr_range = (650, 950)
        speed_range = (5.0, 7.5)
        accel_range = (3.5, 5.5)
    elif quality_level == "Average Team":
        bpm_range = (75, 95)
        rr_range = (600, 1000)
        speed_range = (4.0, 6.5)
        accel_range = (3.0, 5.0)
    elif quality_level == "Mixed Quality":
        bpm_range = (65, 100)
        rr_range = (550, 1100)
        speed_range = (3.5, 8.0)
        accel_range = (2.5, 6.0)
    else:  # Random
        bpm_range = (60, 110)
        rr_range = (500, 1200)
        speed_range = (2.0, 10.0)
        accel_range = (2.0, 7.0)
    
    players = []
    used_numbers = set()
    
    for i in range(min(num_players, len(positions))):
        # Generate unique jersey number
        jersey_num = random.randint(1, 99)
        while jersey_num in used_numbers:
            jersey_num = random.randint(1, 99)
        used_numbers.add(jersey_num)
        
        # Generate realistic stats based on position
        position = positions[i]
        
        # Position-specific stat adjustments
        if position in ["RB", "WR", "CB"]:  # Speed positions
            speed_multiplier = 1.2
            bpm_adjustment = -5
        elif position in ["OL", "DL"]:  # Power positions
            speed_multiplier = 0.8
            bpm_adjustment = 5
        elif position == "QB":  # Quarterbacks
            speed_multiplier = 0.9
            bpm_adjustment = -2
        else:  # Default
            speed_multiplier = 1.0
            bpm_adjustment = 0
        
        # Generate stats
        bpm = max(50, min(120, random.uniform(*bpm_range) + bpm_adjustment))
        rr_ms = random.uniform(*rr_range)
        speed = max(1.0, min(12.0, random.uniform(*speed_range) * speed_multiplier))
        acceleration = max(1.0, min(8.0, random.uniform(*accel_range) * speed_multiplier))
        
        # Create player
        player = {
            "name": f"{random.choice(first_names)} {random.choice(last_names)}",
            "number": jersey_num,
            "position": position,
            "team": team_name,
            "avg_bpm": round(bpm, 1),
            "rr_ms": round(rr_ms, 1),
            "avg_speed": round(speed, 2),
            "acceleration": round(acceleration, 2),
            "status": random.choice(["active"] * 8 + ["benched"] * 1 + ["practice squad"] * 1),  # 80% active
            "photo_path": None
        }
        
        # Calculate fatigue prediction
        player['fatigue_prediction'] = calculate_fatigue_prediction(
            player['avg_bpm'], player['rr_ms'], player['avg_speed'], player['acceleration']
        )
        
        players.append(player)
    
    return players

def initialize_sample_players():
    """Initialize sample player data."""
    players = []
    
    # Calculate fatigue predictions for each player
    for player in players:
        player['fatigue_prediction'] = calculate_fatigue_prediction(
            player['avg_bpm'], player['rr_ms'], player['avg_speed'], player['acceleration']
        )
    
    return players

def calculate_fatigue_prediction(bpm, rr_ms, speed, acceleration):
    """Calculate fatigue prediction based on metrics."""
    # Simple fatigue calculation (you can make this more sophisticated)
    # Higher BPM, lower RR_MS, higher speed/acceleration = higher fatigue
    bpm_factor = (bpm - 60) / 40  # Normalize BPM
    rr_factor = (1200 - rr_ms) / 400  # Inverse RR_MS (lower is more fatigued)
    speed_factor = speed / 10  # Normalize speed
    accel_factor = acceleration / 6  # Normalize acceleration
    
    fatigue_score = (bpm_factor * 0.3 + rr_factor * 0.3 + speed_factor * 0.2 + accel_factor * 0.2)
    fatigue_percentage = max(0, min(100, fatigue_score * 100))
    
    return round(fatigue_percentage, 1)

def get_fatigue_color(fatigue_level):
    """Get color indicator based on fatigue level."""
    if fatigue_level < 60:
        return "[LOW]"  # Low fatigue
    elif fatigue_level < 80:
        return "[MEDIUM]"  # Medium fatigue
    else:
        return "[HIGH]"  # High fatigue



def analyze_fatigue_reasons(bpm, rr_ms, speed, acceleration):
    """Analyze and explain fatigue level based on the four metrics with detailed precision."""
    high_fatigue_reasons = []
    moderate_fatigue_reasons = []
    good_condition_reasons = []
    
    # Detailed BPM Analysis (more precise thresholds)
    if bpm >= 110:
        high_fatigue_reasons.append("very high heart rate (>110 BPM)")
    elif bpm >= 95:
        high_fatigue_reasons.append("high heart rate (95-110 BPM)")
    elif bpm >= 85:
        moderate_fatigue_reasons.append("elevated heart rate (85-94 BPM)")
    elif bpm >= 70:
        good_condition_reasons.append("normal heart rate (70-84 BPM)")
    else:
        good_condition_reasons.append("excellent resting heart rate (<70 BPM)")
    
    # Detailed RR_MS Analysis (Heart Rate Variability - more precise)
    if rr_ms <= 500:
        high_fatigue_reasons.append("critically low HRV (<500ms - severe stress)")
    elif rr_ms <= 650:
        high_fatigue_reasons.append("very low HRV (500-650ms - high stress)")
    elif rr_ms <= 750:
        moderate_fatigue_reasons.append("low HRV (650-750ms - moderate stress)")
    elif rr_ms <= 900:
        moderate_fatigue_reasons.append("below average HRV (750-900ms)")
    elif rr_ms <= 1100:
        good_condition_reasons.append("good HRV (900-1100ms)")
    else:
        good_condition_reasons.append("excellent HRV (>1100ms - optimal recovery)")
    
    # Detailed Speed Analysis (more granular)
    if speed >= 8.0:
        high_fatigue_reasons.append("very high speed (>8.0 yd/s - sprint level)")
    elif speed >= 6.5:
        high_fatigue_reasons.append("high movement speed (6.5-8.0 yd/s)")
    elif speed >= 5.0:
        moderate_fatigue_reasons.append("moderate speed (5.0-6.4 yd/s)")
    elif speed >= 3.5:
        good_condition_reasons.append("controlled speed (3.5-4.9 yd/s)")
    else:
        good_condition_reasons.append("low impact speed (<3.5 yd/s)")
    
    # Detailed Acceleration Analysis (more precise thresholds)
    if acceleration >= 5.0:
        high_fatigue_reasons.append("very high acceleration (>5.0 yd/s² - explosive)")
    elif acceleration >= 4.0:
        high_fatigue_reasons.append("high acceleration (4.0-5.0 yd/s²)")
    elif acceleration >= 3.0:
        moderate_fatigue_reasons.append("moderate acceleration (3.0-3.9 yd/s²)")
    elif acceleration >= 2.0:
        good_condition_reasons.append("controlled acceleration (2.0-2.9 yd/s²)")
    else:
        good_condition_reasons.append("low acceleration demands (<2.0 yd/s²)")
    
    # Compile comprehensive analysis
    all_reasons = []
    
    if high_fatigue_reasons:
        all_reasons.append("HIGH STRESS: " + ", ".join(high_fatigue_reasons))
    
    if moderate_fatigue_reasons:
        all_reasons.append("MODERATE: " + ", ".join(moderate_fatigue_reasons))
    
    if good_condition_reasons:
        all_reasons.append("GOOD: " + ", ".join(good_condition_reasons))
    
    # Return detailed multi-line analysis
    if len(all_reasons) == 0:
        return "Normal physiological parameters across all metrics"
    
    return "\n".join(all_reasons)

def generate_player_suggestions(bpm, rr_ms, speed, acceleration, fatigue_level):
    """Generate personalized suggestions based on player metrics and fatigue level."""
    suggestions = []
    
    # Heart Rate based suggestions
    if bpm >= 110:
        suggestions.append("Immediate rest required - heart rate critically high")
        suggestions.append("Increase hydration and electrolyte intake")
        suggestions.append("Apply cooling strategies (ice baths, cooling vests)")
    elif bpm >= 95:
        suggestions.append("Reduce training intensity for next session")
        suggestions.append("Focus on breathing exercises and relaxation techniques")
    elif bpm >= 85:
        suggestions.append("Monitor closely - consider lighter workouts")
        suggestions.append("Ensure adequate sleep (8+ hours)")
    elif bpm <= 70:
        suggestions.append("Excellent cardiovascular fitness - can handle increased load")
        suggestions.append("Ready for high-intensity training sessions")
    
    # Heart Rate Variability suggestions
    if rr_ms <= 500:
        suggestions.append("Critical stress levels - mandatory rest day")
        suggestions.append("Consider stress management counseling")
        suggestions.append("Implement meditation or mindfulness practices")
    elif rr_ms <= 650:
        suggestions.append("High stress detected - reduce training volume")
        suggestions.append("Schedule recovery activities (massage, stretching)")
        suggestions.append("Prioritize sleep quality and duration")
    elif rr_ms <= 750:
        suggestions.append("Balance training with adequate recovery time")
        suggestions.append("Focus on anti-inflammatory nutrition")
    elif rr_ms >= 1100:
        suggestions.append("Excellent recovery status - can increase training intensity")
        suggestions.append("Optimal condition for skill development work")
    
    # Speed based suggestions
    if speed >= 8.0:
        suggestions.append("High-speed work detected - monitor for overuse injuries")
        suggestions.append("Extra focus on leg muscle recovery and stretching")
        suggestions.append("Limit high-speed activities in next 24-48 hours")
    elif speed >= 6.5:
        suggestions.append("Alternate high-speed days with recovery sessions")
        suggestions.append("Include dynamic warm-ups before training")
    elif speed <= 3.5:
        suggestions.append("Can safely increase movement intensity")
        suggestions.append("Good candidate for speed development drills")
    
    # Acceleration based suggestions
    if acceleration >= 5.0:
        suggestions.append("Explosive work overload - risk of muscle strain")
        suggestions.append("Apply ice to major muscle groups post-training")
        suggestions.append("Avoid plyometric exercises for 24 hours")
    elif acceleration >= 4.0:
        suggestions.append("High explosive demands - ensure proper warm-up")
        suggestions.append("Include mobility work in daily routine")
    elif acceleration <= 2.0:
        suggestions.append("Low explosive load - can add power training")
        suggestions.append("Consider strength and conditioning focus")
    
    # Overall fatigue level suggestions
    if fatigue_level > 80:
        suggestions.append("CRITICAL: Complete rest recommended")
        suggestions.append("Consider medical evaluation if symptoms persist")
        suggestions.append("Implement continuous monitoring protocol")
    elif fatigue_level >= 60:
        suggestions.append("HIGH FATIGUE: Light activity only (walking, stretching)")
        suggestions.append("Focus on recovery nutrition (protein, antioxidants)")
        suggestions.append("Daily monitoring required")
    elif fatigue_level >= 40:
        suggestions.append("MODERATE: 50-70% of normal training intensity")
        suggestions.append("Consider alternative low-impact activities")
    elif fatigue_level <= 30:
        suggestions.append("GOOD CONDITION: Normal training can proceed")
        suggestions.append("Excellent time for skill refinement")
        suggestions.append("Can handle increased training load if needed")
    
    # Remove duplicates and limit to most relevant suggestions
    unique_suggestions = list(dict.fromkeys(suggestions))
    return unique_suggestions[:6]  # Limit to top 6 suggestions

def sort_players_by_status(players_data):
    """Sort players by status priority: active, benched, practice squad, injured."""
    status_priority = {"active": 1, "benched": 2, "practice squad": 3, "injured": 4}
    return sorted(players_data, key=lambda x: status_priority.get(x.get('status', 'active'), 5))

def display_players_grid(players_data):
    """Display players in a grid layout (4 per row), sorted by status."""
    # Sort players by status before displaying
    sorted_players = sort_players_by_status(players_data)
    
    # Create rows of 4 players each
    for i in range(0, len(sorted_players), 4):
        cols = st.columns(4)
        
        for j, col in enumerate(cols):
            if i + j < len(sorted_players):
                player = sorted_players[i + j]
                
                with col:
                    # Player card container
                    with st.container():
                        st.markdown(f"""
                        <div style="
                            border: 2px solid #ddd;
                            border-radius: 10px;
                            padding: 15px;
                            margin: 10px 0;
                            background-color: #f9f9f9;
                            text-align: center;
                        ">
                        """, unsafe_allow_html=True)
                        
                        # Player name (bigger and on top, white colored)
                        st.markdown(f"<h3 style='text-align: center; margin-bottom: 10px; color: white;'><strong>{player['name']}</strong></h3>", unsafe_allow_html=True)
                        
                        # Player photo (use uploaded photo if available, otherwise placeholder)
                        if player.get('photo_path') and os.path.exists(player['photo_path']):
                            try:
                                st.image(player['photo_path'], width=150)
                            except:
                                st.image("https://via.placeholder.com/150x150/cccccc/ffffff?text=Player", 
                                        width=150)
                        else:
                            st.image("https://via.placeholder.com/150x150/cccccc/ffffff?text=Player", 
                                    width=150)
                        
                        # Player number and position (below photo)
                        st.markdown(f"**#{player['number']} - {player['position']}**")
                        st.markdown(f"*{player['team']}*")
                        
                        # Player status
                        st.markdown(f"**Status: {player.get('status', 'active').title()}**")
                        
                        # Fatigue prediction with color indicator
                        fatigue_color = get_fatigue_color(player['fatigue_prediction'])
                        st.markdown(f"### {fatigue_color} {player['fatigue_prediction']}%")
                        st.markdown("**Fatigue Level**")
                        
                        # Fatigue analysis reason
                        fatigue_reason = analyze_fatigue_reasons(
                            player['avg_bpm'], player['rr_ms'], 
                            player['avg_speed'], player['acceleration']
                        )
                        st.markdown(f"*{fatigue_reason}*")
                        
                        # Player suggestions
                        suggestions = generate_player_suggestions(
                            player['avg_bpm'], player['rr_ms'], 
                            player['avg_speed'], player['acceleration'],
                            player['fatigue_prediction']
                        )
                        
                        # Display suggestions in an expandable section
                        if suggestions:
                            with st.expander("Recommendations", expanded=False):
                                for suggestion in suggestions:
                                    st.markdown(f"• {suggestion}")
                        
                        
                        # Key metrics
                        st.markdown("---")
                        st.markdown("**Metrics:**")
                        st.markdown(f"BPM: {player['avg_bpm']}")
                        st.markdown(f"RR_MS: {player['rr_ms']}")
                        st.markdown(f"Speed: {player['avg_speed']} yd/s")
                        st.markdown(f"Accel: {player['acceleration']} yd/s²")
                        
                        st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
