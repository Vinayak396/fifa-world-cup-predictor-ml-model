# ⚽ FIFA World Cup 2026 Prediction Model

A complete machine learning pipeline and Monte Carlo tournament simulator to predict the winner of the **FIFA World Cup 2026**, built with XGBoost and powered by FIFA rankings, EA FC 26 squad ratings, and historical match data.

---

## 📊 Overview

The model estimates team strengths using historical international match results, historical FIFA rankings, and **EA FC 26 squad ratings**, then simulates the full 48-team 2026 tournament structure 10,000 times to compute winning probabilities for each country.

The tournament simulation covers the entire bracket:
- Group stage (12 groups of 4)
- Best 8 third-placed teams selection (backtracking bipartite matcher)
- Round of 32 → Round of 16 → Quarterfinals → Semifinals → Final

A companion **[interactive web app](#-interactive-web-predictor)** visualises match-level Win / Draw / Win probabilities for all 72 group stage matches.

---

## 🌟 Model Features

### Core Model
- **XGBoost Poisson Regression**: `objective='count:poisson'` — captures non-linear interactions between rank, form, and squad strength. Trained on competitive matches (2016–2026) with recency + importance sample weights.
- **Dixon-Coles Correction**: Low-score bias correction (ρ = −0.13) applied to every simulated scoreline to match real-world international football score distributions.
- **High-Performance Simulation Cache**: Expected goals (λ) pre-calculated in a single bulk matrix operation for all 2,256 possible matchups, enabling 10,000 Monte Carlo runs in under **5 seconds**.

### Advanced Feature Engineering
| Feature | Description |
|---------|-------------|
| `rank_diff` | Relative FIFA ranking difference (scaled /60) |
| `point_diff` | Relative FIFA ranking points (scaled /300) |
| `is_home` | Home/neutral venue advantage |
| `squad_atk_self` | EA FC 26 Attack Score of the team |
| `squad_def_opp` | EA FC 26 Defense Score of the opponent |
| `squad_ovr_diff` | EA FC 26 Overall Rating difference |
| `form_attack_self` | Exponentially decayed attacking form (365-day half-life) |
| `form_defense_opp` | Exponentially decayed defensive form of opponent |
| `h2h_win_rate` | Head-to-head win rate in competitive matches (2016+) |

### Model Improvements

**v4.0 — Live Matchday 1 Results & Squad Lists (latest)**
- Recomputed squad statistics using **actual named squads** scraped and cross-referenced with EA FC ratings.
- Updated results database with actual scores of completed Matchday 1 fixtures (Groups A–H).
- Shifted form decay reference evaluation date to `2026-06-16` to capture Matchday 1 results as recent match history.
- Initialized group standings using real Matchday 1 scores, simulating only the remaining matches.
- Synchronized web dashboard to display Matchday 1 results with pre-match predicted probabilities.

**v3.0 — XGBoost + Dixon-Coles**
- Replaced custom NumPy Poisson with **XGBoost Poisson regressor** (`count:poisson` objective)
- Added **Dixon-Coles scoreline correction** for low-score match cells (0-0, 1-0, 0-1, 1-1)
- Added **head-to-head win rate** as a training feature (competitive matches, last 10 years)
- Upgraded fixtures to use **confirmed teams** for all previously unconfirmed playoff slots

**v2.0 — Squad Ratings + Form Decay**
- EA FC 26 squad ratings (`Top11_OVR`, `Attack_Score`, `Defense_Score`, `Penalty_Score`) integrated as model features
- Exponential time decay for form (365-day half-life); match importance weighting (WC = 2.0×, Friendlies = 0.1×)
- Training restricted to competitive matches from 2016 onwards
- Penalty shootout probability: historical win rate (40%) + FIFA rank (10%) + EA FC 26 Penalty Score (50%)
- Group draw difficulty adjustment: ±3% lambda modifier in knockout rounds based on group opponent strength
- WC pedigree multiplier: teams with deep WC history get a small KO boost (max +4%)

**Manual Override Multipliers** (expert calibration):
| Team | Multiplier | Reason |
|------|-----------|--------|
| Brazil | ×1.12 | 5× WC champions; most WC wins all time |
| Netherlands | ×1.10 | Consistently underrated; elite squad depth |
| Germany | ×1.08 | 4× WC champions; ruthless in KO rounds |
| Portugal | ×1.07 | Strong WC QF/R16 history; elite squad |
| France | ×1.05 | Defending finalists 2022; deepest squad |
| Morocco | ×1.04 | 2022 semi-finalists; peak squad |
| England | ×1.03 | Peak Bellingham-era squad; unrivalled depth |
| Argentina | ×0.97 | Messi at 38; squad in transition |
| Belgium | ×0.91 | Aging golden generation |
| Qatar | ×0.87 | Host qualifier; domestic level below WC |

---

## 📈 Latest Prediction Results (Top 15)

> Results from 10,000 Monte Carlo simulations — v4.0 model (post-Matchday 1).

| Rank | Team | Group | FIFA Rank | R16 (%) | QF (%) | SF (%) | Final (%) | **Winner (%)** |
|------|------|-------|-----------|---------|--------|--------|-----------|----------------|
| 1 | 🇫🇷 **France** | I | 1 | 58.23% | 39.77% | 27.66% | 17.75% | **12.21%** |
| 2 | 🏴󠁧󠁢󠁥󠁮󠁧󠁿 **England** | L | 4 | 64.58% | 40.86% | 25.91% | 15.58% | **8.77%** |
| 3 | 🇪🇸 **Spain** | H | 2 | 53.08% | 34.80% | 22.76% | 14.32% | **8.76%** |
| 4 | 🇦🇷 **Argentina** | J | 3 | 49.44% | 32.83% | 20.82% | 11.88% | **6.57%** |
| 5 | 🇵🇹 **Portugal** | K | 5 | 55.46% | 34.56% | 19.60% | 11.28% | **6.33%** |
| 6 | 🇲🇦 **Morocco** | C | 8 | 55.58% | 35.55% | 18.84% | 11.28% | **6.12%** |
| 7 | 🇧🇷 **Brazil** | C | 6 | 57.00% | 36.16% | 21.11% | 11.50% | **6.11%** |
| 8 | 🇧🇪 **Belgium** | G | 9 | 46.88% | 28.41% | 17.20% | 8.86% | **4.74%** |
| 9 | 🇩🇪 **Germany** | E | 10 | 61.72% | 32.70% | 18.16% | 9.64% | **4.70%** |
| 10 | 🇨🇴 **Colombia** | K | 13 | 41.84% | 22.28% | 12.20% | 6.14% | **2.78%** |
| 11 | 🇭🇷 **Croatia** | L | 11 | 35.01% | 20.56% | 11.80% | 5.93% | **2.67%** |
| 12 | 🇦🇺 **Australia** | D | 27 | 53.31% | 26.03% | 13.24% | 5.67% | **2.51%** |
| 13 | 🇳🇱 **Netherlands** | F | 7 | 35.42% | 19.98% | 9.47% | 4.64% | **2.26%** |
| 14 | 🇲🇽 **Mexico** | A | 15 | 57.25% | 25.29% | 11.18% | 5.05% | **2.24%** |
| 15 | 🇺🇸 **United States** | D | 16 | 54.34% | 26.91% | 11.88% | 5.33% | **2.18%** |

Full results for all 48 teams: [`fifa_2026_prediction_results.csv`](./fifa_2026_prediction_results.csv)

---

## 🌐 Interactive Web Predictor

A companion website visualises **Win / Draw / Win probabilities** for every group stage match.

**Features:**
- 🏆 Predicted tournament winner spotlight (France, 12.21%)
- 📊 Top 10 contenders with animated probability bars
- ⚽ All 72 group stage matches across 12 group tabs (A–L)
- Match cards displaying completed Matchday 1 final scores alongside pre-match odds
- Fully responsive — dark navy design with gold accents and glassmorphic card layouts

**Run locally:**
```bash
cd website
python -m http.server 8765
# Open http://localhost:8765
```

---

## 📁 Repository Structure

| File | Description |
|------|-------------|
| `predict_world_cup.py` | Main Python pipeline and simulation script |
| `predict_world_cup.ipynb` | Self-contained, documented Jupyter notebook |
| `get_wc_squads.py` | Scrapes Wikipedia squad list and cross-references it with EA FC ratings |
| `update_results_md1.py` | Helper utility to populate Matchday 1 results into `results.csv` |
| `fifa_2026_prediction_results.csv` | Full probability stats for all 48 teams |
| `fifa_2026_prediction_plot.png` | Winner probability bar chart |
| `FIFA2026_schedule_Fixtures.csv` | Confirmed teams for all 104 matches |
| `wc2026_squads.csv` | Compiled actual named squads for all 2026 WC nations |
| `eafc26_wc_team_summary.csv` | EA FC 26 squad ratings for all 48 WC nations |
| `results.csv` | Historical international match results + Matchday 1 scores |
| `fifa_mens_rank.csv` | Historical FIFA rankings (1993–2026) |
| `shootouts.csv` | Historical penalty shootout results |
| `former_names.csv` | Historical team name mapping database |
| `website/` | Interactive match predictor web app |

---

## 🚀 How to Run

1. **Activate the Environment**:
   ```powershell
   # Windows (PowerShell)
   .\myenv\Scripts\Activate.ps1
   ```

2. **Install Dependencies**:
   ```bash
   pip install pandas numpy matplotlib seaborn xgboost
   ```

3. **Execute the Pipeline**:
   ```bash
   python predict_world_cup.py
   ```
   Trains the model, runs 10,000 simulations, prints predictions, and outputs results CSV and probability chart.

4. **Interact via Notebook**:
   Open and run `predict_world_cup.ipynb` in any Jupyter environment.

5. **View the Website**:
   ```bash
   cd website && python -m http.server 8765
   ```

---

## 🛠️ Tech Stack

- **Language**: Python 3.11
- **Libraries**: `xgboost`, `numpy`, `pandas`, `matplotlib`, `seaborn`
- **Model**: XGBoost Poisson Regression + Dixon-Coles correction
- **Simulation**: Monte Carlo (10,000 iterations)
- **Data**: Kaggle international football results + EA FC 26 squad ratings + FIFA rankings
- **Website**: HTML / Vanilla CSS / JavaScript (no framework)
