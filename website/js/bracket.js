// ── KNOCKOUT BRACKET DATA ────────────────────────────────────────────────────
// win probability for incomplete matches: ratio of model winner% values
function matchupProb(home, away) {
  const wH = (TEAMS[home] || {}).winner || 0.01;
  const wA = (TEAMS[away] || {}).winner || 0.01;
  const t = wH + wA;
  return { home: +(wH / t * 100).toFixed(1), away: +(wA / t * 100).toFixed(1) };
}

// Round of 32 — 16 matches
// result: null = upcoming, { hg, ag, winner } = played, add pens string if shootout
const R32 = [
  // -- LEFT HALF --
  // M89 feeds
  { id:74, home:"Germany",     away:"Paraguay",     date:"Jun 29",
    result:{ hg:1, ag:1, winner:"Paraguay", pens:"Paraguay 4–3" } },
  { id:77, home:"France",      away:"Ivory Coast",  date:"Jun 30",
    result:{ hg:2, ag:0, winner:"France" } },
  // M90 feeds
  { id:75, home:"Netherlands", away:"Morocco",      date:"Jun 29",
    result:{ hg:1, ag:1, winner:"Morocco",  pens:"Morocco 3–2" } },
  { id:73, home:"Canada",      away:"South Africa", date:"Jun 28",
    result:{ hg:1, ag:0, winner:"Canada" } },
  // M91 feeds
  { id:76, home:"Brazil",      away:"Japan",        date:"Jun 29",
    result:{ hg:2, ag:1, winner:"Brazil" } },
  { id:78, home:"Norway",      away:"Ecuador",      date:"Jun 30",
    result:{ hg:2, ag:1, winner:"Norway" } },
  // M92 feeds
  { id:79, home:"Mexico",      away:"South Korea",  date:"Jun 30",
    result:{ hg:1, ag:0, winner:"Mexico" } },
  { id:80, home:"England",     away:"Ghana",        date:"Jul 1",
    result:{ hg:4, ag:0, winner:"England" } },
  // -- RIGHT HALF --
  // M93 feeds
  { id:83, home:"Portugal",    away:"Croatia",      date:"Jul 2",
    result:{ hg:2, ag:1, winner:"Portugal" } },
  { id:84, home:"Spain",       away:"Austria",      date:"Jul 2",
    result:{ hg:3, ag:0, winner:"Spain" } },
  // M94 feeds
  { id:81, home:"USA",         away:"Algeria",      date:"Jul 1",
    result:{ hg:2, ag:1, winner:"USA" } },
  { id:82, home:"Belgium",     away:"Senegal",      date:"Jul 1",
    result:{ hg:3, ag:0, winner:"Belgium" } },
  // M95 feeds
  { id:86, home:"Argentina",   away:"Cape Verde",   date:"Jul 3",
    result:{ hg:4, ag:0, winner:"Argentina" } },
  { id:88, home:"Egypt",       away:"Australia",    date:"Jul 3",
    result:{ hg:2, ag:0, winner:"Egypt" } },
  // M96 feeds
  { id:85, home:"Switzerland", away:"Bosnia and Herzegovina", date:"Jul 2",
    result:{ hg:3, ag:1, winner:"Switzerland" } },
  { id:87, home:"Colombia",    away:"Turkey",       date:"Jul 3",
    result:{ hg:2, ag:1, winner:"Colombia" } },
];

// Round of 16 — uses winner labels when not yet determined
const R16 = [
  { id:89, src:[74,77], date:"Jul 5",  result:{ hg:1, ag:0, winner:"France" } },
  { id:90, src:[75,73], date:"Jul 4",  result:{ hg:3, ag:0, winner:"Morocco" } },
  { id:91, src:[76,78], date:"Jul 5",  result:{ hg:2, ag:1, winner:"Norway" } },
  { id:92, src:[79,80], date:"Jul 5",  result:{ hg:3, ag:2, winner:"England" } },
  { id:93, src:[83,84], date:"Jul 6",  result:{ hg:1, ag:0, winner:"Spain" } },
  { id:94, src:[81,82], date:"Jul 6",  result:{ hg:4, ag:1, winner:"Belgium" } },
  { id:95, src:[86,88], date:"Jul 7",  result:{ hg:3, ag:2, winner:"Argentina" } },
  { id:96, src:[85,87], date:"Jul 7",  result:{ hg:0, ag:0, winner:"Switzerland", pens:"Switzerland 4–3" } },
];
const QF = [
  { id:97, src:[89,90], date:"Jul 9",  result:{ hg:2, ag:0, winner:"France" } },
  { id:99, src:[91,92], date:"Jul 11", result:{ hg:1, ag:2, winner:"England" } },
  { id:98, src:[93,94], date:"Jul 10", result:{ hg:2, ag:1, winner:"Spain" } },
  { id:100,src:[95,96], date:"Jul 11", result:{ hg:3, ag:1, winner:"Argentina" } },
];
const SF = [
  { id:101, src:[97,98],  date:"Jul 14", result:{ hg:0, ag:2, winner:"Spain" } },
  { id:102, src:[99,100], date:"Jul 15", result:{ hg:1, ag:2, winner:"Argentina" } },
];
const THIRD_PLACE = { id:103, src:[101,102], date:"Jul 18",
  result:{ hg:4, ag:6, winner:"England" } }; // France 4-6 England (losers bracket)
const FINAL = { id:104, src:[101,102], date:"Jul 19 🏆" };

// ── BRACKET RENDERER ─────────────────────────────────────────────────────────
function flagUrl2(code) {
  return `https://flagcdn.com/w40/${(code||'un').toLowerCase()}.png`;
}
function getFlag(name) {
  return (TEAMS[name] || {}).flag || 'un';
}

// Build a lookup: matchId → winner name (if result known)
function buildWinnerMap() {
  const m = {};
  R32.forEach(f => {
    if (f.result && f.result.winner) m[f.id] = f.result.winner;
  });
  return m;
}

function getTeamForSlot(srcId, winnerMap) {
  if (winnerMap[srcId]) return winnerMap[srcId];
  // Try to find from R16/QF/SF
  const all = [...R16, ...QF, ...SF];
  const match = all.find(m => m.id === srcId);
  if (match && match.result && match.result.winner) return match.result.winner;
  return null;
}

// Render a single bracket match card
function makeBracketCard(topName, botName, matchId, result, date, isPast) {
  const p = (topName && botName) ? matchupProb(topName, botName) : null;

  function teamRow(name, isWinner, isTop) {
    const flag = getFlag(name || '');
    const scoreStr = result
      ? (isTop ? result.hg : result.ag)
      : (p ? (isTop ? p.home : p.away) + '%' : '');
    const wonClass = (result && result.winner === name) ? ' bk-winner' : '';
    const lostClass = (result && result.winner && result.winner !== name) ? ' bk-loser' : '';
    return `<div class="bk-team${wonClass}${lostClass}">
      <div class="bk-team-left">
        ${name ? `<img class="bk-flag" src="${flagUrl2(flag)}" alt="${name}">` : '<div class="bk-flag bk-tbd"></div>'}
        <span class="bk-name">${name || 'TBD'}</span>
      </div>
      <span class="bk-score${result ? ' bk-score-final' : ' bk-score-prob'}">${scoreStr}</span>
    </div>`;
  }

  const pens = result && result.pens ? `<div class="bk-pens">${result.pens}</div>` : '';
  const statusClass = isPast ? 'bk-card--done' : 'bk-card--upcoming';

  return `<div class="bk-card ${statusClass}" data-match="${matchId}">
    <div class="bk-card-header">M${matchId}<span class="bk-date">${date}</span></div>
    ${teamRow(topName, result && result.winner === topName, true)}
    ${teamRow(botName, result && result.winner === botName, false)}
    ${pens}
  </div>`;
}

// Build a column of cards with connectors
function makeColumn(matches, label) {
  const inner = matches.map(m => `
    <div class="bk-slot">
      ${m.card}
      <div class="bk-connector"></div>
    </div>`).join('');
  return `<div class="bk-col">
    <div class="bk-col-label">${label}</div>
    <div class="bk-col-slots">${inner}</div>
  </div>`;
}

// ── MAIN BUILD FUNCTION ───────────────────────────────────────────────────────
function buildKnockoutBracket() {
  const container = document.getElementById('bracket-inner');
  if (!container) return;

  const winnerMap = buildWinnerMap();

  // Helpers to get team name or label for later-round matches
  function getTeam(srcId) {
    if (winnerMap[srcId]) return winnerMap[srcId];
    return null; // TBD
  }
  function label(srcId) {
    return winnerMap[srcId] || `W${srcId}`;
  }

  // ── R32 cards ──
  function r32Card(idx) {
    const f = R32[idx];
    const p = !f.result && f.home && f.away ? matchupProb(f.home, f.away) : null;
    const topScore = f.result ? f.result.hg : (p ? p.home + '%' : '');
    const botScore = f.result ? f.result.ag : (p ? p.away + '%' : '');
    const winnerH = f.result && f.result.winner === f.home;
    const winnerA = f.result && f.result.winner === f.away;
    const pens = f.result && f.result.pens ? `<div class="bk-pens">${f.result.pens}</div>` : '';

    return `<div class="bk-card ${f.result ? 'bk-card--done' : 'bk-card--upcoming'}">
      <div class="bk-card-header">M${f.id}<span class="bk-date">${f.date}</span></div>
      <div class="bk-team${winnerH ? ' bk-winner' : winnerA ? ' bk-loser' : ''}">
        <div class="bk-team-left"><img class="bk-flag" src="${flagUrl2(getFlag(f.home))}" alt="${f.home}">
        <span class="bk-name">${f.home}</span></div>
        <span class="bk-score ${f.result ? 'bk-score-final' : 'bk-score-prob'}">${topScore}</span>
      </div>
      <div class="bk-team${winnerA ? ' bk-winner' : winnerH ? ' bk-loser' : ''}">
        <div class="bk-team-left"><img class="bk-flag" src="${flagUrl2(getFlag(f.away))}" alt="${f.away}">
        <span class="bk-name">${f.away}</span></div>
        <span class="bk-score ${f.result ? 'bk-score-final' : 'bk-score-prob'}">${botScore}</span>
      </div>
      ${pens}
    </div>`;
  }

  // ── Later round card (R16, QF, SF, Final) ──
  function laterCard(match, allCards) {
    const topName = getTeam(match.src[0]);
    const botName = getTeam(match.src[1]);
    const topLabel = topName || `W${match.src[0]}`;
    const botLabel = botName || `W${match.src[1]}`;
    const p = (topName && botName) ? matchupProb(topName, botName) : null;
    const res = match.result || null;
    const topScore = res ? res.hg : (p ? p.home + '%' : '');
    const botScore = res ? res.ag : (p ? p.away + '%' : '');
    const winnerTop = res && res.winner === topName;
    const winnerBot = res && res.winner === botName;
    const topFlag = topName ? getFlag(topName) : 'un';
    const botFlag = botName ? getFlag(botName) : 'un';
    const pens = res && res.pens ? `<div class="bk-pens">${res.pens}</div>` : '';

    const topRowClass = `bk-team${winnerTop ? ' bk-winner' : (winnerBot ? ' bk-loser' : '')}`;
    const botRowClass = `bk-team${winnerBot ? ' bk-winner' : (winnerTop ? ' bk-loser' : '')}`;

    return `<div class="bk-card ${res ? 'bk-card--done' : 'bk-card--upcoming'}">
      <div class="bk-card-header">M${match.id}<span class="bk-date">${match.date}</span></div>
      <div class="${topRowClass}">
        <div class="bk-team-left">${topName ? `<img class="bk-flag" src="${flagUrl2(topFlag)}" alt="${topLabel}">` : '<div class="bk-flag bk-tbd"></div>'}
        <span class="bk-name">${topLabel}</span></div>
        <span class="bk-score ${res ? 'bk-score-final' : (p ? 'bk-score-prob' : 'bk-score-tbd')}">${topScore}</span>
      </div>
      <div class="${botRowClass}">
        <div class="bk-team-left">${botName ? `<img class="bk-flag" src="${flagUrl2(botFlag)}" alt="${botLabel}">` : '<div class="bk-flag bk-tbd"></div>'}
        <span class="bk-name">${botLabel}</span></div>
        <span class="bk-score ${res ? 'bk-score-final' : (p ? 'bk-score-prob' : 'bk-score-tbd')}">${botScore}</span>
      </div>
      ${pens}
    </div>`;
  }

  // Update winnerMap with later rounds
  function registerWinner(match) {
    if (match.result && match.result.winner) winnerMap[match.id] = match.result.winner;
  }
  R16.forEach(registerWinner);
  QF.forEach(registerWinner);
  SF.forEach(registerWinner);

  // ── BUILD LEFT COLUMN: R32 (indices 0-7) ──
  const leftR32Slots = [0,1,2,3,4,5,6,7].map(i => `
    <div class="bk-slot bk-slot--r32 ${i < 4 ? 'bk-slot-pair-top' : 'bk-slot-pair-bot'}">
      ${r32Card(i)}
    </div>`).join('');

  // ── R16 LEFT (M89, M90, M91, M92) ──
  const leftR16Slots = [R16[0], R16[1], R16[2], R16[3]].map(m => `
    <div class="bk-slot bk-slot--r16">
      ${laterCard(m)}
    </div>`).join('');

  // ── QF LEFT (M97, M99) ──
  const leftQFSlots = [QF[0], QF[1]].map(m => `
    <div class="bk-slot bk-slot--qf">
      ${laterCard(m)}
    </div>`).join('');

  // ── SF LEFT (M101) ──
  const leftSFSlot = `<div class="bk-slot bk-slot--sf">${laterCard(SF[0])}</div>`;

  // ── FINAL ──
  const finalSlot = `<div class="bk-slot bk-slot--final">${laterCard(FINAL)}</div>`;

  // ── SF RIGHT (M102) ──
  const rightSFSlot = `<div class="bk-slot bk-slot--sf">${laterCard(SF[1])}</div>`;

  // ── QF RIGHT (M98, M100) ──
  const rightQFSlots = [QF[2], QF[3]].map(m => `
    <div class="bk-slot bk-slot--qf">
      ${laterCard(m)}
    </div>`).join('');

  // ── R16 RIGHT (M93, M94, M95, M96) ──
  const rightR16Slots = [R16[4], R16[5], R16[6], R16[7]].map(m => `
    <div class="bk-slot bk-slot--r16">
      ${laterCard(m)}
    </div>`).join('');

  // ── RIGHT R32 (indices 8-15) ──
  const rightR32Slots = [8,9,10,11,12,13,14,15].map(i => `
    <div class="bk-slot bk-slot--r32 ${i < 12 ? 'bk-slot-pair-top' : 'bk-slot-pair-bot'}">
      ${r32Card(i)}
    </div>`).join('');

  container.innerHTML = `
    <div class="bk-col">
      <div class="bk-col-label">Round of 32</div>
      <div class="bk-col-slots bk-col--r32-left">${leftR32Slots}</div>
    </div>
    <div class="bk-connectors bk-connectors--r32-r16-left"></div>
    <div class="bk-col">
      <div class="bk-col-label">Round of 16</div>
      <div class="bk-col-slots bk-col--r16-left">${leftR16Slots}</div>
    </div>
    <div class="bk-connectors bk-connectors--r16-qf-left"></div>
    <div class="bk-col">
      <div class="bk-col-label">Quarter-finals</div>
      <div class="bk-col-slots bk-col--qf-left">${leftQFSlots}</div>
    </div>
    <div class="bk-connectors bk-connectors--qf-sf-left"></div>
    <div class="bk-col">
      <div class="bk-col-label">Semi-finals</div>
      <div class="bk-col-slots bk-col--sf-left">${leftSFSlot}</div>
    </div>
    <div class="bk-connectors bk-connectors--sf-final"></div>
    <div class="bk-col bk-col--final">
      <div class="bk-col-label">🏆 Final</div>
      <div class="bk-col-slots bk-col--final-slot">${finalSlot}</div>
    </div>
    <div class="bk-connectors bk-connectors--sf-final"></div>
    <div class="bk-col">
      <div class="bk-col-label">Semi-finals</div>
      <div class="bk-col-slots bk-col--sf-right">${rightSFSlot}</div>
    </div>
    <div class="bk-connectors bk-connectors--qf-sf-right"></div>
    <div class="bk-col">
      <div class="bk-col-label">Quarter-finals</div>
      <div class="bk-col-slots bk-col--qf-right">${rightQFSlots}</div>
    </div>
    <div class="bk-connectors bk-connectors--r16-qf-right"></div>
    <div class="bk-col">
      <div class="bk-col-label">Round of 16</div>
      <div class="bk-col-slots bk-col--r16-right">${rightR16Slots}</div>
    </div>
    <div class="bk-connectors bk-connectors--r32-r16-right"></div>
    <div class="bk-col">
      <div class="bk-col-label">Round of 32</div>
      <div class="bk-col-slots bk-col--r32-right">${rightR32Slots}</div>
    </div>`;
}
