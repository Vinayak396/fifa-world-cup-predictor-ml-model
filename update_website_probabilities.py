import json
import re
import math
import sys
import io

# Force stdout encoding to UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def get_outcome_probs(lambda_h, lambda_a):
    def poisson_pmf(lam, k):
        return (lam**k) * math.exp(-lam) / math.factorial(k)
        
    p_home = 0.0
    p_draw = 0.0
    p_away = 0.0
    
    for h in range(16):
        pmf_h = poisson_pmf(lambda_h, h)
        for a in range(16):
            pmf_a = poisson_pmf(lambda_a, a)
            prob = pmf_h * pmf_a
            if h > a:
                p_home += prob
            elif h == a:
                p_draw += prob
            else:
                p_away += prob
                
    total = p_home + p_draw + p_away
    return round((p_home / total) * 100, 1), round((p_draw / total) * 100, 1), round((p_away / total) * 100, 1)

def main():
    print("============================================================")
    print("Updating website/js/data.js with new simulation results")
    print("============================================================")
    
    # 1. Import predict_world_cup to get model lambdas and data
    print("Importing predict_world_cup (this trains model)...")
    import predict_world_cup as pwc
    
    # 2. Get the new pre-match probabilities for QF matches
    print("\nCalculating QF match pre-match probabilities...")
    # Norway vs England
    l_nor, l_eng = pwc.get_cached_lambdas("Norway", "England", 1)
    nor_w, nor_d, eng_w = get_outcome_probs(l_nor, l_eng)
    print(f"  Norway vs England: lambdas=({l_nor:.3f}, {l_eng:.3f}) -> H:{nor_w}%, D:{nor_d}%, A:{eng_w}%")
    
    # Argentina vs Switzerland
    l_arg, l_sui = pwc.get_cached_lambdas("Argentina", "Switzerland", 1)
    arg_w, arg_d, sui_w = get_outcome_probs(l_arg, l_sui)
    print(f"  Argentina vs Switzerland: lambdas=({l_arg:.3f}, {l_sui:.3f}) -> H:{arg_w}%, D:{arg_d}%, A:{sui_w}%")
    
    # 3. Read the simulated winner probabilities from CSV
    print("\nReading simulated winner probabilities from CSV...")
    import pandas as pd
    prob_df = pd.read_csv("fifa_2026_prediction_results.csv")
    winner_probs = {}
    for idx, row in prob_df.iterrows():
        winner_probs[row['Team']] = float(row['Winner (%)'])
        
    # 4. Load website/js/data.js
    js_path = "website/js/data.js"
    with open(js_path, 'r', encoding='utf-8') as f:
        js_content = f.read()
        
    # 5. Update TEAMS winner probabilities
    print("\nUpdating TEAMS winner probabilities in data.js...")
    
    def replace_team_winner(match):
        line = match.group(0)
        team_name = match.group(1)
        if team_name in winner_probs:
            new_prob = winner_probs[team_name]
            # Replace winner:XX.XX
            line = re.sub(r'winner:\s*[0-9.]+', f'winner:{new_prob:.2f}', line)
        return line

    # Matches lines like: "Spain": { group:"H", rank:2, winner:53.07, flag:"es" }
    js_content = re.sub(r'"([^"]+)":\s*\{\s*group:[^,]+,\s*rank:[^,]+,\s*winner:[^,]+,\s*flag:[^}]+\}', replace_team_winner, js_content)
    
    # 6. Update preMatchProbs for Match 99 and Match 100
    print("Updating QF preMatchProbs in data.js...")
    
    def replace_qf_probs(match):
        text = match.group(0)
        id_val = int(match.group(1))
        if id_val == 99:
            # Replace preMatchProbs
            text = re.sub(r'preMatchProbs:\s*\{\s*home:[0-9.]+\s*,\s*draw:[0-9.]+\s*,\s*away:[0-9.]+\s*\}', 
                          f'preMatchProbs: {{ home:{nor_w:.1f}, draw:{nor_d:.1f}, away:{eng_w:.1f} }}', text)
        elif id_val == 100:
            text = re.sub(r'preMatchProbs:\s*\{\s*home:[0-9.]+\s*,\s*draw:[0-9.]+\s*,\s*away:[0-9.]+\s*\}', 
                          f'preMatchProbs: {{ home:{arg_w:.1f}, draw:{arg_d:.1f}, away:{sui_w:.1f} }}', text)
        return text

    # Matches QF fixture lines
    js_content = re.sub(r'\{\s*id:\s*(99|100),.*\}', replace_qf_probs, js_content)
    
    # Write updated js content
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write(js_content)
        
    print("\n✅ Successfully updated website/js/data.js!")

if __name__ == '__main__':
    main()
