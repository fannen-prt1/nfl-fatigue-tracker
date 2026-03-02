# NFL Player Fatigue Tracking Platform

A full-stack web application for monitoring and analyzing NFL player fatigue levels using physiological metrics and match performance data. Built with a **React** frontend and **FastAPI** backend.

## Features

### Dashboard
- Team-level stat cards (total players, avg fatigue, active count, at-risk players)
- Fatigue trend chart from match overview data
- High fatigue alert panel
- Fatigue & status distribution pie charts
- Team metrics bar chart
- AI-generated team report with risk level and recommendations

### Player Management
- Full roster table with search, filter (status/position), and sort
- Add individual players with complete metrics
- Generate random players (balanced/defensive/offensive/random, quality levels)
- Export roster to CSV
- Inline delete and bulk clear

### Player Detail
- Player profile with photo upload
- Real-time fatigue ring indicator
- Metric cards (BPM, HRV, Speed, Acceleration)
- Fatigue analysis breakdown (high/moderate/good stress factors)
- Personalized recovery & training recommendations
- Match history management (add/edit/delete matches)
- Performance charts: heart rate & HRV, fatigue, speed, acceleration over matches

### Matches & Analysis
- **Match Overview**: aggregate stats, fatigue timeline, all match records table
- **Lineup Optimizer**: fatigue threshold slider, position-grouped lineup (DL, LB, DB, QB, RB, WR, TE, OL), excluded high-fatigue players list
- **Performance Trends**: multi-metric trend chart, performance correlations, AI insights

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19, Vite 7, React Router 7, Recharts, Framer Motion, Lucide Icons |
| Backend | FastAPI, Uvicorn, Python 3.10+ |
| Data | JSON file persistence (`players_data.json`, `matches_history/`) |

## Installation

### Prerequisites
- Python 3.10+
- Node.js 18+
- npm or yarn

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/fannen-prt1/nfl-fatigue-tracker.git
   cd nfl-fatigue-tracker
   ```

2. **Backend setup**
   ```bash
   python -m venv venv
   # Windows PowerShell
   .\venv\Scripts\Activate.ps1
   # macOS/Linux
   source venv/bin/activate

   pip install -r requirements.txt
   ```

3. **Frontend setup**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

## Usage

1. **Start the API server** (from project root, with venv activated)
   ```bash
   python api.py
   ```
   The API runs at `http://localhost:8000`.

2. **Start the React dev server** (in a second terminal)
   ```bash
   cd frontend
   npm run dev
   ```
   The UI runs at `http://localhost:5173`.

3. **Navigate the app**
   - **Dashboard** (`/`) — team overview and analytics
   - **Players** (`/players`) — roster management
   - **Player Detail** (`/players/:id`) — individual player view
   - **Matches** (`/matches`) — match analysis & lineup optimizer

## Project Structure

```
nfl-fatigue-tracker/
├── api.py                  # FastAPI REST backend
├── requirements.txt        # Python dependencies
├── players_data.json       # Player data store (auto-generated)
├── player_photos/          # Uploaded photos (auto-generated)
├── matches_history/        # Per-player match JSON files (auto-generated)
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   └── src/
│       ├── main.jsx
│       ├── index.css
│       ├── App.jsx             # Router & layout
│       ├── components/
│       │   └── Sidebar.jsx
│       ├── context/
│       │   └── AppContext.jsx   # Global state (players CRUD)
│       ├── pages/
│       │   ├── Dashboard.jsx
│       │   ├── PlayerList.jsx
│       │   ├── PlayerDetail.jsx
│       │   └── Matches.jsx
│       └── utils/
│           └── api.js           # API service layer
├── LICENSE
└── README.md
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/players` | List all players |
| POST | `/api/players` | Add a player |
| PUT | `/api/players/{id}` | Update a player |
| DELETE | `/api/players/{id}` | Delete a player |
| DELETE | `/api/players` | Clear all players |
| POST | `/api/players/generate` | Generate random players |
| POST | `/api/players/{id}/photo` | Upload player photo |
| GET | `/api/players/{id}/matches` | Get player matches |
| POST | `/api/players/{id}/matches` | Add a match |
| PUT | `/api/players/{id}/matches/{num}` | Update a match |
| DELETE | `/api/players/{id}/matches/{num}` | Delete a match |
| DELETE | `/api/players/{id}/matches` | Clear player matches |
| GET | `/api/matches` | All match records |
| GET | `/api/matches/overview` | Match overview stats |
| GET | `/api/matches/trends` | Performance trends |
| GET | `/api/lineup/optimize?max_fatigue=80` | Optimize lineup |
| GET | `/api/team/report` | Team report |

## Fatigue Algorithm

```
fatigue = ((BPM - 60) / 40) × 0.3
        + ((1200 - RR_MS) / 400) × 0.3
        + (Speed / 10) × 0.2
        + (Acceleration / 6) × 0.2
```
Result clamped to 0–100. Weights: BPM 30%, HRV 30%, Speed 20%, Acceleration 20%.

## Key Metrics

| Metric | Unit | Normal | Elevated | High |
|--------|------|--------|----------|------|
| Heart Rate | BPM | 60–84 | 85–99 | 100+ |
| HRV (RR_MS) | ms | 900+ | 750–900 | <750 |
| Speed | yd/s | <3.5 | 3.5–6.4 | 6.5+ |
| Acceleration | yd/s² | <2.0 | 2.0–3.9 | 4.0+ |

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes (`git commit -m 'Add my feature'`)
4. Push to the branch (`git push origin feature/my-feature`)
5. Open a Pull Request

## License

MIT License — see [LICENSE](LICENSE) for details.