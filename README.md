# ⚽ Football Injury AI Prediction System

This project focuses on predicting football player injuries using **pre-match** statistics and, in the future, **in-match** real-time data. It is designed to assist coaches and medical staff in making better, proactive decisions.

## 📂 Project Structure

```
📁 root/
├── 1k_pos_sample.csv              # Positive injury samples (1,000)
├── 2k_neg_sample.csv              # Negative samples (2,400)
├── new_100_pos_samples.csv        # Additional 100 positive samples
├── pos_samples_generation.ipynb   # Notebook to generate positive samples
├── neg_samples_generation.ipynb   # Notebook to generate negative samples
├── football-model.ipynb           # Training and evaluation of first pre-match model
└── README.md
```

## 🧠 Project Summary

Injuries can drastically affect team performance and player health. This system uses structured football data to anticipate injury risks **before matches** (and eventually **during live games**).

We focus on:
- Past player & team stats
- Current match context
- Recent match history (team & opponent)
- [Coming soon] In-match stats (e.g., distance, fouls)

## 🚀 How to Run

1. Clone this repository:
   ```bash
   git clone https://github.com/Sameer-13/AI_Football_Injury_Prevention.git
   cd football-injury-prediction
   ```

2. Open and run the model training notebook:
   ```
   football-model.ipynb
   ```

3. All required data is provided in `.csv` files.

4. To regenerate data:
   - Use `pos_samples_generation.ipynb` for injuries
   - Use `neg_samples_generation.ipynb` for healthy samples

> ⚠ Make sure you set up your API key from [https://www.api-football.com/](https://www.api-football.com/) inside the data generation notebooks.

## 📌 Progress Status

| Component                  | Status        |
|---------------------------|---------------|
| Data Preparation (Pre-Match)    | ✅ Completed   |
| Modeling (Pre-Match)            | ✅ Completed   |
| Data Preparation (In-Match)     | 🚧 In Progress |
| Modeling (In-Match)             | 🚧 In Progress |
| UI / Dashboard            | 🔧 Planned     |


---

🔮 **Coming soon:** In-match live model + UI to help coaches assess injury risk minute-by-minute during matches.
