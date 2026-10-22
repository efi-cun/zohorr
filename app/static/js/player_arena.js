// Player Arena Controller

let socket = null;
let playerData = null;
let activeQuestion = null;
let selectedOrder = []; // Array of option IDs selected in sequence

const avatarEmojis = {
  cyber_scout: "🤖",
  talent_hunter: "⚡",
  quantum_ai: "🧠",
  matrix_scout: "🎯"
};

window.addEventListener('DOMContentLoaded', () => {
  lucide.createIcons();
  loadPlayerProfile();
  connectWebSocket();
  bindPlayerEvents();
});

function loadPlayerProfile() {
  const urlParams = new URLSearchParams(window.location.search);
  const pinParam = urlParams.get('pin');
  const idParam = urlParams.get('id');

  const stored = sessionStorage.getItem('cyber_player');
  if (stored) {
    playerData = JSON.parse(stored);
  } else if (pinParam && idParam) {
    playerData = {
      id: idParam,
      room_code: pinParam.toUpperCase(),
      nickname: "Operador",
      avatar: "cyber_scout"
    };
  } else {
    // No session found, return to registration
    window.location.href = "/";
    return;
  }

  // Populate UI headers
  const emoji = avatarEmojis[playerData.avatar] || "🤖";
  document.getElementById('playerAvatarHeader').innerText = emoji;
  document.getElementById('playerNickHeader').innerText = playerData.nickname;
  document.getElementById('playerPinDisplay').innerText = playerData.room_code;
  document.getElementById('lobbyLargeAvatar').innerText = emoji;
  document.getElementById('lobbyPlayerName').innerText = playerData.nickname;
}

function connectWebSocket() {
  if (!playerData) return;
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const wsUrl = `${protocol}//${window.location.host}/ws/${playerData.room_code}/player?client_id=${playerData.id}`;

  socket = new WebSocket(wsUrl);

  socket.onopen = () => {
    console.log("Player connected to Arena WebSocket.");
  };

  socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    handleServerMessage(data);
  };

  socket.onclose = () => {
    console.warn("Player WS disconnected. Retrying in 2s...");
    setTimeout(connectWebSocket, 2000);
  };

  socket.onerror = (err) => {
    console.error("Player WS error:", err);
  };
}

function handleServerMessage(data) {
  switch (data.type) {
    case 'JOIN_SUCCESS':
      if (data.player) {
        updateScoreHeader(data.player.score, data.player.streak);
      }
      break;

    case 'QUESTION_ACTIVE':
      activeQuestion = data.question;
      setupQuestionView(data);
      break;

    case 'TIMER_TICK':
      document.getElementById('playerTimer').innerText = `${data.remaining}s`;
      cyberAudio.playTick(data.remaining);
      break;

    case 'ANSWER_ACKNOWLEDGED':
      switchView('playerSubmittedView');
      updateScoreHeader(data.total_score, data.streak);
      break;

    case 'ROUND_FEEDBACK':
      showRoundFeedback(data);
      break;

    case 'FINAL_PODIUM_PLAYER':
      showFinalView(data);
      break;
  }
}

function setupQuestionView(data) {
  switchView('playerQuestionView');
  selectedOrder = [];
  const q = data.question;

  document.getElementById('playerQIndex').innerText = `MISIÓN ${data.question_index + 1} DE ${data.total_questions}`;
  document.getElementById('playerTimer').innerText = `${q.time_limit_sec}s`;

  const orderContainer = document.getElementById('playerOrderContainer');
  const choiceGrid = document.getElementById('playerChoiceGrid');

  if (q.type === 'ORDER_SEQUENCE') {
    // Show order sequence UI
    choiceGrid.classList.add('hidden');
    orderContainer.classList.remove('hidden');
    renderOrderOptions(q.options);
  } else {
    // Show standard choice buttons
    orderContainer.classList.add('hidden');
    choiceGrid.classList.remove('hidden');
    setupChoiceButtons(q.options);
  }

  lucide.createIcons();
}

function renderOrderOptions(options) {
  const list = document.getElementById('orderCardsList');
  list.innerHTML = "";
  updateConfirmButton();

  // Create shuffled clone for ordering challenge
  const shuffled = [...options].sort(() => Math.random() - 0.5);

  shuffled.forEach((opt) => {
    const card = document.createElement('div');
    card.id = `order_card_${opt.id}`;
    card.className = "cyber-btn-opt p-3.5 rounded-xl border border-slate-700 bg-slate-900/90 flex items-center justify-between transition-all cursor-pointer";
    card.innerHTML = `
      <span class="text-sm font-semibold text-slate-200 select-none">${escapeHtml(opt.text)}</span>
      <div id="badge_${opt.id}" class="w-8 h-8 rounded-lg border border-slate-700 bg-slate-800 flex items-center justify-center font-orbitron font-black text-sm text-slate-500">
        -
      </div>
    `;

    card.addEventListener('click', () => {
      toggleOrderSelection(opt.id);
    });

    list.appendChild(card);
  });
}

function toggleOrderSelection(optId) {
  cyberAudio.playOrderSnap();

  // If already in list, deselect
  const existingIndex = selectedOrder.indexOf(optId);
  if (existingIndex !== -1) {
    selectedOrder.splice(existingIndex, 1);
  } else {
    // Add to sequence
    if (selectedOrder.length < 4) {
      selectedOrder.push(optId);
    }
  }

  // Re-render badges
  activeQuestion.options.forEach(opt => {
    const badge = document.getElementById(`badge_${opt.id}`);
    const card = document.getElementById(`order_card_${opt.id}`);
    const idx = selectedOrder.indexOf(opt.id);

    if (badge && card) {
      if (idx !== -1) {
        badge.innerText = `#${idx + 1}`;
        badge.className = "w-8 h-8 rounded-lg border-2 border-amber-400 bg-amber-500 text-slate-950 flex items-center justify-center font-orbitron font-black text-sm shadow-[0_0_10px_rgba(255,184,0,0.5)]";
        card.className = "cyber-btn-opt p-3.5 rounded-xl border-2 border-amber-500 bg-amber-950/40 flex items-center justify-between transition-all cursor-pointer";
      } else {
        badge.innerText = "-";
        badge.className = "w-8 h-8 rounded-lg border border-slate-700 bg-slate-800 flex items-center justify-center font-orbitron font-black text-sm text-slate-500";
        card.className = "cyber-btn-opt p-3.5 rounded-xl border border-slate-700 bg-slate-900/90 flex items-center justify-between transition-all cursor-pointer";
      }
    }
  });

  updateConfirmButton();
}

function updateConfirmButton() {
  const btn = document.getElementById('confirmOrderBtn');
  const count = selectedOrder.length;
  btn.innerText = `CONFIRMAR ORDEN (${count}/4)`;
  btn.disabled = (count < 4);
}

function setupChoiceButtons(options) {
  ['choice_opt_A', 'choice_opt_B', 'choice_opt_C', 'choice_opt_D'].forEach((btnId, idx) => {
    const btn = document.getElementById(btnId);
    if (!btn) return;

    if (options[idx]) {
      btn.style.display = "flex";
      // Clear previous event listener
      const newBtn = btn.cloneNode(true);
      btn.parentNode.replaceChild(newBtn, btn);

      newBtn.addEventListener('click', () => {
        submitChoiceAnswer(options[idx].id);
      });
    } else {
      btn.style.display = "none";
    }
  });
}

function submitChoiceAnswer(optionId) {
  cyberAudio.playOrderSnap();
  if (navigator.vibrate) navigator.vibrate(50);

  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify({
      action: "SUBMIT_ANSWER",
      answer: optionId
    }));
  }
}

function submitOrderAnswer() {
  if (selectedOrder.length < 4) return;
  cyberAudio.playOrderSnap();
  if (navigator.vibrate) navigator.vibrate(80);

  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify({
      action: "SUBMIT_ANSWER",
      answer: selectedOrder
    }));
  }
}

function showRoundFeedback(data) {
  switchView('playerFeedbackView');

  const iconBox = document.getElementById('feedbackIconBox');
  const title = document.getElementById('feedbackTitle');
  const pts = document.getElementById('feedbackPoints');
  const rank = document.getElementById('feedbackRank');
  const expl = document.getElementById('feedbackExplanation');

  expl.innerText = data.explanation || "";
  rank.innerText = `Posición actual: Puesto #${data.rank} en la Arena`;
  updateScoreHeader(data.total_score, data.streak);

  if (data.is_correct) {
    cyberAudio.playCorrect();
    iconBox.className = "w-16 h-16 mx-auto rounded-full bg-emerald-500/20 border-2 border-emerald-400 text-emerald-400 flex items-center justify-center text-3xl shadow-[0_0_20px_rgba(0,255,157,0.4)]";
    iconBox.innerText = "✓";
    title.innerText = "¡ACIERTO CRÍTICO!";
    title.className = "font-orbitron text-xl font-black tracking-wider text-emerald-400 glow-green";
    pts.innerText = `+${data.points_earned.toLocaleString()} PTS`;
    pts.className = "font-orbitron text-lg font-bold text-emerald-300 my-1";
  } else {
    cyberAudio.playWrong();
    iconBox.className = "w-16 h-16 mx-auto rounded-full bg-pink-500/20 border-2 border-pink-500 text-pink-500 flex items-center justify-center text-3xl shadow-[0_0_20px_rgba(255,0,127,0.4)]";
    iconBox.innerText = "✗";
    title.innerText = "¡ERROR DE PROTOCOLO!";
    title.className = "font-orbitron text-xl font-black tracking-wider text-pink-400 glow-magenta";
    pts.innerText = "0 PTS";
    pts.className = "font-orbitron text-lg font-bold text-slate-400 my-1";
  }
}

function showFinalView(data) {
  switchView('playerFinalView');
  cyberAudio.playPodium();

  confetti({
    particleCount: 100,
    spread: 70,
    origin: { y: 0.6 }
  });

  document.getElementById('playerFinalRankDisplay').innerText = `#${data.final_rank} PUESTO`;
  document.getElementById('playerFinalScoreDisplay').innerText = `${data.total_score.toLocaleString()} Puntos Totales`;
}

function updateScoreHeader(score, streak) {
  document.getElementById('playerScoreHeader').innerText = `${score.toLocaleString()} PTS`;
  const streakBadge = document.getElementById('streakBadge');
  if (streak >= 2) {
    streakBadge.innerText = `🔥 x${streak}`;
    streakBadge.classList.remove('hidden');
  } else {
    streakBadge.classList.add('hidden');
  }
}

function bindPlayerEvents() {
  document.getElementById('confirmOrderBtn').addEventListener('click', submitOrderAnswer);
  document.getElementById('resetOrderBtn').addEventListener('click', () => {
    selectedOrder = [];
    if (activeQuestion) {
      renderOrderOptions(activeQuestion.options);
    }
  });
}

function switchView(viewId) {
  ['playerLobbyView', 'playerQuestionView', 'playerSubmittedView', 'playerFeedbackView', 'playerFinalView'].forEach(id => {
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
