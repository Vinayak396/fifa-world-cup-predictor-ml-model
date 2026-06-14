# FIFA 2026 World Cup AI Predictor — Website

A stunning single-page web app showing AI-powered predictions for every FIFA 2026 World Cup group stage match, powered by XGBoost Poisson regression.

## 🌐 Live Preview

Open `index.html` directly in a browser, or run a local server:

```bash
python -m http.server 8765
```

Then visit `http://localhost:8765`

## 🔮 Features

- **Predicted Tournament Winner** — England (9.32%) based on 10,000 Monte Carlo simulations
- **Top 10 Contenders** — animated probability bars
- **All 72 Group Stage Matches** — Win / Draw / Win probabilities for every match across Groups A–L
- **Interactive Tab Navigation** — switch between all 12 groups
- **Animated on Scroll** — probability bars animate into view as you scroll

## 🧠 Model

Built on top of an XGBoost Poisson regression model trained on historical international match results (2016–2026), incorporating:

- FIFA World Rankings & ELO points
- EA FC 26 squad ratings (attack, defense, overall)
- Exponential time-decay weighting (recent form weighted higher)
- Dixon-Coles low-score correction
- Head-to-head win rates (competitive matches, last 10 years)
- WC pedigree multipliers

Per-match Win/Draw/Win probabilities are derived from each team's tournament winner probability using a Bradley-Terry style conversion with draw scaling.

## 📁 Structure

```
fifa2026-predictor/
├── index.html          # Main page
├── css/styles.css      # Dark navy theme, gold accents, glassmorphism
├── js/data.js          # 48 teams + 72 fixture definitions
└── js/app.js           # Probability engine + rendering logic
```

## 🏆 Predicted Group Winners

| Group | Winner | Runner-Up |
|-------|--------|-----------|
| A | Mexico | South Korea |
| B | Switzerland | Canada |
| C | Morocco | Brazil |
| D | USA | Turkey |
| E | Germany | Ecuador |
| F | Netherlands | Japan |
| G | Belgium | Egypt |
| H | Spain | Uruguay |
| I | France | Senegal |
| J | Argentina | Algeria |
| K | Portugal | Colombia |
| L | **England** 🏆 | Croatia |
