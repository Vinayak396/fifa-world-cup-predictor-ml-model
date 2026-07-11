// ─── TEAM DATA ───────────────────────────────────────────────────────────────
// winner: overall tournament winner probability (%) — XGBoost model
//         R16 complete + QF1 France 2-0 Morocco + QF2 Spain 2-1 Belgium locked
//         QF3/QF4 simulated — retrained Jul 11 2026
// flag:   ISO 3166-1 alpha-2 code for flagcdn.com
const TEAMS = {
  "Spain":                 { group:"H", rank:2,  winner:53.07, flag:"es"     },
  "France":                { group:"I", rank:1,  winner:17.57, flag:"fr"     },
  "Argentina":             { group:"J", rank:3,  winner:13.80, flag:"ar"     },
  "England":               { group:"L", rank:4,  winner:11.57, flag:"gb-eng" },
  "Switzerland":           { group:"B", rank:19, winner:2.99,  flag:"ch"     },
  "Norway":                { group:"I", rank:31, winner:1.00,  flag:"no"     },
  "Morocco":               { group:"C", rank:8,  winner:0.00,  flag:"ma"     },
  "Brazil":                { group:"C", rank:6,  winner:0.00,  flag:"br"     },
  "Portugal":              { group:"K", rank:5,  winner:0.00,  flag:"pt"     },
  "Belgium":               { group:"G", rank:9,  winner:0.00,  flag:"be"     },
  "Paraguay":              { group:"D", rank:40, winner:0.00,  flag:"py"     },
  "Colombia":              { group:"K", rank:13, winner:0.00,  flag:"co"     },
  "Mexico":                { group:"A", rank:15, winner:0.00,  flag:"mx"     },
  "USA":                   { group:"D", rank:16, winner:0.00,  flag:"us"     },
  "Algeria":               { group:"J", rank:28, winner:0.00,  flag:"dz"     },
  "Egypt":                 { group:"G", rank:29, winner:0.00,  flag:"eg"     },
  "Iran":                  { group:"G", rank:21, winner:0.00,  flag:"ir"     },
  "Croatia":               { group:"L", rank:11, winner:0.00,  flag:"hr"     },
  "Ecuador":               { group:"E", rank:23, winner:0.00,  flag:"ec"     },
  "Turkey":                { group:"D", rank:22, winner:0.00,  flag:"tr"     },
  "Uruguay":               { group:"H", rank:17, winner:0.00,  flag:"uy"     },
  "Austria":               { group:"J", rank:24, winner:0.00,  flag:"at"     },
  "Australia":             { group:"D", rank:27, winner:0.00,  flag:"au"     },
  "Senegal":               { group:"I", rank:14, winner:0.00,  flag:"sn"     },
  "Ghana":                 { group:"L", rank:74, winner:0.00,  flag:"gh"     },
  "DR Congo":              { group:"K", rank:46, winner:0.00,  flag:"cd"     },
  "Canada":                { group:"B", rank:30, winner:0.00,  flag:"ca"     },
  "Cape Verde":            { group:"H", rank:69, winner:0.00,  flag:"cv"     },
  "Germany":               { group:"E", rank:10, winner:0.00,  flag:"de"     },
  "Netherlands":           { group:"F", rank:7,  winner:0.00,  flag:"nl"     },
  "Japan":                 { group:"F", rank:18, winner:0.00,  flag:"jp"     },
  "South Africa":          { group:"A", rank:60, winner:0.00,  flag:"za"     },
  "Ivory Coast":           { group:"E", rank:34, winner:0.00,  flag:"ci"     },
  "South Korea":           { group:"A", rank:25, winner:0.00,  flag:"kr"     },
  "Uzbekistan":            { group:"K", rank:50, winner:0.00,  flag:"uz"     },
  "Tunisia":               { group:"F", rank:44, winner:0.00,  flag:"tn"     },
  "Czech Republic":        { group:"A", rank:41, winner:0.00,  flag:"cz"     },
  "Scotland":              { group:"C", rank:43, winner:0.00,  flag:"gb-sct" },
  "Iraq":                  { group:"I", rank:57, winner:0.00,  flag:"iq"     },
  "Bosnia and Herzegovina":{ group:"B", rank:65, winner:0.00,  flag:"ba"     },
  "Jordan":                { group:"J", rank:63, winner:0.00,  flag:"jo"     },
  "Saudi Arabia":          { group:"H", rank:61, winner:0.00,  flag:"sa"     },
  "Curacao":               { group:"E", rank:82, winner:0.00,  flag:"cw"     },
  "Qatar":                 { group:"B", rank:55, winner:0.00,  flag:"qa"     },
  "New Zealand":           { group:"G", rank:85, winner:0.00,  flag:"nz"     },
  "Haiti":                 { group:"C", rank:83, winner:0.00,  flag:"ht"     },
  "Panama":                { group:"L", rank:33, winner:0.00,  flag:"pa"     },
  "Sweden":                { group:"F", rank:38, winner:0.00,  flag:"se"     }
};

// ─── FIXTURES (Group Stage only — 72 matches) ────────────────────────────────
const FIXTURES = [
  // ── GROUP A ──
  { id:1,  md:1, date:"Jun 11", home:"Mexico",       away:"South Africa",  group:"A", venue:"Estadio Azteca", result: { homeScore:2, awayScore:0 }, preMatchProbs: { home:67.9, draw:18.1, away:14.0 } },
  { id:2,  md:1, date:"Jun 11", home:"South Korea",  away:"Czech Republic",group:"A", venue:"Estadio Akron", result: { homeScore:2, awayScore:1 }, preMatchProbs: { home:54.0, draw:21.8, away:24.2 } },
  { id:28, md:2, date:"Jun 18", home:"Mexico",       away:"South Korea",   group:"A", venue:"Estadio Akron", result: { homeScore:1, awayScore:0 }, preMatchProbs: { home:68.7, draw:17.5, away:13.8 } },
  { id:25, md:2, date:"Jun 18", home:"Czech Republic",away:"South Africa", group:"A", venue:"Mercedes-Benz Stadium", result: { homeScore:1, awayScore:1 }, preMatchProbs: { home:50.1, draw:22.5, away:27.4 } },
  { id:53, md:3, date:"Jun 24", home:"Czech Republic",away:"Mexico",       group:"A", venue:"Estadio Azteca", result: { homeScore:0, awayScore:3 }, preMatchProbs: { home:36.2, draw:23.5, away:40.3 } },
  { id:54, md:3, date:"Jun 24", home:"South Africa", away:"South Korea",   group:"A", venue:"Estadio BBVA", result: { homeScore:1, awayScore:0 }, preMatchProbs: { home:27.8, draw:23.6, away:48.6 } },
  // ── GROUP B ──
  { id:3,  md:1, date:"Jun 12", home:"Canada",       away:"Bosnia and Herzegovina", group:"B", venue:"BMO Field Toronto", result: { homeScore:1, awayScore:1 }, preMatchProbs: { home:62.2, draw:19.6, away:18.2 } },
  { id:8,  md:1, date:"Jun 13", home:"Qatar",        away:"Switzerland",   group:"B", venue:"Levi's Stadium", result: { homeScore:1, awayScore:1 }, preMatchProbs: { home:5.2, draw:15.1, away:79.7 } },
  { id:27, md:2, date:"Jun 18", home:"Canada",       away:"Qatar",         group:"B", venue:"BC Place Vancouver", result: { homeScore:6, awayScore:0 }, preMatchProbs: { home:68.5, draw:18.3, away:13.2 } },
  { id:26, md:2, date:"Jun 18", home:"Switzerland",  away:"Bosnia and Herzegovina", group:"B", venue:"SoFi Stadium", result: { homeScore:4, awayScore:1 }, preMatchProbs: { home:72.9, draw:17.1, away:10.0 } },
  { id:51, md:3, date:"Jun 24", home:"Switzerland",  away:"Canada",        group:"B", venue:"BC Place Vancouver", result: { homeScore:2, awayScore:1 }, preMatchProbs: { home:60.4, draw:20.3, away:19.3 } },
  { id:52, md:3, date:"Jun 24", home:"Bosnia and Herzegovina",away:"Qatar",group:"B", venue:"Lumen Field Seattle", result: { homeScore:3, awayScore:1 }, preMatchProbs: { home:28.3, draw:23.1, away:48.6 } },
  // ── GROUP C ──
  { id:5,  md:1, date:"Jun 13", home:"Haiti",        away:"Scotland",      group:"C", venue:"Gillette Stadium", result: { homeScore:0, awayScore:1 }, preMatchProbs: { home:6.3, draw:15.5, away:78.2 } },
  { id:7,  md:1, date:"Jun 13", home:"Brazil",       away:"Morocco",       group:"C", venue:"MetLife Stadium", result: { homeScore:1, awayScore:1 }, preMatchProbs: { home:34.4, draw:26.1, away:39.5 } },
  { id:29, md:2, date:"Jun 19", home:"Brazil",       away:"Haiti",         group:"C", venue:"Lincoln Financial Field", result: { homeScore:3, awayScore:0 }, preMatchProbs: { home:82.3, draw:12.4, away:5.3 } },
  { id:30, md:2, date:"Jun 19", home:"Scotland",     away:"Morocco",       group:"C", venue:"Gillette Stadium", result: { homeScore:0, awayScore:1 }, preMatchProbs: { home:32.6, draw:23.1, away:44.3 } },
  { id:49, md:3, date:"Jun 24", home:"Scotland",     away:"Brazil",        group:"C", venue:"Hard Rock Stadium", result: { homeScore:0, awayScore:3 }, preMatchProbs: { home:23.1, draw:21.8, away:55.1 } },
  { id:50, md:3, date:"Jun 24", home:"Morocco",      away:"Haiti",         group:"C", venue:"Mercedes-Benz Stadium", result: { homeScore:4, awayScore:2 }, preMatchProbs: { home:68.7, draw:18.2, away:13.1 } },
  // ── GROUP D ──
  { id:4,  md:1, date:"Jun 12", home:"USA",          away:"Paraguay",      group:"D", venue:"SoFi Stadium", result: { homeScore:4, awayScore:1 }, preMatchProbs: { home:66.5, draw:18.5, away:15.0 } },
  { id:6,  md:1, date:"Jun 13", home:"Australia",    away:"Turkey",        group:"D", venue:"BC Place Vancouver", result: { homeScore:2, awayScore:0 }, preMatchProbs: { home:27.9, draw:23.3, away:48.8 } },
  { id:32, md:2, date:"Jun 19", home:"USA",          away:"Australia",     group:"D", venue:"Lumen Field Seattle", result: { homeScore:2, awayScore:0 }, preMatchProbs: { home:71.4, draw:16.3, away:12.3 } },
  { id:31, md:2, date:"Jun 19", home:"Turkey",       away:"Paraguay",      group:"D", venue:"Levi's Stadium", result: { homeScore:0, awayScore:1 }, preMatchProbs: { home:46.2, draw:22.8, away:31.0 } },
  { id:59, md:3, date:"Jun 25", home:"Turkey",       away:"USA",           group:"D", venue:"SoFi Stadium", result: { homeScore:3, awayScore:2 }, preMatchProbs: { home:33.8, draw:23.7, away:42.5 } },
  { id:60, md:3, date:"Jun 25", home:"Paraguay",     away:"Australia",     group:"D", venue:"Levi's Stadium", result: { homeScore:0, awayScore:0 }, preMatchProbs: { home:21.6, draw:23.9, away:54.5 } },
  // ── GROUP E ──
  { id:9,  md:1, date:"Jun 14", home:"Ivory Coast",  away:"Ecuador",       group:"E", venue:"Lincoln Financial Field", result: { homeScore:1, awayScore:0 }, preMatchProbs: { home:10.9, draw:17.1, away:72.0 } },
  { id:10, md:1, date:"Jun 14", home:"Germany",      away:"Curacao",       group:"E", venue:"NRG Stadium Houston", result: { homeScore:7, awayScore:1 }, preMatchProbs: { home:83.0, draw:14.3, away:2.7 } },
  { id:33, md:2, date:"Jun 20", home:"Germany",      away:"Ivory Coast",   group:"E", venue:"BMO Field Toronto", result: { homeScore:2, awayScore:1 }, preMatchProbs: { home:76.2, draw:14.5, away:9.3 } },
  { id:34, md:2, date:"Jun 20", home:"Ecuador",      away:"Curacao",       group:"E", venue:"Arrowhead Stadium", result: { homeScore:0, awayScore:0 }, preMatchProbs: { home:55.1, draw:21.4, away:23.5 } },
  { id:56, md:3, date:"Jun 25", home:"Ecuador",      away:"Germany",       group:"E", venue:"MetLife Stadium", result: { homeScore:2, awayScore:1 }, preMatchProbs: { home:16.3, draw:20.5, away:63.2 } },
  { id:55, md:3, date:"Jun 25", home:"Curacao",      away:"Ivory Coast",   group:"E", venue:"Lincoln Financial Field", result: { homeScore:0, awayScore:2 }, preMatchProbs: { home:7.4, draw:16.2, away:76.4 } },
  // ── GROUP F ──
  { id:11, md:1, date:"Jun 14", home:"Netherlands",  away:"Japan",         group:"F", venue:"AT&T Stadium", result: { homeScore:2, awayScore:2 }, preMatchProbs: { home:40.4, draw:25.8, away:33.8 } },
  { id:12, md:1, date:"Jun 14", home:"Sweden",       away:"Tunisia",       group:"F", venue:"Estadio BBVA", result: { homeScore:5, awayScore:1 }, preMatchProbs: { home:28.8, draw:23.7, away:47.5 } },
  { id:35, md:2, date:"Jun 20", home:"Netherlands",  away:"Sweden",        group:"F", venue:"NRG Stadium Houston", result: { homeScore:5, awayScore:1 }, preMatchProbs: { home:58.2, draw:20.1, away:21.7 } },
  { id:36, md:2, date:"Jun 20", home:"Tunisia",      away:"Japan",         group:"F", venue:"Estadio BBVA", result: { homeScore:0, awayScore:4 }, preMatchProbs: { home:14.8, draw:19.7, away:65.5 } },
  { id:57, md:3, date:"Jun 25", home:"Japan",        away:"Sweden",        group:"F", venue:"AT&T Stadium", result: { homeScore:1, awayScore:1 }, preMatchProbs: { home:41.7, draw:24.8, away:33.5 } },
  { id:58, md:3, date:"Jun 25", home:"Tunisia",      away:"Netherlands",   group:"F", venue:"Arrowhead Stadium", result: { homeScore:1, awayScore:3 }, preMatchProbs: { home:10.2, draw:17.1, away:72.7 } },
  // ── GROUP G ──
  { id:15, md:1, date:"Jun 15", home:"Iran",         away:"New Zealand",   group:"G", venue:"SoFi Stadium", result: { homeScore:2, awayScore:2 }, preMatchProbs: { home:75.9, draw:16.1, away:8.0 } },
  { id:16, md:1, date:"Jun 15", home:"Belgium",      away:"Egypt",         group:"G", venue:"Lumen Field Seattle", result: { homeScore:1, awayScore:1 }, preMatchProbs: { home:61.4, draw:19.8, away:18.8 } },
  { id:39, md:2, date:"Jun 21", home:"Belgium",      away:"Iran",          group:"G", venue:"SoFi Stadium", result: { homeScore:0, awayScore:0 }, preMatchProbs: { home:65.1, draw:19.4, away:15.5 } },
  { id:40, md:2, date:"Jun 21", home:"New Zealand",  away:"Egypt",         group:"G", venue:"BC Place Vancouver", result: { homeScore:1, awayScore:3 }, preMatchProbs: { home:7.3, draw:16.8, away:75.9 } },
  { id:63, md:3, date:"Jun 26", home:"Egypt",        away:"Iran",          group:"G", venue:"Lumen Field Seattle", result: { homeScore:1, awayScore:1 }, preMatchProbs: { home:23.3, draw:22.7, away:54.0 } },
  { id:64, md:3, date:"Jun 26", home:"New Zealand",  away:"Belgium",       group:"G", venue:"BC Place Vancouver", result: { homeScore:1, awayScore:5 }, preMatchProbs: { home:9.8, draw:16.9, away:73.3 } },
  // ── GROUP H ──
  { id:13, md:1, date:"Jun 15", home:"Saudi Arabia", away:"Uruguay",       group:"H", venue:"Hard Rock Stadium", result: { homeScore:1, awayScore:1 }, preMatchProbs: { home:3.6, draw:14.6, away:81.8 } },
  { id:14, md:1, date:"Jun 15", home:"Spain",        away:"Cape Verde",    group:"H", venue:"Mercedes-Benz Stadium", result: { homeScore:0, awayScore:0 }, preMatchProbs: { home:81.0, draw:14.8, away:4.2 } },
  { id:37, md:2, date:"Jun 21", home:"Uruguay",      away:"Cape Verde",    group:"H", venue:"Hard Rock Stadium", result: { homeScore:2, awayScore:2 }, preMatchProbs: { home:63.2, draw:20.4, away:16.4 } },
  { id:38, md:2, date:"Jun 21", home:"Spain",        away:"Saudi Arabia",  group:"H", venue:"Mercedes-Benz Stadium", result: { homeScore:4, awayScore:0 }, preMatchProbs: { home:85.3, draw:10.5, away:4.2 } },
  { id:65, md:3, date:"Jun 26", home:"Cape Verde",   away:"Saudi Arabia",  group:"H", venue:"NRG Stadium Houston", result: { homeScore:0, awayScore:0 }, preMatchProbs: { home:11.2, draw:18.6, away:70.2 } },
  { id:66, md:3, date:"Jun 26", home:"Uruguay",      away:"Spain",         group:"H", venue:"Estadio Akron", result: { homeScore:0, awayScore:1 }, preMatchProbs: { home:11.6, draw:18.3, away:70.1 } },
  // ── GROUP I ──
  { id:17, md:1, date:"Jun 16", home:"France",       away:"Senegal",       group:"I", venue:"MetLife Stadium", result: { homeScore:3, awayScore:1 }, preMatchProbs: { home:72.1, draw:16.2, away:11.7 } },
  { id:18, md:1, date:"Jun 16", home:"Iraq",         away:"Norway",        group:"I", venue:"Gillette Stadium", result: { homeScore:1, awayScore:4 }, preMatchProbs: { home:4.1, draw:13.3, away:82.6 } },
  { id:42, md:2, date:"Jun 22", home:"France",       away:"Iraq",          group:"I", venue:"Lincoln Financial Field", result: { homeScore:3, awayScore:0 }, preMatchProbs: { home:87.4, draw:9.1, away:3.5 } },
  { id:41, md:2, date:"Jun 22", home:"Norway",       away:"Senegal",       group:"I", venue:"MetLife Stadium", result: { homeScore:3, awayScore:2 }, preMatchProbs: { home:51.7, draw:22.1, away:26.2 } },
  { id:61, md:3, date:"Jun 26", home:"Norway",       away:"France",        group:"I", venue:"Gillette Stadium", result: { homeScore:1, awayScore:4 }, preMatchProbs: { home:35.4, draw:23.3, away:41.3 } },
  { id:62, md:3, date:"Jun 26", home:"Senegal",      away:"Iraq",          group:"I", venue:"BMO Field Toronto", result: { homeScore:5, awayScore:0 }, preMatchProbs: { home:77.6, draw:14.8, away:7.6 } },
  // ── GROUP J ──
  { id:19, md:1, date:"Jun 16", home:"Argentina",    away:"Algeria",       group:"J", venue:"Arrowhead Stadium", result: { homeScore:3, awayScore:0 }, preMatchProbs: { home:87.2, draw:9.2, away:3.6 } },
  { id:20, md:1, date:"Jun 16", home:"Austria",      away:"Jordan",        group:"J", venue:"Levi's Stadium", result: { homeScore:3, awayScore:1 }, preMatchProbs: { home:55.3, draw:22.1, away:22.6 } },
  { id:43, md:2, date:"Jun 22", home:"Argentina",    away:"Austria",       group:"J", venue:"AT&T Stadium", result: { homeScore:2, awayScore:0 }, preMatchProbs: { home:78.5, draw:13.8, away:7.7 } },
  { id:44, md:2, date:"Jun 22", home:"Jordan",       away:"Algeria",       group:"J", venue:"Levi's Stadium", result: { homeScore:1, awayScore:2 }, preMatchProbs: { home:32.2, draw:24.1, away:43.7 } },
  { id:70, md:3, date:"Jun 27", home:"Jordan",       away:"Argentina",     group:"J", venue:"AT&T Stadium", result: { homeScore:1, awayScore:3 }, preMatchProbs: { home:11.5, draw:18.2, away:70.3 } },
  { id:69, md:3, date:"Jun 27", home:"Algeria",      away:"Austria",       group:"J", venue:"Arrowhead Stadium", result: { homeScore:3, awayScore:3 }, preMatchProbs: { home:37.4, draw:23.8, away:38.8 } },
  // ── GROUP K ──
  { id:23, md:1, date:"Jun 17", home:"Portugal",     away:"DR Congo",      group:"K", venue:"NRG Stadium Houston", result: { homeScore:1, awayScore:1 }, preMatchProbs: { home:74.2, draw:17.3, away:8.5 } },
  { id:24, md:1, date:"Jun 17", home:"Uzbekistan",   away:"Colombia",      group:"K", venue:"Estadio Azteca", result: { homeScore:1, awayScore:3 }, preMatchProbs: { home:18.9, draw:22.4, away:58.7 } },
  { id:47, md:2, date:"Jun 23", home:"Portugal",     away:"Uzbekistan",    group:"K", venue:"NRG Stadium Houston", result: { homeScore:5, awayScore:0 }, preMatchProbs: { home:82.1, draw:12.3, away:5.6 } },
  { id:48, md:2, date:"Jun 23", home:"Colombia",     away:"DR Congo",      group:"K", venue:"Estadio Akron", result: { homeScore:1, awayScore:0 }, preMatchProbs: { home:59.4, draw:20.8, away:19.8 } },
  { id:71, md:3, date:"Jun 27", home:"Colombia",     away:"Portugal",      group:"K", venue:"Hard Rock Stadium", result: { homeScore:0, awayScore:0 }, preMatchProbs: { home:35.2, draw:23.5, away:41.3 } },
  { id:72, md:3, date:"Jun 27", home:"DR Congo",     away:"Uzbekistan",    group:"K", venue:"Mercedes-Benz Stadium", result: { homeScore:3, awayScore:1 }, preMatchProbs: { home:41.8, draw:24.1, away:34.1 } },
  // ── GROUP L ──
  { id:21, md:1, date:"Jun 17", home:"Ghana",        away:"Panama",        group:"L", venue:"BMO Field Toronto", result: { homeScore:1, awayScore:0 }, preMatchProbs: { home:26.4, draw:24.1, away:49.5 } },
  { id:22, md:1, date:"Jun 17", home:"England",      away:"Croatia",       group:"L", venue:"AT&T Stadium", result: { homeScore:4, awayScore:2 }, preMatchProbs: { home:63.4, draw:19.8, away:16.8 } },
  { id:45, md:2, date:"Jun 23", home:"England",      away:"Ghana",         group:"L", venue:"Gillette Stadium", result: { homeScore:0, awayScore:0 }, preMatchProbs: { home:73.8, draw:16.5, away:9.7 } },
  { id:46, md:2, date:"Jun 23", home:"Panama",       away:"Croatia",       group:"L", venue:"BMO Field Toronto", result: { homeScore:0, awayScore:1 }, preMatchProbs: { home:21.4, draw:22.6, away:56.0 } },
  { id:67, md:3, date:"Jun 27", home:"Panama",       away:"England",       group:"L", venue:"MetLife Stadium", result: { homeScore:0, awayScore:2 }, preMatchProbs: { home:21.9, draw:22.5, away:55.6 } },
  { id:68, md:3, date:"Jun 27", home:"Croatia",      away:"Ghana",         group:"L", venue:"Lincoln Financial Field", result: { homeScore:2, awayScore:1 }, preMatchProbs: { home:45.3, draw:23.9, away:30.8 } }
];

// ─── ROUND OF 32 FIXTURES ────────────────────────────────────────────────────
const R32_FIXTURES = [
  { id:73, date:"Jun 28", home:"Canada",      away:"South Africa",          venue:"SoFi Stadium",       result: { homeScore:1, awayScore:0 },              preMatchProbs: { home:52.1, draw:22.4, away:25.5 } },
  { id:74, date:"Jun 29", home:"Germany",     away:"Paraguay",              venue:"Gillette Stadium",   result: { homeScore:1, awayScore:1, pens:"Paraguay 4–3" }, preMatchProbs: { home:71.2, draw:16.8, away:12.0 } },
  { id:75, date:"Jun 29", home:"Netherlands", away:"Morocco",               venue:"Estadio BBVA",       result: { homeScore:1, awayScore:1, pens:"Morocco 3–2" },  preMatchProbs: { home:55.3, draw:22.1, away:22.6 } },
  { id:76, date:"Jun 29", home:"Brazil",      away:"Japan",                 venue:"NRG Stadium",        result: { homeScore:2, awayScore:1 },              preMatchProbs: { home:68.4, draw:17.2, away:14.4 } },
  { id:77, date:"Jun 30", home:"France",      away:"Ivory Coast",           venue:"Lincoln Financial Field", result: { homeScore:2, awayScore:0 },         preMatchProbs: { home:78.3, draw:12.4, away:9.3 } },
  { id:78, date:"Jun 30", home:"Norway",      away:"Ecuador",               venue:"Estadio BBVA",       result: { homeScore:2, awayScore:1 },              preMatchProbs: { home:48.2, draw:22.6, away:29.2 } },
  { id:79, date:"Jun 30", home:"Mexico",      away:"South Korea",           venue:"Estadio Akron",      result: { homeScore:1, awayScore:0 },              preMatchProbs: { home:55.3, draw:21.8, away:22.9 } },
  { id:80, date:"Jul 1",  home:"England",     away:"Ghana",                 venue:"AT&T Stadium",       result: { homeScore:4, awayScore:0 },              preMatchProbs: { home:74.1, draw:15.3, away:10.6 } },
  { id:81, date:"Jul 1",  home:"USA",         away:"Algeria",               venue:"Arrowhead Stadium",  result: { homeScore:2, awayScore:1 },              preMatchProbs: { home:58.4, draw:21.2, away:20.4 } },
  { id:82, date:"Jul 1",  home:"Belgium",     away:"Senegal",               venue:"Lumen Field",        result: { homeScore:3, awayScore:0 },              preMatchProbs: { home:64.7, draw:19.1, away:16.2 } },
  { id:83, date:"Jul 2",  home:"Portugal",    away:"Croatia",               venue:"Hard Rock Stadium",  result: { homeScore:2, awayScore:1 },              preMatchProbs: { home:59.2, draw:21.0, away:19.8 } },
  { id:84, date:"Jul 2",  home:"Spain",       away:"Austria",               venue:"Mercedes-Benz Stadium", result: { homeScore:3, awayScore:0 },          preMatchProbs: { home:72.4, draw:16.8, away:10.8 } },
  { id:85, date:"Jul 2",  home:"Switzerland", away:"Bosnia and Herzegovina",venue:"BMO Field Toronto",  result: { homeScore:3, awayScore:1 },              preMatchProbs: { home:67.8, draw:18.3, away:13.9 } },
  { id:86, date:"Jul 3",  home:"Argentina",   away:"Cape Verde",            venue:"AT&T Stadium",       result: { homeScore:4, awayScore:0 },              preMatchProbs: { home:88.1, draw:8.7,  away:3.2 } },
  { id:87, date:"Jul 3",  home:"Colombia",    away:"Turkey",                venue:"NRG Stadium",        result: { homeScore:2, awayScore:1 },              preMatchProbs: { home:52.6, draw:22.4, away:25.0 } },
  { id:88, date:"Jul 3",  home:"Egypt",       away:"Australia",             venue:"SoFi Stadium",       result: { homeScore:2, awayScore:0 },              preMatchProbs: { home:38.4, draw:24.2, away:37.4 } }
];

// ─── ROUND OF 16 FIXTURES ────────────────────────────────────────────────────
const R16_FIXTURES = [
  { id:89, date:"Jul 5",  home:"France",       away:"Paraguay",     venue:"MetLife Stadium",     result: { homeScore:1, awayScore:0 },              preMatchProbs: { home:72.1, draw:16.8, away:11.1 } },
  { id:90, date:"Jul 4",  home:"Morocco",      away:"Canada",       venue:"SoFi Stadium",        result: { homeScore:3, awayScore:0 },              preMatchProbs: { home:56.2, draw:22.0, away:21.8 } },
  { id:91, date:"Jul 5",  home:"Norway",       away:"Brazil",       venue:"Estadio Akron",       result: { homeScore:2, awayScore:1 },              preMatchProbs: { home:34.8, draw:24.1, away:41.1 } },
  { id:92, date:"Jul 5",  home:"England",      away:"Mexico",       venue:"AT&T Stadium",        result: { homeScore:3, awayScore:2 },              preMatchProbs: { home:62.7, draw:19.8, away:17.5 } },
  { id:93, date:"Jul 6",  home:"Spain",        away:"Portugal",     venue:"Arrowhead Stadium",   result: { homeScore:1, awayScore:0 },              preMatchProbs: { home:54.8, draw:22.5, away:22.7 } },
  { id:94, date:"Jul 6",  home:"Belgium",      away:"USA",          venue:"Levi's Stadium",      result: { homeScore:4, awayScore:1 },              preMatchProbs: { home:60.3, draw:20.4, away:19.3 } },
  { id:95, date:"Jul 7",  home:"Argentina",    away:"Egypt",        venue:"Hard Rock Stadium",   result: { homeScore:3, awayScore:2 },              preMatchProbs: { home:76.4, draw:14.3, away:9.3 } },
  { id:96, date:"Jul 7",  home:"Switzerland",  away:"Colombia",     venue:"Lincoln Financial Field", result: { homeScore:0, awayScore:0, pens:"Switzerland 4–3" }, preMatchProbs: { home:46.2, draw:24.1, away:29.7 } }
];

// ─── QUARTER-FINAL FIXTURES ──────────────────────────────────────────────────
const QF_FIXTURES = [
  { id:97,  date:"Jul 9",  home:"France",       away:"Morocco",      venue:"Gillette Stadium",    result: { homeScore:2, awayScore:0 },              preMatchProbs: { home:58.4, draw:21.2, away:20.4 } },
  { id:98,  date:"Jul 10", home:"Spain",        away:"Belgium",      venue:"MetLife Stadium",     result: { homeScore:2, awayScore:1 },              preMatchProbs: { home:61.7, draw:20.3, away:18.0 } },
  { id:99,  date:"Jul 11", home:"Norway",       away:"England",      venue:"AT&T Stadium",        result: null,                                     preMatchProbs: { home:35.7, draw:24.2, away:40.1 } },
  { id:100, date:"Jul 11", home:"Argentina",    away:"Switzerland",  venue:"SoFi Stadium",        result: null,                                     preMatchProbs: { home:73.2, draw:16.4, away:10.4 } }
];
