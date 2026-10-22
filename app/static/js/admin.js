// ==============================================================================
// Admin & Facilitator Dashboard Controller
// ==============================================================================

let currentUser = null;
let currentActiveTopic = null;
let currentQuestionsList = [];

// Initialize on page load
window.addEventListener('DOMContentLoaded', async () => {
  lucide.createIcons();
  await checkAuth();
  await loadOverviewStats();
  await loadTopics();
  if (currentUser && currentUser.role === 'admin') {
    await loadUsers();
  }
  await loadSessions();
});

// --- Authentication & Session Validation ---

async function checkAuth() {
  const token = localStorage.getItem('arena_token');
  try {
    const res = await fetch('/api/auth/me', {
      headers: token ? { 'Authorization': `Bearer ${token}` } : {}
    });

    if (!res.ok) {
      window.location.href = '/login';
      return;
    }

    const data = await res.json();
    currentUser = data.user;

    // Render user profile in header
    document.getElementById('userFullNameDisplay').innerText = currentUser.full_name;
    document.getElementById('heroUserName').innerText = currentUser.full_name.toUpperCase();
    
    const roleBadge = document.getElementById('userRoleBadge');
    const usersTabBtn = document.getElementById('tabBtn-users');
    const mobileUsersTabBtn = document.getElementById('mobileTabBtn-users');
    const quickAddUserBtn = document.getElementById('quickAddUserBtn');

    if (currentUser.role === 'admin') {
      roleBadge.innerText = '👑 ADMINISTRADOR';
      roleBadge.className = 'text-[10px] font-mono px-1.5 py-0.5 rounded bg-amber-950 text-amber-300 border border-amber-800';
      if (usersTabBtn) usersTabBtn.classList.remove('hidden');
      if (mobileUsersTabBtn) mobileUsersTabBtn.classList.remove('hidden');
      if (quickAddUserBtn) quickAddUserBtn.classList.remove('hidden');
    } else {
      roleBadge.innerText = '🎓 FACILITADOR';
      roleBadge.className = 'text-[10px] font-mono px-1.5 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800';
      
      // Strict role check: Facilitators cannot create users or manage roles
      if (usersTabBtn) usersTabBtn.classList.add('hidden');
      if (mobileUsersTabBtn) mobileUsersTabBtn.classList.add('hidden');
      if (quickAddUserBtn) quickAddUserBtn.classList.add('hidden');

      // If user section was somehow open, redirect to overview
      const currentUsersSec = document.getElementById('tab-users');
      if (currentUsersSec && !currentUsersSec.classList.contains('hidden')) {
        switchTab('overview');
      }
    }

  } catch (err) {
    window.location.href = '/login';
  }
}

async function logout() {
  const token = localStorage.getItem('arena_token');
  try {
    await fetch('/api/auth/logout', {
      method: 'POST',
      headers: token ? { 'Authorization': `Bearer ${token}` } : {}
    });
  } catch (e) {}

  localStorage.removeItem('arena_token');
  localStorage.removeItem('arena_user');
  window.location.href = '/login';
}

function getAuthHeaders() {
  const token = localStorage.getItem('arena_token');
  return {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {})
  };
}

// --- Navigation Tabs Switcher ---

function switchTab(tabName) {
  // Role gate: Prevent facilitators from opening the Users tab
  if (tabName === 'users' && (!currentUser || currentUser.role !== 'admin')) {
    alert("Acceso Restringido: Tu perfil de Facilitador no tiene permisos para crear usuarios ni asignar roles.");
    switchTab('overview');
    return;
  }

  const tabs = ['overview', 'topics', 'users', 'sessions'];
  tabs.forEach(t => {
    const sec = document.getElementById(`tab-${t}`);
    const btn = document.getElementById(`tabBtn-${t}`);
    const mobBtn = document.getElementById(`mobileTabBtn-${t}`);
    if (sec) sec.classList.add('hidden');
    if (btn) {
      btn.className = "tab-btn px-3 py-1.5 rounded-lg text-xs font-orbitron tracking-wider flex items-center gap-1.5 transition-all text-slate-400 hover:text-white";
    }
    if (mobBtn) {
      mobBtn.className = "tab-btn px-2.5 py-1 text-[11px] font-orbitron text-slate-400 whitespace-nowrap";
    }
  });

  const activeSec = document.getElementById(`tab-${tabName}`);
  const activeBtn = document.getElementById(`tabBtn-${tabName}`);
  const activeMobBtn = document.getElementById(`mobileTabBtn-${tabName}`);
  if (activeSec) activeSec.classList.remove('hidden');
  if (activeBtn) {
    activeBtn.className = "tab-btn px-3 py-1.5 rounded-lg text-xs font-orbitron tracking-wider flex items-center gap-1.5 transition-all text-cyan-400 bg-cyan-950/60 border border-cyan-500/40";
  }
  if (activeMobBtn) {
    activeMobBtn.className = "tab-btn px-2.5 py-1 text-[11px] font-orbitron text-cyan-400 whitespace-nowrap";
  }
}

// --- Overview & Metrics ---

async function loadOverviewStats() {
  try {
    const res = await fetch('/api/admin/stats', { headers: getAuthHeaders() });
    if (!res.ok) return;
    const stats = await res.json();

    document.getElementById('statActiveRooms').innerText = stats.active_rooms_count;
    document.getElementById('statTotalTopics').innerText = stats.total_topics;
    document.getElementById('statTotalQuestions').innerText = stats.total_questions;
    document.getElementById('statTotalUsers').innerText = stats.total_users;
    document.getElementById('statTotalSessions').innerText = stats.total_sessions;
    document.getElementById('statTotalParticipants').innerText = stats.total_participants;
  } catch (err) {
    console.error("Stats load error:", err);
  }
}

// --- Topics & Evaluations ---

async function loadTopics() {
  try {
    const res = await fetch('/api/admin/topics', { headers: getAuthHeaders() });
    if (!res.ok) return;
    const topics = await res.json();

    renderTopicsGrid(topics);
    renderOverviewTopics(topics);
  } catch (err) {
    console.error("Topics load error:", err);
  }
}

function renderOverviewTopics(topics) {
  const container = document.getElementById('overviewTopicsGrid');
  if (!container) return;
  container.innerHTML = "";

  topics.slice(0, 4).forEach(t => {
    const isActive = t.is_active !== false;
    const card = document.createElement('div');
    card.className = `p-4 rounded-xl bg-slate-900/80 border ${isActive ? 'border-slate-800' : 'border-amber-900/40 opacity-75'} flex flex-col justify-between`;
    card.innerHTML = `
      <div>
        <div class="flex items-center justify-between mb-1.5">
          <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800">${t.badge || 'TEMA'}</span>
          <span class="text-[10px] font-mono font-bold ${isActive ? 'text-emerald-400' : 'text-amber-400'}">
            ${isActive ? '● VISIBLE' : '● OCULTO'}
          </span>
        </div>
        <h4 class="font-orbitron text-sm font-bold text-white">${t.name}</h4>
        <p class="text-xs text-slate-400 font-mono mt-1 line-clamp-2">${t.description || ''}</p>
      </div>
      <div class="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between">
        <span class="text-xs font-mono text-cyan-400">${t.question_count} preguntas</span>
        ${isActive 
          ? `<a href="/host?topic=${t.id}&pin=${t.default_pin}" target="_blank" class="px-2.5 py-1 rounded bg-cyan-500/20 hover:bg-cyan-500 hover:text-slate-950 text-cyan-300 text-xs font-mono font-bold transition-all">
               Lanzar ➔
             </a>`
          : `<span class="text-xs font-mono text-amber-500/70 italic">Oculto</span>`
        }
      </div>
    `;
    container.appendChild(card);
  });
}

function renderTopicsGrid(topics) {
  const container = document.getElementById('topicsGrid');
  if (!container) return;
  container.innerHTML = "";

  if (topics.length === 0) {
    container.innerHTML = `
      <div class="col-span-full text-center py-12 cyber-card rounded-2xl">
        <i data-lucide="layers" class="w-12 h-12 text-slate-600 mx-auto mb-3"></i>
        <h3 class="font-orbitron text-base font-bold text-white mb-1">No hay evaluaciones registradas</h3>
        <p class="text-xs text-slate-400 font-mono mb-4">Crea una nueva evaluación para comenzar a cargar preguntas.</p>
        <button onclick="openNewTopicModal()" class="px-4 py-2 rounded-lg bg-cyan-500 text-slate-950 font-orbitron text-xs font-bold">
          Crear Primera Evaluación
        </button>
      </div>
    `;
    lucide.createIcons();
    return;
  }

  topics.forEach(t => {
    const isActive = t.is_active !== false;
    const safeName = (t.name || '').replace(/'/g, "\\'");
    const card = document.createElement('div');
    card.className = `cyber-card rounded-2xl p-5 flex flex-col justify-between space-y-4 transition-all ${isActive ? 'border-slate-800 hover:border-cyan-500/50' : 'border-amber-900/40 bg-amber-950/10 opacity-80'}`;
    card.innerHTML = `
      <div>
        <div class="flex items-center justify-between mb-2 flex-wrap gap-1.5">
          <div class="flex items-center gap-1.5">
            <span class="text-[11px] font-mono px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800 font-bold">${t.badge || 'CAPACITACIÓN'}</span>
            ${isActive 
              ? `<span class="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950/80 text-emerald-400 border border-emerald-700/60 font-bold flex items-center gap-1">
                   <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                   VISIBLE
                 </span>`
              : `<span class="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-950/80 text-amber-400 border border-amber-700/60 font-bold flex items-center gap-1">
                   <span class="w-1.5 h-1.5 rounded-full bg-amber-400"></span>
                   OCULTO
                 </span>`
            }
          </div>
          <span class="text-xs font-mono px-2 py-0.5 rounded bg-slate-900 text-slate-300 border border-slate-700 font-bold">PIN: ${t.default_pin || 'ZR2026'}</span>
        </div>
        <h3 class="font-orbitron text-base font-bold text-white mb-1">${t.name}</h3>
        <p class="text-xs text-slate-400 font-mono">${t.description || 'Sin descripción.'}</p>
      </div>

      <div class="pt-3 border-t border-slate-800 flex items-center justify-between flex-wrap gap-2">
        <span class="text-xs font-mono text-cyan-400 flex items-center gap-1">
          <i data-lucide="help-circle" class="w-3.5 h-3.5"></i>
          <span>${t.question_count} Preguntas</span>
        </span>

        <div class="flex items-center gap-1.5">
          <!-- Toggle Visibility (Ocultar / Mostrar) -->
          <button onclick="toggleTopicVisibility('${t.id}', ${!isActive})" title="${isActive ? 'Ocultar del selector y de la sala del Host' : 'Hacer visible en el selector y sala del Host'}" class="px-2.5 py-1.5 rounded-lg bg-slate-900 border ${isActive ? 'border-slate-700 text-slate-300 hover:border-amber-400 hover:text-amber-300' : 'border-emerald-700/60 text-emerald-400 hover:bg-emerald-950/30'} text-xs font-mono flex items-center gap-1 transition-all">
            <i data-lucide="${isActive ? 'eye-off' : 'eye'}" class="w-3.5 h-3.5 ${isActive ? 'text-amber-400' : 'text-emerald-400'}"></i>
            <span>${isActive ? 'Ocultar' : 'Mostrar'}</span>
          </button>

          <!-- Manage Questions -->
          <button onclick="openQuestionsModal('${t.id}')" title="Administrar banco de preguntas" class="px-2.5 py-1.5 rounded-lg bg-slate-900 border border-slate-700 hover:border-cyan-400 text-xs font-mono text-white flex items-center gap-1 transition-all">
            <i data-lucide="edit-3" class="w-3.5 h-3.5 text-cyan-400"></i>
            <span>Preguntas</span>
          </button>

          <!-- Launch Host Screen -->
          ${isActive 
            ? `<a href="/host?topic=${t.id}&pin=${t.default_pin}" target="_blank" title="Lanzar sala de juego interactiva" class="px-2.5 py-1.5 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-slate-950 text-xs font-orbitron font-bold flex items-center gap-1 transition-all">
                 <i data-lucide="play" class="w-3.5 h-3.5"></i>
                 <span>Lanzar</span>
               </a>`
            : `<button disabled title="Evaluación oculta. Haz clic en 'Mostrar' para habilitarla en vivo." class="px-2.5 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-600 text-xs font-orbitron font-bold flex items-center gap-1 cursor-not-allowed">
                 <i data-lucide="play" class="w-3.5 h-3.5 text-slate-600"></i>
                 <span>Lanzar</span>
               </button>`
          }

          <!-- Delete Topic -->
          <button onclick="deleteTopic('${t.id}', '${safeName}')" title="Eliminar evaluación permanentemente" class="p-1.5 rounded-lg bg-slate-900 border border-slate-700 hover:border-red-500/80 hover:bg-red-950/40 text-slate-400 hover:text-red-400 transition-all cursor-pointer">
            <i data-lucide="trash-2" class="w-3.5 h-3.5"></i>
          </button>
        </div>
      </div>
    `;
    container.appendChild(card);
  });
  lucide.createIcons();
}

// --- Topic Visibility Toggle & Deletion ---

async function toggleTopicVisibility(topicId, newStatus) {
  try {
    const res = await fetch(`/api/admin/topics/${topicId}/visibility`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify({ is_active: newStatus })
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Error al actualizar visibilidad");
    }

    await loadTopics();
    await loadOverviewStats();
  } catch (err) {
    alert("Error: " + err.message);
  }
}

async function deleteTopic(topicId, topicName) {
  const confirmMsg = `¿Estás seguro de que deseas ELIMINAR permanentemente la evaluación:\n\n"${topicName}"?\n\n⚠️ Esta acción borrará todas sus preguntas y no se puede deshacer.`;
  if (!confirm(confirmMsg)) return;

  try {
    const res = await fetch(`/api/admin/topics/${topicId}`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Error al eliminar la evaluación");
    }

    await loadTopics();
    await loadOverviewStats();
  } catch (err) {
    alert("Error: " + err.message);
  }
}

// --- Topic Modal CRUD ---

function openNewTopicModal() {
  document.getElementById('topicForm').reset();
  document.getElementById('topicModalTitle').innerText = "NUEVA EVALUACIÓN / TEMA";
  document.getElementById('topicModal').classList.remove('hidden');
}

document.getElementById('topicForm')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const payload = {
    id: document.getElementById('topicIdInput').value.trim(),
    name: document.getElementById('topicNameInput').value.trim(),
    badge: document.getElementById('topicBadgeInput').value.trim(),
    default_pin: document.getElementById('topicPinInput').value.trim(),
    description: document.getElementById('topicDescInput').value.trim()
  };

  try {
    const res = await fetch('/api/admin/topics', {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Error guardando tema');
    }

    closeModal('topicModal');
    await loadTopics();
    await loadOverviewStats();
  } catch (err) {
    alert("Error: " + err.message);
  }
});

// --- Questions Modal & CRUD ---

async function openQuestionsModal(topicId) {
  currentActiveTopic = topicId;
  const modal = document.getElementById('questionsModal');
  modal.classList.remove('hidden');
  closeQuestionForm();

  try {
    const res = await fetch(`/api/admin/topics/${topicId}`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error("No se pudo cargar la evaluación");
    const topic = await res.json();

    document.getElementById('qModalTopicTitle').innerText = topic.name;
    document.getElementById('qModalTopicBadge').innerText = topic.badge || 'TEMA';
    currentQuestionsList = topic.questions || [];

    renderQuestionsList();
  } catch (err) {
    alert("Error: " + err.message);
  }
}

function renderQuestionsList() {
  const container = document.getElementById('questionsList');
  container.innerHTML = "";

  if (currentQuestionsList.length === 0) {
    container.innerHTML = `
      <div class="text-center py-8 text-slate-500 font-mono text-xs">
        No hay preguntas registradas en este tema. ¡Haz clic en "+ Añadir Pregunta" para crear la primera!
      </div>
    `;
    return;
  }

  currentQuestionsList.forEach((q, idx) => {
    const item = document.createElement('div');
    item.className = "p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2 text-xs font-mono";

    const typeBadge = {
      CHOICE: 'bg-cyan-950 text-cyan-300 border-cyan-800',
      ORDER_SEQUENCE: 'bg-pink-950 text-pink-300 border-pink-800',
      SCENARIO: 'bg-amber-950 text-amber-300 border-amber-800',
      SPEED_TRIAL: 'bg-emerald-950 text-emerald-300 border-emerald-800'
    }[q.type] || 'bg-slate-800 text-slate-300';

    item.innerHTML = `
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <span class="w-6 h-6 rounded bg-slate-800 text-white font-bold flex items-center justify-center font-orbitron">${q.order_num || idx + 1}</span>
          <span class="px-2 py-0.5 rounded border text-[10px] ${typeBadge}">${q.type}</span>
          <span class="text-slate-400 font-bold">${q.category || ''}</span>
        </div>
        <div class="flex items-center gap-2">
          <span class="text-[11px] text-slate-500">⏱️ ${q.time_limit_sec}s | ⭐ ${q.points_base} pts</span>
          <button onclick="editQuestion('${q.id}')" class="p-1 rounded hover:bg-slate-800 text-cyan-400" title="Editar">
            <i data-lucide="edit-2" class="w-3.5 h-3.5"></i>
          </button>
          <button onclick="deleteQuestion('${q.id}')" class="p-1 rounded hover:bg-slate-800 text-red-400" title="Eliminar">
            <i data-lucide="trash-2" class="w-3.5 h-3.5"></i>
          </button>
        </div>
      </div>

      <div class="text-white font-semibold">${q.question_text}</div>

      <div class="grid grid-cols-2 gap-2 text-[11px] pt-1">
        ${(q.options || []).map(opt => `
          <div class="p-1.5 rounded bg-slate-950/80 border border-slate-800 truncate text-slate-300">
            <span class="font-bold text-slate-500">${opt.id}:</span> ${opt.text}
          </div>
        `).join('')}
      </div>

      ${q.explanation ? `<div class="text-[11px] text-slate-500 italic pt-1">💡 ${q.explanation}</div>` : ''}
    `;
    container.appendChild(item);
  });
  lucide.createIcons();
}

function openQuestionForm(qData = null) {
  const form = document.getElementById('questionForm');
  form.reset();
  document.getElementById('qTopicId').value = currentActiveTopic;
  document.getElementById('questionFormContainer').classList.remove('hidden');

  if (qData) {
    document.getElementById('qFormTitle').innerText = "EDITAR PREGUNTA";
    document.getElementById('qId').value = qData.id || '';
    document.getElementById('qOrderNum').value = qData.order_num || 1;
    document.getElementById('qType').value = qData.type || 'CHOICE';
    document.getElementById('qCategory').value = qData.category || '';
    document.getElementById('qTitle').value = qData.title || '';
    document.getElementById('qText').value = qData.question_text || '';
    document.getElementById('qTimeLimit').value = qData.time_limit_sec || 25;
    document.getElementById('qPoints').value = qData.points_base || 1000;
    document.getElementById('qExplanation').value = qData.explanation || '';

    const opts = qData.options || [];
    if (opts[0]) document.getElementById('optA').value = opts[0].text;
    if (opts[1]) document.getElementById('optB').value = opts[1].text;
    if (opts[2]) document.getElementById('optC').value = opts[2].text;
    if (opts[3]) document.getElementById('optD').value = opts[3].text;

    document.getElementById('qCorrectChoice').value = qData.correct_answer || 'opt_A';
  } else {
    document.getElementById('qFormTitle').innerText = "AÑADIR PREGUNTA";
    document.getElementById('qId').value = '';
    document.getElementById('qOrderNum').value = currentQuestionsList.length + 1;
  }

  toggleQuestionOptionsUI();
}

function closeQuestionForm() {
  document.getElementById('questionFormContainer').classList.add('hidden');
}

function toggleQuestionOptionsUI() {
  const type = document.getElementById('qType').value;
  const isSpeedTrial = type === 'SPEED_TRIAL';
  const isSequence = type === 'ORDER_SEQUENCE';

  document.getElementById('optC_container').style.display = isSpeedTrial ? 'none' : 'block';
  document.getElementById('optD_container').style.display = isSpeedTrial ? 'none' : 'block';

  document.getElementById('correctChoiceUI').style.display = isSequence ? 'none' : 'block';
  document.getElementById('correctOrderUI').style.display = isSequence ? 'block' : 'none';
}

function editQuestion(qId) {
  const q = currentQuestionsList.find(item => item.id === qId);
  if (q) openQuestionForm(q);
}

document.getElementById('questionForm')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const qType = document.getElementById('qType').value;
  const isSpeedTrial = qType === 'SPEED_TRIAL';
  const isSequence = qType === 'ORDER_SEQUENCE';

  const options = [
    { id: 'opt_A', text: document.getElementById('optA').value.trim() },
    { id: 'opt_B', text: document.getElementById('optB').value.trim() }
  ];

  if (!isSpeedTrial) {
    options.push({ id: 'opt_C', text: document.getElementById('optC').value.trim() || 'Opción C' });
    options.push({ id: 'opt_D', text: document.getElementById('optD').value.trim() || 'Opción D' });
  }

  const payload = {
    id: document.getElementById('qId').value.trim() || undefined,
    topic_id: document.getElementById('qTopicId').value,
    order_num: parseInt(document.getElementById('qOrderNum').value) || 1,
    type: qType,
    category: document.getElementById('qCategory').value.trim(),
    title: document.getElementById('qTitle').value.trim(),
    question_text: document.getElementById('qText').value.trim(),
    options: options,
    correct_answer: isSequence ? null : document.getElementById('qCorrectChoice').value,
    correct_order: isSequence ? ['opt_A', 'opt_B', 'opt_C', 'opt_D'] : null,
    explanation: document.getElementById('qExplanation').value.trim(),
    time_limit_sec: parseInt(document.getElementById('qTimeLimit').value) || 25,
    points_base: parseInt(document.getElementById('qPoints').value) || 1000
  };

  try {
    const res = await fetch('/api/admin/questions', {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Error guardando pregunta');
    }

    closeQuestionForm();
    await openQuestionsModal(currentActiveTopic);
    await loadTopics();
    await loadOverviewStats();
  } catch (err) {
    alert("Error: " + err.message);
  }
});

async function deleteQuestion(qId) {
  if (!confirm("¿Seguro que deseas eliminar esta pregunta?")) return;
  try {
    const res = await fetch(`/api/admin/questions/${qId}`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    });
    if (!res.ok) throw new Error("Error eliminando pregunta");
    await openQuestionsModal(currentActiveTopic);
    await loadTopics();
    await loadOverviewStats();
  } catch (err) {
    alert("Error: " + err.message);
  }
}

// --- Users Management (Admin Only) ---

async function loadUsers() {
  try {
    const res = await fetch('/api/admin/users', { headers: getAuthHeaders() });
    if (!res.ok) return;
    const users = await res.json();

    const tbody = document.getElementById('usersTableBody');
    if (!tbody) return;
    tbody.innerHTML = "";

    users.forEach(u => {
      const tr = document.createElement('tr');
      tr.className = "hover:bg-slate-900/50 transition-colors";
      
      const roleBadge = u.role === 'admin' 
        ? '<span class="px-2 py-0.5 rounded bg-amber-950 text-amber-300 border border-amber-800 font-bold">👑 ADMIN</span>'
        : '<span class="px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800 font-bold">🎓 FACILITADOR</span>';

      const statusBadge = u.is_active
        ? '<span class="text-emerald-400 font-bold">● Activo</span>'
        : '<span class="text-red-400 font-bold">● Inactivo</span>';

      tr.innerHTML = `
        <td class="p-3.5 text-white font-bold">${u.full_name}</td>
        <td class="p-3.5 text-slate-400">${u.username}</td>
        <td class="p-3.5 text-slate-400">${u.email}</td>
        <td class="p-3.5">${roleBadge}</td>
        <td class="p-3.5">${statusBadge}</td>
        <td class="p-3.5 text-right space-x-1">
          <button onclick="toggleUserStatus('${u.id}', ${!u.is_active})" class="px-2 py-1 rounded bg-slate-900 hover:bg-slate-800 border border-slate-700 text-[11px] text-slate-300" title="Cambiar Estado">
            ${u.is_active ? 'Desactivar' : 'Activar'}
          </button>
          <button onclick="deleteUser('${u.id}')" class="px-2 py-1 rounded bg-red-950/80 hover:bg-red-900 border border-red-800 text-[11px] text-red-300" title="Eliminar">
            Eliminar
          </button>
        </td>
      `;
      tbody.appendChild(tr);
    });

  } catch (err) {
    console.error("Users load error:", err);
  }
}

function openNewUserModal() {
  if (!currentUser || currentUser.role !== 'admin') {
    alert("Permiso denegado: Solo el perfil de Administrador puede crear usuarios y asignar roles.");
    return;
  }
  document.getElementById('userForm').reset();
  document.getElementById('userModal').classList.remove('hidden');
}

document.getElementById('userForm')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const payload = {
    full_name: document.getElementById('uFullName').value.trim(),
    email: document.getElementById('uEmail').value.trim(),
    username: document.getElementById('uUsername').value.trim(),
    password: document.getElementById('uPassword').value,
    role: document.getElementById('uRole').value
  };

  try {
    const res = await fetch('/api/admin/users', {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Error creando usuario');
    }

    closeModal('userModal');
    await loadUsers();
    await loadOverviewStats();
  } catch (err) {
    alert("Error: " + err.message);
  }
});

async function toggleUserStatus(userId, newStatus) {
  try {
    const res = await fetch(`/api/admin/users/${userId}/status`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify({ is_active: newStatus })
    });
    if (!res.ok) throw new Error("Error cambiando estado");
    await loadUsers();
  } catch (err) {
    alert("Error: " + err.message);
  }
}

async function deleteUser(userId) {
  if (!confirm("¿Seguro que deseas eliminar a este usuario del sistema?")) return;
  try {
    const res = await fetch(`/api/admin/users/${userId}`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Error eliminando usuario");
    }
    await loadUsers();
    await loadOverviewStats();
  } catch (err) {
    alert("Error: " + err.message);
  }
}

// --- Sessions & Reports ---

async function loadSessions() {
  try {
    const res = await fetch('/api/admin/sessions', { headers: getAuthHeaders() });
    if (!res.ok) return;
    const sessions = await res.json();

    const tbody = document.getElementById('sessionsTableBody');
    if (!tbody) return;
    tbody.innerHTML = "";

    if (sessions.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" class="p-6 text-center text-slate-500">No hay sesiones de juego registradas aún.</td></tr>`;
      return;
    }

    sessions.forEach(s => {
      const tr = document.createElement('tr');
      tr.className = "hover:bg-slate-900/50 transition-colors";
      const dateStr = s.created_at ? new Date(s.created_at).toLocaleString() : '---';

      tr.innerHTML = `
        <td class="p-3.5 font-orbitron font-bold text-cyan-300">${s.room_code}</td>
        <td class="p-3.5 text-white font-semibold">${s.title}</td>
        <td class="p-3.5"><span class="px-2 py-0.5 rounded bg-slate-900 border border-slate-700 text-[10px] text-slate-300">${s.status}</span></td>
        <td class="p-3.5 text-slate-400">${dateStr}</td>
        <td class="p-3.5 text-cyan-400 font-bold">${s.total_participants} jugadores</td>
        <td class="p-3.5 text-slate-300 font-bold">${s.avg_score} pts</td>
        <td class="p-3.5 text-right">
          <a href="/api/session/${s.room_code}/export" target="_blank" class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-500/20 hover:bg-emerald-500 text-emerald-300 hover:text-slate-950 border border-emerald-500/40 font-orbitron text-[11px] font-bold transition-all">
            <i data-lucide="download" class="w-3.5 h-3.5"></i>
            <span>EXCEL / CSV</span>
          </a>
        </td>
      `;
      tbody.appendChild(tr);
    });
    lucide.createIcons();

  } catch (err) {
    console.error("Sessions load error:", err);
  }
}

// --- Helpers ---

function closeModal(modalId) {
  const m = document.getElementById(modalId);
  if (m) m.classList.add('hidden');
}
