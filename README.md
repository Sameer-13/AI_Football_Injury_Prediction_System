![WHITELOGO_2025-04-10_15-15-27-removebg-preview](https://github.com/user-attachments/assets/56038766-fa45-4b6a-9af6-2908b6776f92)

# Football Injury AI Prediction System

This project focuses on predicting football player injuries using **pre-match** statistics and, in the future, **in-match** real-time data. It is designed to assist coaches and medical staff in making better, proactive decisions to prevent player injuries.

## Table of Contents

- [Project Overview](#-project-overview)
- [Data Collection Process](#-data-collection-process)
- [Feature Engineering](#-feature-engineering)
- [Model Architecture](#-model-architecture)
- [Project Structure](#-project-structure)
- [How to Run](#-how-to-run)
- [Results & Performance](#-results--performance)
- [Future Work](#-future-work)

## Project Overview

Injuries can drastically affect team performance and player health. This AI-driven system uses structured football data from API-Football to anticipate injury risks **before matches** (and eventually **during live games**).

Our solution focuses on:
- Past player & team statistics
- Current match context (opponent analysis)
- Recent match history (team & opponent performance)
- [Coming soon] In-match stats (e.g., distance covered, sprint counts, fatigue indicators)

The system was built using a machine learning pipeline with **XGBoost** as the primary classification algorithm, achieving an F1 score of **0.80** and accuracy of **0.85**, significantly outperforming baseline predictions.

## 📊 Data Collection Process

The data collection involves several steps:

### 1. Positive Sample Generation (`pos_samples_generation.ipynb`)

This notebook collects data for players who suffered injuries:

1. **Injury Data Collection**:
   - Query the API for players with recorded injuries in the 2024 season
   - Extract injury dates, player details, and match contexts

2. **Feature Expansion**:
   - For each injury, identify:
     - The opponent team
     - Previous 5 fixtures for the player's team
     - Previous 5 fixtures for the opponent team

3. **Previous Season Stats**:
   - Gather player statistics from the previous season (2023)
   - Include comprehensive metrics like appearances, goals, assists, etc.

4. **Raw Stats Collection**:
   - For each of the previous 5 matches:
     - Collect player-specific performance metrics
     - Team aggregate statistics (shots, possession, passing accuracy)
     - Opponent team statistics

### 2. Negative Sample Generation (`neg_samples_generation.ipynb`)

This notebook collects data for non-injured players to create balanced training data:

1. **Non-Injury Player Identification**:
   - Find players who participated in matches without injuries
   
2. **Random Fixture Selection**:
   - For each non-injured player, randomly select 5 fixtures they participated in
   - Tag these as "non-injury" examples (label = 0)

3. **Feature Parity**:
   - Apply the same feature extraction process as positive samples
   - Ensure negative examples have identical feature structure

### 3. Data Preprocessing

Both positive and negative samples undergo identical preprocessing:

- **Feature Extraction**:
  - Transform raw API responses into structured features
  - Handle missing values
  - Normalize and standardize metrics

- **Temporal Features**:
  - Calculate days since last injury
  - Count injury occurrences in the last 6 months

- **Comparative Metrics**:
  - Generate team vs. opponent differential metrics
  - Calculate performance ratios between teams

## 🔍 Feature Engineering

The system leverages a rich set of features derived from raw data:

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

## 🤖 Model Architecture

The core predictive engine uses **XGBoost**, a gradient boosting framework known for its performance in structured data problems:

1. **Preprocessing Pipeline**:
   - Feature cleaning and normalization
   - Missing value imputation
   - Feature selection based on importance

2. **Model Configuration**:
   - Optimized hyperparameters (n_estimators=80, learning_rate=0.1)
   - Cross-validation with StratifiedGroupKFold to prevent data leakage
   - Group-based splitting by player_id to ensure no player appears in both train/test sets

3. **Training Strategy**:
   - F1-macro optimization (balancing precision and recall)
   - Per-fold feature importance analysis
   - Permutation importance for robust feature selection

4. **Evaluation Metrics**:
   - Overall F1 Score: 0.80
   - Accuracy: 0.85
   - Significant improvement over baseline (0.41 F1 / 0.69 accuracy)

## 📂 Project Structure

```
📁 root/
├── 1k_pos_sample.csv              # Positive injury samples (1,000)
├── 2k_neg_sample.csv              # Negative samples (2,400)
├── new_100_pos_samples.csv        # Additional 100 positive samples
├── pos_samples_generation.ipynb   # Notebook to generate positive samples
├── neg_samples_generation.ipynb   # Notebook to generate negative samples
├── football-model.ipynb           # Training and evaluation of pre-match model
└── README.md
```

### Key Files Explained

- **football-model.ipynb**: Contains the model training pipeline, including:
  - Data loading and preprocessing
  - Feature selection via permutation importance
  - Model training with cross-validation
  - Performance evaluation and visualization

- **pos_samples_generation.ipynb**: Implements the data collection for injury cases:
  - API interaction with detailed error handling and rate limiting
  - Comprehensive player and match data collection
  - Feature extraction and transformation

- **neg_samples_generation.ipynb**: Collects balanced non-injury examples:
  - Identifies players without injuries
  - Samples appropriate fixtures
  - Applies identical feature extraction process

## 🚀 How to Run

1. Clone this repository:
   ```bash
   git clone https://github.com/Sameer-13/AI_Football_Injury_Prevention.git
   cd football-injury-prediction
   ```

2. Set up your API key:
   - Register for an API key at [https://www.api-football.com/](https://www.api-football.com/)
   - Insert your API key in the appropriate notebooks

3. Run the notebooks in this order:
   1. `pos_samples_generation.ipynb` (if you need new positive samples)
   2. `neg_samples_generation.ipynb` (if you need new negative samples) 
   3. `football-model.ipynb` (for model training and evaluation)

4. All required data is provided in `.csv` files if you don't want to regenerate the datasets.

## 📈 Results & Performance

The model achieves strong predictive performance:

- **F1 Score (macro)**: 0.80 
- **Accuracy**: 0.85
- **Baseline F1**: 0.41
- **Baseline Accuracy**: 0.69

### Key Performance Insights:

1. **Most Predictive Features**:
   - `inj_count_last_6m`: Number of injuries in last 6 months
   - `days_since_last_injury`: Time since last injury incident
   - `prev_player_age`: Player's age
   - `team_pass_acc_ratio_5`: Team's passing accuracy in last 5 matches

2. **Model Limitations**:
   - Performance varies by injury type
   - Some rare injury causes remain difficult to predict
   - Requires recent performance data to make accurate predictions

## 📌 Progress Status

| Component                  | Status        |
|---------------------------|---------------|
| Data Preparation (Pre-Match)    | ✅ Completed   |
| Modeling (Pre-Match)            | ✅ Completed   |
| Data Preparation (In-Match)     | 🚧 In Progress |
| Modeling (In-Match)             | 🚧 In Progress |
| UI / Dashboard            | 🚧 In Progress     |

## 🔮 Future Work

1. **In-Match Prediction**:
   - Develop real-time data collection system
   - Create streaming prediction pipeline
   - Implement fatigue estimation algorithms

2. **UI Development**:
   - Create interactive dashboard for coaches
   - Live injury risk monitoring
   - Visual analytics for risk factors

3. **Enhanced Features**:
   - Integrate physical performance metrics (GPS data)
   - Add biomechanical risk factors when available
   - Incorporate weather and pitch conditions

4. **Model Improvements**:
   - Experiment with deep learning architectures
   - Test ensemble methods for improved accuracy
   - Implement explainable AI features for coaching staff

---

🔮 **Coming soon:** In-match live model + UI to help coaches assess injury risk minute-by-minute during matches.
