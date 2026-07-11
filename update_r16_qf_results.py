"""
Update predict_world_cup.py with all R16 results + QF1 (France 2-0 Morocco) + QF2 (Spain 2-1 Belgium),
then run the model and extract new winner probabilities.

R16 Results (Jul 4-7):
  89: France 1-0 Paraguay           (src: 74 Paraguay, 77 France→ France wins)
  90: Morocco 3-0 Canada            (src: 75 Morocco, 73 Canada → Morocco wins)
  91: Norway 2-1 Brazil             (src: 76 Brazil, 78 Norway → Norway wins)
  92: England 3-2 Mexico            (src: 79 Mexico, 80 England → England wins)
  93: Spain 1-0 Portugal            (src: 83 Portugal, 84 Spain → Spain wins)
  94: Belgium 4-1 USA               (src: 81 USA, 82 Belgium → Belgium wins)
  95: Argentina 3-2 Egypt           (src: 86 Argentina, 88 Egypt → Argentina wins)
  96: Switzerland 0-0 Colombia AET, Switzerland 4-3 pens (src: 85 Switzerland, 87 Colombia → Switzerland wins)

QF Results (Jul 9-10):
  97: France 2-0 Morocco            (src: 89 France, 90 Morocco → France wins)
  98: Spain 2-1 Belgium             (src: 93 Spain, 94 Belgium → Spain wins)
  99: Norway vs England             (src: 91 Norway, 92 England → Jul 11 TODAY)
 100: Argentina vs Switzerland      (src: 95 Argentina, 96 Switzerland → Jul 11 TODAY)
"""

import subprocess
import sys
import re

py_path = r"c:\Users\VINAYAK R VIBHUTI\OneDrive\Desktop\predictor\predict_world_cup.py"

with open(py_path, 'r', encoding='utf-8') as f:
    src = f.read()

# ── PATCH 1: Update completed R32 section to include all R32 real results ──────
# The existing code only has 4 R32 results. We need all 16 now.
# The actual R32 real results were encoded in bracket.js:
# M73: Canada 1-0 South Africa     → Canada wins
# M74: Germany 1-1 Paraguay (pens) → Paraguay 4-3 wins
# M75: Netherlands 1-1 Morocco (pens) → Morocco 3-2 wins
# M76: Brazil 2-1 Japan            → Brazil wins
# But those 4 were already in predict_world_cup.py.
# The remaining 12 R32 matches were simulated. In reality the results fed into R16:
# The actual R16 contestants tell us:
#   M89: France vs Paraguay → France won (so M77 France won their R32)
#   M90: Morocco vs Canada → Morocco won (consistent)
#   M91: Norway vs Brazil → Norway won (so Norway won M78)
#   M92: England vs Mexico → England won (so England won M80, Mexico won M79)
#   M93: Spain vs Portugal → Spain won (so Spain won M84, Portugal won M83)
#   M94: Belgium vs USA → Belgium won (so Belgium won M82, USA won M81)
#   M95: Argentina vs Egypt → Argentina won (so Argentina won M86, Egypt won M88)
#   M96: Switzerland vs Colombia → Switzerland won (so Switzerland won M85, Colombia won M87)

# Lock all R32 results in the simulate_tournament function:
OLD_R32_SECTION = '''    # ── COMPLETED R32 RESULTS (real outcomes — not simulated) ──────────────────
    # Match 73 (Jun 28): Canada 1-0 South Africa
    ko_winners[73] = 'Canada'
    
    # Match 74 (Jun 29): Germany 1-1 Paraguay (aet), Paraguay win 4-3 on pens
    ko_winners[74] = 'Paraguay'
    
    # Match 75 (Jun 29): Netherlands 1-1 Morocco (aet), Morocco win 3-2 on pens
    ko_winners[75] = 'Morocco'
    
    # Match 76 (Jun 29): Brazil 2-1 Japan
    ko_winners[76] = 'Brazil'
    # ── END OF COMPLETED RESULTS ────────────────────────────────────────────────
    
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
    ko_winners[88] = runners_up['Group D'] if g88_h > g88_a else runners_up['Group G']'''

NEW_R32_SECTION = '''    # ── COMPLETED R32 RESULTS (real outcomes — not simulated) ──────────────────
    # Match 73 (Jun 28): Canada 1-0 South Africa
    ko_winners[73] = 'Canada'
    
    # Match 74 (Jun 29): Germany 1-1 Paraguay (aet), Paraguay win 4-3 on pens
    ko_winners[74] = 'Paraguay'
    
    # Match 75 (Jun 29): Netherlands 1-1 Morocco (aet), Morocco win 3-2 on pens
    ko_winners[75] = 'Morocco'
    
    # Match 76 (Jun 29): Brazil 2-1 Japan
    ko_winners[76] = 'Brazil'
    
    # Match 77 (Jun 30): France won their R32 match → advanced to face Paraguay in R16
    ko_winners[77] = 'France'
    
    # Match 78 (Jun 30): Norway won their R32 match → advanced to face Brazil in R16
    ko_winners[78] = 'Norway'
    
    # Match 79 (Jun 30): Mexico won their R32 match → advanced to R16
    ko_winners[79] = 'Mexico'
    
    # Match 80 (Jul 1): England won their R32 match → advanced to face Mexico in R16
    ko_winners[80] = 'England'
    
    # Match 81 (Jul 1): USA won their R32 match → advanced to face Belgium in R16
    ko_winners[81] = 'USA'
    
    # Match 82 (Jul 1): Belgium won their R32 match → advanced to face USA in R16
    ko_winners[82] = 'Belgium'
    
    # Match 83 (Jul 2): Portugal won their R32 match → advanced to face Spain in R16
    ko_winners[83] = 'Portugal'
    
    # Match 84 (Jul 2): Spain won their R32 match → advanced to face Portugal in R16
    ko_winners[84] = 'Spain'
    
    # Match 85 (Jul 2): Switzerland won their R32 match → advanced to face Colombia in R16
    ko_winners[85] = 'Switzerland'
    
    # Match 86 (Jul 3): Argentina won their R32 match → advanced to face Egypt in R16
    ko_winners[86] = 'Argentina'
    
    # Match 87 (Jul 3): Colombia won their R32 match → advanced to face Switzerland in R16
    ko_winners[87] = 'Colombia'
    
    # Match 88 (Jul 3): Egypt won their R32 match → advanced to face Argentina in R16
    ko_winners[88] = 'Egypt'
    # ── END OF COMPLETED R32 RESULTS ────────────────────────────────────────────'''

# ── PATCH 2: Replace all R16 simulation with real results ──────────────────────
OLD_R16_SECTION = '''    # 3. ROUND OF 16
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
    ko_winners[100] = ko_winners[95] if g100_h > g100_a else ko_winners[96]'''

NEW_R16_SECTION = '''    # 3. ROUND OF 16 — ALL RESULTS FINAL (Jul 4-7)
    # Match 89 (Jul 5): France 1-0 Paraguay
    ko_winners[89] = 'France'
    
    # Match 90 (Jul 4): Morocco 3-0 Canada
    ko_winners[90] = 'Morocco'
    
    # Match 91 (Jul 5): Norway 2-1 Brazil
    ko_winners[91] = 'Norway'
    
    # Match 92 (Jul 5): England 3-2 Mexico
    ko_winners[92] = 'England'
    
    # Match 93 (Jul 6): Spain 1-0 Portugal
    ko_winners[93] = 'Spain'
    
    # Match 94 (Jul 6): Belgium 4-1 USA
    ko_winners[94] = 'Belgium'
    
    # Match 95 (Jul 7): Argentina 3-2 Egypt
    ko_winners[95] = 'Argentina'
    
    # Match 96 (Jul 7): Switzerland 0-0 Colombia AET, Switzerland 4-3 pens
    ko_winners[96] = 'Switzerland'
    
    # 4. QUARTERFINALS
    # Match 97 (Jul 9): France 2-0 Morocco — COMPLETED
    ko_winners[97] = 'France'
    
    # Match 98 (Jul 10): Spain 2-1 Belgium — COMPLETED
    ko_winners[98] = 'Spain'
    
    # Match 99 (Jul 11): Norway vs England — ONGOING/UPCOMING
    g99_h, g99_a = simulate_match(ko_winners[91], ko_winners[92], neutral=1, is_knockout=True)
    ko_winners[99] = ko_winners[91] if g99_h > g99_a else ko_winners[92]
    
    # Match 100 (Jul 11): Argentina vs Switzerland — ONGOING/UPCOMING
    g100_h, g100_a = simulate_match(ko_winners[95], ko_winners[96], neutral=1, is_knockout=True)
    ko_winners[100] = ko_winners[95] if g100_h > g100_a else ko_winners[96]'''

if OLD_R32_SECTION in src:
    src = src.replace(OLD_R32_SECTION, NEW_R32_SECTION)
    print("✅ R32 section patched successfully")
else:
    print("❌ Could not find OLD_R32_SECTION — checking partial match...")
    # Try to find just the beginning
    snippet = '    # ── COMPLETED R32 RESULTS'
    idx = src.find(snippet)
    print(f"  Found at index: {idx}")

if OLD_R16_SECTION in src:
    src = src.replace(OLD_R16_SECTION, NEW_R16_SECTION)
    print("✅ R16+QF section patched successfully")
else:
    print("❌ Could not find OLD_R16_SECTION")
    snippet = '    # 3. ROUND OF 16'
    idx = src.find(snippet)
    print(f"  R16 section found at index: {idx}")

with open(py_path, 'w', encoding='utf-8') as f:
    f.write(src)

print("\n✅ predict_world_cup.py patched. Running model now...")
print("=" * 60)

# Run the model
result = subprocess.run(
    [sys.executable, py_path],
    capture_output=True, text=True,
    cwd=r"c:\Users\VINAYAK R VIBHUTI\OneDrive\Desktop\predictor"
)

print(result.stdout[-8000:] if len(result.stdout) > 8000 else result.stdout)
if result.returncode != 0:
    print("STDERR:", result.stderr[-3000:])
    raise RuntimeError("Model run failed!")

print("\n✅ Model run complete. Reading new probabilities...")

import pandas as pd
df = pd.read_csv(r"c:\Users\VINAYAK R VIBHUTI\OneDrive\Desktop\predictor\fifa_2026_prediction_results.csv")
print("\n=== NEW WINNER PROBABILITIES (top 20) ===")
print(df[['Team', 'Winner (%)']].head(20).to_string(index=False))
