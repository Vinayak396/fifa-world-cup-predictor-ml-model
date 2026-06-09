# ⚽ FIFA World Cup 2026 Prediction Model

A complete machine learning pipeline and Monte Carlo tournament simulator to predict the winner of the **FIFA World Cup 2026**, built with pure NumPy — no scikit-learn required.

---

## 📊 Overview

The model estimates team strengths using historical international match results, historical FIFA rankings, and **EA FC 26 squad ratings**, then simulates the full 48-team 2026 tournament structure 10,000 times to compute winning probabilities for each country.

The tournament simulation covers the entire bracket:
- Group stage (12 groups of 4)
- Best 8 third-placed teams selection (backtracking bipartite matcher)
- Round of 32 → Round of 16 → Quarterfinals → Semifinals → Final

---

## 🌟 Model Features

### Core Model
- **Pure NumPy Poisson Regression**: A custom generalized linear model with a log-link trained via gradient descent. No C-extension dependencies — runs cleanly under restricted Windows environments.
- **High-Performance Simulation Cache**: Expected goals (λ) pre-calculated in a single bulk matrix operation for all 2,256 possible matchups, enabling 10,000 Monte Carlo runs in under **5 seconds**.

### Advanced Feature Engineering
| Feature | Description |
|---------|-------------|
| `rank_diff` | Relative FIFA ranking difference |
| `point_diff` | Relative FIFA ranking points |
| `is_home` | Home/neutral venue advantage |
| `squad_atk_self` | EA FC 26 Attack Score of the team |
| `squad_def_opp` | EA FC 26 Defense Score of the opponent |
| `squad_ovr_diff` | EA FC 26 Overall Rating difference |
| `form_attack_self` | Exponentially decayed attacking form |
| `form_defense_opp` | Exponentially decayed defensive form of opponent |

### Accuracy Improvements (v2.0)

**Fix 1 — EA FC 26 Squad Ratings**
- Loaded `Top11_OVR`, `Attack_Score`, `Defense_Score`, and `Penalty_Score` for all 48 nations from EA FC 26 data.
- Added squad quality as direct model features, replacing a pure FIFA-rank-based proxy.
- Regression-based fallback for any non-WC opponents.

**Fix 2 — Exponential Form Decay**
- Team form now uses **exponential time decay** with a 365-day half-life (recent matches dominate, old ones fade).
- Match importance weights applied: World Cup Final = 2.0×, Qualifiers = 1.5×, Friendlies = 0.1×.

**Fix 3 — Competitive Match Weighting**
- Training data restricted to **competitive matches from 2016 onwards** only.
- Each training sample weighted by recency (4-year half-life toward the WC date) × match importance.

**Fix 4 — Shootout Logic Enhancement**
- Penalty shootout winner probability now combines: historical shootout win rate (40%) + FIFA rank (10%) + **EA FC 26 Penalty Score** (50%).

**Fix 5 — Group Draw Difficulty Adjustment**
- Each team's 3 group opponents are rated by avg EA FC OVR.
- Teams from harder groups receive up to **+3% lambda boost** in knockouts (battle-hardened effect).
- Teams from easy groups receive up to **−3% penalty** (e.g. Belgium: Iran/Egypt/New Zealand → penalised).

**Fix 6 — Manual Squad Override Multipliers**
- Expert-calibrated multipliers applied to all rounds to correct systematic model biases:

| Team | Multiplier | Reason |
|------|-----------|--------|
| Germany | ×1.04 | Strong Nagelsmann rebuild; ruthless at Euro 2024 |
| Morocco | ×1.04 | 2022 semi-finalists; peak squad, organized |
| United States | ×1.03 | Home nation; athletic MNT generation at peak |
| Canada | ×1.02 | Home nation; Davies-led golden generation |
| England | ×1.02 | Peak Bellingham-era squad; unrivalled depth |
| Japan | ×1.02 | Consistent overperformer; Europe-based stars |
| Mexico | ×1.01 | Home nation; passionate support |
| Argentina | ×0.97 | Messi at 38; squad in transition |
| Uruguay | ×0.96 | Aging defensive core |
| Belgium | ×0.92 | Aging golden generation; De Bruyne concerns |
| Qatar | ×0.90 | Host qualifier; domestic standard below WC level |

---

## 📈 Prediction Results (Top 15)

> Results from 10,000 Monte Carlo simulations — updated with all v2.0 improvements.

| Rank | Team | Group | FIFA Rank | R16 (%) | QF (%) | SF (%) | Final (%) | Winner (%) |
|------|------|-------|-----------|---------|--------|--------|-----------|------------|
| 1 | **England** | Group L | 4 | 67.08 | 45.16 | 27.95 | 17.89 | **11.22%** |
| 2 | **Spain** | Group H | 2 | 64.90 | 42.68 | 29.38 | 17.86 | **11.00%** |
| 3 | **France** | Group I | 1 | 62.25 | 38.86 | 23.63 | 13.89 | **7.87%** |
| 4 | **Portugal** | Group K | 5 | 59.27 | 37.34 | 22.67 | 12.46 | **6.99%** |
| 5 | **Germany** | Group E | 10 | 61.10 | 34.80 | 20.16 | 11.36 | **6.32%** |
| 6 | **Argentina** | Group J | 3 | 53.69 | 34.02 | 20.52 | 11.10 | **6.20%** |
| 7 | **Netherlands** | Group F | 7 | 54.09 | 35.74 | 20.86 | 11.96 | **6.10%** |
| 8 | **Morocco** | Group C | 8 | 53.50 | 32.92 | 18.68 | 10.54 | **5.48%** |
| 9 | **Belgium** | Group G | 9 | 57.10 | 32.95 | 16.94 | 8.48 | **4.09%** |
| 10 | **Japan** | Group F | 18 | 46.22 | 26.58 | 14.09 | 7.35 | **3.65%** |
| 11 | **Brazil** | Group C | 6 | 45.93 | 26.26 | 13.86 | 7.00 | **3.53%** |
| 12 | **Croatia** | Group L | 11 | 48.84 | 26.57 | 14.79 | 7.57 | **3.51%** |
| 13 | **Norway** | Group I | 31 | 48.58 | 25.47 | 12.79 | 6.44 | **3.06%** |
| 14 | **United States** | Group D | 16 | 47.35 | 23.77 | 10.87 | 4.75 | **2.12%** |
| 15 | **Senegal** | Group I | 14 | 42.89 | 20.92 | 10.08 | 5.04 | **2.11%** |

Full results for all 48 teams available in [`fifa_2026_prediction_results.csv`](./fifa_2026_prediction_results.csv).

---

## 📁 Repository Structure

| File | Description |
|------|-------------|
| `predict_world_cup.py` | Main Python pipeline and simulation script |
| `predict_world_cup.ipynb` | Self-contained, documented Jupyter notebook |
| `fifa_2026_prediction_results.csv` | Full probability stats for all 48 teams |
| `fifa_2026_prediction_plot.png` | Winner probability bar chart |
| `eafc26_wc_team_summary.csv` | EA FC 26 squad ratings for all 48 WC nations |
| `results.csv` | Historical international match results (1872–2026) |
| `fifa_mens_rank.csv` | Historical FIFA rankings (1993–2026) |
| `shootouts.csv` | Historical penalty shootout results |
| `FIFA2026_schedule_Fixtures.csv` | 2026 World Cup groups and fixture schedule |
| `former_names.csv` | Historical team name mapping database |

---

## 🚀 How to Run

1. **Activate the Environment**:
   ```powershell
   # Windows (PowerShell)
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
   This trains the model, runs 10,000 simulations, prints predictions, and auto-generates the notebook, results CSV, and probability chart.

4. **Interact via Notebook**:
   Open and run `predict_world_cup.ipynb` in any Jupyter environment.

---

## 🛠️ Tech Stack

- **Language**: Python 3.11
- **Libraries**: `numpy`, `pandas`, `matplotlib`, `seaborn`
- **Model**: Custom Poisson Regression (pure NumPy gradient descent)
- **Simulation**: Monte Carlo (10,000 iterations)
- **Data**: Kaggle international football results + EA FC 26 squad ratings
