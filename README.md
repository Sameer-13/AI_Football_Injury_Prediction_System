# InjurySense.AI: Football Injury Prevention System

![InjurySense.AI Logo](https://github.com/user-attachments/assets/56038766-fa45-4b6a-9af6-2908b6776f92)

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Project Architecture](#project-architecture)
- [Pre-Match Analysis](#pre-match-analysis)
- [In-Match Analysis](#in-match-analysis)
- [Data Collection Process](#data-collection-process)
- [Feature Engineering](#feature-engineering)
- [Model Architecture](#model-architecture)
- [Project Structure](#project-structure)
- [How to Run](#how-to-run)
- [Results & Performance](#results--performance)
- [Future Work](#future-work)

## Overview

InjurySense.AI is an advanced football injury prediction system using machine learning to help teams proactively prevent player injuries. The system offers two complementary modes of analysis:

1. **Pre-Match Analysis**: Predicts injury risks before matches based on historical data
2. **In-Match Analysis**: Provides real-time monitoring of injury risks during games

![Pre-Match Dashboard](https://github.com/user-attachments/assets/7263370b-62d1-4726-866f-922e06e3c84a)

*Pre-Match Injury Risk Dashboard showing player risks, position breakdowns, and team risk assessment*

![In-Match Monitoring](https://github.com/user-attachments/assets/df8f3611-176d-4240-b2d3-bbe523c12012)
*In-Match Live Risk Monitoring showing real-time player risk tracking throughout the match*

This AI-driven solution helps coaches and medical staff make data-informed decisions to optimize player health and team performance.

## Key Features

### Pre-Match Analysis
- Player-specific injury risk predictions before games
- Confidence intervals for risk assessment
- Visual risk distribution by player position
- Identification of high-risk players requiring special attention
- Team vs. opponent contextual analysis

### In-Match Analysis
- Real-time player risk monitoring
- Dynamic risk ranking tracking over time
- High-risk zone alerts
- Minute-by-minute risk trend visualization
- Auto-refresh capabilities for live data

## Project Architecture

The system is built on a three-layer architecture:

1. **Data Layer**: 
   - Historical player and match data collection via API-Football
   - Feature preprocessing and transformation
   - Storage of pre-computed models and inference results

2. **Model Layer**:
   - Pre-match XGBoost classification model (F1 score: 0.80)
   - In-match streaming prediction pipeline
   - Feature importance analysis for explainability

3. **Presentation Layer**:
   - Interactive Streamlit dashboard
   - Real-time visualization components
   - Team and player selection interface
   - Risk distribution charts and player cards

## Pre-Match Analysis

The pre-match analysis system uses a combination of:

- **Previous season statistics** for baseline player metrics
- **Player's recent match data** (previous 5 matches)
- **Team performance metrics** in recent matches
- **Opponent team analysis** and match context
- **Historical injury records** to identify recurring patterns

The model generates a risk probability score (0-1) for each player with confidence intervals, allowing medical staff to prioritize preventative measures.

![image](https://github.com/user-attachments/assets/90b9f1d7-7cbe-43d4-ba5a-0a211e2680bb)
![Pre-Match Risk per Player](https://github.com/user-attachments/assets/7263370b-62d1-4726-866f-922e06e3c84a)
*Pre-match injury risk visualization per player with confidence intervals*

### Pre-Match Dashboard Sections:

1. **Team Risk Overview**: Summary of high vs. low risk players
2. **Risk Distribution by Position**: Analysis of which positions have the highest injury rates
3. **High Risk Players Spotlight**: Focused attention on players requiring intervention
4. **Player Injury Risk Assessment**: Detailed risk assessment with confidence intervals

## In-Match Analysis

The in-match analysis system provides:

- **Live Risk Rankings**: Current risk status of all players
- **Risk Trend Visualization**: How player risk evolves over match time
- **High Risk Zone Tracking**: Visual identification of players entering dangerous risk levels
- **Position-Specific Monitoring**: Different thresholds based on player roles

The system updates every minute during live matches and visualizes which players are trending toward higher risk, allowing coaches to make substitution decisions or adjust player roles.

![image](https://github.com/user-attachments/assets/fa670fda-aaa0-4ba7-a2ef-3b042f4e5a38)
*In-match risk trends showing how player risk evolves throughout the game*

## Data Collection Process

### Positive Sample Generation

This process collects data for players who suffered injuries:

1. **Injury Data Collection**:
   - Query the API for players with recorded injuries in the 2024 season
   - Extract injury dates, player details, and match contexts

2. **Feature Expansion**:
   - For each injury, identify the opponent team
   - Gather previous 5 fixtures for the player's team
   - Gather previous 5 fixtures for the opponent team

3. **Previous Season Stats Collection**:
   - Gather player statistics from the previous season
   - Include metrics like appearances, goals, assists, etc.

4. **Raw Stats Collection**:
   - For each of the previous 5 matches:
     - Collect player-specific performance metrics
     - Team aggregate statistics (shots, possession, passing accuracy)
     - Opponent team statistics

### Negative Sample Generation

This collects data for non-injured players to create balanced training data:

1. **Non-Injury Player Identification**:
   - Find players who participated in matches without injuries
   
2. **Random Fixture Selection**:
   - For each non-injured player, randomly select 5 fixtures they participated in
   - Tag these as "non-injury" examples (label = 0)

## Feature Engineering

The system leverages these feature categories:

### Player-Specific Features
- Recent form indicators (avg. minutes, rating, shots, goals)
- Physical load metrics (duels, tackles, fouls)
- Performance consistency measures
- Historical injury patterns
- Position-specific metrics

### Team Context Features
- Team's recent shooting efficiency
- Ball possession patterns
- Team passing accuracy
- Defensive metrics (tackles, interceptions)
- Set piece statistics (corners, free kicks)

### Opponent Analysis Features
- Opponent's aggressive play indicators
- Match difficulty based on opponent form
- Opponent pressing intensity

### Derived Interaction Features
- Team vs. opponent statistical differentials
- Performance ratios (shots, possession, passing)
- Historical matchup patterns

## Model Architecture

The core predictive engine uses **XGBoost**, optimized for injury prediction:

1. **Preprocessing Pipeline**:
   - Feature cleaning and normalization
   - Missing value imputation
   - Feature selection based on importance

2. **Model Configuration**:
   - Optimized hyperparameters (n_estimators=80, learning_rate=0.1)
   - Cross-validation with StratifiedGroupKFold to prevent data leakage
   - Group-based splitting by player_id to ensure no player appears in both train/test sets

3. **Evaluation Metrics**:
   - Overall F1 Score: 0.80
   - Accuracy: 0.85
   - Significant improvement over baseline (0.41 F1 / 0.69 accuracy)

4. **Key Performance Insights**:
   - Most predictive features:
     - Number of injuries in last 6 months
     - Days since last injury incident
     - Player's age
     - Team's passing accuracy in last 5 matches

## Project Structure

```
📁 AI_Football_Injury_Prevention/
├── assets/                      # UI assets and logos
├── components/                  # Streamlit UI components
│   ├── in_match_analysis.py     # In-match analysis page
│   ├── live_match_visualization.py  # Real-time visualizations
│   ├── metric_plane.py          # Team risk summary components
│   ├── player_cards.py          # Player spotlight cards
│   ├── risk_charts.py           # Distribution charts
│   ├── sidebar.py               # Navigation sidebar
│   └── table.py                 # Player risk table
├── data/                        # Data storage
├── model_inferences/            # Model inference outputs
├── models/                      # Trained models
├── scripts/                     # Data preparation scripts
│   ├── neg_samples_generation.ipynb  # Negative samples collection
│   ├── pos_samples_generation.ipynb  # Positive samples collection
│   └── football-model.ipynb     # Model training
├── utils/                       # Utility functions
├── config.yaml                  # Configuration settings
├── main.py                      # Main application entry point
└── README.md                    # This file
```

## How to Run

1. Clone this repository:
   ```bash
   git clone https://github.com/username/AI_Football_Injury_Prevention.git
   cd AI_Football_Injury_Prevention
   ```

2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the Streamlit application:
   ```bash
   streamlit run main.py
   ```

4. Access the dashboard at http://localhost:8501

## Results & Performance

The model achieves strong predictive performance:

- **F1 Score (macro)**: 0.80 
- **Accuracy**: 0.85
- **Baseline F1**: 0.41
- **Baseline Accuracy**: 0.69

### Model Limitations:
- Performance varies by injury type
- Some rare injury causes remain difficult to predict
- Requires recent performance data to make accurate predictions

## Future Work

1. **In-Match Enhancement**:
   - Integrate GPS tracking data for more precise fatigue estimation
   - Implement computer vision analysis for movement patterns
   - Create personalized player risk profiles

2. **UI Development**:
   - Expand team comparison features
   - Add predictive substitution recommendations
   - Develop mobile application for sideline use

3. **Enhanced Features**:
   - Integrate physical performance metrics (GPS data)
   - Add biomechanical risk factors when available
   - Incorporate weather and pitch conditions

4. **Model Improvements**:
   - Experiment with deep learning architectures
   - Test ensemble methods for improved accuracy
   - Implement explainable AI features for coaching staff

---

**InjurySense.AI © 2025 | Powered by AI Football Injury Prevention System**
