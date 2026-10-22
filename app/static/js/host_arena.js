// Host Arena Controller

let socket = null;
let currentRoomCode = "ZR2026";
let activeQuestion = null;
const avatarEmojis = {
  cyber_scout: "🤖",
  talent_hunter: "⚡",
  quantum_ai: "🧠",
  matrix_scout: "🎯"
};

const optionStyles = [
  { border: "border-cyan-400", bg: "bg-cyan-950/40", text: "text-cyan-300", badge: "bg-cyan-500 text-slate-950", icon: "▲", name: "opt-cyan" },
  { border: "border-pink-500", bg: "bg-pink-950/40", text: "text-pink-300", badge: "bg-pink-500 text-slate-950", icon: "◆", name: "opt-magenta" },
  { border: "border-amber-400", bg: "bg-amber-950/40", text: "text-amber-300", badge: "bg-amber-500 text-slate-950", icon: "●", name: "opt-amber" },
  { border: "border-emerald-400", bg: "bg-emerald-950/40", text: "text-emerald-300", badge: "bg-emerald-500 text-slate-950", icon: "■", name: "opt-green" }
];

// Initialize on page load
window.addEventListener('DOMContentLoaded', async () => {
  lucide.createIcons();
  setupAudioButton();
  await setupNetworkAndQR();
  connectWebSocket();
  bindHostButtons();
});

function setupAudioButton() {
  const btn = document.getElementById('audioToggleBtn');
  const icon = document.getElementById('audioIcon');
  const text = document.getElementById('audioText');

  btn.addEventListener('click', () => {
    const isMuted = cyberAudio.toggleMute();
    if (isMuted) {
      text.innerText = "SONIDO: OFF";
      btn.classList.add('opacity-50');
    } else {
      text.innerText = "SONIDO: ON";
      btn.classList.remove('opacity-50');
      cyberAudio.playTone(600, 'sine', 0.1);
    }
  });
}

async function setupNetworkAndQR() {
  try {
    const res = await fetch('/api/network-ip');
    const data = await res.json();
    const joinUrl = `${data.join_url}?pin=${currentRoomCode}`;
    
    document.getElementById('joinUrlText').innerText = joinUrl;
    document.getElementById('headerPin').innerText = currentRoomCode;
    document.getElementById('lobbyPinDisplay').innerText = currentRoomCode;

    // Generate QR
    const qrContainer = document.getElementById('qrcode');
    qrContainer.innerHTML = "";
    new QRCode(qrContainer, {
      text: joinUrl,
      width: 140,
      height: 140,
      colorDark: "#070a12",
      colorLight: "#ffffff",
      correctLevel: QRCode.CorrectLevel.M
    });
  } catch (err) {
    console.error("Network config error:", err);
  }
}

function connectWebSocket() {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const wsUrl = `${protocol}//${window.location.host}/ws/${currentRoomCode}/host`;

  socket = new WebSocket(wsUrl);

  socket.onopen = () => {
    console.log("Host WebSocket connected.");
  };

  socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    handleServerMessage(data);
  };

  socket.onclose = () => {
    console.warn("Host WebSocket closed. Reconnecting in 2s...");
    setTimeout(connectWebSocket, 2000);
  };

  socket.onerror = (err) => {
    console.error("Host WS error:", err);
  };
}

function handleServerMessage(data) {
  switch (data.type) {
    case 'ROOM_STATE':
      if (data.players) {
        data.players.forEach(p => renderPlayerTag(p));
        updatePlayerCount(data.players.length);
      }
      break;

    case 'PLAYER_JOINED':
      cyberAudio.playJoin();
      renderPlayerTag(data.player);
      updatePlayerCount(data.total_players);
      break;

    case 'QUESTION_START':
      activeQuestion = data.question;
      showQuestionView(data);
      break;

    case 'TIMER_TICK':
      updateTimer(data.remaining, data.duration);
      cyberAudio.playTick(data.remaining);
      break;

    case 'ANSWER_RECEIVED_COUNT':
      document.getElementById('answersCount').innerText = `${data.answered} / ${data.total}`;
      break;

    case 'REVEAL_RESULTS':
      showRevealView(data);
      break;

    case 'LEADERBOARD_UPDATE':
      showLeaderboardView(data);
      break;

    case 'FINAL_PODIUM':
      showPodiumView(data);
      break;
  }
}

function renderPlayerTag(player) {
  const waitingMsg = document.getElementById('waitingMsg');
  if (waitingMsg) waitingMsg.remove();

  const container = document.getElementById('playerList');
  if (document.getElementById(`player_tag_${player.id}`)) return;

  const tag = document.createElement('div');
  tag.id = `player_tag_${player.id}`;
  tag.className = "flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900/90 border border-cyan-500/40 text-cyan-200 text-xs font-mono shadow-[0_0_10px_rgba(0,240,255,0.2)] animate-pulse";
  
  const emoji = avatarEmojis[player.avatar] || "🤖";
  tag.innerHTML = `
    <span>${emoji}</span>
    <span class="font-bold text-white">${escapeHtml(player.nickname)}</span>
    <span class="text-slate-500 text-[10px]">(${escapeHtml(player.role_or_area || 'CUN')})</span>
  `;
  container.appendChild(tag);
}

function updatePlayerCount(count) {
  document.getElementById('playerCount').innerText = count;
}

function showQuestionView(data) {
  switchView('questionView');
  const q = data.question;

  document.getElementById('questionNumBadge').innerText = `MISIÓN ${data.question_index + 1} DE ${data.total_questions}`;
  document.getElementById('questionCategory').innerText = q.category;
  
  const isOrderMode = (q.type === 'ORDER_SEQUENCE');
  const typeBadge = document.getElementById('questionTypeBadge');
  const orderBanner = document.getElementById('orderModeBanner');

  if (isOrderMode) {
    typeBadge.innerText = "MODO ORDENAR (PUZZLE)";
    typeBadge.className = "px-3 py-1.5 rounded-lg bg-amber-950/60 border border-amber-500/40 text-amber-300 font-mono text-xs uppercase tracking-wider";
    orderBanner.classList.remove('hidden');
  } else {
    typeBadge.innerText = (q.type === 'SPEED_TRIAL') ? "PRUEBA RELÁMPAGO" : "OPCIÓN TÁCTICA";
    typeBadge.className = "px-3 py-1.5 rounded-lg bg-cyan-950/60 border border-cyan-500/40 text-cyan-300 font-mono text-xs uppercase tracking-wider";
    orderBanner.classList.add('hidden');
  }

  document.getElementById('questionTitle').innerText = q.title;
  document.getElementById('questionPrompt').innerText = q.question_text;
  document.getElementById('timerSeconds').innerText = q.time_limit_sec;
  document.getElementById('answersCount').innerText = `0 / ${data.players_count}`;

  // Render 4 options cards
  const grid = document.getElementById('optionsGrid');
  grid.innerHTML = "";

  q.options.forEach((opt, idx) => {
    const style = optionStyles[idx % optionStyles.length];
    const card = document.createElement('div');
    card.id = `host_opt_${opt.id}`;
    card.className = `p-4 md:p-5 rounded-xl border-2 ${style.border} ${style.bg} flex items-center gap-4 transition-all`;
    card.innerHTML = `
      <div class="w-10 h-10 rounded-lg flex items-center justify-center font-orbitron font-black text-lg ${style.badge}">
        ${style.icon}
      </div>
      <div class="flex-1">
        <span class="text-slate-100 font-medium text-sm md:text-base leading-snug">
          ${escapeHtml(opt.text)}
        </span>
      </div>
    `;
    grid.appendChild(card);
  });

  lucide.createIcons();
}

function updateTimer(remaining, duration) {
  const el = document.getElementById('timerSeconds');
  el.innerText = remaining;
  if (remaining <= 5) {
    el.className = "font-orbitron text-2xl font-black text-pink-500 animate-ping";
  } else {
    el.className = "font-orbitron text-2xl font-black text-white";
  }
}

function showRevealView(data) {
  switchView('revealView');
  const q = data.question;
  const container = document.getElementById('revealCorrectContainer');
  container.innerHTML = "";

  document.getElementById('explanationText').innerText = data.explanation;

  if (q.type === 'ORDER_SEQUENCE') {
    // Show correct chronological sequence
    const title = document.createElement('div');
    title.className = "text-xs font-orbitron text-amber-400 tracking-wider mb-2 uppercase";
    title.innerText = "SECUENCIA CRONOLÓGICA CORRECTA:";
    container.appendChild(title);

    const correctIds = data.correct_answer; // Array of IDs
    correctIds.forEach((optId, idx) => {
      const opt = q.options.find(o => o.id === optId);
      const row = document.createElement('div');
      row.className = "flex items-center gap-3 p-3 rounded-lg bg-emerald-950/40 border border-emerald-400 text-emerald-200";
      row.innerHTML = `
        <span class="font-orbitron font-black text-lg px-2.5 py-1 rounded bg-emerald-500 text-slate-950">
          #${idx + 1}
        </span>
        <span class="text-sm font-semibold">${escapeHtml(opt ? opt.text : optId)}</span>
      `;
      container.appendChild(row);
    });
  } else {
    // Single choice / boolean
    const correctOpt = q.options.find(o => o.id === data.correct_answer);
    const box = document.createElement('div');
    box.className = "p-4 rounded-xl bg-emerald-950/50 border-2 border-emerald-400 text-emerald-200 flex items-center gap-3";
    box.innerHTML = `
      <div class="w-8 h-8 rounded-full bg-emerald-400 text-slate-950 flex items-center justify-center font-bold">
        ✓
      </div>
      <div>
        <span class="text-xs font-mono text-emerald-400 block uppercase">OPCIÓN CORRECTA:</span>
        <span class="text-base font-bold text-white">${escapeHtml(correctOpt ? correctOpt.text : data.correct_answer)}</span>
      </div>
    `;
    container.appendChild(box);
  }

  lucide.createIcons();
}

function showLeaderboardView(data) {
  switchView('leaderboardView');
  const list = document.getElementById('leaderboardList');
  list.innerHTML = "";

  const isFinal = (data.question_index + 1 >= data.total_questions);
  document.getElementById('nextBtnText').innerText = isFinal ? "VER PODIO FINAL 🏆" : "SIGUIENTE MISIÓN ➔";

  data.leaderboard.forEach((p, idx) => {
    const row = document.createElement('div');
    const isTop1 = (idx === 0);
    const border = isTop1 ? "border-amber-400 bg-amber-950/30" : "border-slate-800 bg-slate-900/60";
    const rankColor = idx === 0 ? "text-amber-400" : (idx === 1 ? "text-cyan-400" : (idx === 2 ? "text-pink-400" : "text-slate-400"));

    const emoji = avatarEmojis[p.avatar] || "🤖";
    const streakFlame = p.streak >= 2 ? `<span class="text-pink-400 font-bold ml-1">🔥 x${p.streak}</span>` : "";

    row.className = `flex items-center justify-between p-3.5 rounded-xl border ${border} transition-all`;
    row.innerHTML = `
      <div class="flex items-center gap-3">
        <span class="font-orbitron font-extrabold text-lg w-7 ${rankColor}">#${idx + 1}</span>
        <span class="text-2xl">${emoji}</span>
        <div>
          <span class="font-bold text-white text-sm block">${escapeHtml(p.nickname)}</span>
          <span class="text-[11px] text-slate-400 font-mono">${escapeHtml(p.full_name)} ● ${escapeHtml(p.role_or_area || 'CUN')}</span>
        </div>
      </div>
      <div class="text-right">
        <span class="font-orbitron font-extrabold text-base text-cyan-300 block">${p.score.toLocaleString()} pts</span>
        <span class="text-[10px] text-slate-400 font-mono">${p.correct_answers} aciertos ${streakFlame}</span>
      </div>
    `;
    list.appendChild(row);
  });
}

function showPodiumView(data) {
  switchView('podiumView');
  cyberAudio.playPodium();

  // Trigger celebration confetti
  confetti({
    particleCount: 150,
    spread: 80,
    origin: { y: 0.6 }
  });

  const podium = data.podium || [];

  if (podium[0]) {
    document.getElementById('podium1Name').innerText = podium[0].nickname;
    document.getElementById('podium1Score').innerText = `${podium[0].score.toLocaleString()} pts`;
    document.getElementById('podium1Avatar').innerText = avatarEmojis[podium[0].avatar] || "👑";
  }
  if (podium[1]) {
    document.getElementById('podium2Name').innerText = podium[1].nickname;
    document.getElementById('podium2Score').innerText = `${podium[1].score.toLocaleString()} pts`;
    document.getElementById('podium2Avatar').innerText = avatarEmojis[podium[1].avatar] || "⚡";
  }
  if (podium[2]) {
    document.getElementById('podium3Name').innerText = podium[2].nickname;
    document.getElementById('podium3Score').innerText = `${podium[2].score.toLocaleString()} pts`;
    document.getElementById('podium3Avatar').innerText = avatarEmojis[podium[2].avatar] || "🧠";
  }

  // Set export download link
  document.getElementById('exportBtn').href = `/api/session/${currentRoomCode}/export`;
}

function bindHostButtons() {
  document.getElementById('startGameBtn').addEventListener('click', () => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({ action: "START_GAME" }));
    }
  });

  document.getElementById('forceRevealBtn').addEventListener('click', () => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({ action: "REVEAL_RESULTS" }));
    }
  });

  document.getElementById('toLeaderboardBtn').addEventListener('click', () => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({ action: "SHOW_LEADERBOARD" }));
    }
  });

  document.getElementById('nextQuestionBtn').addEventListener('click', () => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({ action: "NEXT_QUESTION" }));
    }
  });
}

function switchView(viewId) {
  ['lobbyView', 'questionView', 'revealView', 'leaderboardView', 'podiumView'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.classList.add('hidden');
  });
  const activeEl = document.getElementById(viewId);
  if (activeEl) activeEl.classList.remove('hidden');
}

function escapeHtml(text) {
  if (!text) return "";
  const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
  return String(text).replace(/[&<>"']/g, m => map[m]);
}
