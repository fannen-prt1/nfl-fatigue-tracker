# NFL Player Fatigue Tracking Platform

A comprehensive web-based platform for monitoring and analyzing NFL player fatigue levels using real-time physiological metrics and performance data.

## Features

### Core Functionality
- **Player Management**: Add, update, and remove NFL players with complete profiles
- **Fatigue Analysis**: Real-time fatigue prediction based on multiple physiological metrics
- **Status Tracking**: Monitor player status (Active, Benched, Practice Squad, Injured)
- **Photo Management**: Upload and manage player photos
- **Data Persistence**: All data is automatically saved and persists across sessions

### Analytics & Insights
- **Multi-Metric Analysis**: Heart rate (BPM), heart rate variability (RR_MS), movement speed, and acceleration
- **Intelligent Fatigue Prediction**: Advanced algorithm analyzing all metrics for accurate fatigue assessment
- **Detailed Reasoning**: Comprehensive explanations for why fatigue levels are elevated or low
- **Personalized Recommendations**: AI-generated suggestions for training, recovery, and player management

### User Interface
- **Interactive Dashboard**: Clean, professional interface with player cards in grid layout
- **Status-Based Sorting**: Players automatically organized by status priority
- **Expandable Recommendations**: Detailed suggestions available for each player
- **Real-time Updates**: Instant feedback and automatic data saving

## Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/fannen-prt1/nfl-fatigue-tracker.git
   cd nfl-fatigue-tracker
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   - **Windows (PowerShell):**
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   - **Windows (Command Prompt):**
     ```cmd
     venv\Scripts\activate
     ```
   - **macOS/Linux:**
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Dependencies

The following Python packages are required:

```
streamlit>=1.28.0
pandas>=2.0.0
pillow>=10.0.0
numpy>=1.24.0
```

## Usage

1. **Start the application**
   ```bash
   streamlit run main.py
   ```

2. **Access the platform**
   - Open your web browser and navigate to `http://localhost:8501`
   - The platform will be accessible at this URL

3. **Platform Navigation**
   - **Main Dashboard**: View all players with fatigue analysis and recommendations
   - **Players Page**: Detailed player management (coming soon)
   - **Matches Page**: Match-based fatigue analysis (coming soon)

## File Structure

```
nfl-fatigue-tracker/
├── main.py                 # Main application file
├── players_page.py         # Players management module
├── matches_page.py         # Matches analysis module
├── requirements.txt        # Python dependencies
├── README.md              # Project documentation
├── players_data.json      # Player data storage (auto-generated)
├── player_photos/         # Player photo storage (auto-generated)
└── venv/                  # Virtual environment (created locally)
```

## Key Metrics Explained

### Heart Rate (BPM)
- **Normal Range**: 60-100 BPM at rest
- **Training Range**: 100-180+ BPM during activity
- **Impact**: Higher heart rates indicate increased cardiovascular stress

### Heart Rate Variability (RR_MS)
- **Healthy Range**: 900-1100+ ms
- **Stress Indicators**: <650 ms indicates high stress/poor recovery
- **Impact**: Lower variability suggests inadequate recovery

### Movement Speed (yards/second)
- **Low Impact**: <3.5 yd/s
- **Moderate**: 3.5-6.4 yd/s
- **High Impact**: >6.5 yd/s
- **Impact**: Higher speeds increase physical demands

### Acceleration (yards/second²)
- **Low Demand**: <2.0 yd/s²
- **Moderate**: 2.0-3.9 yd/s²
- **High Demand**: >4.0 yd/s²
- **Impact**: Higher acceleration increases injury risk

## Fatigue Analysis Algorithm

The platform uses a sophisticated algorithm that combines all four metrics:

```python
fatigue_score = (bpm_factor * 0.3) + (rr_factor * 0.3) + (speed_factor * 0.2) + (accel_factor * 0.2)
```

- **BPM Factor**: Normalized heart rate impact (30% weight)
- **RR Factor**: Inverse heart rate variability impact (30% weight)
- **Speed Factor**: Movement intensity impact (20% weight)
- **Acceleration Factor**: Explosive movement impact (20% weight)

## Player Status Categories

- **Active**: Starting players available for games
- **Benched**: Available but not starting
- **Practice Squad**: Developmental players
- **Injured**: Unavailable due to injury

Players are automatically sorted by status priority in the dashboard.

## Data Management

### Automatic Saving
- All player data is automatically saved to `players_data.json`
- Photo uploads are stored in the `player_photos/` directory
- Changes persist across browser refreshes and application restarts

### Data Operations
- **Add Players**: Complete player profiles with optional photos
- **Update Metrics**: Real-time metric adjustments with automatic fatigue recalculation
- **Photo Management**: Upload, update, or clear player photos
- **Bulk Operations**: Clear all photos or reset entire platform

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Future Enhancements

- **Advanced Analytics**: Trend analysis and predictive modeling
- **Team Comparisons**: Cross-team fatigue analysis
- **Match Integration**: Game-specific fatigue tracking
- **API Integration**: Real-time data feeds from wearable devices
- **Reporting**: PDF report generation for coaching staff
- **Mobile App**: Companion mobile application

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, questions, or feature requests, please open an issue on GitHub.

## Acknowledgments

- Built with [Streamlit](https://streamlit.io/) for the web interface
- Physiological metrics based on sports science research
- Designed for NFL coaching staff and sports scientists