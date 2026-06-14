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

**v3.0 — XGBoost + Dixon-Coles (latest)**
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

> Results from 10,000 Monte Carlo simulations — v3.0 model.

| Rank | Team | Group | FIFA Rank | R16 (%) | QF (%) | SF (%) | Final (%) | **Winner (%)** |
|------|------|-------|-----------|---------|--------|--------|-----------|----------------|
| 1 | 🏴󠁧󠁢󠁥󠁮󠁧󠁿 **England** | L | 4 | 61.96 | 40.49 | 25.38 | 15.62 | **9.32%** |
| 2 | 🇫🇷 **France** | I | 1 | 55.39 | 35.52 | 23.31 | 14.58 | **9.02%** |
| 3 | 🇦🇷 **Argentina** | J | 3 | 51.39 | 34.33 | 22.41 | 13.00 | **8.04%** |
| 4 | 🇪🇸 **Spain** | H | 2 | 52.29 | 34.03 | 21.66 | 12.43 | **7.24%** |
| 5 | 🇲🇦 **Morocco** | C | 8 | 52.99 | 33.51 | 19.18 | 11.99 | **6.56%** |
| 6 | 🇧🇷 **Brazil** | C | 6 | 51.67 | 31.83 | 18.93 | 10.51 | **5.73%** |
| 7 | 🇵🇹 **Portugal** | K | 5 | 50.94 | 29.17 | 15.27 | 8.02 | **4.12%** |
| 8 | 🇩🇪 **Germany** | E | 10 | 51.18 | 27.65 | 15.19 | 8.36 | **4.05%** |
| 9 | 🇧🇪 **Belgium** | G | 9 | 44.77 | 24.87 | 14.74 | 7.01 | **3.48%** |
| 10 | 🇺🇾 **Uruguay** | H | 17 | 45.36 | 26.90 | 15.45 | 7.38 | **3.46%** |
| 11 | 🇪🇨 **Ecuador** | E | 23 | 42.44 | 22.05 | 11.14 | 6.19 | **3.22%** |
| 12 | 🇳🇱 **Netherlands** | F | 7 | 42.16 | 23.83 | 12.01 | 6.40 | **3.11%** |
| 13 | 🇨🇴 **Colombia** | K | 13 | 43.47 | 23.15 | 12.61 | 6.20 | **3.01%** |
| 14 | 🇯🇵 **Japan** | F | 18 | 35.90 | 18.65 | 9.72 | 5.11 | **2.61%** |
| 15 | 🇺🇸 **United States** | D | 16 | 51.46 | 27.14 | 11.67 | 5.26 | **2.58%** |

Full results for all 48 teams: [`fifa_2026_prediction_results.csv`](./fifa_2026_prediction_results.csv)

---

## 🌐 Interactive Web Predictor

A companion website visualises **Win / Draw / Win probabilities** for every group stage match.

**Features:**
- 🏆 Predicted tournament winner spotlight (England, 9.32%)
- 📊 Top 10 contenders with animated probability bars
- ⚽ All 72 group stage matches across 12 group tabs (A–L)
- Match cards with team flags, venue, date, and tri-colour probability bars
- Fully responsive — dark navy design with gold accents

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
| `fifa_2026_prediction_results.csv` | Full probability stats for all 48 teams |
| `fifa_2026_prediction_plot.png` | Winner probability bar chart |
| `FIFA2026_schedule_Fixtures.csv` | **Updated** — confirmed teams for all 104 matches |
| `eafc26_wc_team_summary.csv` | EA FC 26 squad ratings for all 48 WC nations |
| `results.csv` | Historical international match results (1872–2026) |
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
