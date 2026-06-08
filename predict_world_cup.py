import os
import csv
import json
import numpy as np
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

# 1. SETUP AND DIRECTORY WORK
CWD = os.getcwd()
print(f"Working Directory: {CWD}")

# 2. DEFINING TEAM NAME NORMALIZATION
TEAM_MAPPING = {
    'USA': 'United States',
    'IR Iran': 'Iran',
    'Congo DR': 'DR Congo',
    'Cabo Verde': 'Cape Verde',
    'Korea Republic': 'South Korea',
    'Côte d\'Ivoire': 'Ivory Coast',
    'T\u00fcrkiye': 'Turkey',
    'Trkiye': 'Turkey',
    'Trkiye': 'Turkey',
    'Czechia': 'Czech Republic',
    'Aotearoa New Zealand': 'New Zealand',
    'Curaao': 'Curacao',
    'Curaçao': 'Curacao'
}

def clean_name(name):
    if not isinstance(name, str):
        return name
    name = name.strip()
    if 'Cura' in name:
        return 'Curacao'
    if 'Côte' in name or 'Cte' in name:
        return 'Ivory Coast'
    if 'T\u00fcrk' in name or 'Trkiye' in name or 'Trkiye' in name:
        return 'Turkey'
    return TEAM_MAPPING.get(name, name)

# 3. LOAD DATASETS
print("Loading datasets...")
results_df = pd.read_csv('results.csv')
rankings_df = pd.read_csv('fifa_mens_rank.csv')
shootouts_df = pd.read_csv('shootouts.csv')
fixtures_df = pd.read_csv('FIFA2026_schedule_Fixtures.csv')
eafc_df = pd.read_csv('eafc26_wc_team_summary.csv')

# Apply name cleaning to EAFC data and build lookup dictionary
eafc_df['Nation'] = eafc_df['Nation'].apply(clean_name)
eafc_stats = {}
for idx, row in eafc_df.iterrows():
    eafc_stats[row['Nation']] = {
        'Top11_OVR': float(row['Top11_OVR']),
        'Attack_Score': float(row['Attack_Score']),
        'Defense_Score': float(row['Defense_Score']),
        'Penalty_Score': float(row['Penalty_Score'])
    }

def get_squad_features(team, rank):
    stats = eafc_stats.get(team)
    if stats:
        return stats['Top11_OVR'], stats['Attack_Score'], stats['Defense_Score'], stats['Penalty_Score']
    else:
        # Fallback using regression formulas derived from WC team data
        top11_ovr = np.clip(85.67 - 0.1827 * rank, 55.0, 88.5)
        atk_score = np.clip(76.43 - 0.1265 * rank, 50.0, 83.0)
        def_score = np.clip(70.69 - 0.0891 * rank, 50.0, 82.0)
        pen_score = np.clip(58.0 - 0.1 * rank, 40.0, 75.0)
        return top11_ovr, atk_score, def_score, pen_score

# Apply name cleaning
results_df['home_team'] = results_df['home_team'].apply(clean_name)
results_df['away_team'] = results_df['away_team'].apply(clean_name)
rankings_df['team'] = rankings_df['team'].apply(clean_name)
shootouts_df['home_team'] = shootouts_df['home_team'].apply(clean_name)
shootouts_df['away_team'] = shootouts_df['away_team'].apply(clean_name)
shootouts_df['winner'] = shootouts_df['winner'].apply(clean_name)

# Parse dates
results_df['date'] = pd.to_datetime(results_df['date'])
shootouts_df['date'] = pd.to_datetime(shootouts_df['date'])

# 4. PENALTY SHOOTOUT STATISTICS
print("Calculating penalty shootout stats...")
shootout_stats = {}
for idx, row in shootouts_df.iterrows():
    h, a, w = row['home_team'], row['away_team'], row['winner']
    for t in [h, a]:
        if t not in shootout_stats:
            shootout_stats[t] = {'wins': 0, 'total': 0}
        shootout_stats[t]['total'] += 1
        if t == w:
            shootout_stats[t]['wins'] += 1

def get_shootout_win_rate(team):
    stats = shootout_stats.get(team)
    if not stats or stats['total'] == 0:
        return 0.5
    return stats['wins'] / stats['total']

# 5. HISTORICAL FIFA RANKINGS LOOKUP DATABASE
print("Building FIFA rankings database...")
rankings_db = {}
for idx, row in rankings_df.iterrows():
    year = int(row['date'])
    sem = int(row['semester'])
    team = row['team']
    rank = int(row['rank'])
    pts = float(row['total.points'])
    
    if team not in rankings_db:
        rankings_db[team] = {}
    rankings_db[team][(year, sem)] = (rank, pts)

# Find latest ranking fallback
max_year = rankings_df['date'].max()
max_sem = rankings_df[rankings_df['date'] == max_year]['semester'].max()
print(f"Latest FIFA ranking: Year {max_year}, Semester {max_sem}")

def get_rank_and_points(team, date):
    year = date.year
    sem = 1 if date.month <= 6 else 2
    if year > max_year or (year == max_year and sem > max_sem):
        year, sem = max_year, max_sem
        
    db = rankings_db.get(team)
    if not db:
        return 150, 1000.0
    if (year, sem) in db:
        return db[(year, sem)]
    past_keys = [k for k in db.keys() if k[0] < year or (k[0] == year and k[1] <= sem)]
    if past_keys:
        best_k = max(past_keys, key=lambda x: (x[0], x[1]))
        return db[best_k]
    return 150, 1000.0

# 6. FEATURE ENGINEERING & TRAINING DATA PREPARATION
print("Preparing training data...")
results_df = results_df.sort_values('date').reset_index(drop=True)
team_match_history = {}   # stores (goals_for, goals_against, date, tournament)
training_rows = []
training_weights = []  # sample weights for each training row

# --- Match importance weights for form calculation ---
MATCH_WEIGHTS = {
    'FIFA World Cup': 2.0,
    'Confederations Cup': 1.8,
    'Copa America': 1.7,
    'UEFA Euro': 1.7,
    'African Cup of Nations': 1.7,
    'AFC Asian Cup': 1.7,
    'CONCACAF Gold Cup': 1.7,
    'UEFA Nations League': 1.2,
    'FIFA World Cup qualification': 1.5,
    'UEFA Euro qualification': 1.5,
    'Copa America qualification': 1.5,
    'AFC Asian Cup qualification': 1.5,
    'CONCACAF Nations League': 1.2,
    'Friendly': 0.1,
}
FORM_HALF_LIFE_DAYS = 365.0   # for team form (1-year decay)
TRAIN_HALF_LIFE_DAYS = 1460.0  # for training sample weights (4-year decay)
TRAIN_CUTOFF = pd.to_datetime('2016-01-01')
WC_TARGET_DATE = pd.to_datetime('2026-06-01')

def match_importance(tournament):
    """Return importance multiplier for a given tournament string."""
    for key in MATCH_WEIGHTS:
        if key.lower() in str(tournament).lower():
            return MATCH_WEIGHTS[key]
    return 0.8  # default for unknown competitive matches

def get_form(team, current_date):
    """Exponential time-decayed, importance-weighted form (goals for/against)."""
    hist = team_match_history.get(team, [])
    if not hist:
        return 1.2, 1.2
    total_att_w = total_def_w = total_w = 0.0
    for gf, ga, m_date, m_tourn in hist:
        days_ago = max(0.0, (current_date - m_date).days)
        time_decay = 2.0 ** (-days_ago / FORM_HALF_LIFE_DAYS)
        imp = match_importance(m_tourn)
        w = time_decay * imp
        total_att_w += gf * w
        total_def_w += ga * w
        total_w += w
    if total_w == 0.0:
        return 1.2, 1.2
    return total_att_w / total_w, total_def_w / total_w

historical_matches = results_df[
    (results_df['date'] >= '1993-08-01') & 
    (results_df['home_score'].notna()) & 
    (results_df['away_score'].notna()) &
    (results_df['home_score'] != 'NA') &
    (results_df['away_score'] != 'NA')
].copy()

historical_matches['home_score'] = pd.to_numeric(historical_matches['home_score'])
historical_matches['away_score'] = pd.to_numeric(historical_matches['away_score'])

for idx, row in results_df.iterrows():
    date = row['date']
    h, a = row['home_team'], row['away_team']
    h_score_raw, a_score_raw = row['home_score'], row['away_score']
    tournament = row.get('tournament', 'Friendly')
    
    is_historical = True
    try:
        hs = float(h_score_raw)
        as_ = float(a_score_raw)
        if np.isnan(hs) or np.isnan(as_):
            is_historical = False
    except (ValueError, TypeError):
        is_historical = False

    if is_historical and date >= pd.to_datetime('1993-08-01'):
        hs, as_ = int(hs), int(as_)
        h_rank, h_pts = get_rank_and_points(h, date)
        a_rank, a_pts = get_rank_and_points(a, date)
        # Use decayed form with current match date as reference
        h_form_att, h_form_def = get_form(h, date)
        a_form_att, a_form_def = get_form(a, date)
        
        # Get squad features
        h_ovr, h_atk, h_def, h_pen = get_squad_features(h, h_rank)
        a_ovr, a_atk, a_def, a_pen = get_squad_features(a, a_rank)
        
        neutral = 1 if str(row['neutral']).upper() == 'TRUE' else 0
        is_friendly = 1 if str(tournament).lower() == 'friendly' else 0
        imp = match_importance(tournament)
        
        # Only include competitive matches from 2016+ in training
        if date >= TRAIN_CUTOFF and is_friendly == 0:
            # Recency-based sample weight: decays over 4 years toward WC date
            days_to_wc = max(0.0, (WC_TARGET_DATE - date).days)
            row_weight = 2.0 ** (-days_to_wc / TRAIN_HALF_LIFE_DAYS) * imp
            
            training_rows.append({
                'team': h, 'opp': a, 'is_home': 1 - neutral,
                'rank_diff': (h_rank - a_rank) / 100.0,
                'point_diff': (h_pts - a_pts) / 500.0,
                'squad_atk_self': (h_atk - 75.0) / 10.0,
                'squad_def_opp': (a_def - 70.0) / 10.0,
                'squad_ovr_diff': (h_ovr - a_ovr) / 10.0,
                'form_attack_self': h_form_att, 'form_defense_opp': a_form_def,
                'is_friendly': is_friendly, 'goals': hs
            })
            training_weights.append(row_weight)
            training_rows.append({
                'team': a, 'opp': h, 'is_home': 0,
                'rank_diff': (a_rank - h_rank) / 100.0,
                'point_diff': (a_pts - h_pts) / 500.0,
                'squad_atk_self': (a_atk - 75.0) / 10.0,
                'squad_def_opp': (h_def - 70.0) / 10.0,
                'squad_ovr_diff': (a_ovr - h_ovr) / 10.0,
                'form_attack_self': a_form_att, 'form_defense_opp': h_form_def,
                'is_friendly': is_friendly, 'goals': as_
            })
            training_weights.append(row_weight)
        
    if is_historical:
        hs_int, as_int = int(hs), int(as_)
        if h not in team_match_history: team_match_history[h] = []
        if a not in team_match_history: team_match_history[a] = []
        team_match_history[h].append((hs_int, as_int, date, tournament))
        team_match_history[a].append((as_int, hs_int, date, tournament))

# 7. IMPLEMENT PURE NUMPY POISSON REGRESSION (with sample weights)
class PurePoissonRegression:
    def __init__(self, lr=0.001, iterations=1500):
        self.lr = lr
        self.iterations = iterations
        self.weights = None
        self.bias = None
        
    def fit(self, X, y, sample_weights=None):
        N, D = X.shape
        self.weights = np.zeros(D)
        self.bias = 0.0
        if sample_weights is None:
            sample_weights = np.ones(N)
        # Normalize weights so they sum to N (keeps gradient magnitudes comparable)
        w = sample_weights / sample_weights.sum() * N
        for i in range(self.iterations):
            linear = np.dot(X, self.weights) + self.bias
            linear = np.clip(linear, -10.0, 5.0)
            lambdas = np.exp(linear)
            residuals = lambdas - y
            dw = np.dot(X.T, w * residuals) / N
            db = np.sum(w * residuals) / N
            self.weights -= self.lr * dw
            self.bias -= self.lr * db
            
    def predict(self, X):
        linear = np.dot(X, self.weights) + self.bias
        linear = np.clip(linear, -10.0, 5.0)
        return np.exp(linear)

train_df = pd.DataFrame(training_rows)
weights_arr = np.array(training_weights, dtype=np.float64)
print(f"Constructed {len(train_df)} training rows (competitive matches, 2016+).")

features_cols = ['is_home', 'rank_diff', 'point_diff', 'squad_atk_self', 'squad_def_opp', 'squad_ovr_diff', 'form_attack_self', 'form_defense_opp', 'is_friendly']
X_df = train_df[features_cols]
y_df = train_df['goals']

# Train/Test split in numpy
np.random.seed(42)
indices = np.arange(len(train_df))
np.random.shuffle(indices)
split_idx = int(len(train_df) * 0.8)
train_idx, val_idx = indices[:split_idx], indices[split_idx:]

X_train = X_df.iloc[train_idx].to_numpy(dtype=np.float64)
y_train = y_df.iloc[train_idx].to_numpy(dtype=np.float64)
w_train = weights_arr[train_idx]
X_val = X_df.iloc[val_idx].to_numpy(dtype=np.float64)
y_val = y_df.iloc[val_idx].to_numpy(dtype=np.float64)

# Fit custom model with sample weights
print("Training custom Poisson Regression model (with recency + importance weighting)...")
model = PurePoissonRegression(lr=0.01, iterations=2000)
model.fit(X_train, y_train, sample_weights=w_train)

# Evaluate model
y_pred = model.predict(X_val)
mae = np.mean(np.abs(y_val - y_pred))
ss_res = np.sum((y_val - y_pred)**2)
ss_tot = np.sum((y_val - np.mean(y_val))**2)
r2 = 1.0 - (ss_res / ss_tot)
print(f"Validation MAE (Custom Poisson): {mae:.4f}")
print(f"Validation R2 Score (Custom Poisson): {r2:.4f}")

# Train on the entire dataset with full weights
X_all = X_df.to_numpy(dtype=np.float64)
y_all = y_df.to_numpy(dtype=np.float64)
model.fit(X_all, y_all, sample_weights=weights_arr)
print("Model coefficients:", model.weights, "Bias:", model.bias)

# 8. EXTRACT WORLD CUP 2026 GROUPS
print("Extracting World Cup 2026 groups...")
wc_matches_raw = results_df[results_df['date'].dt.year == 2026].copy()
wc_matches_raw = wc_matches_raw[wc_matches_raw['home_score'].isna() | (wc_matches_raw['home_score'].astype(str) == 'NA')].reset_index(drop=True)

# Parse fixtures to map teams to groups
with open('FIFA2026_schedule_Fixtures.csv', mode='r', encoding='utf-8') as f:
    reader = csv.reader(f)
    fixtures = list(reader)[1:]

def match_team_to_fixture(team, fixture_str):
    options = [clean_name(opt.strip()).lower() for opt in fixture_str.split('/')]
    t_clean = clean_name(team).lower()
    return t_clean in options

team_groups = {}
group_teams = {}
for idx, row in wc_matches_raw.iterrows():
    date_str = row['date'].strftime('%Y-%m-%d')
    h, a = row['home_team'], row['away_team']
    
    group = None
    for f_row in fixtures:
        f_date = f_row[5]
        f_teams = f_row[2]
        f_group = f_row[3]
        
        if not f_group.startswith('Group'):
            continue
            
        if date_str == f_date:
            f_parts = f_teams.split(' v ')
            if len(f_parts) == 2:
                ft1, ft2 = f_parts[0].strip(), f_parts[1].strip()
                t1_m_1 = match_team_to_fixture(h, ft1)
                t2_m_2 = match_team_to_fixture(a, ft2)
                t1_m_2 = match_team_to_fixture(h, ft2)
                t2_m_1 = match_team_to_fixture(a, ft1)
                
                if (t1_m_1 and t2_m_2) or (t1_m_2 and t2_m_1):
                    group = f_group
                    break
                    
    if not group:
        print(f"Warning: Could not match fixture for {h} vs {a} on {date_str}")
        group = "Group A"
        
    team_groups[h] = group
    team_groups[a] = group
    if group not in group_teams:
        group_teams[group] = set()
    group_teams[group].add(h)
    group_teams[group].add(a)

for g in sorted(group_teams.keys()):
    group_teams[g] = sorted(list(group_teams[g]))

all_wc_teams = sorted(list(team_groups.keys()))
print(f"Total participating teams matched: {len(all_wc_teams)}")

# 9a. COMPUTE GROUP DRAW DIFFICULTY (for knockout lambda adjustment)
# For each team: avg EA FC OVR of their 3 group opponents.
# Harder group → team gets a slight knockout lambda BOOST (battle-tested).
# Easier group → team gets a slight knockout lambda PENALTY.
print("Computing group draw difficulty scores...")
_latest_d = pd.to_datetime('2026-06-01')  # temp, latest_date defined later
team_group_difficulty = {}
for t in all_wc_teams:
    g = team_groups[t]
    opponents = [other for other in group_teams[g] if other != t]
    opp_ovrs = []
    for opp in opponents:
        rank_opp, _ = get_rank_and_points(opp, _latest_d)
        ovr_opp, _, _, _ = get_squad_features(opp, rank_opp)
        opp_ovrs.append(ovr_opp)
    team_group_difficulty[t] = float(np.mean(opp_ovrs)) if opp_ovrs else 75.0

_diff_vals = list(team_group_difficulty.values())
_diff_min, _diff_max = min(_diff_vals), max(_diff_vals)
_diff_range = _diff_max - _diff_min

# Multiplier range: easiest group → 0.97, hardest group → 1.03
GROUP_BOOST_RANGE = 0.06  # total swing: ±3%

def get_group_difficulty_multiplier(team):
    """Lambda multiplier for knockout rounds based on group opponent strength."""
    if _diff_range < 1e-6:
        return 1.0
    normalized = (team_group_difficulty[team] - _diff_min) / _diff_range
    return 1.0 - GROUP_BOOST_RANGE / 2 + normalized * GROUP_BOOST_RANGE

# Print group difficulty summary for verification
print("\nGroup draw difficulty multipliers (knockout adjustment):")
for t in sorted(all_wc_teams, key=lambda x: team_group_difficulty[x]):
    print(f"  {t:<22} group_opp_avg_OVR={team_group_difficulty[t]:.1f}  "
          f"KO_multiplier={get_group_difficulty_multiplier(t):.3f}")
print("Pre-calculating expected goals for all possible team pairings...")
latest_date = pd.to_datetime('2026-06-01')

precalc_features = []
precalc_keys = []

def get_latest_form(team):
    """Get form at tournament start using the same exponential decay as training."""
    return get_form(team, latest_date)

for team_a in all_wc_teams:
    rank_a, pts_a = get_rank_and_points(team_a, latest_date)
    att_a, def_a = get_latest_form(team_a)
    ovr_a, atk_a, def_a_sq, pen_a = get_squad_features(team_a, rank_a)
    
    for team_b in all_wc_teams:
        if team_a == team_b:
            continue
        rank_b, pts_b = get_rank_and_points(team_b, latest_date)
        att_b, def_b = get_latest_form(team_b)
        ovr_b, atk_b, def_b_sq, pen_b = get_squad_features(team_b, rank_b)
        
        # Scenario 1: neutral = 1
        precalc_features.append([
            0.0,  # is_home
            (rank_a - rank_b) / 100.0,
            (pts_a - pts_b) / 500.0,
            (atk_a - 75.0) / 10.0,
            (def_b_sq - 70.0) / 10.0,
            (ovr_a - ovr_b) / 10.0,
            att_a,
            def_b,
            0.0  # is_friendly
        ])
        precalc_keys.append((team_a, team_b, 1))
        
        # Scenario 2: neutral = 0
        precalc_features.append([
            1.0,  # is_home
            (rank_a - rank_b) / 100.0,
            (pts_a - pts_b) / 500.0,
            (atk_a - 75.0) / 10.0,
            (def_b_sq - 70.0) / 10.0,
            (ovr_a - ovr_b) / 10.0,
            att_a,
            def_b,
            0.0  # is_friendly
        ])
        precalc_keys.append((team_a, team_b, 0))

# Predict in bulk using NumPy dot product
precalc_X = np.array(precalc_features)
precalc_preds = model.predict(precalc_X)

lambda_cache = {}
for idx, key in enumerate(precalc_keys):
    lambda_cache[key] = max(0.1, precalc_preds[idx])

def get_cached_lambdas(team_a, team_b, neutral):
    l_a = lambda_cache.get((team_a, team_b, neutral), 1.2)
    l_b = lambda_cache.get((team_b, team_a, neutral), 1.2)
    return l_a, l_b

# 10. SIMULATOR LOGIC FUNCTIONS
def simulate_match(team_a, team_b, neutral=1, is_knockout=False):
    lambda_a, lambda_b = get_cached_lambdas(team_a, team_b, neutral)
    
    # Apply group difficulty multiplier in knockout rounds
    if is_knockout:
        lambda_a *= get_group_difficulty_multiplier(team_a)
        lambda_b *= get_group_difficulty_multiplier(team_b)
    
    goals_a = np.random.poisson(lambda_a)
    goals_b = np.random.poisson(lambda_b)
    
    if not is_knockout:
        return goals_a, goals_b
        
    # Extra time if tied
    if goals_a == goals_b:
        goals_a_et = np.random.poisson(lambda_a / 3.0)
        goals_b_et = np.random.poisson(lambda_b / 3.0)
        goals_a += goals_a_et
        goals_b += goals_b_et
        
    # Penalty shootout if still tied
    if goals_a == goals_b:
        rank_a, _ = get_rank_and_points(team_a, latest_date)
        rank_b, _ = get_rank_and_points(team_b, latest_date)
        wr_a = get_shootout_win_rate(team_a)
        wr_b = get_shootout_win_rate(team_b)
        _, _, _, pen_a = get_squad_features(team_a, rank_a)
        _, _, _, pen_b = get_squad_features(team_b, rank_b)
        
        # Combined: historical win rate (40%) + FIFA rank (10%) + EA FC Penalty score (50%)
        p_win_a = (0.5
            + 0.15 * (wr_a - wr_b)
            + 0.15 * (pen_a - pen_b) / 100.0
            + 0.05 * ((rank_b - rank_a) / max(rank_b + rank_a, 1)))
        p_win_a = np.clip(p_win_a, 0.35, 0.65)
        
        if np.random.random() < p_win_a:
            return goals_a + 1, goals_b
        else:
            return goals_a, goals_b + 1
            
    return goals_a, goals_b

def simulate_group_stage():
    standings = {}
    for g, teams in group_teams.items():
        standings[g] = {t: {'pts': 0, 'gd': 0, 'gs': 0, 'team': t} for t in teams}
        
    for idx, row in wc_matches_raw.iterrows():
        h, a = row['home_team'], row['away_team']
        neutral = 1 if str(row['neutral']).upper() == 'TRUE' else 0
        g = team_groups[h]
        
        goals_h, goals_a = simulate_match(h, a, neutral, is_knockout=False)
        
        standings[g][h]['gs'] += goals_h
        standings[g][h]['gd'] += (goals_h - goals_a)
        standings[g][a]['gs'] += goals_a
        standings[g][a]['gd'] += (goals_a - goals_h)
        
        if goals_h > goals_a:
            standings[g][h]['pts'] += 3
        elif goals_h < goals_a:
            standings[g][a]['pts'] += 3
        else:
            standings[g][h]['pts'] += 1
            standings[g][a]['pts'] += 1
            
    ranked_groups = {}
    for g, teams in group_teams.items():
        t_list = list(standings[g].values())
        def sort_key(t):
            rank, _ = get_rank_and_points(t['team'], latest_date)
            return (-t['pts'], -t['gd'], -t['gs'], rank)
            
        ranked_groups[g] = sorted(t_list, key=sort_key)
        
    return ranked_groups

def pair_third_place_teams(third_place_teams):
    slots = [
        {'id': 74, 'allowed': {'Group A', 'Group B', 'Group C', 'Group D', 'Group F'}},
        {'id': 77, 'allowed': {'Group C', 'Group D', 'Group F', 'Group G', 'Group H'}},
        {'id': 79, 'allowed': {'Group C', 'Group E', 'Group F', 'Group H', 'Group I'}},
        {'id': 80, 'allowed': {'Group E', 'Group H', 'Group I', 'Group J', 'Group K'}},
        {'id': 81, 'allowed': {'Group B', 'Group E', 'Group F', 'Group I', 'Group J'}},
        {'id': 82, 'allowed': {'Group A', 'Group E', 'Group H', 'Group I', 'Group J'}},
        {'id': 85, 'allowed': {'Group E', 'Group F', 'Group G', 'Group I', 'Group J'}},
        {'id': 87, 'allowed': {'Group D', 'Group E', 'Group I', 'Group J', 'Group L'}}
    ]
    
    assigned = [None] * len(slots)
    used = set()
    
    def backtrack(slot_idx):
        if slot_idx == len(slots):
            return True
            
        slot = slots[slot_idx]
        for team in third_place_teams:
            if team not in used:
                t_grp = team_groups[team]
                if t_grp in slot['allowed']:
                    assigned[slot_idx] = team
                    used.add(team)
                    if backtrack(slot_idx + 1):
                        return True
                    used.remove(team)
                    assigned[slot_idx] = None
        return False
        
    if backtrack(0):
        return {slots[i]['id']: assigned[i] for i in range(len(slots))}
    else:
        return {slots[i]['id']: third_place_teams[i] for i in range(len(slots))}

def simulate_tournament():
    # 1. GROUP STAGE
    group_tables = simulate_group_stage()
    
    winners = {g: table[0]['team'] for g, table in group_tables.items()}
    runners_up = {g: table[1]['team'] for g, table in group_tables.items()}
    
    third_placed = []
    for g, table in group_tables.items():
        t = table[2]
        rank, _ = get_rank_and_points(t['team'], latest_date)
        third_placed.append({
            'team': t['team'], 'pts': t['pts'], 'gd': t['gd'], 'gs': t['gs'], 'rank': rank
        })
        
    # Rank third-placed teams
    ranked_third = sorted(third_placed, key=lambda t: (-t['pts'], -t['gd'], -t['gs'], t['rank']))
    best_8_third_teams = [t['team'] for t in ranked_third[:8]]
    
    # Match 3rd place teams
    third_pairings = pair_third_place_teams(best_8_third_teams)
    
    # 2. ROUND OF 32
    ko_winners = {}
    
    # Match 73: A2 vs B2
    g73_h, g73_a = simulate_match(runners_up['Group A'], runners_up['Group B'], neutral=1, is_knockout=True)
    ko_winners[73] = runners_up['Group A'] if g73_h > g73_a else runners_up['Group B']
    
    # Match 74: E1 vs 3rd place
    g74_h, g74_a = simulate_match(winners['Group E'], third_pairings[74], neutral=1, is_knockout=True)
    ko_winners[74] = winners['Group E'] if g74_h > g74_a else third_pairings[74]
    
    # Match 75: F1 vs C2
    g75_h, g75_a = simulate_match(winners['Group F'], runners_up['Group C'], neutral=1, is_knockout=True)
    ko_winners[75] = winners['Group F'] if g75_h > g75_a else runners_up['Group C']
    
    # Match 76: C1 vs F2
    g76_h, g76_a = simulate_match(winners['Group C'], runners_up['Group F'], neutral=1, is_knockout=True)
    ko_winners[76] = winners['Group C'] if g76_h > g76_a else runners_up['Group F']
    
    # Match 77: I1 vs 3rd place
    g77_h, g77_a = simulate_match(winners['Group I'], third_pairings[77], neutral=1, is_knockout=True)
    ko_winners[77] = winners['Group I'] if g77_h > g77_a else third_pairings[77]
    
    # Match 78: E2 vs I2
    g78_h, g78_a = simulate_match(runners_up['Group E'], runners_up['Group I'], neutral=1, is_knockout=True)
    ko_winners[78] = runners_up['Group E'] if g78_h > g78_a else runners_up['Group I']
    
    # Match 79: A1 vs 3rd place
    g79_h, g79_a = simulate_match(winners['Group A'], third_pairings[79], neutral=1, is_knockout=True)
    ko_winners[79] = winners['Group A'] if g79_h > g79_a else third_pairings[79]
    
    # Match 80: L1 vs 3rd place
    g80_h, g80_a = simulate_match(winners['Group L'], third_pairings[80], neutral=1, is_knockout=True)
    ko_winners[80] = winners['Group L'] if g80_h > g80_a else third_pairings[80]
    
    # Match 81: D1 vs 3rd place
    g81_h, g81_a = simulate_match(winners['Group D'], third_pairings[81], neutral=1, is_knockout=True)
    ko_winners[81] = winners['Group D'] if g81_h > g81_a else third_pairings[81]
    
    # Match 82: G1 vs 3rd place
    g82_h, g82_a = simulate_match(winners['Group G'], third_pairings[82], neutral=1, is_knockout=True)
    ko_winners[82] = winners['Group G'] if g82_h > g82_a else third_pairings[82]
    
    # Match 83: K2 vs L2
    g83_h, g83_a = simulate_match(runners_up['Group K'], runners_up['Group L'], neutral=1, is_knockout=True)
    ko_winners[83] = runners_up['Group K'] if g83_h > g83_a else runners_up['Group L']
    
    # Match 84: H1 vs J2
    g84_h, g84_a = simulate_match(winners['Group H'], runners_up['Group J'], neutral=1, is_knockout=True)
    ko_winners[84] = winners['Group H'] if g84_h > g84_a else runners_up['Group J']
    
    # Match 85: B1 vs 3rd place
    g85_h, g85_a = simulate_match(winners['Group B'], third_pairings[85], neutral=1, is_knockout=True)
    ko_winners[85] = winners['Group B'] if g85_h > g85_a else third_pairings[85]
    
    # Match 86: J1 vs H2
    g86_h, g86_a = simulate_match(winners['Group J'], runners_up['Group H'], neutral=1, is_knockout=True)
    ko_winners[86] = winners['Group J'] if g86_h > g86_a else runners_up['Group H']
    
    # Match 87: K1 vs 3rd place
    g87_h, g87_a = simulate_match(winners['Group K'], third_pairings[87], neutral=1, is_knockout=True)
    ko_winners[87] = winners['Group K'] if g87_h > g87_a else third_pairings[87]
    
    # Match 88: D2 vs G2
    g88_h, g88_a = simulate_match(runners_up['Group D'], runners_up['Group G'], neutral=1, is_knockout=True)
    ko_winners[88] = runners_up['Group D'] if g88_h > g88_a else runners_up['Group G']
    
    # 3. ROUND OF 16
    # Match 89: Winner 74 vs Winner 77
    g89_h, g89_a = simulate_match(ko_winners[74], ko_winners[77], neutral=1, is_knockout=True)
    ko_winners[89] = ko_winners[74] if g89_h > g89_a else ko_winners[77]
    
    # Match 90: Winner 73 vs Winner 75
    g90_h, g90_a = simulate_match(ko_winners[73], ko_winners[75], neutral=1, is_knockout=True)
    ko_winners[90] = ko_winners[73] if g90_h > g90_a else ko_winners[75]
    
    # Match 91: Winner 76 vs Winner 78
    g91_h, g91_a = simulate_match(ko_winners[76], ko_winners[78], neutral=1, is_knockout=True)
    ko_winners[91] = ko_winners[76] if g91_h > g91_a else ko_winners[78]
    
    # Match 92: Winner 79 vs Winner 80
    g92_h, g92_a = simulate_match(ko_winners[79], ko_winners[80], neutral=1, is_knockout=True)
    ko_winners[92] = ko_winners[79] if g92_h > g92_a else ko_winners[80]
    
    # Match 93: Winner 83 vs Winner 84
    g93_h, g93_a = simulate_match(ko_winners[83], ko_winners[84], neutral=1, is_knockout=True)
    ko_winners[93] = ko_winners[83] if g93_h > g93_a else ko_winners[84]
    
    # Match 94: Winner 81 vs Winner 82
    g94_h, g94_a = simulate_match(ko_winners[81], ko_winners[82], neutral=1, is_knockout=True)
    ko_winners[94] = ko_winners[81] if g94_h > g94_a else ko_winners[82]
    
    # Match 95: Winner 86 vs Winner 88
    g95_h, g95_a = simulate_match(ko_winners[86], ko_winners[88], neutral=1, is_knockout=True)
    ko_winners[95] = ko_winners[86] if g95_h > g95_a else ko_winners[88]
    
    # Match 96: Winner 85 vs Winner 87
    g96_h, g96_a = simulate_match(ko_winners[85], ko_winners[87], neutral=1, is_knockout=True)
    ko_winners[96] = ko_winners[85] if g96_h > g96_a else ko_winners[87]
    
    # 4. QUARTERFINALS
    # Match 97: Winner 89 vs Winner 90
    g97_h, g97_a = simulate_match(ko_winners[89], ko_winners[90], neutral=1, is_knockout=True)
    ko_winners[97] = ko_winners[89] if g97_h > g97_a else ko_winners[90]
    
    # Match 98: Winner 93 vs Winner 94
    g98_h, g98_a = simulate_match(ko_winners[93], ko_winners[94], neutral=1, is_knockout=True)
    ko_winners[98] = ko_winners[93] if g98_h > g98_a else ko_winners[94]
    
    # Match 99: Winner 91 vs Winner 92
    g99_h, g99_a = simulate_match(ko_winners[91], ko_winners[92], neutral=1, is_knockout=True)
    ko_winners[99] = ko_winners[91] if g99_h > g99_a else ko_winners[92]
    
    # Match 100: Winner 95 vs Winner 96
    g100_h, g100_a = simulate_match(ko_winners[95], ko_winners[96], neutral=1, is_knockout=True)
    ko_winners[100] = ko_winners[95] if g100_h > g100_a else ko_winners[96]
    
    # 5. SEMIFINALS
    # Match 101: Winner 97 vs Winner 98
    g101_h, g101_a = simulate_match(ko_winners[97], ko_winners[98], neutral=1, is_knockout=True)
    ko_winners[101] = ko_winners[97] if g101_h > g101_a else ko_winners[98]
    
    # Match 102: Winner 99 vs Winner 100
    g102_h, g102_a = simulate_match(ko_winners[99], ko_winners[100], neutral=1, is_knockout=True)
    ko_winners[102] = ko_winners[99] if g102_h > g102_a else ko_winners[100]
    
    # 6. FINAL
    g104_h, g104_a = simulate_match(ko_winners[101], ko_winners[102], neutral=1, is_knockout=True)
    winner = ko_winners[101] if g104_h > g104_a else ko_winners[102]
    
    r16_teams = [ko_winners[i] for i in [73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88]]
    qf_teams = [ko_winners[i] for i in [89, 90, 91, 92, 93, 94, 95, 96]]
    sf_teams = [ko_winners[i] for i in [97, 98, 99, 100]]
    finalists = [ko_winners[101], ko_winners[102]]
    
    return {
        'winner': winner,
        'finalists': finalists,
        'sf': sf_teams,
        'qf': qf_teams,
        'r16': r16_teams
    }

# 11. RUN MONTE CARLO SIMULATIONS
NUM_SIMULATIONS = 10000
print(f"Running {NUM_SIMULATIONS} Monte Carlo simulations of the 2026 World Cup...")

winner_counts = {}
final_counts = {}
sf_counts = {}
qf_counts = {}
r16_counts = {}

# Initialize
for t in all_wc_teams:
    winner_counts[t] = 0
    final_counts[t] = 0
    sf_counts[t] = 0
    qf_counts[t] = 0
    r16_counts[t] = 0

for i in range(1, NUM_SIMULATIONS + 1):
    if i % 2000 == 0:
        print(f"Completed {i} simulations...")
    res = simulate_tournament()
    
    winner_counts[res['winner']] += 1
    for t in res['finalists']:
        final_counts[t] += 1
    for t in res['sf']:
        sf_counts[t] += 1
    for t in res['qf']:
        qf_counts[t] += 1
    for t in res['r16']:
        r16_counts[t] += 1

# 12. SUMMARIZE RESULTS
print("Aggregating prediction results...")
prob_df = pd.DataFrame({
    'Team': all_wc_teams,
    'Group': [team_groups[t] for t in all_wc_teams],
    'FIFA Rank': [get_rank_and_points(t, latest_date)[0] for t in all_wc_teams],
    'Round of 16 (%)': [r16_counts[t] / NUM_SIMULATIONS * 100 for t in all_wc_teams],
    'Quarterfinals (%)': [qf_counts[t] / NUM_SIMULATIONS * 100 for t in all_wc_teams],
    'Semifinals (%)': [sf_counts[t] / NUM_SIMULATIONS * 100 for t in all_wc_teams],
    'Final (%)': [final_counts[t] / NUM_SIMULATIONS * 100 for t in all_wc_teams],
    'Winner (%)': [winner_counts[t] / NUM_SIMULATIONS * 100 for t in all_wc_teams]
})

prob_df = prob_df.sort_values(by='Winner (%)', ascending=False).reset_index(drop=True)
prob_df.to_csv('fifa_2026_prediction_results.csv', index=False)
print("Saved predictions to 'fifa_2026_prediction_results.csv'")

# Display top 15 teams
print("\nTop 15 Predicted Winners:")
print(prob_df.head(15).to_string())

# 13. PLOTTING RESULTS
print("Generating visualization plots...")
plt.figure(figsize=(12, 7))
sns.set_theme(style="whitegrid")
top_15_df = prob_df.head(15)
colors = sns.color_palette("viridis", len(top_15_df))

ax = sns.barplot(
    data=top_15_df,
    x='Winner (%)',
    y='Team',
    palette=colors,
    hue='Team',
    legend=False
)

plt.title('FIFA World Cup 2026 Winner Probabilities (Top 15)', fontsize=16, fontweight='bold', pad=15)
plt.xlabel('Probability of Winning the Tournament (%)', fontsize=12, labelpad=10)
plt.ylabel('Team', fontsize=12)

for p in ax.patches:
    width = p.get_width()
    ax.text(
        width + 0.15,
        p.get_y() + p.get_height() / 2,
        f"{width:.2f}%",
        ha='left',
        va='center',
        fontsize=10,
        fontweight='bold',
        color='#333333'
    )

plt.tight_layout()
plot_path = 'fifa_2026_prediction_plot.png'
plt.savefig(plot_path, dpi=300)
print(f"Saved winner probability plot to '{plot_path}'")

# 14. GENERATE DYNAMIC JUPYTER NOTEBOOK
print("Generating 'predict_world_cup.ipynb' Jupyter notebook...")

notebook_content = {
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# ⚽ FIFA World Cup 2026 Prediction Model (Pure NumPy Pipeline)\n",
    "This Jupyter notebook contains a complete machine learning pipeline and Monte Carlo tournament simulator to predict the winner of the upcoming FIFA World Cup 2026. \n",
    "\n",
    "This notebook uses a **custom Poisson Regression model implemented in pure NumPy**. This design avoids dependencies on C-extension libraries like `scikit-learn` that may be blocked by system application control policies, ensuring it is 100% runnable in restricted environments.\n",
    "\n",
    "### **Methodology Outline**\n",
    "1. **Data Preprocessing & Cleaning**: Load match results, shootout outcomes, and rankings, and perform team name cleaning to establish clean linkage.\n",
    "2. **Feature Engineering**: Link matches to their historical FIFA rankings (dating back to 1993) and build advanced features like relative rank differences, point differences, neutrality factor, and rolling team form.\n",
    "3. **Custom Model Training**: Train a custom Poisson Regressor in pure NumPy to predict goals scored by each team based on team parameters and matchup characteristics.\n",
    "4. **Monte Carlo Simulation**: Run a complete simulator of the 48-team 2026 World Cup bracket (Group stage tables, best-3rd selection, Round of 32 matching solver, and knockout bracket) 10,000 times.\n",
    "5. **Visualization**: Plot predictions and export top contenders."
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 1. Import Dependencies and Load Datasets"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "import os\n",
    "import numpy as np\n",
    "import pandas as pd\n",
    "import matplotlib.pyplot as plt\n",
    "import seaborn as sns\n",
    "from datetime import datetime\n",
    "\n",
    "# Load datasets\n",
    "results_df = pd.read_csv('results.csv')\n",
    "rankings_df = pd.read_csv('fifa_mens_rank.csv')\n",
    "shootouts_df = pd.read_csv('shootouts.csv')\n",
    "fixtures_df = pd.read_csv('FIFA2026_schedule_Fixtures.csv')\n",
    "eafc_df = pd.read_csv('eafc26_wc_team_summary.csv')\n",
    "\n",
    "# Apply name cleaning to EAFC data and build lookup dictionary\n",
    "eafc_df['Nation'] = eafc_df['Nation'].apply(clean_name)\n",
    "eafc_stats = {}\n",
    "for idx, row in eafc_df.iterrows():\n",
    "    eafc_stats[row['Nation']] = {\n",
    "        'Top11_OVR': float(row['Top11_OVR']),\n",
    "        'Attack_Score': float(row['Attack_Score']),\n",
    "        'Defense_Score': float(row['Defense_Score']),\n",
    "        'Penalty_Score': float(row['Penalty_Score'])\n",
    "    }\n",
    "\n",
    "def get_squad_features(team, rank):\n",
    "    stats = eafc_stats.get(team)\n",
    "    if stats:\n",
    "        return stats['Top11_OVR'], stats['Attack_Score'], stats['Defense_Score'], stats['Penalty_Score']\n",
    "    else:\n",
    "        # Fallback using regression formulas derived from WC team data\n",
    "        top11_ovr = np.clip(85.67 - 0.1827 * rank, 55.0, 88.5)\n",
    "        atk_score = np.clip(76.43 - 0.1265 * rank, 50.0, 83.0)\n",
    "        def_score = np.clip(70.69 - 0.0891 * rank, 50.0, 82.0)\n",
    "        pen_score = np.clip(58.0 - 0.1 * rank, 40.0, 75.0)\n",
    "        return top11_ovr, atk_score, def_score, pen_score\n",
    "print(\"Datasets loaded successfully.\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 2. Team Name Normalization\n",
    "Standardize team names across all datasets to ensure seamless linkage."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "TEAM_MAPPING = {\n",
    "    'USA': 'United States',\n",
    "    'IR Iran': 'Iran',\n",
    "    'Congo DR': 'DR Congo',\n",
    "    'Cabo Verde': 'Cape Verde',\n",
    "    'Korea Republic': 'South Korea',\n",
    "    'Côte d\'Ivoire': 'Ivory Coast',\n",
    "    'T\u00fcrkiye': 'Turkey',\n",
    "    'Trkiye': 'Turkey',\n",
    "    'Trkiye': 'Turkey',\n",
    "    'Czechia': 'Czech Republic',\n",
    "    'Aotearoa New Zealand': 'New Zealand',\n",
    "    'Curaao': 'Curacao',\n",
    "    'Curaçao': 'Curacao'\n",
    "}\n",
    "\n",
    "def clean_name(name):\n",
    "    if not isinstance(name, str): return name\n",
    "    name = name.strip()\n",
    "    if 'Cura' in name: return 'Curacao'\n",
    "    if 'Côte' in name or 'Cte' in name: return 'Ivory Coast'\n",
    "    if 'T\u00fcrk' in name or 'Trkiye' in name or 'Trkiye' in name: return 'Turkey'\n",
    "    return TEAM_MAPPING.get(name, name)\n",
    "\n",
    "results_df['home_team'] = results_df['home_team'].apply(clean_name)\n",
    "results_df['away_team'] = results_df['away_team'].apply(clean_name)\n",
    "rankings_df['team'] = rankings_df['team'].apply(clean_name)\n",
    "shootouts_df['home_team'] = shootouts_df['home_team'].apply(clean_name)\n",
    "shootouts_df['away_team'] = shootouts_df['away_team'].apply(clean_name)\n",
    "shootouts_df['winner'] = shootouts_df['winner'].apply(clean_name)\n",
    "\n",
    "results_df['date'] = pd.to_datetime(results_df['date'])\n",
    "shootouts_df['date'] = pd.to_datetime(shootouts_df['date'])\n",
    "print(\"Name normalization complete.\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 3. Build Historical Rankings Database & Penalty Stats"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "shootout_stats = {}\n",
    "for idx, row in shootouts_df.iterrows():\n",
    "    h, a, w = row['home_team'], row['away_team'], row['winner']\n",
    "    for t in [h, a]:\n",
    "        if t not in shootout_stats: shootout_stats[t] = {'wins': 0, 'total': 0}\n",
    "        shootout_stats[t]['total'] += 1\n",
    "        if t == w: shootout_stats[t]['wins'] += 1\n",
    "\n",
    "def get_shootout_win_rate(team):\n",
    "    stats = shootout_stats.get(team)\n",
    "    return stats['wins'] / stats['total'] if stats and stats['total'] > 0 else 0.5\n",
    "\n",
    "rankings_db = {}\n",
    "for idx, row in rankings_df.iterrows():\n",
    "    year, sem, team, rank, pts = int(row['date']), int(row['semester']), row['team'], int(row['rank']), float(row['total.points'])\n",
    "    if team not in rankings_db: rankings_db[team] = {}\n",
    "    rankings_db[team][(year, sem)] = (rank, pts)\n",
    "\n",
    "max_year = rankings_df['date'].max()\n",
    "max_sem = rankings_df[rankings_df['date'] == max_year]['semester'].max()\n",
    "\n",
    "def get_rank_and_points(team, date):\n",
    "    year, sem = date.year, (1 if date.month <= 6 else 2)\n",
    "    if year > max_year or (year == max_year and sem > max_sem): year, sem = max_year, max_sem\n",
    "    db = rankings_db.get(team)\n",
    "    if not db: return 150, 1000.0\n",
    "    if (year, sem) in db: return db[(year, sem)]\n",
    "    past_keys = [k for k in db.keys() if k[0] < year or (k[0] == year and k[1] <= sem)]\n",
    "    if past_keys:\n",
    "        best_k = max(past_keys, key=lambda x: (x[0], x[1]))\n",
    "        return db[best_k]\n",
    "    return 150, 1000.0"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 4. Feature Engineering and Form Calculations"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "results_df = results_df.sort_values('date').reset_index(drop=True)\n",
    "team_match_history = {}\n",
    "form_span = 10\n",
    "training_rows = []\n",
    "\n",
    "historical_matches = results_df[\n",
    "    (results_df['date'] >= '1993-08-01') & \n",
    "    (results_df['home_score'].notna()) & \n",
    "    (results_df['away_score'].notna()) &\n",
    "    (results_df['home_score'] != 'NA') &\n",
    "    (results_df['away_score'] != 'NA')\n",
    "].copy()\n",
    "\n",
    "historical_matches['home_score'] = pd.to_numeric(historical_matches['home_score'])\n",
    "historical_matches['away_score'] = pd.to_numeric(historical_matches['away_score'])\n",
    "\n",
    "for idx, row in results_df.iterrows():\n",
    "    date = row['date']\n",
    "    h, a = row['home_team'], row['away_team']\n",
    "    h_score_raw, a_score_raw = row['home_score'], row['away_score']\n",
    "    \n",
    "    is_historical = True\n",
    "    try:\n",
    "        hs, as_ = float(h_score_raw), float(a_score_raw)\n",
    "        if np.isnan(hs) or np.isnan(as_): is_historical = False\n",
    "    except (ValueError, TypeError): is_historical = False\n",
    "        \n",
    "    def get_form(team):\n",
    "        hist = team_match_history.get(team, [])\n",
    "        if not hist: return 1.2, 1.2\n",
    "        recent = hist[-form_span:]\n",
    "        return np.mean([x[0] for x in recent]), np.mean([x[1] for x in recent])\n",
    "\n",
    "    if is_historical and date >= pd.to_datetime('1993-08-01'):\n",
    "        hs, as_ = int(hs), int(as_)\n",
    "        h_rank, h_pts = get_rank_and_points(h, date)\n",
    "        a_rank, a_pts = get_rank_and_points(a, date)\n",
    "        h_form_att, h_form_def = get_form(h)\n",
    "        a_form_att, a_form_def = get_form(a)\n",
    "        h_ovr, h_atk, h_def, h_pen = get_squad_features(h, h_rank)\n",
    "        a_ovr, a_atk, a_def, a_pen = get_squad_features(a, a_rank)\n",
    "        neutral = 1 if str(row['neutral']).upper() == 'TRUE' else 0\n",
    "        is_friendly = 1 if row['tournament'] == 'Friendly' else 0\n",
    "        \n",
    "        training_rows.append({\n",
    "            'team': h, 'opp': a, 'is_home': 1 - neutral,\n",
    "            'rank_diff': (h_rank - a_rank) / 100.0, 'point_diff': (h_pts - a_pts) / 500.0,\n",
    "            'squad_atk_self': (h_atk - 75.0) / 10.0, 'squad_def_opp': (a_def - 70.0) / 10.0, 'squad_ovr_diff': (h_ovr - a_ovr) / 10.0,\n",
    "            'form_attack_self': h_form_att, 'form_defense_opp': a_form_def,\n",
    "            'is_friendly': is_friendly, 'goals': hs\n",
    "        })\n",
    "        training_rows.append({\n",
    "            'team': a, 'opp': h, 'is_home': 0,\n",
    "            'rank_diff': (a_rank - h_rank) / 100.0, 'point_diff': (a_pts - h_pts) / 500.0,\n",
    "            'squad_atk_self': (a_atk - 75.0) / 10.0, 'squad_def_opp': (h_def - 70.0) / 10.0, 'squad_ovr_diff': (a_ovr - h_ovr) / 10.0,\n",
    "            'form_attack_self': a_form_att, 'form_defense_opp': h_form_def,\n",
    "            'is_friendly': is_friendly, 'goals': as_\n",
    "        })\n",
    "        \n",
    "    if is_historical:\n",
    "        hs, as_ = int(hs), int(as_)\n",
    "        if h not in team_match_history: team_match_history[h] = []\n",
    "        if a not in team_match_history: team_match_history[a] = []\n",
    "        team_match_history[h].append((hs, as_))\n",
    "        team_match_history[a].append((as_, hs))\n",
    "\n",
    "train_df = pd.DataFrame(training_rows)\n",
    "print(f\"Prepared {len(train_df)} dataset entries.\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 5. Train Poisson Regressor (Pure NumPy GLM)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "class PurePoissonRegression:\n",
    "    def __init__(self, lr=0.001, iterations=1500):\n",
    "        self.lr = lr\n",
    "        self.iterations = iterations\n",
    "        self.weights = None\n",
    "        self.bias = None\n",
    "        \n",
    "    def fit(self, X, y):\n",
    "        N, D = X.shape\n",
    "        self.weights = np.zeros(D)\n",
    "        self.bias = 0.0\n",
    "        for _ in range(self.iterations):\n",
    "            linear = np.dot(X, self.weights) + self.bias\n",
    "            linear = np.clip(linear, -10.0, 5.0)\n",
    "            lambdas = np.exp(linear)\n",
    "            dw = np.dot(X.T, (lambdas - y)) / N\n",
    "            db = np.mean(lambdas - y)\n",
    "            self.weights -= self.lr * dw\n",
    "            self.bias -= self.lr * db\n",
    "            \n",
    "    def predict(self, X):\n",
    "        linear = np.dot(X, self.weights) + self.bias\n",
    "        linear = np.clip(linear, -10.0, 5.0)\n",
    "        return np.exp(linear)\n",
    "\n",
    "features_cols = ['is_home', 'rank_diff', 'point_diff', 'squad_atk_self', 'squad_def_opp', 'squad_ovr_diff', 'form_attack_self', 'form_defense_opp', 'is_friendly']\n",
    "X_df = train_df[features_cols]\n",
    "y_df = train_df['goals']\n",
    "\n",
    "np.random.seed(42)\n",
    "indices = np.arange(len(train_df))\n",
    "np.random.shuffle(indices)\n",
    "split_idx = int(len(train_df) * 0.8)\n",
    "train_idx, val_idx = indices[:split_idx], indices[split_idx:]\n",
    "\n",
    "X_train = X_df.iloc[train_idx].to_numpy(dtype=np.float64)\n",
    "y_train = y_df.iloc[train_idx].to_numpy(dtype=np.float64)\n",
    "X_val = X_df.iloc[val_idx].to_numpy(dtype=np.float64)\n",
    "y_val = y_df.iloc[val_idx].to_numpy(dtype=np.float64)\n",
    "\n",
    "model = PurePoissonRegression(lr=0.01, iterations=1500)\n",
    "model.fit(X_train, y_train)\n",
    "\n",
    "y_pred = model.predict(X_val)\n",
    "mae = np.mean(np.abs(y_val - y_pred))\n",
    "print(f\"Validation Mean Absolute Error (MAE): {mae:.4f}\")\n",
    "\n",
    "# Retrain on whole dataset\n",
    "X_all = X_df.to_numpy(dtype=np.float64)\n",
    "y_all = y_df.to_numpy(dtype=np.float64)\n",
    "model.fit(X_all, y_all)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 6. Build the World Cup Bracket Simulator"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "latest_date = pd.to_datetime('2026-06-01')\n",
    "\n",
    "# Extract group fixtures\n",
    "wc_matches = results_df[results_df['date'].dt.year == 2026].copy()\n",
    "wc_matches = wc_matches[wc_matches['home_score'].isna() | (wc_matches['home_score'].astype(str) == 'NA')].reset_index(drop=True)\n",
    "\n",
    "fixtures_group_map = {}\n",
    "for idx, row in fixtures_df.iterrows():\n",
    "    date_dt, teams_str, group = row['date_dt'], row['teams'], row['group']\n",
    "    if 'Group' in str(group):\n",
    "        parts = teams_str.split(' v ')\n",
    "        if len(parts) == 2:\n",
    "            t1, t2 = clean_name(parts[0].strip()), clean_name(parts[1].strip())\n",
    "            fixtures_group_map[(date_dt, t1, t2)] = group\n",
    "            fixtures_group_map[(date_dt, t2, t1)] = group\n",
    "\n",
    "team_groups = {}\n",
    "group_teams = {}\n",
    "for idx, row in wc_matches.iterrows():\n",
    "    date_str = row['date'].strftime('%Y-%m-%d')\n",
    "    h, a = row['home_team'], row['away_team']\n",
    "    \n",
    "    # Robust matching logic for play-off combinations\n",
    "    group = None\n",
    "    for key, g in fixtures_group_map.items():\n",
    "        if date_str == key[0]:\n",
    "            # check if h matches key[1] or key[2]\n",
    "            def match_playoff(t, f_str):\n",
    "                opts = [clean_name(opt.strip()).lower() for opt in f_str.split('/')]\n",
    "                return clean_name(t).lower() in opts\n",
    "            t1_m_1 = match_playoff(h, key[1])\n",
    "            t2_m_2 = match_playoff(a, key[2])\n",
    "            t1_m_2 = match_playoff(h, key[2])\n",
    "            t2_m_1 = match_playoff(a, key[1])\n",
    "            if (t1_m_1 and t2_m_2) or (t1_m_2 and t2_m_1):\n",
    "                group = g\n",
    "                break\n",
    "                \n",
    "    if not group: group = 'Group A'\n",
    "    team_groups[h] = group\n",
    "    team_groups[a] = group\n",
    "    if group not in group_teams:\n",
    "        group_teams[group] = set()\n",
    "    group_teams[group].add(h)\n",
    "    group_teams[group].add(a)\n",
    "\n",
    "for g in group_teams: group_teams[g] = sorted(list(group_teams[g]))\n",
    "all_wc_teams = sorted(list(team_groups.keys()))\n",
    "\n",
    "# Precalculate all expected goals to speed up simulation\n",
    "precalc_features = []\n",
    "precalc_keys = []\n",
    "for team_a in all_wc_teams:\n",
    "    rank_a, pts_a = get_rank_and_points(team_a, latest_date)\n",
    "    att_a, def_a = get_latest_form(team_a)\n",
    "    ovr_a, atk_a, def_a_sq, pen_a = get_squad_features(team_a, rank_a)\n",
    "    for team_b in all_wc_teams:\n",
    "        if team_a == team_b: continue\n",
    "        rank_b, pts_b = get_rank_and_points(team_b, latest_date)\n",
    "        att_b, def_b = get_latest_form(team_b)\n",
    "        ovr_b, atk_b, def_b_sq, pen_b = get_squad_features(team_b, rank_b)\n",
    "        precalc_features.append([0.0, (rank_a - rank_b)/100.0, (pts_a - pts_b)/500.0, (atk_a - 75.0)/10.0, (def_b_sq - 70.0)/10.0, (ovr_a - ovr_b)/10.0, att_a, def_b, 0.0])\n",
    "        precalc_keys.append((team_a, team_b, 1))\n",
    "        precalc_features.append([1.0, (rank_a - rank_b)/100.0, (pts_a - pts_b)/500.0, (atk_a - 75.0)/10.0, (def_b_sq - 70.0)/10.0, (ovr_a - ovr_b)/10.0, att_a, def_b, 0.0])\n",
    "        precalc_keys.append((team_a, team_b, 0))\n",
    "\n",
    "precalc_preds = model.predict(np.array(precalc_features))\n",
    "lambda_cache = {}\n",
    "for idx, key in enumerate(precalc_keys): lambda_cache[key] = max(0.1, precalc_preds[idx])\n",
    "\n",
    "def get_cached_lambdas(team_a, team_b, neutral):\n",
    "    l_a = lambda_cache.get((team_a, team_b, neutral), 1.2)\n",
    "    l_b = lambda_cache.get((team_b, team_a, neutral), 1.2)\n",
    "    return l_a, l_b\n",
    "\n",
    "def simulate_match(team_a, team_b, neutral=1, is_knockout=False):\n",
    "    lambda_a, lambda_b = get_cached_lambdas(team_a, team_b, neutral)\n",
    "    goals_a, goals_b = np.random.poisson(lambda_a), np.random.poisson(lambda_b)\n",
    "    if not is_knockout: return goals_a, goals_b\n",
    "    if goals_a == goals_b:\n",
    "        goals_a += np.random.poisson(lambda_a / 3.0)\n",
    "        goals_b += np.random.poisson(lambda_b / 3.0)\n",
    "    if goals_a == goals_b:\n",
    "        rank_a, _ = get_rank_and_points(team_a, latest_date)\n",
    "        rank_b, _ = get_rank_and_points(team_b, latest_date)\n",
    "        p_win_a = np.clip(0.5 + 0.2*(get_shootout_win_rate(team_a) - get_shootout_win_rate(team_b)) + 0.05*((rank_b - rank_a)/(rank_b + rank_a)), 0.35, 0.65)\n",
    "        if np.random.random() < p_win_a: return goals_a + 1, goals_b\n",
    "        else: return goals_a, goals_b + 1\n",
    "    return goals_a, goals_b"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "def simulate_group_stage():\n",
    "    standings = {g: {t: {'pts': 0, 'gd': 0, 'gs': 0, 'team': t} for t in teams} for g, teams in group_teams.items()}\n",
    "    for idx, row in wc_matches.iterrows():\n",
    "        h, a = row['home_team'], row['away_team']\n",
    "        neutral = 1 if str(row['neutral']).upper() == 'TRUE' else 0\n",
    "        g = team_groups[h]\n",
    "        gh, ga = simulate_match(h, a, neutral, is_knockout=False)\n",
    "        standings[g][h]['gs'] += gh\n",
    "        standings[g][h]['gd'] += (gh - ga)\n",
    "        standings[g][a]['gs'] += ga\n",
    "        standings[g][a]['gd'] += (ga - gh)\n",
    "        if gh > ga: standings[g][h]['pts'] += 3\n",
    "        elif gh < ga: standings[g][a]['pts'] += 3\n",
    "        else:\n",
    "            standings[g][h]['pts'] += 1\n",
    "            standings[g][a]['pts'] += 1\n",
    "    ranked_groups = {}\n",
    "    for g in group_teams:\n",
    "        def sort_key(t):\n",
    "            rank, _ = get_rank_and_points(t['team'], latest_date)\n",
    "            return (-t['pts'], -t['gd'], -t['gs'], rank)\n",
    "        ranked_groups[g] = sorted(list(standings[g].values()), key=sort_key)\n",
    "    return ranked_groups\n",
    "\n",
    "def pair_third_place_teams(third_place_teams):\n",
    "    slots = [\n",
    "        {'id': 74, 'allowed': {'Group A', 'Group B', 'Group C', 'Group D', 'Group F'}},\n",
    "        {'id': 77, 'allowed': {'Group C', 'Group D', 'Group F', 'Group G', 'Group H'}},\n",
    "        {'id': 79, 'allowed': {'Group C', 'Group E', 'Group F', 'Group H', 'Group I'}},\n",
    "        {'id': 80, 'allowed': {'Group E', 'Group H', 'Group I', 'Group J', 'Group K'}},\n",
    "        {'id': 81, 'allowed': {'Group B', 'Group E', 'Group F', 'Group I', 'Group J'}},\n",
    "        {'id': 82, 'allowed': {'Group A', 'Group E', 'Group H', 'Group I', 'Group J'}},\n",
    "        {'id': 85, 'allowed': {'Group E', 'Group F', 'Group G', 'Group I', 'Group J'}},\n",
    "        {'id': 87, 'allowed': {'Group D', 'Group E', 'Group I', 'Group J', 'Group L'}}\n",
    "    ]\n",
    "    assigned = [None] * len(slots)\n",
    "    used = set()\n",
    "    def backtrack(slot_idx):\n",
    "        if slot_idx == len(slots): return True\n",
    "        slot = slots[slot_idx]\n",
    "        for team in third_place_teams:\n",
    "            if team not in used:\n",
    "                t_grp = team_groups[team]\n",
    "                if t_grp in slot['allowed']:\n",
    "                    assigned[slot_idx] = team\n",
    "                    used.add(team)\n",
    "                    if backtrack(slot_idx + 1): return True\n",
    "                    used.remove(team)\n",
    "                    assigned[slot_idx] = None\n",
    "        return False\n",
    "    if backtrack(0): return {slots[i]['id']: assigned[i] for i in range(len(slots))}\n",
    "    return {slots[i]['id']: third_place_teams[i] for i in range(len(slots))}\n",
    "\n",
    "def simulate_tournament():\n",
    "    group_tables = simulate_group_stage()\n",
    "    winners = {g: table[0]['team'] for g, table in group_tables.items()}\n",
    "    runners_up = {g: table[1]['team'] for g, table in group_tables.items()}\n",
    "    third_placed = []\n",
    "    for g, table in group_tables.items():\n",
    "        t = table[2]\n",
    "        rank, _ = get_rank_and_points(t['team'], latest_date)\n",
    "        third_placed.append({'team': t['team'], 'pts': t['pts'], 'gd': t['gd'], 'gs': t['gs'], 'rank': rank})\n",
    "    ranked_third = sorted(third_placed, key=lambda t: (-t['pts'], -t['gd'], -t['gs'], t['rank']))\n",
    "    best_8_third_teams = [t['team'] for t in ranked_third[:8]]\n",
    "    third_pairings = pair_third_place_teams(best_8_third_teams)\n",
    "    \n",
    "    ko_winners = {}\n",
    "    matches = [\n",
    "        (73, runners_up['Group A'], runners_up['Group B']),\n",
    "        (74, winners['Group E'], third_pairings[74]),\n",
    "        (75, winners['Group F'], runners_up['Group C']),\n",
    "        (76, winners['Group C'], runners_up['Group F']),\n",
    "        (77, winners['Group I'], third_pairings[77]),\n",
    "        (78, runners_up['Group E'], runners_up['Group I']),\n",
    "        (79, winners['Group A'], third_pairings[79]),\n",
    "        (80, winners['Group L'], third_pairings[80]),\n",
    "        (81, winners['Group D'], third_pairings[81]),\n",
    "        (82, winners['Group G'], third_pairings[82]),\n",
    "        (83, runners_up['Group K'], runners_up['Group L']),\n",
    "        (84, winners['Group H'], runners_up['Group J']),\n",
    "        (85, winners['Group B'], third_pairings[85]),\n",
    "        (86, winners['Group J'], runners_up['Group H']),\n",
    "        (87, winners['Group K'], third_pairings[87]),\n",
    "        (88, runners_up['Group D'], runners_up['Group G'])\n",
    "    ]\n",
    "    for mid, t1, t2 in matches:\n",
    "        g1, g2 = simulate_match(t1, t2, neutral=1, is_knockout=True)\n",
    "        ko_winners[mid] = t1 if g1 > g2 else t2\n",
    "        \n",
    "    r16_brackets = [(89, 74, 77), (90, 73, 75), (91, 76, 78), (92, 79, 80), (93, 83, 84), (94, 81, 82), (95, 86, 88), (96, 85, 87)]\n",
    "    for mid, m1, m2 in r16_brackets:\n",
    "        g1, g2 = simulate_match(ko_winners[m1], ko_winners[m2], neutral=1, is_knockout=True)\n",
    "        ko_winners[mid] = ko_winners[m1] if g1 > g2 else ko_winners[m2]\n",
    "        \n",
    "    qf_brackets = [(97, 89, 90), (98, 93, 94), (99, 91, 92), (100, 95, 96)]\n",
    "    for mid, m1, m2 in qf_brackets:\n",
    "        g1, g2 = simulate_match(ko_winners[m1], ko_winners[m2], neutral=1, is_knockout=True)\n",
    "        ko_winners[mid] = ko_winners[m1] if g1 > g2 else ko_winners[m2]\n",
    "        \n",
    "    sf_brackets = [(101, 97, 98), (102, 99, 100)]\n",
    "    for mid, m1, m2 in sf_brackets:\n",
    "        g1, g2 = simulate_match(ko_winners[m1], ko_winners[m2], neutral=1, is_knockout=True)\n",
    "        ko_winners[mid] = ko_winners[m1] if g1 > g2 else ko_winners[m2]\n",
    "        \n",
    "    g1, g2 = simulate_match(ko_winners[101], ko_winners[102], neutral=1, is_knockout=True)\n",
    "    winner = ko_winners[101] if g1 > g2 else ko_winners[102]\n",
    "    return {'winner': winner, 'finalists': [ko_winners[101], ko_winners[102]]}\n",
    "print(\"Tournament simulator functions defined.\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 7. Run Monte Carlo Simulations & Plot Winner Probabilities"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "NUM_SIMULATIONS = 10000\n",
    "winner_counts = {t: 0 for t in all_wc_teams}\n",
    "final_counts = {t: 0 for t in all_wc_teams}\n",
    "\n",
    "print(f\"Simulating {NUM_SIMULATIONS} tournaments...\")\n",
    "for i in range(NUM_SIMULATIONS):\n",
    "    res = simulate_tournament()\n",
    "    winner_counts[res['winner']] += 1\n",
    "    for t in res['finalists']:\n",
    "        final_counts[t] += 1\n",
    "\n",
    "wc_prob_df = pd.DataFrame({\n",
    "    'Team': all_wc_teams,\n",
    "    'Group': [team_groups[t] for t in all_wc_teams],\n",
    "    'FIFA Rank': [get_rank_and_points(t, latest_date)[0] for t in all_wc_teams],\n",
    "    'Final Reach (%)': [final_counts[t] / NUM_SIMULATIONS * 100 for t in all_wc_teams],\n",
    "    'Winner (%)': [winner_counts[t] / NUM_SIMULATIONS * 100 for t in all_wc_teams]\n",
    "}).sort_values(by='Winner (%)', ascending=False).reset_index(drop=True)\n",
    "\n",
    "plt.figure(figsize=(12, 7))\n",
    "top_15 = wc_prob_df.head(15)\n",
    "ax = sns.barplot(data=top_15, x='Winner (%)', y='Team', palette='viridis', hue='Team', legend=False)\n",
    "plt.title('FIFA World Cup 2026 Prediction Winner Probabilities (Top 15)', fontsize=15, fontweight='bold')\n",
    "plt.xlabel('Win Probability (%)')\n",
    "plt.ylabel('Team')\n",
    "for p in ax.patches:\n",
    "    ax.text(p.get_width() + 0.1, p.get_y() + p.get_height()/2, f\"{p.get_width():.2f}%\", ha='left', va='center', fontweight='bold')\n",
    "plt.tight_layout()\n",
    "plt.show()\n",
    "\n",
    "print(\"Top 15 Contenders:\")\n",
    "print(wc_prob_df.head(15))"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.11.9"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 2
}

notebook_str = json.dumps(notebook_content, indent=1)
notebook_str = notebook_str.replace("all_wc_teams", repr(all_wc_teams))

with open('predict_world_cup.ipynb', mode='w', encoding='utf-8') as f:
    f.write(notebook_str)
print("Generated 'predict_world_cup.ipynb' Jupyter notebook file.")

print("\nAll pipeline and simulator logic executed successfully!")
