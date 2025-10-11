"""
NFL Player Fatigue Tracking Platform - Players Page
This module handles all player-related functionality.
"""

import streamlit as st
import pandas as pd
import numpy as np
import os
import json
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go

def show_players_page():
    """Display the players page with comprehensive player management functionality."""
    st.title("👥 Players Management")
    st.markdown("---")
    
    # Initialize session state for players data if not exists
    if 'players_data' not in st.session_state:
        st.session_state.players_data = load_players_data()
    
    # Check if there are any players
    if not st.session_state.players_data:
        st.info("No players found. Please add players from the Main Dashboard first.")
        return
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["📊 Overview", "📋 Player List", "⚙️ Management"])
    
    with tab1:
        show_players_overview()
    
    with tab2:
        show_detailed_player_list()
    
    with tab3:
        show_player_management()

def load_players_data():
    """Load players data from JSON file."""
    try:
        if os.path.exists("players_data.json"):
            with open("players_data.json", 'r') as f:
                return json.load(f)
        return []
    except Exception as e:
        st.error(f"Error loading player data: {e}")
        return []

def save_players_data(players_data):
    """Save players data to JSON file."""
    try:
        with open("players_data.json", 'w') as f:
            json.dump(players_data, f, indent=2)
    except Exception as e:
        st.error(f"Error saving player data: {e}")

def get_fatigue_color_rgb(fatigue_level):
    """Get RGB color based on fatigue level."""
    if fatigue_level < 60:
        return "rgb(46, 125, 50)"  # Green
    elif fatigue_level < 80:
        return "rgb(255, 152, 0)"  # Orange
    else:
        return "rgb(211, 47, 47)"  # Red

def show_players_overview():
    """Display players overview with key metrics."""
    st.header("📊 Team Overview")
    
    players = st.session_state.players_data
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Players", len(players))
    
    with col2:
        active_players = len([p for p in players if p.get('status', 'active') == 'active'])
        st.metric("Active Players", active_players)
    
    with col3:
        avg_fatigue = np.mean([p['fatigue_prediction'] for p in players]) if players else 0
        st.metric("Average Fatigue", f"{avg_fatigue:.1f}%")
    
    with col4:
        high_fatigue = len([p for p in players if p['fatigue_prediction'] > 80])
        st.metric("High Fatigue Players", high_fatigue, delta_color="inverse")
    
    # Status distribution chart
    st.subheader("📈 Player Status Distribution")
    
    status_counts = {}
    for player in players:
        status = player.get('status', 'active')
        status_counts[status] = status_counts.get(status, 0) + 1
    
    if status_counts:
        fig = px.pie(
            values=list(status_counts.values()),
            names=list(status_counts.keys()),
            title="📊 Player Status Distribution"
        )
        st.plotly_chart(fig, width='stretch')
    
    # Fatigue level distribution
    st.subheader("⚡ Fatigue Level Distribution")
    
    fatigue_ranges = {"Low (0-60%)": 0, "Medium (60-80%)": 0, "High (80-100%)": 0}
    for player in players:
        fatigue = player['fatigue_prediction']
        if fatigue < 60:
            fatigue_ranges["Low (0-60%)"] += 1
        elif fatigue <= 80:
            fatigue_ranges["Medium (60-80%)"] += 1
        else:
            fatigue_ranges["High (80-100%)"] += 1
    
    fig2 = px.bar(
        x=list(fatigue_ranges.keys()),
        y=list(fatigue_ranges.values()),
        title="Fatigue Level Distribution",
        color=list(fatigue_ranges.values()),
        color_continuous_scale="RdYlGn_r"
    )
    st.plotly_chart(fig2, width='stretch')
    
    # Team Average Metrics Charts
    st.subheader("📊 Team Average Metrics")
    
    if players:
        # Calculate team averages
        avg_bpm = np.mean([p['avg_bpm'] for p in players])
        avg_rr = np.mean([p['rr_ms'] for p in players])
        avg_speed = np.mean([p['avg_speed'] for p in players])
        avg_acceleration = np.mean([p['acceleration'] for p in players])
        avg_fatigue = np.mean([p['fatigue_prediction'] for p in players])
        
        # Create two rows of charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Average BPM Chart
            fig_bpm = px.bar(
                x=['Team Average'],
                y=[avg_bpm],
                title="Average Heart Rate (BPM)",
                color=[avg_bpm],
                color_continuous_scale="Reds",
                text=[f"{avg_bpm:.1f}"]
            )
            fig_bpm.update_traces(textposition="outside")
            fig_bpm.update_layout(showlegend=False, yaxis_title="BPM")
            st.plotly_chart(fig_bpm, width='stretch')
            
            # Average Speed Chart
            fig_speed = px.bar(
                x=['Team Average'],
                y=[avg_speed],
                title="Average Speed (yd/s)",
                color=[avg_speed],
                color_continuous_scale="Blues",
                text=[f"{avg_speed:.2f}"]
            )
            fig_speed.update_traces(textposition="outside")
            fig_speed.update_layout(showlegend=False, yaxis_title="Speed (yd/s)")
            st.plotly_chart(fig_speed, width='stretch')
        
        with col2:
            # Average RR Intervals Chart
            fig_rr = px.bar(
                x=['Team Average'],
                y=[avg_rr],
                title="Average RR Intervals (ms)",
                color=[avg_rr],
                color_continuous_scale="Greens",
                text=[f"{avg_rr:.0f}"]
            )
            fig_rr.update_traces(textposition="outside")
            fig_rr.update_layout(showlegend=False, yaxis_title="RR Intervals (ms)")
            st.plotly_chart(fig_rr, width='stretch')
            
            # Average Acceleration Chart
            fig_acc = px.bar(
                x=['Team Average'],
                y=[avg_acceleration],
                title="Average Acceleration (yd/s²)",
                color=[avg_acceleration],
                color_continuous_scale="Purples",
                text=[f"{avg_acceleration:.2f}"]
            )
            fig_acc.update_traces(textposition="outside")
            fig_acc.update_layout(showlegend=False, yaxis_title="Acceleration (yd/s²)")
            st.plotly_chart(fig_acc, width='stretch')
        
        # Combined metrics comparison chart
        st.subheader("📈 Metrics Comparison")
        
        metrics_data = {
            'Metric': ['Heart Rate (BPM)', 'RR Intervals (ms)', 'Speed (yd/s)', 'Acceleration (yd/s²)', 'Fatigue (%)'],
            'Value': [avg_bpm, avg_rr, avg_speed, avg_acceleration, avg_fatigue],
            'Normalized': [
                (avg_bpm / 200) * 100,  # Normalize BPM to 0-100 scale
                (avg_rr / 1000) * 100,  # Normalize RR to 0-100 scale
                avg_speed * 10,  # Scale speed for visibility
                avg_acceleration * 20,  # Scale acceleration for visibility
                avg_fatigue  # Fatigue is already 0-100
            ]
        }
        
        fig_combined = px.bar(
            x=metrics_data['Metric'],
            y=metrics_data['Normalized'],
            title="Team Metrics Overview (Normalized Scale)",
            color=metrics_data['Normalized'],
            color_continuous_scale="viridis",
            text=[f"{val:.1f}" for val in metrics_data['Value']]
        )
        fig_combined.update_traces(textposition="outside")
        fig_combined.update_layout(
            showlegend=False, 
            yaxis_title="Normalized Value (0-100)",
            xaxis_title="Metrics"
        )
        st.plotly_chart(fig_combined, width='stretch')
    
    else:
        st.info("No player data available for team metrics analysis.")

def show_detailed_player_list():
    """Display detailed list of all players."""
    st.header("📋 Detailed Player List")
    
    players = st.session_state.players_data
    
    # Search and filter options
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search_term = st.text_input("🔍 Search players", placeholder="Enter player name or team...")
    
    with col2:
        status_filter = st.selectbox("Filter by Status", 
                                   ["All"] + list(set([p.get('status', 'active') for p in players])))
    
    with col3:
        position_filter = st.selectbox("Filter by Position",
                                     ["All"] + list(set([p['position'] for p in players])))
    
    # Filter players
    filtered_players = players
    
    if search_term:
        filtered_players = [p for p in filtered_players 
                          if search_term.lower() in p['name'].lower() or 
                             search_term.lower() in p['team'].lower()]
    
    if status_filter != "All":
        filtered_players = [p for p in filtered_players 
                          if p.get('status', 'active') == status_filter]
    
    if position_filter != "All":
        filtered_players = [p for p in filtered_players 
                          if p['position'] == position_filter]
    
    # Sort options
    sort_by = st.selectbox("Sort by", 
                          ["Fatigue Level (High to Low)", "Fatigue Level (Low to High)", 
                           "Name (A-Z)", "Name (Z-A)", "Jersey Number"])
    
    if sort_by == "Fatigue Level (High to Low)":
        filtered_players.sort(key=lambda x: x['fatigue_prediction'], reverse=True)
    elif sort_by == "Fatigue Level (Low to High)":
        filtered_players.sort(key=lambda x: x['fatigue_prediction'])
    elif sort_by == "Name (A-Z)":
        filtered_players.sort(key=lambda x: x['name'])
    elif sort_by == "Name (Z-A)":
        filtered_players.sort(key=lambda x: x['name'], reverse=True)
    elif sort_by == "Jersey Number":
        filtered_players.sort(key=lambda x: x['number'])
    
    # Display players
    st.write(f"Showing {len(filtered_players)} of {len(players)} players")
    
    for i, player in enumerate(filtered_players):
        # Create expandable container for each player
        with st.expander(f"👤 {player['name']} #{player['number']} | {player['position']} | {player['team']} | Fatigue: {player['fatigue_prediction']}%", expanded=False):
            
            # Player basic info row
            col1, col2, col3 = st.columns([1, 2, 2])
            
            with col1:
                # Player photo
                if player.get('photo_path') and os.path.exists(player['photo_path']):
                    try:
                        st.image(player['photo_path'], width=100)
                    except:
                        st.image("https://via.placeholder.com/100x100/cccccc/ffffff?text=Player", width=100)
                else:
                    st.image("https://via.placeholder.com/100x100/cccccc/ffffff?text=Player", width=100)
            
            with col2:
                st.markdown("### Player Information")
                st.markdown(f"**Name:** {player['name']}")
                st.markdown(f"**Jersey:** #{player['number']}")
                st.markdown(f"**Position:** {player['position']}")
                st.markdown(f"**Team:** {player['team']}")
                st.markdown(f"**Status:** {player.get('status', 'active').title()}")
            
            with col3:
                st.markdown("### Current Metrics")
                fatigue = player['fatigue_prediction']
                color = get_fatigue_color_rgb(fatigue)
                
                st.markdown(f"**Fatigue Level:** <span style='color: {color}; font-size: 20px; font-weight: bold;'>{fatigue}%</span>", unsafe_allow_html=True)
                st.markdown(f"**Heart Rate:** {player['avg_bpm']} BPM")
                st.markdown(f"**HRV (RR_MS):** {player['rr_ms']} ms")
                st.markdown(f"**Speed:** {player['avg_speed']} yd/s")
                st.markdown(f"**Acceleration:** {player['acceleration']} yd/s²")
            
            st.markdown("---")
            
            # Metrics charts section
            st.markdown("### 📊 Performance Metrics Over Time")
            
            # Get actual match data from session state or load from persistent storage
            match_key = f"matches_{player['name']}"
            match_data = get_match_data_for_player(player['name'])
            
            # Match selector section
            st.markdown("#### 🎯 Match Analysis & Management")
            
            # Create tabs for different analysis types
            match_tab1, match_tab2 = st.tabs(["🎯 Single Match", "⚙️ Manage Matches"])
            
            with match_tab1:
                # Get current match data for single match analysis
                current_match_data = st.session_state.get(f"matches_{player['name']}", match_data)
                
                if current_match_data:
                    col_selector1, col_selector2 = st.columns([1, 2])
                    
                    with col_selector1:
                        # Single match selector
                        match_numbers = [m['match_number'] for m in current_match_data]
                        selected_match = st.selectbox(
                            f"Select Match for {player['name']}:",
                            options=match_numbers,
                            format_func=lambda x: f"Match {x}",
                            key=f"single_match_selector_{player['name']}_{i}"
                        )
                    
                    with col_selector2:
                        if selected_match and current_match_data:
                            selected_match_data = next((m for m in current_match_data if m['match_number'] == selected_match), None)
                            if selected_match_data:
                                st.markdown(f"**Selected: Match {selected_match}**")
                                
                                # Show selected match metrics in a compact format
                                metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
                                with metric_col1:
                                    st.metric("BPM", f"{selected_match_data['avg_bpm']}")
                                with metric_col2:
                                    st.metric("HRV", f"{selected_match_data['rr_ms']}")
                                with metric_col3:
                                    st.metric("Speed", f"{selected_match_data['speed']}")
                                with metric_col4:
                                    st.metric("Fatigue", f"{selected_match_data['fatigue']}%")
                    
                    # Single match metrics chart
                    if selected_match and current_match_data:
                        selected_match_data = next((m for m in current_match_data if m['match_number'] == selected_match), None)
                        if selected_match_data:
                            st.markdown(f"#### 📊 Match {selected_match} - Average Metrics")
                            single_match_chart = create_single_match_chart(selected_match_data, player['name'])
                            st.plotly_chart(single_match_chart, width='stretch', key=f"single_match_chart_{player['name']}_{i}")
                    elif current_match_data:
                        st.info("Select a match above to view its detailed metrics.")
                else:
                    st.info("No matches available. Add matches in the 'Manage Matches' tab first.")
                    selected_match = None
            
            with match_tab2:
                show_match_management(player, i, match_data)
                
                # Force chart refresh when match data changes
                if st.button(f"🔄 Refresh Charts for {player['name']}", key=f"refresh_charts_{player['name']}_{i}"):
                    st.rerun()
            
            st.markdown("#### 📈 Performance Over All Matches")
            
            # Create charts for metrics over matches
            col_chart1, col_chart2 = st.columns(2)
            
            # Get updated match data from session state for charts
            current_match_data = get_match_data_for_player(player['name'])
            
            if current_match_data:
                with col_chart1:
                    # Heart Rate and HRV over matches
                    fig1 = create_heart_metrics_chart(current_match_data, player['name'])
                    st.plotly_chart(fig1, width='stretch', key=f"heart_chart_{player['name']}_{i}")
                    
                    # Speed over matches
                    fig3 = create_speed_chart(current_match_data, player['name'])
                    st.plotly_chart(fig3, width='stretch', key=f"speed_chart_{player['name']}_{i}")
                
                with col_chart2:
                    # Fatigue level over matches
                    fig2 = create_fatigue_chart(current_match_data, player['name'])
                    st.plotly_chart(fig2, width='stretch', key=f"fatigue_chart_{player['name']}_{i}")
                    
                    # Acceleration over matches
                    fig4 = create_acceleration_chart(current_match_data, player['name'])
                    st.plotly_chart(fig4, width='stretch', key=f"accel_chart_{player['name']}_{i}")
            else:
                st.info("No match data available for charts. Add matches in the 'Manage Matches' tab.")
            
            # Performance summary
            st.markdown("### 📈 Performance Summary")
            
            if current_match_data and len(current_match_data) > 0:
                col_summary1, col_summary2, col_summary3, col_summary4 = st.columns(4)
                
                with col_summary1:
                    avg_match_bpm = np.mean([m['avg_bpm'] for m in current_match_data])
                    trend_bpm = "📈" if len(current_match_data) > 1 and current_match_data[-1]['avg_bpm'] > current_match_data[0]['avg_bpm'] else "📉"
                    st.metric("Avg Match BPM", f"{avg_match_bpm:.1f}", delta=f"{trend_bpm} Trend")
                
                with col_summary2:
                    avg_match_fatigue = np.mean([m['fatigue'] for m in current_match_data])
                    trend_fatigue = "📈" if len(current_match_data) > 1 and current_match_data[-1]['fatigue'] > current_match_data[0]['fatigue'] else "📉"
                    st.metric("Avg Match Fatigue", f"{avg_match_fatigue:.1f}%", delta=f"{trend_fatigue} Trend")
                
                with col_summary3:
                    avg_match_speed = np.mean([m['speed'] for m in current_match_data])
                    trend_speed = "📈" if len(current_match_data) > 1 and current_match_data[-1]['speed'] > current_match_data[0]['speed'] else "📉"
                    st.metric("Avg Match Speed", f"{avg_match_speed:.1f} yd/s", delta=f"{trend_speed} Trend")
                
                with col_summary4:
                    avg_match_accel = np.mean([m['acceleration'] for m in current_match_data])
                    trend_accel = "📈" if len(current_match_data) > 1 and current_match_data[-1]['acceleration'] > current_match_data[0]['acceleration'] else "📉"
                    st.metric("Avg Match Accel", f"{avg_match_accel:.1f} yd/s²", delta=f"{trend_accel} Trend")
            else:
                st.info("No match data available for performance summary. Add matches in the 'Manage Matches' tab.")

def show_player_management():
    """Display player management tools."""
    st.header("⚙️ Player Management")
    
    players = st.session_state.players_data
    
    # Bulk operations
    st.subheader("📦 Bulk Operations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 Export Player Data", type="secondary"):
            # Convert to CSV
            df = pd.DataFrame(players)
            csv = df.to_csv(index=False)
            st.download_button(
                label="💾 Download CSV",
                data=csv,
                file_name="players_data.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("Generate Report", type="secondary"):
            generate_team_report(players)
    
    # Individual player management
    st.subheader("Individual Player Management")
    
    if players:
        selected_player_name = st.selectbox(
            "Select Player to Manage:",
            [f"{p['name']} (#{p['number']})" for p in players]
        )
        
        if selected_player_name:
            player_index = next(i for i, p in enumerate(players) 
                              if f"{p['name']} (#{p['number']})" == selected_player_name)
            player = players[player_index]
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("### Player Details")
                st.write(f"**Name:** {player['name']}")
                st.write(f"**Number:** #{player['number']}")
                st.write(f"**Position:** {player['position']}")
                st.write(f"**Team:** {player['team']}")
                st.write(f"**Status:** {player.get('status', 'active').title()}")
                st.write(f"**Fatigue Level:** {player['fatigue_prediction']}%")
            
            with col2:
                st.markdown("### Quick Actions")
                
                new_status = st.selectbox(
                    "Update Status:",
                    ["active", "benched", "practice squad", "injured"],
                    index=["active", "benched", "practice squad", "injured"].index(player.get('status', 'active'))
                )
                
                if st.button("Update Status"):
                    st.session_state.players_data[player_index]['status'] = new_status
                    save_players_data(st.session_state.players_data)
                    st.success(f"Status updated to {new_status}")
                    st.rerun()
    
    else:
        st.info("No players available for management.")

def generate_sample_match_data(player):
    """Generate sample match data for a player (replace with actual match data)."""
    import random
    
    # Generate data for last 10 matches
    matches = []
    base_bpm = player['avg_bpm']
    base_speed = player['avg_speed']
    base_accel = player['acceleration']
    base_rr_ms = player['rr_ms']
    
    for i in range(10):
        # Add some realistic variation
        match_bpm = base_bpm + random.uniform(-10, 15)
        match_rr_ms = base_rr_ms + random.uniform(-100, 100)
        match_speed = max(0, base_speed + random.uniform(-1, 2))
        match_accel = max(0, base_accel + random.uniform(-0.5, 1))
        
        # Calculate fatigue based on metrics
        fatigue = calculate_match_fatigue(match_bpm, match_rr_ms, match_speed, match_accel)
        
        matches.append({
            'match': f"Match {i+1}",
            'match_number': i+1,
            'avg_bpm': round(match_bpm, 1),
            'rr_ms': round(match_rr_ms, 1),
            'speed': round(match_speed, 1),
            'acceleration': round(match_accel, 1),
            'fatigue': round(fatigue, 1)
        })
    
    return matches

def calculate_match_fatigue(bpm, rr_ms, speed, acceleration):
    """Calculate fatigue for a specific match."""
    bpm_factor = (bpm - 60) / 40
    rr_factor = (1200 - rr_ms) / 400
    speed_factor = speed / 10
    accel_factor = acceleration / 6
    
    fatigue_score = (bpm_factor * 0.3 + rr_factor * 0.3 + speed_factor * 0.2 + accel_factor * 0.2)
    return max(0, min(100, fatigue_score * 100))

def create_heart_metrics_chart(match_data, player_name):
    """Create heart rate and HRV chart."""
    matches = [m['match'] for m in match_data]
    bpm_values = [m['avg_bpm'] for m in match_data]
    rr_values = [m['rr_ms'] for m in match_data]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=matches, y=bpm_values,
        mode='lines+markers',
        name='Heart Rate (BPM)',
        line=dict(color='red', width=3),
        yaxis='y'
    ))
    
    fig.add_trace(go.Scatter(
        x=matches, y=rr_values,
        mode='lines+markers',
        name='HRV (RR_MS)',
        line=dict(color='blue', width=3),
        yaxis='y2'
    ))
    
    fig.update_layout(
        title=f"{player_name} - Heart Metrics Over Matches",
        xaxis_title="Matches",
        yaxis=dict(title="Heart Rate (BPM)", side="left", color="red"),
        yaxis2=dict(title="HRV (RR_MS)", side="right", overlaying="y", color="blue"),
        height=300
    )
    
    return fig

def create_fatigue_chart(match_data, player_name):
    """Create fatigue level chart."""
    matches = [m['match'] for m in match_data]
    fatigue_values = [m['fatigue'] for m in match_data]
    
    # Color based on fatigue level
    colors = ['green' if f < 30 else 'orange' if f < 60 else 'red' for f in fatigue_values]
    
    fig = go.Figure(data=go.Scatter(
        x=matches, y=fatigue_values,
        mode='lines+markers',
        name='Fatigue Level',
        line=dict(color='purple', width=3),
        marker=dict(color=colors, size=8)
    ))
    
    # Add fatigue threshold lines
    fig.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Low Fatigue")
    fig.add_hline(y=60, line_dash="dash", line_color="orange", annotation_text="Medium Fatigue")
    fig.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="High Fatigue")
    
    fig.update_layout(
        title=f"{player_name} - Fatigue Level Over Matches",
        xaxis_title="Matches",
        yaxis_title="Fatigue Level (%)",
        yaxis=dict(range=[0, 100]),
        height=300
    )
    
    return fig

def create_speed_chart(match_data, player_name):
    """Create speed chart."""
    matches = [m['match'] for m in match_data]
    speed_values = [m['speed'] for m in match_data]
    
    fig = go.Figure(data=go.Scatter(
        x=matches, y=speed_values,
        mode='lines+markers',
        name='Speed',
        line=dict(color='green', width=3),
        fill='tonexty'
    ))
    
    fig.update_layout(
        title=f"{player_name} - Speed Over Matches",
        xaxis_title="Matches",
        yaxis_title="Speed (yd/s)",
        height=300
    )
    
    return fig

def create_acceleration_chart(match_data, player_name):
    """Create acceleration chart."""
    matches = [m['match'] for m in match_data]
    accel_values = [m['acceleration'] for m in match_data]
    
    fig = go.Figure(data=go.Bar(
        x=matches, y=accel_values,
        name='Acceleration',
        marker_color='lightblue'
    ))
    
    fig.update_layout(
        title=f"{player_name} - Acceleration Over Matches",
        xaxis_title="Matches",
        yaxis_title="Acceleration (yd/s²)",
        height=300
    )
    
    return fig

def create_single_match_chart(match_data, player_name):
    """Create a comprehensive chart for a single match's metrics."""
    
    # Prepare data for the chart
    metrics = ['BPM', 'HRV (RR_MS)', 'Speed (yd/s)', 'Acceleration (yd/s²)', 'Fatigue (%)']
    values = [
        match_data['avg_bpm'],
        match_data['rr_ms'] / 10,  # Scale down for better visualization
        match_data['speed'] * 10,   # Scale up for better visualization
        match_data['acceleration'] * 10,  # Scale up for better visualization
        match_data['fatigue']
    ]
    
    # Create colors based on metric type
    colors = ['red', 'blue', 'green', 'orange', 'purple']
    
    # Create a comprehensive bar chart
    fig = go.Figure()
    
    # Add bars for each metric
    fig.add_trace(go.Bar(
        x=metrics,
        y=values,
        text=[f"{match_data['avg_bpm']}", 
              f"{match_data['rr_ms']}", 
              f"{match_data['speed']}", 
              f"{match_data['acceleration']}", 
              f"{match_data['fatigue']}%"],
        textposition='auto',
        marker_color=colors,
        name=f"Match {match_data['match_number']} Metrics"
    ))
    
    fig.update_layout(
        title=f"{player_name} - Match {match_data['match_number']} Average Metrics",
        xaxis_title="Metrics",
        yaxis_title="Scaled Values (for visualization)",
        height=400,
        showlegend=False
    )
    
    # Add annotations to explain scaling
    fig.add_annotation(
        text="Note: HRV divided by 10, Speed & Acceleration multiplied by 10 for better visualization",
        xref="paper", yref="paper",
        x=0.5, y=-0.15,
        showarrow=False,
        font=dict(size=10, color="gray")
    )
    
    return fig



def show_match_management(player, player_index, match_data):
    """Show match management interface for adding, editing, and deleting matches."""
    st.markdown("#### ⚙️ Match Data Management")
    
    # Initialize match data in session state if not exists
    match_key = f"matches_{player['name']}"
    if match_key not in st.session_state:
        st.session_state[match_key] = match_data
    
    # Management options
    management_option = st.radio(
        "Choose action:",
        ["Add New Match", "Edit Existing Match", "Delete Match"],
        key=f"management_option_{player['name']}_{player_index}",
        horizontal=True
    )
    
    if management_option == "Add New Match":
        show_add_match_form(player, player_index)
    
    elif management_option == "Edit Existing Match":
        show_edit_match_form(player, player_index)
    
    elif management_option == "Delete Match":
        show_delete_match_form(player, player_index)
    
    # Display current matches summary
    st.markdown("#### 📋 Current Matches Summary")
    display_matches_summary(player)

def show_add_match_form(player, player_index):
    """Show form to add a new match."""
    st.markdown("##### ➕ Add New Match")
    
    match_key = f"matches_{player['name']}"
    current_matches = get_match_data_for_player(player['name'])
    next_match_number = len(current_matches) + 1
    
    with st.form(f"add_match_form_{player['name']}_{player_index}"):
        st.write(f"**Adding Match {next_match_number} for {player['name']}**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            new_bpm = st.number_input("Average BPM", min_value=40.0, max_value=200.0, value=75.0, key=f"new_bpm_{player['name']}_{player_index}")
            new_speed = st.number_input("Speed (yd/s)", min_value=0.0, max_value=15.0, value=5.0, step=0.1, key=f"new_speed_{player['name']}_{player_index}")
        
        with col2:
            new_rr_ms = st.number_input("HRV (RR_MS)", min_value=200.0, max_value=2000.0, value=800.0, key=f"new_rr_ms_{player['name']}_{player_index}")
            new_acceleration = st.number_input("Acceleration (yd/s²)", min_value=0.0, max_value=10.0, value=3.5, step=0.1, key=f"new_accel_{player['name']}_{player_index}")
        
        # Optional match details
        st.markdown("**Optional Match Details:**")
        match_date = st.date_input("Match Date", key=f"match_date_{player['name']}_{player_index}")
        opponent = st.text_input("Opponent", placeholder="e.g., Dallas Cowboys", key=f"opponent_{player['name']}_{player_index}")
        match_notes = st.text_area("Match Notes", placeholder="Any additional notes...", key=f"match_notes_{player['name']}_{player_index}")
        
        submitted = st.form_submit_button("Add Match", type="primary")
        
        if submitted:
            # Calculate fatigue for this match
            fatigue = calculate_match_fatigue(new_bpm, new_rr_ms, new_speed, new_acceleration)
            
            new_match = {
                'match': f"Match {next_match_number}",
                'match_number': next_match_number,
                'avg_bpm': round(new_bpm, 1),
                'rr_ms': round(new_rr_ms, 1),
                'speed': round(new_speed, 1),
                'acceleration': round(new_acceleration, 1),
                'fatigue': round(fatigue, 1),
                'date': str(match_date) if match_date else None,
                'opponent': opponent if opponent else None,
                'notes': match_notes if match_notes else None
            }
            
            # Add to session state
            if match_key not in st.session_state:
                st.session_state[match_key] = []
            st.session_state[match_key].append(new_match)
            
            # Save to player's persistent data
            save_match_data_to_player(player['name'], st.session_state[match_key])
            
            st.success(f"Match {next_match_number} added successfully!")
            st.rerun()

def show_edit_match_form(player, player_index):
    """Show form to edit an existing match."""
    st.markdown("##### ✏️ Edit Existing Match")
    
    match_key = f"matches_{player['name']}"
    current_matches = get_match_data_for_player(player['name'])
    
    if not current_matches:
        st.info("No matches available to edit.")
        return
    
    # Select match to edit
    match_to_edit = st.selectbox(
        "Select match to edit:",
        options=current_matches,
        format_func=lambda x: f"Match {x['match_number']} - BPM: {x['avg_bpm']}, Fatigue: {x['fatigue']}%",
        key=f"edit_match_selector_{player['name']}_{player_index}"
    )
    
    if match_to_edit:
        with st.form(f"edit_match_form_{player['name']}_{player_index}"):
            st.write(f"**Editing Match {match_to_edit['match_number']} for {player['name']}**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                edit_bpm = st.number_input("Average BPM", min_value=40.0, max_value=200.0, 
                                         value=float(match_to_edit['avg_bpm']), 
                                         key=f"edit_bpm_{player['name']}_{player_index}")
                edit_speed = st.number_input("Speed (yd/s)", min_value=0.0, max_value=15.0, 
                                           value=float(match_to_edit['speed']), step=0.1,
                                           key=f"edit_speed_{player['name']}_{player_index}")
            
            with col2:
                edit_rr_ms = st.number_input("HRV (RR_MS)", min_value=200.0, max_value=2000.0, 
                                           value=float(match_to_edit['rr_ms']),
                                           key=f"edit_rr_ms_{player['name']}_{player_index}")
                edit_acceleration = st.number_input("Acceleration (yd/s²)", min_value=0.0, max_value=10.0, 
                                                  value=float(match_to_edit['acceleration']), step=0.1,
                                                  key=f"edit_accel_{player['name']}_{player_index}")
            
            # Optional match details
            st.markdown("**Optional Match Details:**")
            edit_opponent = st.text_input("Opponent", value=match_to_edit.get('opponent', ''),
                                        key=f"edit_opponent_{player['name']}_{player_index}")
            edit_notes = st.text_area("Match Notes", value=match_to_edit.get('notes', ''),
                                    key=f"edit_notes_{player['name']}_{player_index}")
            
            submitted = st.form_submit_button("Update Match", type="primary")
            
            if submitted:
                # Calculate new fatigue
                new_fatigue = calculate_match_fatigue(edit_bpm, edit_rr_ms, edit_speed, edit_acceleration)
                
                # Find and update the match
                for i, match in enumerate(st.session_state[match_key]):
                    if match['match_number'] == match_to_edit['match_number']:
                        st.session_state[match_key][i] = {
                            'match': f"Match {match_to_edit['match_number']}",
                            'match_number': match_to_edit['match_number'],
                            'avg_bpm': round(edit_bpm, 1),
                            'rr_ms': round(edit_rr_ms, 1),
                            'speed': round(edit_speed, 1),
                            'acceleration': round(edit_acceleration, 1),
                            'fatigue': round(new_fatigue, 1),
                            'date': match_to_edit.get('date'),
                            'opponent': edit_opponent if edit_opponent else None,
                            'notes': edit_notes if edit_notes else None
                        }
                        break
                
                # Save to player's persistent data
                save_match_data_to_player(player['name'], st.session_state[match_key])
                
                st.success(f"Match {match_to_edit['match_number']} updated successfully!")
                st.rerun()

def show_delete_match_form(player, player_index):
    """Show form to delete matches - individual or all."""
    st.markdown("##### 🗑️ Delete Matches")
    
    match_key = f"matches_{player['name']}"
    current_matches = get_match_data_for_player(player['name'])
    
    if not current_matches:
        st.info("No matches available to delete.")
        return
    
    # Choose deletion type
    delete_type = st.radio(
        "What would you like to delete?",
        ["Delete Individual Match", "Clear All Matches"],
        key=f"delete_type_{player['name']}_{player_index}",
        horizontal=True
    )
    
    st.markdown("---")
    
    if delete_type == "Delete Individual Match":
        st.markdown("##### 🎯 Delete Single Match")
        
        # Select match to delete
        match_to_delete = st.selectbox(
            "Select match to delete:",
            options=current_matches,
            format_func=lambda x: f"Match {x['match_number']} - BPM: {x['avg_bpm']}, Fatigue: {x['fatigue']}%",
            key=f"delete_match_selector_{player['name']}_{player_index}"
        )
        
        if match_to_delete:
            st.warning(f"⚠️ You are about to delete Match {match_to_delete['match_number']}")
            
            # Show match details
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("BPM", match_to_delete['avg_bpm'])
            with col2:
                st.metric("HRV", match_to_delete['rr_ms'])
            with col3:
                st.metric("Speed", match_to_delete['speed'])
            with col4:
                st.metric("Fatigue", f"{match_to_delete['fatigue']}%")
            
            # Confirmation
            confirm_delete = st.checkbox(
                f"I confirm I want to delete Match {match_to_delete['match_number']}",
                key=f"confirm_delete_{player['name']}_{player_index}"
            )
            
            if st.button("Delete Match", type="secondary", disabled=not confirm_delete):
                if confirm_delete:
                    # Remove the match
                    st.session_state[match_key] = [m for m in current_matches if m['match_number'] != match_to_delete['match_number']]
                    
                    # Renumber remaining matches
                    for i, match in enumerate(st.session_state[match_key]):
                        match['match_number'] = i + 1
                        match['match'] = f"Match {i + 1}"
                    
                    # Save to player's persistent data
                    save_match_data_to_player(player['name'], st.session_state[match_key])
                    
                    st.success(f"Match deleted successfully!")
                    st.rerun()
    
    elif delete_type == "Clear All Matches":
        st.markdown("##### 🧹 Clear All Matches")
        
        st.warning(f"⚠️ You are about to delete ALL {len(current_matches)} matches for {player['name']}")
        st.error("This action cannot be undone!")
        
        # Show summary of what will be deleted
        st.markdown("**Matches that will be deleted:**")
        for match in current_matches:
            st.write(f"- Match {match['match_number']}: BPM {match['avg_bpm']}, Fatigue {match['fatigue']}%")
        
        # Confirmation
        confirm_clear = st.checkbox(
            f"I confirm I want to delete ALL matches for {player['name']}",
            key=f"confirm_clear_{player['name']}_{player_index}"
        )
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("Clear All Matches", type="secondary", disabled=not confirm_clear, key=f"clear_all_btn_{player['name']}_{player_index}"):
                if confirm_clear:
                    try:
                        # Clear ALL match data completely
                        
                        # 1. Clear session state
                        st.session_state[match_key] = []
                        
                        # 2. Clear any backup references
                        keys_to_remove = []
                        for key in st.session_state.keys():
                            if f"matches_{player['name']}" in key or f"{player['name']}_match" in key:
                                keys_to_remove.append(key)
                        
                        for key in keys_to_remove:
                            if key in st.session_state:
                                del st.session_state[key]
                        
                        # 3. Save empty data to persistent storage
                        if save_match_data_to_player(player['name'], []):
                            st.success("✅ All matches cleared successfully!")
                            st.info("📊 Match history table has been reset")
                            st.balloons()
                            
                            # 4. Force complete refresh by clearing confirmation state
                            if f"confirm_clear_{player['name']}_{player_index}" in st.session_state:
                                del st.session_state[f"confirm_clear_{player['name']}_{player_index}"]
                            
                            # 5. Force complete UI refresh
                            st.rerun()
                        else:
                            st.error("Failed to save cleared data to file")
                        
                    except Exception as e:
                        st.error(f"Error clearing matches: {str(e)}")
                        st.write(f"Debug info: {e}")
                else:
                    st.error("Please confirm by checking the checkbox above.")
        
        with col2:
            if st.button("Cancel", key=f"cancel_clear_{player['name']}_{player_index}"):
                st.info("Clear operation cancelled.")


def display_matches_summary(player):
    """Display a summary of current matches."""
    match_key = f"matches_{player['name']}"
    current_matches = get_match_data_for_player(player['name'])
    
    if not current_matches:
        st.info("No matches recorded yet.")
        return
    
    # Create summary DataFrame
    summary_data = []
    for match in current_matches:
        summary_data.append({
            'Match': match['match_number'],
            'BPM': match['avg_bpm'],
            'HRV': match['rr_ms'],
            'Speed': match['speed'],
            'Acceleration': match['acceleration'],
            'Fatigue %': match['fatigue'],
            'Opponent': match.get('opponent', '-'),
            'Notes': match.get('notes', '-')[:20] + '...' if match.get('notes') and len(match.get('notes')) > 20 else match.get('notes', '-')
        })
    
    summary_df = pd.DataFrame(summary_data)
    st.dataframe(summary_df, width='stretch')
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        avg_bpm = sum(m['avg_bpm'] for m in current_matches) / len(current_matches)
        st.metric("Avg BPM", f"{avg_bpm:.1f}")
    with col2:
        avg_fatigue = sum(m['fatigue'] for m in current_matches) / len(current_matches)
        st.metric("Avg Fatigue", f"{avg_fatigue:.1f}%")
    with col3:
        avg_speed = sum(m['speed'] for m in current_matches) / len(current_matches)
        st.metric("Avg Speed", f"{avg_speed:.1f}")
    with col4:
        st.metric("Total Matches", len(current_matches))

def save_match_data_to_player(player_name, match_data):
    """Save match data to player's persistent storage, sorted by date."""
    import json
    
    # Create matches directory if it doesn't exist
    matches_dir = "matches_history"
    if not os.path.exists(matches_dir):
        os.makedirs(matches_dir)
    
    # Sort matches by date and renumber before saving
    sorted_matches = sort_matches_by_date(match_data)
    for i, match in enumerate(sorted_matches, 1):
        match['match_number'] = i
        match['match'] = f"Match {i}"
    
    # Save match data to player-specific file
    file_path = os.path.join(matches_dir, f"{player_name.replace(' ', '_')}_matches.json")
    
    try:
        with open(file_path, 'w') as f:
            json.dump(sorted_matches, f, indent=2)
        return True
    except Exception as e:
        st.error(f"Error saving match data: {e}")
        return False

def load_match_data_for_player(player_name):
    """Load match data for a specific player."""
    import json
    
    matches_dir = "matches_history"
    file_path = os.path.join(matches_dir, f"{player_name.replace(' ', '_')}_matches.json")
    
    # If file doesn't exist, return empty list
    if not os.path.exists(file_path):
        return []
    
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        # If there's an error loading, return empty list instead of sample data
        return []

def sort_matches_by_date(matches):
    """Sort matches by date, with most recent first. Handle missing dates."""
    def get_sort_key(match):
        # If no date, use a very old date so it appears at the end
        if not match.get('date'):
            return '1900-01-01'
        return match['date']
    
    # Sort by date descending (most recent first)
    return sorted(matches, key=get_sort_key, reverse=True)

def get_match_data_for_player(player_name):
    """Get match data for a player, ensuring it's loaded from persistent storage and sorted by date."""
    match_key = f"matches_{player_name}"
    
    # If not in session state, load from file
    if match_key not in st.session_state:
        st.session_state[match_key] = load_match_data_for_player(player_name)
    
    # Get matches and sort by date
    matches = st.session_state.get(match_key, [])
    sorted_matches = sort_matches_by_date(matches)
    
    # Renumber matches based on date order (1 = most recent)
    for i, match in enumerate(sorted_matches, 1):
        match['match_number'] = i
        match['match'] = f"Match {i}"
    
    # Update session state with sorted and renumbered matches
    st.session_state[match_key] = sorted_matches
    
    return sorted_matches

def generate_team_report(players):
    """Generate a comprehensive team report."""
    st.subheader("📋 Team Fatigue Report")
    
    # Summary statistics
    total_players = len(players)
    avg_fatigue = np.mean([p['fatigue_prediction'] for p in players])
    high_fatigue_count = len([p for p in players if p['fatigue_prediction'] > 70])
    
    st.markdown(f"""
    ### Executive Summary
    
    **Total Players Monitored:** {total_players}
    
    **Average Team Fatigue Level:** {avg_fatigue:.1f}%
    
    **Players with High Fatigue (>70%):** {high_fatigue_count}
    
    **Risk Assessment:** {'HIGH RISK' if avg_fatigue > 60 else 'MODERATE RISK' if avg_fatigue > 40 else 'LOW RISK'}
    """)
    
    # High-risk players
    high_risk_players = [p for p in players if p['fatigue_prediction'] > 70]
    
    if high_risk_players:
        st.markdown("### ⚠️ High-Risk Players (Immediate Attention Required)")
        for player in high_risk_players:
            st.markdown(f"- **{player['name']}** (#{player['number']}) - {player['fatigue_prediction']}% fatigue")
    
    # Recommendations
    st.markdown("### 💡 Recommendations")
    
    if avg_fatigue > 60:
        st.markdown("- **Reduce training intensity** for the entire team")
        st.markdown("- **Implement mandatory rest periods** for high-fatigue players")
        st.markdown("- **Schedule additional recovery sessions**")
    elif avg_fatigue > 40:
        st.markdown("- **Monitor high-fatigue players closely**")
        st.markdown("- **Consider load management strategies**")
        st.markdown("- **Maintain current recovery protocols**")
    else:
        st.markdown("- **Team is in good condition**")
        st.markdown("- **Can handle increased training load if needed**")
        st.markdown("- **Continue current monitoring practices**")