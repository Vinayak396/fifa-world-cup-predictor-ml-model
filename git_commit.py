import os

def main():
    print("Staging files...")
    os.system('git add predict_world_cup.py predict_world_cup.ipynb results.csv fifa_2026_prediction_results.csv fifa_2026_prediction_plot.png eafc26_wc_team_summary.csv website/js/data.js get_wc_squads.py update_results_md1.py wc2026_squads.csv')
    
    print("Committing changes...")
    os.system('git commit -m "Update simulation logic with actual Matchday 1 results and website predictions"')
    
    print("Pushing to GitHub...")
    os.system('git push')
    
    print("Done!")

if __name__ == '__main__':
    main()
