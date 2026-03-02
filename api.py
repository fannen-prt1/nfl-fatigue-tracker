"""
NFL Player Fatigue Tracking Platform - FastAPI Backend
Exposes all core functionalities as REST endpoints for the React frontend.
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List
import json
import os
import shutil
import random
import numpy as np

app = FastAPI(title="NFL Fatigue Tracker API")

# CORS for React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve player photos as static files
PHOTOS_DIR = "player_photos"
PLAYERS_DATA_FILE = "players_data.json"
MATCHES_DIR = "matches_history"

if os.path.exists(PHOTOS_DIR):
    app.mount("/photos", StaticFiles(directory=PHOTOS_DIR), name="photos")


# ─── Pydantic Models ───────────────────────────────────────────────────────────

class PlayerCreate(BaseModel):
    name: str
    number: int
    position: str
    team: str
    avg_bpm: float = 75.0
    rr_ms: float = 800.0
    avg_speed: float = 5.0
    acceleration: float = 3.5
    status: str = "active"

class PlayerUpdate(BaseModel):
    name: Optional[str] = None
    number: Optional[int] = None
    position: Optional[str] = None
    team: Optional[str] = None
    avg_bpm: Optional[float] = None
    rr_ms: Optional[float] = None
    avg_speed: Optional[float] = None
    acceleration: Optional[float] = None
    status: Optional[str] = None

class MatchCreate(BaseModel):
    avg_bpm: float
    rr_ms: float
    speed: float
    acceleration: float
    date: Optional[str] = None
    opponent: Optional[str] = None
    notes: Optional[str] = None

class MatchUpdate(BaseModel):
    avg_bpm: Optional[float] = None
    rr_ms: Optional[float] = None
    speed: Optional[float] = None
    acceleration: Optional[float] = None
    date: Optional[str] = None
    opponent: Optional[str] = None
    notes: Optional[str] = None

class GeneratePlayersRequest(BaseModel):
    count: int = 5
    team_name: str = "Random Team"
    position_distribution: str = "Balanced NFL Roster"
    quality_level: str = "Average Team"


# ─── Helper Functions ──────────────────────────────────────────────────────────

def load_players_data() -> list:
    try:
        if os.path.exists(PLAYERS_DATA_FILE):
            with open(PLAYERS_DATA_FILE, "r") as f:
                players = json.load(f)
                for p in players:
                    p.setdefault("photo_path", None)
                    p.setdefault("status", "active")
                    if "fatigue_prediction" not in p:
                        p["fatigue_prediction"] = calculate_fatigue_prediction(
                            p["avg_bpm"], p["rr_ms"], p["avg_speed"], p["acceleration"]
                        )
                return players
        return []
    except Exception:
        return []

def save_players_data(players: list):
    with open(PLAYERS_DATA_FILE, "w") as f:
        json.dump(players, f, indent=2)

def calculate_fatigue_prediction(bpm, rr_ms, speed, acceleration):
    bpm_factor = (bpm - 60) / 40
    rr_factor = (1200 - rr_ms) / 400
    speed_factor = speed / 10
    accel_factor = acceleration / 6
    fatigue_score = bpm_factor * 0.3 + rr_factor * 0.3 + speed_factor * 0.2 + accel_factor * 0.2
    return round(max(0, min(100, fatigue_score * 100)), 1)

def calculate_match_fatigue(bpm, rr_ms, speed, acceleration):
    return calculate_fatigue_prediction(bpm, rr_ms, speed, acceleration)

def analyze_fatigue_reasons(bpm, rr_ms, speed, acceleration):
    high, moderate, good = [], [], []

    if bpm >= 110:
        high.append("very high heart rate (>110 BPM)")
    elif bpm >= 95:
        high.append("high heart rate (95-110 BPM)")
    elif bpm >= 85:
        moderate.append("elevated heart rate (85-94 BPM)")
    elif bpm >= 70:
        good.append("normal heart rate (70-84 BPM)")
    else:
        good.append("excellent resting heart rate (<70 BPM)")

    if rr_ms <= 500:
        high.append("critically low HRV (<500ms)")
    elif rr_ms <= 650:
        high.append("very low HRV (500-650ms)")
    elif rr_ms <= 750:
        moderate.append("low HRV (650-750ms)")
    elif rr_ms <= 900:
        moderate.append("below average HRV (750-900ms)")
    elif rr_ms <= 1100:
        good.append("good HRV (900-1100ms)")
    else:
        good.append("excellent HRV (>1100ms)")

    if speed >= 8.0:
        high.append("very high speed (>8.0 yd/s)")
    elif speed >= 6.5:
        high.append("high movement speed (6.5-8.0 yd/s)")
    elif speed >= 5.0:
        moderate.append("moderate speed (5.0-6.4 yd/s)")
    elif speed >= 3.5:
        good.append("controlled speed (3.5-4.9 yd/s)")
    else:
        good.append("low impact speed (<3.5 yd/s)")

    if acceleration >= 5.0:
        high.append("very high acceleration (>5.0 yd/s²)")
    elif acceleration >= 4.0:
        high.append("high acceleration (4.0-5.0 yd/s²)")
    elif acceleration >= 3.0:
        moderate.append("moderate acceleration (3.0-3.9 yd/s²)")
    elif acceleration >= 2.0:
        good.append("controlled acceleration (2.0-2.9 yd/s²)")
    else:
        good.append("low acceleration demands (<2.0 yd/s²)")

    return {"high": high, "moderate": moderate, "good": good}

def generate_player_suggestions(bpm, rr_ms, speed, acceleration, fatigue_level):
    suggestions = []
    if bpm >= 110:
        suggestions += ["Immediate rest required - heart rate critically high",
                        "Increase hydration and electrolyte intake"]
    elif bpm >= 95:
        suggestions += ["Reduce training intensity for next session",
                        "Focus on breathing exercises and relaxation"]
    elif bpm >= 85:
        suggestions += ["Monitor closely - consider lighter workouts"]
    elif bpm <= 70:
        suggestions += ["Excellent cardiovascular fitness - can handle increased load"]

    if rr_ms <= 500:
        suggestions += ["Critical stress levels - mandatory rest day",
                        "Implement meditation or mindfulness practices"]
    elif rr_ms <= 650:
        suggestions += ["High stress detected - reduce training volume",
                        "Schedule recovery activities (massage, stretching)"]
    elif rr_ms <= 750:
        suggestions += ["Balance training with adequate recovery time"]
    elif rr_ms >= 1100:
        suggestions += ["Excellent recovery status - can increase training intensity"]

    if speed >= 8.0:
        suggestions += ["High-speed work detected - monitor for overuse injuries"]
    elif speed >= 6.5:
        suggestions += ["Alternate high-speed days with recovery sessions"]

    if acceleration >= 5.0:
        suggestions += ["Explosive work overload - risk of muscle strain"]
    elif acceleration >= 4.0:
        suggestions += ["High explosive demands - ensure proper warm-up"]

    if fatigue_level > 80:
        suggestions += ["CRITICAL: Complete rest recommended"]
    elif fatigue_level >= 60:
        suggestions += ["HIGH FATIGUE: Light activity only"]
    elif fatigue_level >= 40:
        suggestions += ["MODERATE: 50-70% of normal training intensity"]
    elif fatigue_level <= 30:
        suggestions += ["GOOD CONDITION: Normal training can proceed"]

    return list(dict.fromkeys(suggestions))[:6]

def load_match_data_for_player(player_name: str) -> list:
    safe_name = player_name.replace(" ", "_").replace("/", "_").replace("\\", "_")
    filepath = os.path.join(MATCHES_DIR, f"{safe_name}_matches.json")
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except Exception:
        return []

def save_match_data_for_player(player_name: str, matches: list):
    if not os.path.exists(MATCHES_DIR):
        os.makedirs(MATCHES_DIR)
    # Sort by date then renumber
    def sort_key(m):
        return m.get("date") or "1900-01-01"
    matches.sort(key=sort_key, reverse=True)
    for i, m in enumerate(matches, 1):
        m["match_number"] = i
        m["match"] = f"Match {i}"
    safe_name = player_name.replace(" ", "_").replace("/", "_").replace("\\", "_")
    filepath = os.path.join(MATCHES_DIR, f"{safe_name}_matches.json")
    with open(filepath, "w") as f:
        json.dump(matches, f, indent=2)

def load_all_match_data() -> list:
    all_matches = []
    if not os.path.exists(MATCHES_DIR):
        return []
    for filename in os.listdir(MATCHES_DIR):
        if filename.endswith("_matches.json"):
            player_name = filename.replace("_matches.json", "").replace("_", " ")
            filepath = os.path.join(MATCHES_DIR, filename)
            try:
                with open(filepath, "r") as f:
                    player_matches = json.load(f)
                    for m in player_matches:
                        m["player_name"] = player_name
                        all_matches.append(m)
            except Exception:
                pass
    return all_matches

def create_random_players(num, team_name, position_dist, quality_level):
    if position_dist == "Balanced NFL Roster":
        positions = (["QB"]*2 + ["RB"]*3 + ["WR"]*5 + ["TE"]*2 + ["OL"]*8 +
                     ["DL"]*6 + ["LB"]*6 + ["CB"]*4 + ["S"]*3 + ["K", "P"])
    elif position_dist == "Defensive Focus":
        positions = ["DL"]*8 + ["LB"]*8 + ["CB"]*6 + ["S"]*4 + ["QB", "RB", "WR"]
    elif position_dist == "Offensive Focus":
        positions = ["QB"]*3 + ["RB"]*5 + ["WR"]*8 + ["TE"]*3 + ["OL"]*6
    else:
        all_pos = ["QB","RB","WR","TE","OL","DL","LB","CB","S","K","P"]
        positions = [random.choice(all_pos) for _ in range(num)]

    first_names = ["Aaron","Adrian","Antonio","Brandon","Calvin","Dak","Deion","Derek",
                   "Deshaun","Ezekiel","Frank","George","Jarvis","Josh","Julian","Julio",
                   "Lamar","Mac","Michael","Mike","Nick","Odell","Patrick","Rob","Russell",
                   "Stefon","Tom","Travis","Tyreek","Von","Zach","DeAndre","Khalil","Alvin",
                   "Chris","Cooper","Davante","DeVonta","Jalen","Justin","Kyler","Najee","Saquon","Tua"]
    last_names = ["Adams","Allen","Brady","Brown","Cook","Cooper","Davis","Evans","Green",
                  "Hill","Hopkins","Jackson","Johnson","Jones","Kelce","Lewis","Mack","Miller",
                  "Murray","Newton","Robinson","Rogers","Smith","Taylor","Thomas","Watson",
                  "White","Williams","Wilson","Young","Beckham","Bell","Bosa","Donald","Elliott",
                  "Garrett","Gronkowski","Henry","Kamara","Mahomes","McCaffrey","Ramsey","Watt"]

    ranges = {
        "Elite Team":    ((65,85),(700,900),(6.0,9.0),(4.0,6.5)),
        "Good Team":     ((70,90),(650,950),(5.0,7.5),(3.5,5.5)),
        "Average Team":  ((75,95),(600,1000),(4.0,6.5),(3.0,5.0)),
        "Mixed Quality": ((65,100),(550,1100),(3.5,8.0),(2.5,6.0)),
    }.get(quality_level, ((60,110),(500,1200),(2.0,10.0),(2.0,7.0)))

    bpm_r, rr_r, spd_r, acc_r = ranges
    players = []
    used_numbers = set()

    for i in range(min(num, len(positions))):
        jersey = random.randint(1, 99)
        while jersey in used_numbers:
            jersey = random.randint(1, 99)
        used_numbers.add(jersey)

        pos = positions[i]
        spd_mult = 1.2 if pos in ["RB","WR","CB"] else 0.8 if pos in ["OL","DL"] else 0.9 if pos == "QB" else 1.0
        bpm_adj = -5 if pos in ["RB","WR","CB"] else 5 if pos in ["OL","DL"] else -2 if pos == "QB" else 0

        bpm = max(50, min(120, random.uniform(*bpm_r) + bpm_adj))
        rr = random.uniform(*rr_r)
        spd = max(1.0, min(12.0, random.uniform(*spd_r) * spd_mult))
        acc = max(1.0, min(8.0, random.uniform(*acc_r) * spd_mult))

        player = {
            "name": f"{random.choice(first_names)} {random.choice(last_names)}",
            "number": jersey,
            "position": pos,
            "team": team_name,
            "avg_bpm": round(bpm, 1),
            "rr_ms": round(rr, 1),
            "avg_speed": round(spd, 2),
            "acceleration": round(acc, 2),
            "status": random.choice(["active"]*8 + ["benched"] + ["practice squad"]),
            "photo_path": None,
            "fatigue_prediction": 0,
        }
        player["fatigue_prediction"] = calculate_fatigue_prediction(
            player["avg_bpm"], player["rr_ms"], player["avg_speed"], player["acceleration"]
        )
        players.append(player)
    return players


# ─── API Endpoints ─────────────────────────────────────────────────────────────

# ---- Players ----

@app.get("/api/players")
def get_players():
    players = load_players_data()
    # Enrich with analysis
    enriched = []
    for i, p in enumerate(players):
        ep = {**p, "id": i}
        ep["fatigue_analysis"] = analyze_fatigue_reasons(
            p["avg_bpm"], p["rr_ms"], p["avg_speed"], p["acceleration"]
        )
        ep["suggestions"] = generate_player_suggestions(
            p["avg_bpm"], p["rr_ms"], p["avg_speed"], p["acceleration"],
            p["fatigue_prediction"]
        )
        # Convert photo_path to URL
        if p.get("photo_path") and os.path.exists(p["photo_path"]):
            ep["photo_url"] = f"/photos/{os.path.basename(p['photo_path'])}"
        else:
            ep["photo_url"] = None
        enriched.append(ep)
    return enriched

@app.post("/api/players")
def add_player(player: PlayerCreate):
    players = load_players_data()
    existing_numbers = [p["number"] for p in players]
    if player.number in existing_numbers:
        raise HTTPException(status_code=400, detail=f"Jersey number {player.number} is already taken")

    new_player = player.model_dump()
    new_player["photo_path"] = None
    new_player["fatigue_prediction"] = calculate_fatigue_prediction(
        player.avg_bpm, player.rr_ms, player.avg_speed, player.acceleration
    )
    players.append(new_player)
    save_players_data(players)
    return {"message": f"Player {player.name} added successfully", "player": new_player}

@app.put("/api/players/{player_id}")
def update_player(player_id: int, update: PlayerUpdate):
    players = load_players_data()
    if player_id < 0 or player_id >= len(players):
        raise HTTPException(status_code=404, detail="Player not found")

    p = players[player_id]
    update_data = update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        p[key] = value

    p["fatigue_prediction"] = calculate_fatigue_prediction(
        p["avg_bpm"], p["rr_ms"], p["avg_speed"], p["acceleration"]
    )
    players[player_id] = p
    save_players_data(players)
    return {"message": "Player updated", "player": p}

@app.delete("/api/players/{player_id}")
def delete_player(player_id: int):
    players = load_players_data()
    if player_id < 0 or player_id >= len(players):
        raise HTTPException(status_code=404, detail="Player not found")

    player = players[player_id]
    # Remove photo
    if player.get("photo_path") and os.path.exists(player["photo_path"]):
        try:
            os.remove(player["photo_path"])
        except:
            pass
    # Remove matches file
    safe_name = player["name"].replace(" ", "_").replace("/", "_").replace("\\", "_")
    matches_file = os.path.join(MATCHES_DIR, f"{safe_name}_matches.json")
    if os.path.exists(matches_file):
        try:
            os.remove(matches_file)
        except:
            pass

    players.pop(player_id)
    save_players_data(players)
    return {"message": f"Player {player['name']} removed"}

@app.delete("/api/players")
def clear_all_players():
    # Clear photos
    if os.path.exists(PHOTOS_DIR):
        shutil.rmtree(PHOTOS_DIR, ignore_errors=True)
    # Clear matches
    if os.path.exists(MATCHES_DIR):
        shutil.rmtree(MATCHES_DIR, ignore_errors=True)
    save_players_data([])
    return {"message": "All players cleared"}

@app.post("/api/players/generate")
def generate_players(req: GeneratePlayersRequest):
    players = load_players_data()
    existing_numbers = [p["number"] for p in players]
    new_players = create_random_players(req.count, req.team_name, req.position_distribution, req.quality_level)

    added = 0
    for p in new_players:
        attempts = 0
        while p["number"] in existing_numbers and attempts < 99:
            p["number"] = random.randint(1, 99)
            attempts += 1
        if p["number"] not in existing_numbers:
            players.append(p)
            existing_numbers.append(p["number"])
            added += 1

    save_players_data(players)
    return {"message": f"Generated {added} players", "added": added}

@app.post("/api/players/{player_id}/photo")
async def upload_photo(player_id: int, file: UploadFile = File(...)):
    players = load_players_data()
    if player_id < 0 or player_id >= len(players):
        raise HTTPException(status_code=404, detail="Player not found")

    if not os.path.exists(PHOTOS_DIR):
        os.makedirs(PHOTOS_DIR)

    photo_path = os.path.join(PHOTOS_DIR, f"player_{player_id}_{file.filename}")
    with open(photo_path, "wb") as f:
        content = await file.read()
        f.write(content)

    players[player_id]["photo_path"] = photo_path
    save_players_data(players)
    return {"message": "Photo uploaded", "photo_url": f"/photos/{os.path.basename(photo_path)}"}

@app.delete("/api/photos")
def clear_all_photos():
    players = load_players_data()
    for p in players:
        if p.get("photo_path") and os.path.exists(p["photo_path"]):
            try:
                os.remove(p["photo_path"])
            except:
                pass
        p["photo_path"] = None
    save_players_data(players)
    return {"message": "All photos cleared"}


# ---- Matches ----

@app.get("/api/players/{player_id}/matches")
def get_player_matches(player_id: int):
    players = load_players_data()
    if player_id < 0 or player_id >= len(players):
        raise HTTPException(status_code=404, detail="Player not found")
    return load_match_data_for_player(players[player_id]["name"])

@app.post("/api/players/{player_id}/matches")
def add_match(player_id: int, match: MatchCreate):
    players = load_players_data()
    if player_id < 0 or player_id >= len(players):
        raise HTTPException(status_code=404, detail="Player not found")

    matches = load_match_data_for_player(players[player_id]["name"])
    fatigue = calculate_match_fatigue(match.avg_bpm, match.rr_ms, match.speed, match.acceleration)
    new_match = {
        "match": f"Match {len(matches) + 1}",
        "match_number": len(matches) + 1,
        "avg_bpm": round(match.avg_bpm, 1),
        "rr_ms": round(match.rr_ms, 1),
        "speed": round(match.speed, 1),
        "acceleration": round(match.acceleration, 1),
        "fatigue": round(fatigue, 1),
        "date": match.date,
        "opponent": match.opponent,
        "notes": match.notes,
    }
    matches.append(new_match)
    save_match_data_for_player(players[player_id]["name"], matches)
    return {"message": "Match added", "match": new_match}

@app.put("/api/players/{player_id}/matches/{match_num}")
def update_match(player_id: int, match_num: int, update: MatchUpdate):
    players = load_players_data()
    if player_id < 0 or player_id >= len(players):
        raise HTTPException(status_code=404, detail="Player not found")

    matches = load_match_data_for_player(players[player_id]["name"])
    target = next((m for m in matches if m["match_number"] == match_num), None)
    if not target:
        raise HTTPException(status_code=404, detail="Match not found")

    update_data = update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        target[key] = value

    target["fatigue"] = round(calculate_match_fatigue(
        target["avg_bpm"], target["rr_ms"], target["speed"], target["acceleration"]
    ), 1)

    save_match_data_for_player(players[player_id]["name"], matches)
    return {"message": "Match updated", "match": target}

@app.delete("/api/players/{player_id}/matches/{match_num}")
def delete_match(player_id: int, match_num: int):
    players = load_players_data()
    if player_id < 0 or player_id >= len(players):
        raise HTTPException(status_code=404, detail="Player not found")

    matches = load_match_data_for_player(players[player_id]["name"])
    matches = [m for m in matches if m["match_number"] != match_num]
    save_match_data_for_player(players[player_id]["name"], matches)
    return {"message": "Match deleted"}

@app.delete("/api/players/{player_id}/matches")
def clear_player_matches(player_id: int):
    players = load_players_data()
    if player_id < 0 or player_id >= len(players):
        raise HTTPException(status_code=404, detail="Player not found")
    save_match_data_for_player(players[player_id]["name"], [])
    return {"message": "All matches cleared"}


# ---- Global Match Analytics ----

@app.get("/api/matches")
def get_all_matches():
    return load_all_match_data()

@app.get("/api/matches/overview")
def get_match_overview():
    all_matches = load_all_match_data()
    players = load_players_data()

    if not all_matches:
        return {
            "total_matches": 0, "avg_fatigue": 0, "high_fatigue_matches": 0,
            "active_players": len([p for p in players if p.get("status") == "active"]),
            "timeline": [], "matches_by_game": []
        }

    games = {}
    for m in all_matches:
        key = f"{m.get('date', 'Unknown')} vs {m.get('opponent', 'Unknown')}"
        games.setdefault(key, []).append(m)

    timeline = []
    for key, gm in games.items():
        timeline.append({
            "game": key,
            "date": gm[0].get("date", "Unknown"),
            "avg_fatigue": round(float(np.mean([m["fatigue"] for m in gm])), 1),
            "avg_bpm": round(float(np.mean([m["avg_bpm"] for m in gm])), 1),
            "player_count": len(gm),
        })
    timeline.sort(key=lambda x: x["date"], reverse=True)

    return {
        "total_matches": len(set([(m.get("date"), m.get("opponent", "Unknown")) for m in all_matches])),
        "avg_fatigue": round(float(np.mean([m["fatigue"] for m in all_matches])), 1),
        "high_fatigue_matches": len([m for m in all_matches if m["fatigue"] > 80]),
        "active_players": len([p for p in players if p.get("status") == "active"]),
        "timeline": timeline[:10],
    }


@app.get("/api/lineup/optimize")
def optimize_lineup(max_fatigue: int = 80):
    players = load_players_data()
    available = [p for p in players if p["fatigue_prediction"] <= max_fatigue and p.get("status") == "active"]

    by_pos = {}
    for p in available:
        by_pos.setdefault(p["position"], []).append(p)
    for pos in by_pos:
        by_pos[pos].sort(key=lambda x: x["fatigue_prediction"])

    dl = by_pos.get("DL", []) + by_pos.get("DE", []) + by_pos.get("DT", [])
    lb = by_pos.get("LB", []) + by_pos.get("MLB", []) + by_pos.get("OLB", [])
    db = by_pos.get("CB", []) + by_pos.get("S", []) + by_pos.get("FS", []) + by_pos.get("SS", [])

    # Offense
    qb = by_pos.get("QB", [])
    rb = by_pos.get("RB", [])
    wr = by_pos.get("WR", [])
    te = by_pos.get("TE", [])
    ol = by_pos.get("OL", [])

    # Build groups dict matching frontend keys
    groups = {
        "Defensive Line": dl[:4],
        "Linebackers": lb[:4],
        "Defensive Backs": db[:4],
        "Quarterbacks": qb[:2],
        "Running Backs": rb[:3],
        "Wide Receivers": wr[:5],
        "Tight Ends": te[:2],
        "Offensive Line": ol[:5],
    }

    all_lineup = []
    for lst in groups.values():
        all_lineup.extend(lst)

    high_fatigue = [p for p in players if p["fatigue_prediction"] > max_fatigue]

    stats = {}
    if all_lineup:
        stats = {
            "avg_fatigue": round(float(np.mean([p["fatigue_prediction"] for p in all_lineup])), 1),
            "avg_bpm": round(float(np.mean([p["avg_bpm"] for p in all_lineup])), 1),
            "avg_speed": round(float(np.mean([p["avg_speed"] for p in all_lineup])), 2),
            "total_players": len(all_lineup),
        }

    def serialize(lst):
        return [{"name": p["name"], "number": p["number"], "position": p["position"],
                 "fatigue": p["fatigue_prediction"], "avg_bpm": p["avg_bpm"],
                 "avg_speed": p["avg_speed"]} for p in lst]

    serialized_groups = {name: serialize(plist) for name, plist in groups.items()}

    return {
        "groups": serialized_groups,
        "excluded": serialize(high_fatigue),
        "stats": stats,
        "available_count": len(available),
        "total_count": len(players),
    }


@app.get("/api/matches/trends")
def get_performance_trends():
    all_matches = load_all_match_data()
    if not all_matches:
        return {"trends": [], "insights": {}}

    by_date = {}
    for m in all_matches:
        d = m.get("date", "Unknown")
        by_date.setdefault(d, []).append(m)

    trends = []
    for date, matches in by_date.items():
        trends.append({
            "date": date,
            "avg_fatigue": round(float(np.mean([m["fatigue"] for m in matches])), 1),
            "avg_bpm": round(float(np.mean([m["avg_bpm"] for m in matches])), 1),
            "avg_speed": round(float(np.mean([m.get("speed", 0) for m in matches])), 1),
            "avg_acceleration": round(float(np.mean([m.get("acceleration", 0) for m in matches])), 1),
            "player_count": len(matches),
        })
    trends.sort(key=lambda x: x["date"])

    insights = {}
    if len(trends) >= 2:
        latest = trends[-1]["avg_fatigue"]
        prev = trends[-2]["avg_fatigue"]
        change = latest - prev
        insights = {
            "fatigue_change": round(change, 1),
            "latest_fatigue": latest,
            "trend": "increasing" if change > 5 else "decreasing" if change < -5 else "stable",
            "recent_avg": round(float(np.mean([t["avg_fatigue"] for t in trends[-3:]])), 1),
            "condition": "excellent" if latest < 60 else "acceptable" if latest <= 80 else "concerning",
        }

    return {"trends": trends, "insights": insights}


@app.get("/api/team/report")
def get_team_report():
    players = load_players_data()
    if not players:
        return {"total": 0, "avg_fatigue": 0, "high_risk": [], "risk_level": "LOW", "recommendations": []}

    avg_fatigue = round(float(np.mean([p["fatigue_prediction"] for p in players])), 1)
    high_risk = [{"name": p["name"], "number": p["number"], "fatigue": p["fatigue_prediction"]}
                 for p in players if p["fatigue_prediction"] > 70]

    if avg_fatigue > 60:
        risk = "HIGH"
        recs = ["Reduce training intensity for the entire team",
                "Implement mandatory rest periods for high-fatigue players",
                "Schedule additional recovery sessions"]
    elif avg_fatigue > 40:
        risk = "MODERATE"
        recs = ["Monitor high-fatigue players closely",
                "Consider load management strategies",
                "Maintain current recovery protocols"]
    else:
        risk = "LOW"
        recs = ["Team is in good condition",
                "Can handle increased training load if needed",
                "Continue current monitoring practices"]

    return {
        "total": len(players),
        "avg_fatigue": avg_fatigue,
        "high_risk": high_risk,
        "risk_level": risk,
        "recommendations": recs,
        "active": len([p for p in players if p.get("status") == "active"]),
        "injured": len([p for p in players if p.get("status") == "injured"]),
        "benched": len([p for p in players if p.get("status") == "benched"]),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
