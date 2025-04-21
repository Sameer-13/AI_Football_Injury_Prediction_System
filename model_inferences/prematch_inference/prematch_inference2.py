# -*- coding: utf-8 -*-
"""
End‑to‑end inference script for Saudi‑league injury‑risk prediction
=================================================================

Public function
---------------
    predict_match_risk(home_team_name: str,
                       away_team_name: str,
                       save: bool = True) -> pandas.DataFrame

Returned columns
----------------
player_name, age, height_cm, weight_kg, last_rating,
inj_probability, ci_lower_95, ci_upper_95

Prerequisites
-------------
* A directory ``catboost_models/`` containing the bootstrap models **and**
  a ``metadata.json`` file created by ``train_and_save_catboost_bootstrap_models``.
* A CSV ``teams_2024.csv`` with at least two columns: ``team_name`` and ``team_id``.
* Environment variable ``FOOTBALL_API_KEY`` (or hard‑code ``API_KEY`` below).
"""

# pylint: disable=too-many-lines, too-many-locals, too-many-statements
from __future__ import annotations

import json
import math
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List
from dotenv import load_dotenv

import numpy as np
import pandas as pd
import requests
from catboost import CatBoostClassifier
from tqdm import tqdm
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)
load_dotenv()


# ════════════════════════════════════════════════════════════
# ---------------------------- CONFIG ------------------------
# ════════════════════════════════════════════════════════════
API_KEY = os.getenv("FOOTBALL_API_KEY")
BASE_URL = "https://v3.football.api-sports.io"
SEASON = 2024
PREV_SEASON = SEASON - 1
NUM_FIXTURES = 5
TIMEOUT = 10
MAX_RETRY = 6

BOOT_DIR = Path("catboost_models")               # where models live
REF_TEAMS_CSV = Path("teams_2024.csv")           # Saudi‑league only
POS_ENC_FILE = Path("prev_games_position_encoder.json")

CI_LOW, CI_HIGH = 2.5, 97.5                      # bootstrap CI

# ════════════════════════════════════════════════════════════
# ---------------------- API WRAPPER -------------------------
# ════════════════════════════════════════════════════════════
_session = requests.Session()
_session.headers.update({
    "x-rapidapi-host": "v3.football.api-sports.io",
    "x-rapidapi-key": API_KEY,
})
_CACHE: Dict[str, dict] = {}


def _call_api(endpoint: str, params: dict | None = None) -> dict:
    """Cached GET with exponential‑backoff retry and 429 handling."""
    if params is None:
        params = {}
    key = endpoint + "?" + "&".join(f"{k}={v}" for k, v in sorted(params.items()))
    if key in _CACHE:
        return _CACHE[key]

    for retry in range(MAX_RETRY):
        try:
            rsp = _session.get(f"{BASE_URL}{endpoint}", params=params, timeout=TIMEOUT)
            if rsp.status_code == 429:  # rate‑limit: wait and retry
                time.sleep(1 + 2 ** retry)
                continue
            rsp.raise_for_status()
            js = rsp.json()
            _CACHE[key] = js
            return js
        except Exception as exc:  # pylint: disable=broad-except
            if retry == MAX_RETRY - 1:
                raise RuntimeError(f"API call failed {endpoint} {params}: {exc}") from exc
            time.sleep(2 ** retry)
    return {}


# ════════════════════════════════════════════════════════════
# -------------------- HELPER CONVERSIONS --------------------
# ════════════════════════════════════════════════════════════

def _safe_float(x):
    try:
        return float(x)
    except Exception:  # pylint: disable=broad-except
        return math.nan


def _metric_to_number(text: str | float | None):
    if text is None or isinstance(text, float):
        return math.nan
    digits = "".join(ch for ch in str(text) if ch.isdigit())
    return float(digits) if digits else math.nan


# ════════════════════════════════════════════════════════════
# ------------------- STATIC REFERENCE DATA ------------------
# ════════════════════════════════════════════════════════════
team_ref = pd.read_csv(REF_TEAMS_CSV)
TEAM_NAME2ID = dict(zip(team_ref.team_name, team_ref.team_id))

# Position label‑encoder mapping (fitted during training)
if POS_ENC_FILE.exists():
    with open(POS_ENC_FILE, "r", encoding="utf-8") as fh:
        POS2ID = json.load(fh)
else:
    # Fallback: mimic scikit‑learn's LabelEncoder (alphabetical order)
    default_pos = ["Attacker", "Defender", "Goalkeeper", "Midfielder", "None"]
    POS2ID = {p: i for i, p in enumerate(default_pos)}

# ════════════════════════════════════════════════════════════
# -------------------- FEATURE ENGINEERING -------------------
# ════════════════════════════════════════════════════════════

def flatten_player_stats(player_response: dict) -> List[dict]:
    """Return a *list* of dicts (one per team/league block)."""
    out: List[dict] = []
    player = player_response.get("player", {})
    base = {
        "player_id": player.get("id"),
        "player_name": player.get("name"),
        "player_age": player.get("age"),
        # sanitize metrics so they are *numeric* like during training
        "player_height": _metric_to_number(player.get("height")),
        "player_weight": _metric_to_number(player.get("weight")),
    }
    for stat in player_response.get("statistics", []):
        row = base.copy()
        games = stat.get("games", {})
        row.update({
            "games_minutes": _safe_float(games.get("minutes")),
            "games_rating": _safe_float(games.get("rating")),
            "games_position": games.get("position"),
        })
        out.append(row)
    return out or [base]


def aggregate_player_stats(stats_list):
    """
    Comprehensive player stats aggregation - matches training pipeline
    """
    minutes_list, rating_list = [], []

    shots_total_list, shots_on_list = [], []
    goals_total_list, assists_list = [], []
    fouls_committed_list, fouls_drawn_list = [], []
    yellow_cards_list, red_cards_list = [], []
    duels_total_list, duels_won_list = [], []
    
    passes_total_list, passes_key_list, passes_accuracy_list = [], [], []
    tackles_total_list, tackles_blocks_list, tackles_interceptions_list = [], [], []
    
    for st in stats_list:
        if not st:
            # No stats => fill with NaN placeholders
            minutes_list.append(np.nan)
            rating_list.append(np.nan)

            shots_total_list.append(np.nan)
            shots_on_list.append(np.nan)
            goals_total_list.append(np.nan)
            assists_list.append(np.nan)

            fouls_committed_list.append(np.nan)
            fouls_drawn_list.append(np.nan)
            yellow_cards_list.append(np.nan)
            red_cards_list.append(np.nan)

            duels_total_list.append(np.nan)
            duels_won_list.append(np.nan)

            passes_total_list.append(np.nan)
            passes_key_list.append(np.nan)
            passes_accuracy_list.append(np.nan)

            tackles_total_list.append(np.nan)
            tackles_blocks_list.append(np.nan)
            tackles_interceptions_list.append(np.nan)
        else:
            g = st.get("games", {})
            minutes_list.append(_safe_float(g.get("minutes", np.nan)))
            rating_list.append(_safe_float(g.get("rating", np.nan)))

            s = st.get("shots", {})
            shots_total_list.append(_safe_float(s.get("total", np.nan)))
            shots_on_list.append(_safe_float(s.get("on", np.nan)))

            gl = st.get("goals", {})
            goals_total_list.append(_safe_float(gl.get("total", np.nan)))
            assists_list.append(_safe_float(gl.get("assists", np.nan)))

            f = st.get("fouls", {})
            fouls_committed_list.append(_safe_float(f.get("committed", np.nan)))
            fouls_drawn_list.append(_safe_float(f.get("drawn", np.nan)))

            c = st.get("cards", {})
            yellow_cards_list.append(_safe_float(c.get("yellow", np.nan)))
            red_cards_list.append(_safe_float(c.get("red", np.nan)))

            d = st.get("duels", {})
            duels_total_list.append(_safe_float(d.get("total", np.nan)))
            duels_won_list.append(_safe_float(d.get("won", np.nan)))

            p = st.get("passes", {})
            passes_total_list.append(_safe_float(p.get("total", np.nan)))
            passes_key_list.append(_safe_float(p.get("key", np.nan)))
            passes_accuracy_list.append(_safe_float(p.get("accuracy", np.nan)))

            t = st.get("tackles", {})
            tackles_total_list.append(_safe_float(t.get("total", np.nan)))
            tackles_blocks_list.append(_safe_float(t.get("blocks", np.nan)))
            tackles_interceptions_list.append(_safe_float(t.get("interceptions", np.nan)))

    # Summations
    shots_total_5 = np.nansum(shots_total_list)
    duels_total_5 = np.nansum(duels_total_list)

    # Ratio example: duels won
    duels_win_ratio_5 = np.nan
    if duels_total_5 > 0:
        duels_win_ratio_5 = np.nansum(duels_won_list) / duels_total_5

    # Pass accuracy example
    pass_acc_mean = np.nanmean(passes_accuracy_list)  # average across matches

    features = {
        # Averages
        "player_minutes_avg_5":           np.nanmean(minutes_list),
        "player_rating_avg_5":            np.nanmean(rating_list),

        # Sums
        "player_shots_total_5":           shots_total_5,
        "player_shots_on_5":              np.nansum(shots_on_list),
        "player_goals_5":                 np.nansum(goals_total_list),
        "player_assists_5":               np.nansum(assists_list),
        "player_fouls_committed_5":       np.nansum(fouls_committed_list),
        "player_fouls_drawn_5":           np.nansum(fouls_drawn_list),
        "player_yellow_cards_5":          np.nansum(yellow_cards_list),
        "player_red_cards_5":             np.nansum(red_cards_list),
        "player_duels_total_5":           duels_total_5,
        "player_duels_won_5":             np.nansum(duels_won_list),
        "player_passes_total_5":          np.nansum(passes_total_list),
        "player_passes_key_5":            np.nansum(passes_key_list),
        "player_tackles_total_5":         np.nansum(tackles_total_list),
        "player_tackles_blocks_5":        np.nansum(tackles_blocks_list),
        "player_tackles_interceptions_5": np.nansum(tackles_interceptions_list),

        # Ratios
        "player_duels_win_ratio_5":       duels_win_ratio_5,
        "player_pass_acc_mean_5":         pass_acc_mean,
    }

    return features


def aggregate_team_stats(stats_list):
    """Team stats aggregation matching training pipeline"""
    sog_list, sof_list, total_shots_list = [], [], []
    fouls_list, corners_list, offsides_list = [], [], []
    ball_poss_list = []
    yellow_cards_list, red_cards_list = [], []
    passes_list, passes_accurate_list = [], []

    for st in stats_list:
        if not st:
            sog_list.append(np.nan)
            sof_list.append(np.nan)
            total_shots_list.append(np.nan)
            fouls_list.append(np.nan)
            corners_list.append(np.nan)
            offsides_list.append(np.nan)
            ball_poss_list.append(np.nan)
            yellow_cards_list.append(np.nan)
            red_cards_list.append(np.nan)
            passes_list.append(np.nan)
            passes_accurate_list.append(np.nan)
        else:
            sog_list.append(_safe_float(st.get("shots_on_goal", np.nan)))
            sof_list.append(_safe_float(st.get("shots_off_goal", np.nan)))
            total_shots_list.append(_safe_float(st.get("total_shots", np.nan)))
            fouls_list.append(_safe_float(st.get("fouls", np.nan)))
            corners_list.append(_safe_float(st.get("corner_kicks", np.nan)))
            offsides_list.append(_safe_float(st.get("offsides", np.nan)))

            poss_str = st.get("ball_possession", None)
            if poss_str and isinstance(poss_str, str) and poss_str.endswith("%"):
                val = poss_str.replace("%", "")
                ball_poss_list.append(_safe_float(val))
            else:
                ball_poss_list.append(np.nan)

            yellow_cards_list.append(_safe_float(st.get("yellow_cards", np.nan)))
            red_cards_list.append(_safe_float(st.get("red_cards", np.nan)))

            passes_list.append(_safe_float(st.get("total_passes", np.nan)))
            passes_accurate_list.append(_safe_float(st.get("passes_accurate", np.nan)))

    sog_sum = np.nansum(sog_list)
    passes_sum = np.nansum(passes_list)
    passes_acc_sum = np.nansum(passes_accurate_list)

    pass_accuracy_5 = np.nan
    if passes_sum > 0:
        pass_accuracy_5 = passes_acc_sum / passes_sum

    features = {
        "team_shots_on_goal_5":    sog_sum,
        "team_shots_off_goal_5":   np.nansum(sof_list),
        "team_total_shots_5":      np.nansum(total_shots_list),
        "team_fouls_5":            np.nansum(fouls_list),
        "team_corners_5":          np.nansum(corners_list),
        "team_offsides_5":         np.nansum(offsides_list),
        "team_ball_poss_avg_5":    np.nanmean(ball_poss_list),
        "team_yellow_cards_5":     np.nansum(yellow_cards_list),
        "team_red_cards_5":        np.nansum(red_cards_list),
        "team_passes_5":           passes_sum,
        "team_passes_acc_5":       passes_acc_sum,
        "team_pass_acc_ratio_5":   pass_accuracy_5,
    }
    return features


def aggregate_opponent_stats(stats_list):
    """Opponent stats aggregation matching training pipeline"""
    sog_list, sof_list, total_shots_list = [], [], []
    fouls_list, corners_list, offsides_list = [], [], []
    ball_poss_list = []
    yellow_cards_list, red_cards_list = [], []
    passes_list, passes_accurate_list = [], []

    for st in stats_list:
        if not st:
            sog_list.append(np.nan)
            sof_list.append(np.nan)
            total_shots_list.append(np.nan)
            fouls_list.append(np.nan)
            corners_list.append(np.nan)
            offsides_list.append(np.nan)
            ball_poss_list.append(np.nan)
            yellow_cards_list.append(np.nan)
            red_cards_list.append(np.nan)
            passes_list.append(np.nan)
            passes_accurate_list.append(np.nan)
        else:
            sog_list.append(_safe_float(st.get("shots_on_goal", np.nan)))
            sof_list.append(_safe_float(st.get("shots_off_goal", np.nan)))
            total_shots_list.append(_safe_float(st.get("total_shots", np.nan)))
            fouls_list.append(_safe_float(st.get("fouls", np.nan)))
            corners_list.append(_safe_float(st.get("corner_kicks", np.nan)))
            offsides_list.append(_safe_float(st.get("offsides", np.nan)))

            poss_str = st.get("ball_possession", None)
            if poss_str and isinstance(poss_str, str) and poss_str.endswith("%"):
                val = poss_str.replace("%", "")
                ball_poss_list.append(_safe_float(val))
            else:
                ball_poss_list.append(np.nan)

            yellow_cards_list.append(_safe_float(st.get("yellow_cards", np.nan)))
            red_cards_list.append(_safe_float(st.get("red_cards", np.nan)))

            passes_list.append(_safe_float(st.get("total_passes", np.nan)))
            passes_accurate_list.append(_safe_float(st.get("passes_accurate", np.nan)))

    sog_sum = np.nansum(sog_list)
    passes_sum = np.nansum(passes_list)
    passes_acc_sum = np.nansum(passes_accurate_list)

    pass_accuracy_5 = np.nan
    if passes_sum > 0:
        pass_accuracy_5 = passes_acc_sum / passes_sum

    features = {
        "opp_shots_on_goal_5":   sog_sum,
        "opp_shots_off_goal_5":  np.nansum(sof_list),
        "opp_total_shots_5":     np.nansum(total_shots_list),
        "opp_fouls_5":           np.nansum(fouls_list),
        "opp_corners_5":         np.nansum(corners_list),
        "opp_offsides_5":        np.nansum(offsides_list),
        "opp_ball_poss_avg_5":   np.nanmean(ball_poss_list),
        "opp_yellow_cards_5":    np.nansum(yellow_cards_list),
        "opp_red_cards_5":       np.nansum(red_cards_list),
        "opp_passes_5":          passes_sum,
        "opp_passes_acc_5":      passes_acc_sum,
        "opp_pass_acc_ratio_5":  pass_accuracy_5,
    }
    return features


def add_temporal_injury_features(df_main: pd.DataFrame, df_injuries: pd.DataFrame) -> pd.DataFrame:
    """
    Updated to match training pipeline's temporal injury features
    """
    df = df_main.copy()
    df["date"] = pd.to_datetime(df["today"])
    
    # Add prev_fixtures_count with default value 5 (or whatever is appropriate)
    # This is needed for the rate calculations
    df["prev_fixtures_count"] = NUM_FIXTURES  # Using the global constant
    
    if df_injuries.empty:
        # Initialize all injury-related columns
        injury_cols = [
            "inj_count_season", "inj_count_total", "inj_count_last_1m", 
            "inj_count_last_3m", "inj_count_last_6m", "inj_count_last_12m",
            "inj_frac_last_6m", "days_since_last_injury", "days_since_first_injury",
            "inj_seq_overall", "inj_seq_season", "avg_days_between_prev",
            "std_days_between_prev", "inj_count_prev_season", "inj_rate_per_year",
            "inj_rate_per_fixture_total", "inj_rate_per_fixture_6m",
            "inj_on_weekend", "injury_month", "injury_dow", "inj_doy",
            "inj_weekofyear", "inj_quarter"
        ]
        for col in injury_cols:
            df[col] = 0 if "count" in col or "seq" in col else np.nan
        return df

    # Process injury dataframe
    df_inj = df_injuries.copy()
    df_inj["date"] = pd.to_datetime(df_inj["date"]).dt.tz_localize(None)
    df_inj["injury_season"] = df_inj["season"]  # Match the expected column name
    
    agg_list = []
    for _, row in df.iterrows():
        pid, today = row["player_id"], row["date"]
        hist = df_inj[df_inj["player_id"] == pid].copy()
        
        features = {
            "player_id": pid,
            "inj_count_season": 0,
            "inj_count_total": 0,
            "inj_count_last_1m": 0,
            "inj_count_last_3m": 0,
            "inj_count_last_6m": 0,
            "inj_count_last_12m": 0,
            "inj_frac_last_6m": 0,
            "days_since_last_injury": np.nan,
            "days_since_first_injury": np.nan,
            "inj_seq_overall": 0,
            "inj_seq_season": 0,
            "avg_days_between_prev": np.nan,
            "std_days_between_prev": np.nan,
            "inj_count_prev_season": 0,
            "inj_rate_per_year": 0,
            "inj_rate_per_fixture_total": np.nan,
            "inj_rate_per_fixture_6m": np.nan,
            "inj_on_weekend": 0,
            "injury_month": today.month,
            "injury_dow": today.weekday(),
            "inj_doy": today.dayofyear,
            "inj_weekofyear": today.isocalendar()[1],
            "inj_quarter": today.quarter
        }
        
        if hist.empty:
            agg_list.append(features)
            continue
            
        # Sort by date
        hist = hist.sort_values("date")
        
        # First and last injury dates
        first_date = hist["date"].min()
        last_date = hist["date"].max()
        
        # Days since injuries
        days_since_last = (today - last_date).days
        days_since_first = (today - first_date).days
        
        # Count for current season
        inj_season = hist[hist["injury_season"] == SEASON]
        
        # Counts for different time periods
        count_1m = len(hist[hist["date"] >= today - pd.DateOffset(months=1)])
        count_3m = len(hist[hist["date"] >= today - pd.DateOffset(months=3)])
        count_6m = len(hist[hist["date"] >= today - pd.DateOffset(months=6)])
        count_12m = len(hist[hist["date"] >= today - pd.DateOffset(months=12)])
        
        # Add previous dates
        hist["prev_date"] = hist["date"].shift(1)
        hist["days_between_prev_injury"] = (hist["date"] - hist["prev_date"]).dt.days
        
        # Get gap statistics
        gaps = hist["days_between_prev_injury"].dropna()
        
        # Update features
        features.update({
            "inj_count_season": len(inj_season),
            "inj_count_total": len(hist),
            "inj_count_last_1m": count_1m,
            "inj_count_last_3m": count_3m,
            "inj_count_last_6m": count_6m,
            "inj_count_last_12m": count_12m,
            "days_since_last_injury": days_since_last,
            "days_since_first_injury": days_since_first,
            "inj_seq_overall": len(hist),
            "inj_seq_season": len(inj_season),
            "avg_days_between_prev": gaps.mean() if not gaps.empty else np.nan,
            "std_days_between_prev": gaps.std() if not gaps.empty else np.nan,
            "inj_on_weekend": 1 if today.weekday() >= 5 else 0
        })
        
        # Calculate fraction
        if features["inj_count_total"] > 0:
            features["inj_frac_last_6m"] = features["inj_count_last_6m"] / features["inj_count_total"]
        
        # Previous season count (assuming PREV_SEASON is defined)
        prev_season_inj = hist[hist["injury_season"] == PREV_SEASON]
        features["inj_count_prev_season"] = len(prev_season_inj)
        
        # Rate per year
        if days_since_first > 0:
            features["inj_rate_per_year"] = features["inj_count_total"] / (days_since_first / 365)
        else:
            features["inj_rate_per_year"] = features["inj_count_total"]
        
        # Calculate fixture-based rates - using row's prev_fixtures_count from df
        fixtures_count = row.get("prev_fixtures_count", NUM_FIXTURES)
        if fixtures_count > 0:
            features["inj_rate_per_fixture_total"] = features["inj_count_total"] / fixtures_count
            features["inj_rate_per_fixture_6m"] = features["inj_count_last_6m"] / fixtures_count
        
        agg_list.append(features)
        
    # Merge back to main dataframe
    df_agg = pd.DataFrame(agg_list)
    df = df.merge(df_agg, on="player_id", how="left")
    
    return df


# ════════════════════════════════════════════════════════════
# ----------------- RAW DATA COLLECTION HELPERS ---------------
# ════════════════════════════════════════════════════════════

def get_squad(team_id: int) -> List[dict]:
    squad = []
    page = 1
    while True:
        js = _call_api("/players", {"team": team_id, "season": SEASON, "page": page})
        arr = js.get("response", [])
        if not arr:
            break
        for blk in arr:
            p = blk["player"]
            squad.append({
                "player_id": p["id"],
                "player_name": p["name"],
                "age": p.get("age"),
                "height_cm": _metric_to_number(p.get("height")),
                "weight_kg": _metric_to_number(p.get("weight")),
            })
        page += 1
    return squad


def fixtures_before(team_id: int, date_iso: str, k: int = NUM_FIXTURES) -> List[int]:
    js = _call_api("/fixtures", {
        "team": team_id,
        "season": SEASON,
        "to": date_iso,
        "status": "FT",
    })
    pairs = [(f["fixture"]["date"], f["fixture"]["id"]) for f in js.get("response", [])]
    pairs.sort(key=lambda x: x[0], reverse=True)
    return [fid for _, fid in pairs[:k]]


def fixture_team_stats(fixture_id: int, team_id: int) -> dict:
    js = _call_api("/fixtures/statistics", {"fixture": fixture_id, "team": team_id})
    if not js.get("response"):
        return {}
    raw = js["response"][0]["statistics"]
    stats = {i["type"].lower().replace(" ", "_"): i["value"] for i in raw}
    
    # Convert percentage fields
    for key in ["ball_possession"]:
        if key in stats and isinstance(stats[key], str) and stats[key].endswith("%"):
            stats[key] = _safe_float(stats[key].replace("%", ""))
    
    return stats


def fixture_player_stats(fixture_id: int, player_id: int, cache: Dict[int, dict]) -> dict:
    """Parse once per fixture and reuse for all players. Return full stats structure."""
    if fixture_id not in cache:
        js = _call_api("/fixtures/players", {"fixture": fixture_id})
        cache[fixture_id] = js
    js = cache[fixture_id]
    for side in js.get("response", []):
        for entry in side["players"]:
            if entry["player"]["id"] == player_id and entry["statistics"]:
                return entry["statistics"][0]
    return {}


def injury_log(player_id: int) -> pd.DataFrame:
    """Get player injury history by querying with player ID and season parameters"""
    rows = []
    
    # Query current season injuries
    js_current = _call_api("/injuries", {"player": player_id, "season": SEASON})
    for blk in js_current.get("response", []):
        rows.append({
            "player_id": blk["player"]["id"],
            "date": blk["fixture"]["date"],
            "season": blk["league"]["season"],
        })
    
    # Also check previous season
    js_prev = _call_api("/injuries", {"player": player_id, "season": PREV_SEASON})
    for blk in js_prev.get("response", []):
        rows.append({
            "player_id": blk["player"]["id"],
            "date": blk["fixture"]["date"],
            "season": blk["league"]["season"],
        })
    
    return pd.DataFrame(rows)


# ════════════════════════════════════════════════════════════
# ------------------ LOAD BOOTSTRAP ENSEMBLE -----------------
# ════════════════════════════════════════════════════════════
META_FILE = BOOT_DIR / "metadata.json"
if not META_FILE.exists():
    raise FileNotFoundError("metadata.json not found – did you train models?")
with open(META_FILE, "r", encoding="utf-8") as fh:
    meta = json.load(fh)
REQ_FEATURES: List[str] = meta["feature_cols"]
BOOT_FILES: List[str] = meta["model_files"]

MODELS: List[CatBoostClassifier] = []
for fp in BOOT_FILES:
    m = CatBoostClassifier()
    m.load_model(fp)
    MODELS.append(m)

OBJ_COLS = [c for c in REQ_FEATURES if c.endswith("_position")]

# ════════════════════════════════════════════════════════════
# ----------------------- MAIN FUNCTION ----------------------
# ════════════════════════════════════════════════════════════

def predict_match_risk(home_team: str, away_team: str, save: bool = True) -> pd.DataFrame:
    """Return DataFrame of injury probabilities for *home_team* squad."""
    if home_team not in TEAM_NAME2ID or away_team not in TEAM_NAME2ID:
        raise ValueError("Unknown team names – check teams_2024.csv")

    h_id, a_id = TEAM_NAME2ID[home_team], TEAM_NAME2ID[away_team]
    today_iso = datetime.utcnow().strftime("%Y-%m-%d")

    # 1) Fetch squads and fixture lists
    squad = get_squad(h_id)
    if not squad:
        raise RuntimeError(f"Squad not found for team {home_team}")
    h_fix = fixtures_before(h_id, today_iso)
    a_fix = fixtures_before(a_id, today_iso)

    # Pre‑fetch team & opponent stats once
    h_team_stats = [fixture_team_stats(fid, h_id) for fid in h_fix]
    a_team_stats = [fixture_team_stats(fid, a_id) for fid in a_fix]

    # cache for fixture‑player stats
    fp_cache: Dict[int, dict] = {}

    feature_rows, meta_rows = [], []
    for player in tqdm(squad, desc="Building features"):
        feats = {c: math.nan for c in REQ_FEATURES}

        # --- basic bio ---
        feats["player_id"] = player["player_id"]
        feats["prev_player_age"] = player["age"]
        feats["prev_player_height"] = player["height_cm"]
        feats["prev_player_weight"] = player["weight_kg"]

        # --- previous‑season flat stats ---
        js_prev = _call_api("/players", {"id": player["player_id"], "season": PREV_SEASON})
        if js_prev.get("response"):
            flat_prev = flatten_player_stats(js_prev["response"][0])[0]
            # Keep only games_* fields and prefix exactly as in training (prev_games_*)
            prefixed = {f"prev_{k}": v for k, v in flat_prev.items() if k.startswith("games_")}
            # numeric sanitation where needed
            if "prev_games_minutes" in prefixed:
                prefixed["prev_games_minutes"] = _safe_float(prefixed["prev_games_minutes"])
            if "prev_games_rating" in prefixed:
                prefixed["prev_games_rating"] = _safe_float(prefixed["prev_games_rating"])
            feats.update(prefixed)

        # --- last‑5 player stats ---
        p_stats = [fixture_player_stats(fid, player["player_id"], fp_cache) for fid in h_fix]
        feats.update(aggregate_player_stats(p_stats))

        # --- team & opponent stats ---
        feats.update(aggregate_team_stats(h_team_stats))
        feats.update(aggregate_opponent_stats(a_team_stats))

        # --- diff / ratio features (team vs opponent) ---
        # Simple differences
        feats["team_vs_opp_shots_diff_5"] = feats["team_total_shots_5"] - feats["opp_total_shots_5"]
        feats["team_vs_opp_sog_diff_5"] = feats["team_shots_on_goal_5"] - feats["opp_shots_on_goal_5"]
        feats["team_vs_opp_fouls_diff_5"] = feats["team_fouls_5"] - feats["opp_fouls_5"]
        feats["team_vs_opp_corners_diff_5"] = feats["team_corners_5"] - feats["opp_corners_5"]
        feats["team_vs_opp_offsides_diff_5"] = feats["team_offsides_5"] - feats["opp_offsides_5"]
        feats["team_vs_opp_poss_diff_5"] = feats["team_ball_poss_avg_5"] - feats["opp_ball_poss_avg_5"]
        feats["team_vs_opp_pass_acc_diff_5"] = feats["team_pass_acc_ratio_5"] - feats["opp_pass_acc_ratio_5"]

        # Ratios - using np.where for safer division like in training
        feats["team_vs_opp_shots_ratio_5"] = np.nan
        feats["team_vs_opp_sog_ratio_5"] = np.nan
        feats["team_vs_opp_fouls_ratio_5"] = np.nan
        feats["team_vs_opp_corners_ratio_5"] = np.nan
        feats["team_vs_opp_offsides_ratio_5"] = np.nan
        feats["team_vs_opp_poss_ratio_5"] = np.nan
        feats["team_vs_opp_pass_acc_ratio_5"] = np.nan

        # Calculate ratios safely
        if not np.isnan(feats["opp_total_shots_5"]) and feats["opp_total_shots_5"] != 0:
            feats["team_vs_opp_shots_ratio_5"] = feats["team_total_shots_5"] / feats["opp_total_shots_5"]
        
        if not np.isnan(feats["opp_shots_on_goal_5"]) and feats["opp_shots_on_goal_5"] != 0:
            feats["team_vs_opp_sog_ratio_5"] = feats["team_shots_on_goal_5"] / feats["opp_shots_on_goal_5"]
        
        if not np.isnan(feats["opp_fouls_5"]) and feats["opp_fouls_5"] != 0:
            feats["team_vs_opp_fouls_ratio_5"] = feats["team_fouls_5"] / feats["opp_fouls_5"]
        
        if not np.isnan(feats["opp_corners_5"]) and feats["opp_corners_5"] != 0:
            feats["team_vs_opp_corners_ratio_5"] = feats["team_corners_5"] / feats["opp_corners_5"]
        
        if not np.isnan(feats["opp_offsides_5"]) and feats["opp_offsides_5"] != 0:
            feats["team_vs_opp_offsides_ratio_5"] = feats["team_offsides_5"] / feats["opp_offsides_5"]
        
        if not np.isnan(feats["opp_ball_poss_avg_5"]) and feats["opp_ball_poss_avg_5"] != 0:
            feats["team_vs_opp_poss_ratio_5"] = feats["team_ball_poss_avg_5"] / feats["opp_ball_poss_avg_5"]
        
        if not np.isnan(feats["opp_pass_acc_ratio_5"]) and feats["opp_pass_acc_ratio_5"] != 0:
            feats["team_vs_opp_pass_acc_ratio_5"] = feats["team_pass_acc_ratio_5"] / feats["opp_pass_acc_ratio_5"]

        # ---------- add injury‑history block ----------
        inj_hist = injury_log(player["player_id"])
        today_row = pd.DataFrame(
            {
                "player_id": [player["player_id"]],
                "today": [today_iso],
            }
        )
        
        # Add temporal injury features (comprehensive set matching training pipeline)
        temporal_features = add_temporal_injury_features(today_row, inj_hist)
        for col in temporal_features.columns:
            if col not in ["player_id", "today", "date"]:
                feats[col] = temporal_features.iloc[0][col]

        # prev fixtures count (needed for rates)
        feats["prev_fixtures_count"] = len(h_fix)

        # ---------- encode categorical ----------
        raw_pos = feats.get("prev_games_position", "None")
        feats["prev_games_position"] = POS2ID.get(raw_pos, POS2ID["None"])
        feats["prev_games_position_raw"] = raw_pos

        # keep exactly the training‑time columns (others ignored)
        feature_rows.append({k: feats.get(k, np.nan) for k in REQ_FEATURES})
        meta_rows.append(
            {
                "player_id": player["player_id"],
                "player_name": player["player_name"],
                "age": player["age"],
                "height_cm": player["height_cm"],
                "weight_kg": player["weight_kg"],
                "position": feats.get("prev_games_position_raw", np.nan),
                "last_rating": feats.get("player_rating_avg_5"),
            }
        )

    # ════════════════════════════════════════════════════════
    # ------------------ DIAGNOSE FEATURES -------------------
    # ════════════════════════════════════════════════════════
    X_debug = pd.DataFrame(feature_rows)
    
    # Check for missing features
    missing_features = set(REQ_FEATURES) - set(X_debug.columns)
    if missing_features:
        # Add missing features as NaN
        for feat in missing_features:
            X_debug[feat] = np.nan
    
    # Check for all-NaN columns
    na_counts = X_debug.isna().sum()
    na_percent = (na_counts / len(X_debug)) * 100
    high_nan_cols = na_percent[na_percent > 50].sort_values(ascending=False)
    
    # ════════════════════════════════════════════════════════
    # ------------------  PREDICTION  -------------------------
    # ════════════════════════════════════════════════════════
    X = X_debug[REQ_FEATURES]

    # X.to_csv("df.csv",index=False)
    # Cast object / category columns to int, everything else float
    for col in OBJ_COLS:
        X[col] = X[col].fillna(-1).astype(int).replace({-1:np.nan})
    X = X.astype(float)

    # ensemble predictions → bootstrap mean + confidence interval
    boot_mat = np.vstack([m.predict_proba(X)[:, 1] for m in MODELS])
    prob_mean = boot_mat.mean(axis=0)
    prob_low, prob_high = np.percentile(boot_mat, [CI_LOW, CI_HIGH], axis=0)

    df_out = pd.DataFrame(meta_rows)
    df_out["inj_probability"] = prob_mean
    df_out["ci_lower_95"] = prob_low
    df_out["ci_upper_95"] = prob_high

    if save:
        fn = (
            f"risk_{home_team.replace(' ', '_')}"
            f"_vs_{away_team.replace(' ', '_')}.csv"
        )
        df_out.to_csv(fn, index=False)
        print(f"[saved] → {fn}")

    return df_out


# ════════════════════════════════════════════════════════════
# --------------------------- CLI ----------------------------
# ════════════════════════════════════════════════════════════
if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(1)

    home, away = sys.argv[1], sys.argv[2]
    res = predict_match_risk(home, away)
