// ── PROBABILITY ENGINE ───────────────────────────────────────────────────────
function getProbs(homeTeam, awayTeam) {
  const wH = TEAMS[homeTeam]?.winner || 0.1;
  const wA = TEAMS[awayTeam]?.winner || 0.1;
  const total = wH + wA;
  const rawH = wH / total;                              // 0–1 raw home strength
  const balance = 1 - Math.abs(rawH - 0.5) * 2;        // 1 = perfectly even
  const drawPct = 0.27 * (0.5 + 0.5 * balance);        // 14–27% draw range
  const winH = rawH * (1 - drawPct);
  const winA = (1 - rawH) * (1 - drawPct);
  return {
    home: +(winH * 100).toFixed(1),
    draw: +(drawPct * 100).toFixed(1),
    away: +(winA * 100).toFixed(1)
  };
}

// ── FLAG URL ─────────────────────────────────────────────────────────────────
function flagUrl(code) {
  return `https://flagcdn.com/w80/${code.toLowerCase()}.png`;
}

// ── MATCH CARD ───────────────────────────────────────────────────────────────
function buildMatchCard(fix) {
  const p = fix.preMatchProbs || getProbs(fix.home, fix.away);
  const hFlag = TEAMS[fix.home]?.flag || 'un';
  const aFlag = TEAMS[fix.away]?.flag || 'un';

  const vsContent = fix.result ? `${fix.result.homeScore} - ${fix.result.awayScore}` : 'VS';
  const badgeClass = fix.result ? 'vs-badge scored' : 'vs-badge';
  const cardClass = fix.result ? 'match-card completed' : 'match-card';
  const drawLabel = fix.result ? 'Pre-Match Odds' : 'Draw';

  const card = document.createElement('div');
  card.className = cardClass;
  card.innerHTML = `
    <div class="match-meta">
      <span class="match-id">MATCH ${fix.id}${fix.result ? ' · <span class="final-badge">FINAL</span>' : ''}</span>
      <span class="match-venue" title="${fix.venue}">${fix.venue}</span>
      <span class="match-date">${fix.date}</span>
    </div>
    <div class="match-teams">
      <div class="match-team">
        <img class="team-flag" src="${flagUrl(hFlag)}" alt="${fix.home}" loading="lazy">
        <span class="team-name">${fix.home}</span>
      </div>
      <div class="${badgeClass}">${vsContent}</div>
      <div class="match-team away">
        <img class="team-flag" src="${flagUrl(aFlag)}" alt="${fix.away}" loading="lazy">
        <span class="team-name">${fix.away}</span>
      </div>
    </div>
    <div class="prob-bar-container">
      <div class="prob-labels">
        <span class="home-lbl">Win</span>
        <span class="draw-lbl">${drawLabel}</span>
        <span class="away-lbl">Win</span>
      </div>
      <div class="prob-bar">
        <div class="prob-home" style="width:0%" data-w="${p.home}"></div>
        <div class="prob-draw"  style="width:0%" data-w="${p.draw}"></div>
        <div class="prob-away"  style="width:0%" data-w="${p.away}"></div>
      </div>
      <div class="prob-pcts">
        <span class="hp">${p.home}%</span>
        <span class="dp">${p.draw}%</span>
        <span class="ap">${p.away}%</span>
      </div>
    </div>`;
  return card;
}

// ── ANIMATE BARS (IntersectionObserver) ──────────────────────────────────────
const barObserver = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (!e.isIntersecting) return;
    e.target.querySelectorAll('[data-w]').forEach(el => {
      el.style.width = el.dataset.w + '%';
    });
    barObserver.unobserve(e.target);
  });
}, { threshold: 0.2 });

// ── BUILD GROUPS ─────────────────────────────────────────────────────────────
function buildGroups() {
  const groups = ['A','B','C','D','E','F','G','H','I','J','K','L'];

  // Tabs
  const tabsEl = document.getElementById('group-tabs');
  groups.forEach((g, i) => {
    const btn = document.createElement('button');
    btn.className = 'group-tab' + (i === 0 ? ' active' : '');
    btn.textContent = `Group ${g}`;
    btn.dataset.group = g;
    btn.addEventListener('click', () => switchGroup(g));
    tabsEl.appendChild(btn);
  });

  // Panels
  const panelsEl = document.getElementById('group-panels');
  groups.forEach((g, i) => {
    const panel = document.createElement('div');
    panel.className = 'group-panel' + (i === 0 ? ' active' : '');
    panel.id = `panel-${g}`;
    if (i !== 0) panel.style.display = 'none';

    const matchdays = document.createElement('div');
    matchdays.className = 'group-matchdays';

    [1, 2, 3].forEach(md => {
      const fixes = FIXTURES.filter(f => f.group === g && f.md === md);
      if (!fixes.length) return;

      const section = document.createElement('div');
      section.innerHTML = `<div class="matchday-label">Matchday ${md}</div>`;

      const row = document.createElement('div');
      row.className = 'matches-row';
      fixes.forEach(f => {
        const card = buildMatchCard(f);
        barObserver.observe(card);
        row.appendChild(card);
      });
      section.appendChild(row);
      matchdays.appendChild(section);
    });

    panel.appendChild(matchdays);
    panelsEl.appendChild(panel);
  });
}

function switchGroup(g) {
  document.querySelectorAll('.group-tab').forEach(t => {
    t.classList.remove('active');
    if (t.dataset.group === g) t.classList.add('active');
  });
  document.querySelectorAll('.group-panel').forEach(p => {
    p.style.display = 'none';
    p.classList.remove('active');
  });
  const target = document.getElementById(`panel-${g}`);
  if (target) { target.style.display = 'block'; target.classList.add('active'); }
}

// ── TOP CONTENDERS ────────────────────────────────────────────────────────────
function buildContenders() {
  const sorted = Object.entries(TEAMS)
    .sort((a, b) => b[1].winner - a[1].winner)
    .slice(0, 10);

  const maxW = sorted[0][1].winner;

  // gradient colors for bars
  const colors = [
    '#f0c040','#e0a020','#d4853a','#c86a34',
    '#b25530','#9a4028','#2eb86a','#2aa05a',
    '#4a9eff','#3a8ae0'
  ];

  const container = document.getElementById('contenders-list');
  sorted.forEach(([name, data], i) => {
    const pct = (data.winner / maxW * 100).toFixed(1);
    const row = document.createElement('div');
    row.className = 'contender-row';
    row.innerHTML = `
      <div class="contender-team">
        <img class="contender-flag" src="${flagUrl(data.flag)}" alt="${name}" loading="lazy">
        <span class="contender-name">${name}</span>
      </div>
      <div class="contender-bar-track">
        <div class="contender-bar-fill" data-w="${pct}" style="background:${colors[i]};width:0%"></div>
      </div>
      <span class="contender-pct" style="color:${colors[i]}">${data.winner}%</span>`;
    container.appendChild(row);
    barObserver.observe(row);
  });
}

// ── WINNER SPOTLIGHT ──────────────────────────────────────────────────────────
function buildWinner() {
  const sorted = Object.entries(TEAMS).sort((a, b) => b[1].winner - a[1].winner);
  const [name, data] = sorted[0];

  document.getElementById('winner-flag').src = flagUrl(data.flag);
  document.getElementById('winner-flag').alt = name;
  document.getElementById('winner-name').textContent = name;
  document.getElementById('winner-pct-text').innerHTML =
    `Predicted winner probability: <strong>${data.winner}%</strong>`;

  // Top-8 bars in winner section
  const barsEl = document.getElementById('winner-bars');
  sorted.slice(0, 8).forEach(([n, d]) => {
    const pct = (d.winner / data.winner * 100).toFixed(1);
    const wrap = document.createElement('div');
    wrap.style.marginBottom = '0.6rem';
    wrap.innerHTML = `
      <div class="winner-bar-label">
        <span>${n}</span><span>${d.winner}%</span>
      </div>
      <div class="winner-bar-track">
        <div class="winner-bar-fill" data-w="${pct}" style="width:0%"></div>
      </div>`;
    barsEl.appendChild(wrap);
    barObserver.observe(wrap);
  });
}

// ── HERO PARTICLES ────────────────────────────────────────────────────────────
function initParticles() {
  const canvas = document.getElementById('particles');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  let W, H, dots = [];

  function resize() {
    W = canvas.width  = canvas.offsetWidth;
    H = canvas.height = canvas.offsetHeight;
  }
  resize();
  window.addEventListener('resize', resize);

  for (let i = 0; i < 60; i++) {
    dots.push({
      x: Math.random() * 1200, y: Math.random() * 520,
      r: Math.random() * 1.5 + 0.5,
      vx: (Math.random() - 0.5) * 0.3,
      vy: (Math.random() - 0.5) * 0.3,
      a: Math.random() * 0.5 + 0.1
    });
  }

  function draw() {
    ctx.clearRect(0, 0, W, H);
    dots.forEach(d => {
      d.x += d.vx; d.y += d.vy;
      if (d.x < 0) d.x = W; if (d.x > W) d.x = 0;
      if (d.y < 0) d.y = H; if (d.y > H) d.y = 0;
      ctx.beginPath();
      ctx.arc(d.x, d.y, d.r, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(240,192,64,${d.a})`;
      ctx.fill();
    });
    requestAnimationFrame(draw);
  }
  draw();
}

// ── BUILD ROUND OF 32 ────────────────────────────────────────────────────────
function buildR32() {
  const container = document.getElementById('r32-list');
  if (!container || typeof R32_FIXTURES === 'undefined') return;

  R32_FIXTURES.forEach(fix => {
    const hFlag = TEAMS[fix.home]?.flag || 'un';
    const aFlag = TEAMS[fix.away]?.flag || 'un';
    const p = fix.preMatchProbs;
    const hasPens = fix.result?.pens;
    const scoreText = fix.result
      ? `${fix.result.homeScore} - ${fix.result.awayScore}`
      : 'VS';

    const card = document.createElement('div');
    card.className = 'match-card completed r32-card';
    card.innerHTML = `
      <div class="match-meta">
        <span class="match-id">MATCH ${fix.id} · <span class="final-badge">FINAL</span>${hasPens ? ' · <span class="pens-badge">AET</span>' : ''}</span>
        <span class="match-venue" title="${fix.venue}">${fix.venue}</span>
        <span class="match-date">${fix.date}</span>
      </div>
      <div class="match-teams">
        <div class="match-team">
          <img class="team-flag" src="${flagUrl(hFlag)}" alt="${fix.home}" loading="lazy">
          <span class="team-name">${fix.home}</span>
        </div>
        <div class="vs-badge scored">${scoreText}</div>
        <div class="match-team away">
          <img class="team-flag" src="${flagUrl(aFlag)}" alt="${fix.away}" loading="lazy">
          <span class="team-name">${fix.away}</span>
        </div>
      </div>
      ${hasPens ? `<div class="pens-result">Penalties: <strong>${hasPens}</strong></div>` : ''}
      <div class="prob-bar-container">
        <div class="prob-labels">
          <span class="home-lbl">Win</span>
          <span class="draw-lbl">Pre-Match Odds</span>
          <span class="away-lbl">Win</span>
        </div>
        <div class="prob-bar">
          <div class="prob-home" style="width:0%" data-w="${p.home}"></div>
          <div class="prob-draw"  style="width:0%" data-w="${p.draw}"></div>
          <div class="prob-away"  style="width:0%" data-w="${p.away}"></div>
        </div>
        <div class="prob-pcts">
          <span class="hp">${p.home}%</span>
          <span class="dp">${p.draw}%</span>
          <span class="ap">${p.away}%</span>
        </div>
      </div>`;
    barObserver.observe(card);
    container.appendChild(card);
  });
}


// -- BUILD KNOCKOUT ROUNDS (R16 / QF) --------------------------------
function buildKnockoutRound(fixtures, containerId) {
  const container = document.getElementById(containerId);
  if (!container || !fixtures) return;
  fixtures.forEach(fix => {
    const hFlag = TEAMS[fix.home]?.flag || 'un';
    const aFlag = TEAMS[fix.away]?.flag || 'un';
    const p = fix.preMatchProbs;
    const hasPens = fix.result?.pens;
    const isCompleted = !!fix.result;
    const scoreText = isCompleted ? fix.result.homeScore + ' - ' + fix.result.awayScore : 'VS';
    const card = document.createElement('div');
    card.className = 'match-card ' + (isCompleted ? 'completed' : '') + ' r32-card';
    const penHtml = hasPens ? '<div class="pens-result">Penalties: <strong>' + hasPens + '</strong></div>' : '';
    card.innerHTML =
      '<div class="match-meta"><span class="match-id">MATCH ' + fix.id +
      (isCompleted ? ' &middot; <span class="final-badge">FINAL</span>' : '') +
      (hasPens ? ' &middot; <span class="pens-badge">AET</span>' : '') + '</span>' +
      '<span class="match-venue">' + fix.venue + '</span>' +
      '<span class="match-date">' + fix.date + '</span></div>' +
      '<div class="match-teams">' +
      '<div class="match-team"><img class="team-flag" src="' + flagUrl(hFlag) + '" alt="' + fix.home + '" loading="lazy"><span class="team-name">' + fix.home + '</span></div>' +
      '<div class="vs-badge ' + (isCompleted ? 'scored' : '') + '">' + scoreText + '</div>' +
      '<div class="match-team away"><img class="team-flag" src="' + flagUrl(aFlag) + '" alt="' + fix.away + '" loading="lazy"><span class="team-name">' + fix.away + '</span></div></div>' +
      penHtml +
      '<div class="prob-bar-container"><div class="prob-labels">' +
      '<span class="home-lbl">Win</span><span class="draw-lbl">' + (isCompleted ? 'Pre-Match Odds' : 'Draw') + '</span><span class="away-lbl">Win</span></div>' +
      '<div class="prob-bar">' +
      '<div class="prob-home" style="width:0%" data-w="' + p.home + '"></div>' +
      '<div class="prob-draw" style="width:0%" data-w="' + p.draw + '"></div>' +
      '<div class="prob-away" style="width:0%" data-w="' + p.away + '"></div></div>' +
      '<div class="prob-pcts"><span class="hp">' + p.home + '%</span>' +
      '<span class="dp">' + p.draw + '%</span><span class="ap">' + p.away + '%</span></div></div>';
    barObserver.observe(card);
    container.appendChild(card);
  });
}
function buildR16() {
  if (typeof R16_FIXTURES !== 'undefined') buildKnockoutRound(R16_FIXTURES, 'r16-list');
}
function buildQF() {
  if (typeof QF_FIXTURES !== 'undefined') buildKnockoutRound(QF_FIXTURES, 'qf-list');
}
function buildSF() {
  if (typeof SF_FIXTURES !== 'undefined') buildKnockoutRound(SF_FIXTURES, 'sf-list');
}

// -- INIT ------------------------------------------------------------------
document.addEventListener('DOMContentLoaded', () => {
  initParticles();
  buildWinner();
  buildContenders();
  if (typeof buildKnockoutBracket === 'function') buildKnockoutBracket();
  buildSF();
  buildQF();
  buildR16();
  buildR32();
  buildGroups();
});
