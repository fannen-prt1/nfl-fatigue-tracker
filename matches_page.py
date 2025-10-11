"""
NFL Player Fatigue Tracking Platform - Matches Page
This module handles all match-related functionality.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os
import numpy as np

def show_matches_page():
    """Display the matches page with advanced match management and analysis functionality."""
    st.title("🏟️ Matches & Games")
    st.markdown("---")
    
    # Create tabs for different match features
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Match Overview", 
        "🎯 Team Lineup Optimizer", 
        "📅 Match Calendar", 
        "📈 Performance Trends"
    ])
    
    with tab1:
        show_match_overview()
    
    with tab2:
        show_lineup_optimizer()
    
    with tab3:
        show_match_calendar()
    
    with tab4:
        show_performance_trends()

def load_all_match_data():
    """Load all match data from all players."""
    matches_dir = "matches_history"
    all_matches = []
    
    if not os.path.exists(matches_dir):
        return []
    
    for filename in os.listdir(matches_dir):
        if filename.endswith("_matches.json"):
            player_name = filename.replace("_matches.json", "").replace("_", " ")
            filepath = os.path.join(matches_dir, filename)
            
            try:
                with open(filepath, 'r') as f:
                    player_matches = json.load(f)
                    for match in player_matches:
                        match['player_name'] = player_name
                        all_matches.append(match)
            except Exception as e:
                st.error(f"Error loading matches for {player_name}: {e}")
    
    return all_matches

def get_player_current_fatigue():
    """Get current fatigue levels for all players."""
    players = st.session_state.get('players_data', [])
    return {player['name']: player['fatigue_prediction'] for player in players}

def show_match_overview():
    """Display match overview dashboard."""
    st.header("📊 Match Overview Dashboard")
    
    all_matches = load_all_match_data()
    players = st.session_state.get('players_data', [])
    
    if not all_matches:
        st.info("No match data available yet. Add matches through the Players page to see analysis here.")
        return
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_matches = len(set([(m['date'], m.get('opponent', 'Unknown')) for m in all_matches]))
        st.metric("Total Matches", total_matches)
    
    with col2:
        avg_team_fatigue = np.mean([m['fatigue'] for m in all_matches])
        st.metric("Avg Match Fatigue", f"{avg_team_fatigue:.1f}%")
    
    with col3:
        high_fatigue_matches = len([m for m in all_matches if m['fatigue'] > 80])
        st.metric("High Fatigue Matches", high_fatigue_matches)
    
    with col4:
        active_players = len([p for p in players if p.get('status', 'active') == 'active'])
        st.metric("Active Players", active_players)
    
    # Recent matches timeline
    st.subheader("📈 Recent Matches Timeline")
    
    if all_matches:
        # Group matches by date and opponent
        matches_by_game = {}
        for match in all_matches:
            game_key = f"{match['date']} vs {match.get('opponent', 'Unknown')}"
            if game_key not in matches_by_game:
                matches_by_game[game_key] = []
            matches_by_game[game_key].append(match)
        
        # Create timeline data
        timeline_data = []
        for game_key, game_matches in matches_by_game.items():
            avg_fatigue = np.mean([m['fatigue'] for m in game_matches])
            avg_bpm = np.mean([m['avg_bpm'] for m in game_matches])
            player_count = len(game_matches)
            
            timeline_data.append({
                'Game': game_key,
                'Date': game_matches[0]['date'],
                'Avg_Fatigue': avg_fatigue,
                'Avg_BPM': avg_bpm,
                'Player_Count': player_count
            })
        
        # Sort by date
        timeline_data.sort(key=lambda x: x['Date'], reverse=True)
        timeline_data = timeline_data[:10]  # Last 10 matches
        
        if timeline_data:
            fig = px.line(timeline_data, x='Date', y='Avg_Fatigue', 
                         title="Team Fatigue Trend Over Recent Matches",
                         markers=True, hover_data=['Player_Count'])
            fig.update_layout(yaxis_title="Average Team Fatigue (%)")
            st.plotly_chart(fig, width='stretch')

def show_lineup_optimizer():
    """Display team lineup optimizer based on fatigue levels."""
    st.header("🎯 Team Lineup Optimizer")
    
    players = st.session_state.get('players_data', [])
    
    if not players:
        st.info("No player data available. Add players first to use the lineup optimizer.")
        return
    
    st.write("Optimize your team lineup based on current fatigue levels and player positions.")
    
    # Formation selector
    col1, col2 = st.columns(2)
    
    with col1:
        formation = st.selectbox("Select Formation", [
            "4-3-4 (4 DB, 3 LB, 4 DL)",
            "3-4-4 (3 DL, 4 LB, 4 DB)", 
            "Custom Selection"
        ])
    
    with col2:
        max_fatigue = st.slider("Maximum Acceptable Fatigue %", 0, 100, 80)
    
    # Filter available players
    available_players = [p for p in players if p['fatigue_prediction'] <= max_fatigue]
    
    st.subheader("💡 Lineup Recommendations")
    
    if not available_players:
        st.error(f"No players available with fatigue level ≤ {max_fatigue}%. Consider increasing the threshold.")
        return
    
    # Group players by position
    players_by_position = {}
    for player in available_players:
        pos = player['position']
        if pos not in players_by_position:
            players_by_position[pos] = []
        players_by_position[pos].append(player)
    
    # Sort players within each position by fatigue (lowest first)
    for pos in players_by_position:
        players_by_position[pos].sort(key=lambda x: x['fatigue_prediction'])
    
    # Display optimal lineup
    st.subheader("🌟 Optimal Lineup (Lowest Fatigue)")
    
    lineup_cols = st.columns(3)
    
    with lineup_cols[0]:
        st.write("**Defensive Line**")
        dl_players = players_by_position.get('DL', []) + players_by_position.get('DE', []) + players_by_position.get('DT', [])
        for i, player in enumerate(dl_players[:4]):
            fatigue_color = "🟢" if player['fatigue_prediction'] < 60 else "🟡" if player['fatigue_prediction'] <= 80 else "🔴"
            st.write(f"{fatigue_color} {player['name']} - {player['fatigue_prediction']:.1f}%")
    
    with lineup_cols[1]:
        st.write("**Linebackers**")
        lb_players = players_by_position.get('LB', []) + players_by_position.get('MLB', []) + players_by_position.get('OLB', [])
        for i, player in enumerate(lb_players[:4]):
            fatigue_color = "🟢" if player['fatigue_prediction'] < 60 else "🟡" if player['fatigue_prediction'] <= 80 else "🔴"
            st.write(f"{fatigue_color} {player['name']} - {player['fatigue_prediction']:.1f}%")
    
    with lineup_cols[2]:
        st.write("**Defensive Backs**")
        db_players = players_by_position.get('CB', []) + players_by_position.get('S', []) + players_by_position.get('FS', []) + players_by_position.get('SS', [])
        for i, player in enumerate(db_players[:4]):
            fatigue_color = "🟢" if player['fatigue_prediction'] < 60 else "🟡" if player['fatigue_prediction'] <= 80 else "🔴"
            st.write(f"{fatigue_color} {player['name']} - {player['fatigue_prediction']:.1f}%")
    
    # Lineup statistics
    st.subheader("📊 Lineup Statistics")
    
    if available_players:
        optimal_lineup = []
        for pos_group in [dl_players[:4], lb_players[:4], db_players[:4]]:
            optimal_lineup.extend(pos_group)
        
        if optimal_lineup:
            avg_lineup_fatigue = np.mean([p['fatigue_prediction'] for p in optimal_lineup])
            avg_lineup_bpm = np.mean([p['avg_bpm'] for p in optimal_lineup])
            avg_lineup_speed = np.mean([p['avg_speed'] for p in optimal_lineup])
            
            metric_cols = st.columns(3)
            
            with metric_cols[0]:
                st.metric("Avg Lineup Fatigue", f"{avg_lineup_fatigue:.1f}%")
            
            with metric_cols[1]:
                st.metric("Avg Heart Rate", f"{avg_lineup_bpm:.1f} BPM")
            
            with metric_cols[2]:
                st.metric("Avg Speed", f"{avg_lineup_speed:.2f} yd/s")
    
    # Alternative players
    st.subheader("🔄 Alternative Players")
    high_fatigue_players = [p for p in players if p['fatigue_prediction'] > max_fatigue]
    
    if high_fatigue_players:
        st.write(f"**Players above {max_fatigue}% fatigue (consider resting):**")
        for player in high_fatigue_players:
            st.write(f"🔴 {player['name']} ({player['position']}) - {player['fatigue_prediction']:.1f}%")

def show_match_calendar():
    """Display match calendar with fatigue forecasting."""
    st.header("📅 Match Calendar & Schedule")
    
    # Upcoming matches scheduler
    st.subheader("📋 Schedule New Match")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        match_date = st.date_input("Match Date", min_value=datetime.now().date())
    
    with col2:
        opponent = st.text_input("Opponent Team")
    
    with col3:
        match_type = st.selectbox("Match Type", ["Regular Season", "Playoff", "Preseason", "Scrimmage"])
    
    if st.button("📅 Add to Calendar"):
        if opponent:
            # Save to calendar (could be expanded to actual calendar storage)
            st.success(f"Match vs {opponent} scheduled for {match_date}")
        else:
            st.error("Please enter opponent team name")
    
    # Calendar view of past matches
    st.subheader("📅 Match History Calendar")
    
    all_matches = load_all_match_data()
    
    if all_matches:
        # Group matches by date
        matches_by_date = {}
        for match in all_matches:
            date = match['date']
            if date not in matches_by_date:
                matches_by_date[date] = []
            matches_by_date[date].append(match)
        
        # Create calendar data
        calendar_data = []
        for date, matches in matches_by_date.items():
            avg_fatigue = np.mean([m['fatigue'] for m in matches])
            player_count = len(matches)
            opponent = matches[0].get('opponent', 'Unknown')
            
            calendar_data.append({
                'Date': date,
                'Opponent': opponent,
                'Players': player_count,
                'Avg_Fatigue': avg_fatigue,
                'Status': 'Completed'
            })
        
        # Sort by date
        calendar_data.sort(key=lambda x: x['Date'], reverse=True)
        
        # Display as table
        if calendar_data:
            df = pd.DataFrame(calendar_data)
            st.dataframe(df, width='stretch')
    
    # Fatigue prediction for upcoming matches
    st.subheader("🔮 Fatigue Forecast")
    
    players = st.session_state.get('players_data', [])
    
    if players:
        current_avg_fatigue = np.mean([p['fatigue_prediction'] for p in players])
        
        # Simple fatigue progression model
        days_ahead = st.slider("Days ahead to forecast", 1, 14, 7)
        
        # Assume 2% fatigue reduction per day of rest, 5% increase per match day
        forecasted_fatigue = max(0, current_avg_fatigue - (days_ahead * 2))
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Current Avg Fatigue", f"{current_avg_fatigue:.1f}%")
        
        with col2:
            st.metric(f"Forecasted Fatigue (+{days_ahead} days)", f"{forecasted_fatigue:.1f}%", 
                     delta=f"{forecasted_fatigue - current_avg_fatigue:.1f}%")
        
        # Recommendation
        if forecasted_fatigue < 60:
            st.success("✅ Team should be in good condition for upcoming matches")
        elif forecasted_fatigue <= 80:
            st.warning("⚠️ Monitor player fatigue levels closely")
        else:
            st.error("🚨 Consider additional rest or player rotation")

def show_performance_trends():
    """Display team performance trends analysis."""
    st.header("📈 Team Performance Trends")
    
    all_matches = load_all_match_data()
    
    if not all_matches:
        st.info("No match data available for trend analysis. Add matches through the Players page.")
        return
    
    # Performance over time
    st.subheader("📊 Performance Metrics Over Time")
    
    # Group matches by date for trend analysis
    matches_by_date = {}
    for match in all_matches:
        date = match['date']
        if date not in matches_by_date:
            matches_by_date[date] = []
        matches_by_date[date].append(match)
    
    # Calculate daily averages
    trend_data = []
    for date, matches in matches_by_date.items():
        trend_data.append({
            'Date': date,
            'Avg_Fatigue': np.mean([m['fatigue'] for m in matches]),
            'Avg_BPM': np.mean([m['avg_bpm'] for m in matches]),
            'Avg_Speed': np.mean([m['speed'] for m in matches]),
            'Avg_Acceleration': np.mean([m['acceleration'] for m in matches]),
            'Player_Count': len(matches)
        })
    
    # Sort by date
    trend_data.sort(key=lambda x: x['Date'])
    
    if len(trend_data) >= 2:
        # Multi-metric trend chart
        fig = go.Figure()
        
        dates = [item['Date'] for item in trend_data]
        
        fig.add_trace(go.Scatter(
            x=dates, y=[item['Avg_Fatigue'] for item in trend_data],
            mode='lines+markers', name='Fatigue %', yaxis='y1'
        ))
        
        fig.add_trace(go.Scatter(
            x=dates, y=[item['Avg_BPM'] for item in trend_data],
            mode='lines+markers', name='BPM', yaxis='y2'
        ))
        
        fig.update_layout(
            title="Performance Trends Over Time",
            xaxis_title="Date",
            yaxis=dict(title="Fatigue %", side="left"),
            yaxis2=dict(title="BPM", side="right", overlaying="y")
        )
        
        st.plotly_chart(fig, width='stretch')
        
        # Performance correlations
        st.subheader("🔗 Performance Correlations")
        
        if len(trend_data) >= 3:
            df = pd.DataFrame(trend_data)
            numeric_cols = ['Avg_Fatigue', 'Avg_BPM', 'Avg_Speed', 'Avg_Acceleration']
            correlation_matrix = df[numeric_cols].corr()
            
            fig_corr = px.imshow(
                correlation_matrix,
                text_auto=True,
                aspect="auto",
                title="Performance Metrics Correlation Matrix"
            )
            st.plotly_chart(fig_corr, width='stretch')
        
        # Performance insights
        st.subheader("💡 Performance Insights")
        
        latest_fatigue = trend_data[-1]['Avg_Fatigue']
        prev_fatigue = trend_data[-2]['Avg_Fatigue'] if len(trend_data) > 1 else latest_fatigue
        fatigue_change = latest_fatigue - prev_fatigue
        
        col1, col2 = st.columns(2)
        
        with col1:
            if fatigue_change > 5:
                st.error(f"🚨 Fatigue increased by {fatigue_change:.1f}% - Consider rest")
            elif fatigue_change < -5:
                st.success(f"✅ Fatigue decreased by {abs(fatigue_change):.1f}% - Good recovery")
            else:
                st.info(f"📊 Fatigue stable (±{abs(fatigue_change):.1f}%)")
        
        with col2:
            avg_recent_fatigue = np.mean([item['Avg_Fatigue'] for item in trend_data[-3:]])
            if avg_recent_fatigue < 60:
                st.success("🟢 Team in excellent condition")
            elif avg_recent_fatigue <= 80:
                st.warning("🟡 Team condition acceptable")
            else:
                st.error("🔴 Team fatigue levels concerning")
    
    else:
        st.info("Need at least 2 matches to show trends. Add more match data to see analysis.")