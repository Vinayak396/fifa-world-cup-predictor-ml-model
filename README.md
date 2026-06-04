# ⚽ FIFA World Cup 2026 Prediction Model

This repository contains a complete machine learning pipeline and Monte Carlo tournament simulator to predict the winner of the upcoming FIFA World Cup 2026.

## 📊 Overview

The model uses historical international match results (dating back to 1872) and historical FIFA rankings (from 1993 to 2024) to estimate team strengths and predict match scorelines. The simulator then simulates the entire 48-team 2026 tournament structure (Group stage tables, best-3rd place selection, Round of 32 pairings matching, and knockout bracket) 10,000 times to compute the winning probabilities for each country.

## 🌟 Key Features

1. **Pure NumPy Poisson Regression Model**: A custom generalized linear model with a log-link trained using gradient descent. This design avoids external dependency on C-extensions (like `scikit-learn`) which can be blocked by restricted Windows Application Control policies.
2. **Advanced Feature Engineering**: 
   - Relative FIFA rank and ranking point differences.
   - Host home-advantage matching.
   - Rolling team form (attack and defense averages over the last 10 games).
3. **High-Performance Simulation Cache**: Expected goals ($\lambda$) are pre-calculated in a single bulk matrix operation for all $2,256$ possible matchups. This allows the 10,000 Monte Carlo runs to execute in under **5 seconds** by bypassing individual model prediction overhead.
4. **Comprehensive Tournament Logic**:
   - Matches the actual 48 qualified teams into their correct groups.
   - Handles standard FIFA group stage tie-breakers (Points, Goal Difference, Goals Scored, and Rank).
   - Utilizes a backtracking bipartite matching solver to pair the 8 best third-placed teams in the Round of 32 while preventing group stage rematches.
   - Knockouts incorporate extra-time goal scaling and penalty shootouts based on historical penalty shootout records (`shootouts.csv`) and ranks.

## 📈 Prediction Results (Top 15)

From the 10,000 simulations, the top contenders to win the 2026 World Cup are:

| Rank | Team | Group | FIFA Rank | Round of 16 (%) | Semifinals (%) | Final (%) | Winner (%) |
|---|---|---|---|---|---|---|---|
| 1 | **Belgium** | Group G | 8 | 68.57 | 26.41 | 15.60 | **9.15%** |
| 2 | **Argentina** | Group J | 1 | 59.57 | 24.44 | 14.87 | **9.03%** |
| 3 | **Spain** | Group H | 3 | 57.91 | 22.53 | 13.86 | **8.00%** |
| 4 | **France** | Group I | 2 | 58.03 | 21.01 | 12.22 | **6.71%** |
| 5 | **England** | Group L | 4 | 59.39 | 21.34 | 11.95 | **6.56%** |
| 6 | **Netherlands** | Group F | 7 | 53.89 | 20.65 | 11.80 | **6.53%** |
| 7 | **Portugal** | Group K | 6 | 55.79 | 18.56 | 10.20 | **5.54%** |
| 8 | **Brazil** | Group C | 5 | 52.79 | 18.18 | 9.75 | **5.14%** |
| 9 | **Germany** | Group E | 10 | 58.99 | 18.17 | 9.62 | **4.68%** |
| 10 | **Morocco** | Group C | 14 | 49.77 | 16.13 | 8.29 | **4.29%** |
| 11 | **Croatia** | Group L | 13 | 48.95 | 13.72 | 6.71 | **3.35%** |
| 12 | **Colombia** | Group K | 12 | 48.69 | 13.70 | 7.06 | **3.21%** |
| 13 | **Switzerland** | Group B | 20 | 53.16 | 13.55 | 6.39 | **2.80%** |
| 14 | **Austria** | Group J | 22 | 42.13 | 11.27 | 5.44 | **2.67%** |
| 15 | **Japan** | Group F | 15 | 41.61 | 11.71 | 5.40 | **2.58%** |

## 📁 Repository Structure

- `predict_world_cup.py`: Main Python pipeline execution script.
- `predict_world_cup.ipynb`: 100% self-contained and documented Jupyter notebook.
- `fifa_2026_prediction_results.csv`: Complete probability stats for all 48 teams.
- `fifa_2026_prediction_plot.png`: Generated plot of winning probabilities.
- `results.csv`: Historical international match results.
- `fifa_mens_rank.csv`: Historical FIFA rankings.
- `shootouts.csv`: Historical penalty shootout results.
- `former_names.csv`: Mapping database of historical team names.
- `FIFA2026_schedule_Fixtures.csv`: Schedule and fixtures of the 2026 World Cup.

## 🚀 How to Run

1. **Activate the Environment**:
   ```bash
   # On Windows (PowerShell)
   .\myenv\Scripts\Activate.ps1
   ```
2. **Install Dependencies**:
   ```bash
   pip install pandas numpy matplotlib seaborn
   ```
3. **Execute the Pipeline**:
   ```bash
   python predict_world_cup.py
   ```
   This will train the model, run the 10,000 simulations, print predictions, and generate the notebook, results CSV, and probability chart.
4. **Interact via Notebook**:
   Open and run `predict_world_cup.ipynb` in any Jupyter environment.
