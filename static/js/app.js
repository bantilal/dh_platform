/* ═══════════════════════════════════════════
   Digital Heroes — Core JS
   API base: /api/
═══════════════════════════════════════════ */

const API = '/api/';

/* ── Token helpers ─────────────────────────── */
const Auth = {
  save(tokens, user) {
    localStorage.setItem('dh_access',  tokens.access);
    localStorage.setItem('dh_refresh', tokens.refresh);
    localStorage.setItem('dh_user',    JSON.stringify(user));
  },
  clear() {
    localStorage.removeItem('dh_access');
    localStorage.removeItem('dh_refresh');
    localStorage.removeItem('dh_user');
  },
  token()  { return localStorage.getItem('dh_access'); },
  user()   { try { return JSON.parse(localStorage.getItem('dh_user')); } catch { return null; } },
  isAuth() { return !!this.token(); },
  isAdmin(){ const u = this.user(); return u && u.role === 'admin'; },
  isSub()  { const u = this.user(); return u && (u.role === 'subscriber' || u.role === 'admin'); },
};

/* ── HTTP helpers ──────────────────────────── */
async function apiPost(endpoint, body = {}, isForm = false) {
  const headers = {};
  if (Auth.token()) headers['Authorization'] = `Bearer ${Auth.token()}`;
  if (!isForm) headers['Content-Type'] = 'application/json';

  const res = await fetch(API + endpoint, {
    method: 'POST',
    headers,
    body: isForm ? body : JSON.stringify(body),
  });
  return res.json();
}

async function apiGet(endpoint) {
  const headers = {};
  if (Auth.token()) headers['Authorization'] = `Bearer ${Auth.token()}`;
  const res = await fetch(API + endpoint, { headers });
  return res.json();
}

/* ── Toast notifications ───────────────────── */
function showToast(msg, type = 'success') {
  const existing = document.querySelector('.dh-toast');
  if (existing) existing.remove();

  const el = document.createElement('div');
  el.className = `dh-toast alert alert-${type}`;
  el.style.cssText = `
    position:fixed; top:20px; right:20px; z-index:9999;
    min-width:280px; max-width:380px;
    animation: fadeUp 0.3s ease;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
  `;
  const icons = { success: '✅', error: '⚠️', info: 'ℹ️', warning: '⚡' };
  el.innerHTML = `<span>${icons[type] || '●'}</span> ${msg}`;
  document.body.appendChild(el);
  setTimeout(() => el.remove(), 4000);
}

/* ── Loader ────────────────────────────────── */
function setLoading(btn, loading) {
  if (!btn) return;
  if (loading) {
    btn._orig = btn.innerHTML;
    btn.innerHTML = '<span class="spinner"></span> Loading…';
    btn.disabled = true;
  } else {
    btn.innerHTML = btn._orig || btn.innerHTML;
    btn.disabled = false;
  }
}

/* ── Sidebar toggle (mobile) ───────────────── */
function initSidebar() {
  const sidebar  = document.querySelector('.sidebar');
  const overlay  = document.querySelector('.sidebar-overlay');
  const hamburger = document.querySelector('.hamburger');
  if (!sidebar) return;

  hamburger?.addEventListener('click', () => {
    sidebar.classList.toggle('open');
    overlay?.classList.toggle('open');
  });
  overlay?.addEventListener('click', () => {
    sidebar.classList.remove('open');
    overlay.classList.remove('open');
  });

  // Mark active nav item
  const path = window.location.pathname;
  document.querySelectorAll('.nav-item[data-href]').forEach(item => {
    if (item.dataset.href && path.startsWith(item.dataset.href)) {
      item.classList.add('active');
    }
  });

  // Fill user info in sidebar
  const user = Auth.user();
  if (user) {
    const nameEl = document.querySelector('.user-name');
    const roleEl = document.querySelector('.user-role');
    const avatarEl = document.querySelector('.user-avatar');
    if (nameEl) nameEl.textContent = user.first_name + ' ' + (user.last_name || '');
    if (roleEl) roleEl.textContent = user.role.charAt(0).toUpperCase() + user.role.slice(1);
    if (avatarEl) avatarEl.textContent = (user.first_name[0] + (user.last_name?.[0] || '')).toUpperCase();
  }
}

/* ── Guard: redirect if not logged in ─────── */
function requireAuth() {
  if (!Auth.isAuth()) {
    window.location.href = '/login/';
    return false;
  }
  return true;
}
function requireAdmin() {
  if (!Auth.isAuth() || !Auth.isAdmin()) {
    window.location.href = '/login/';
    return false;
  }
  return true;
}

/* ── Format helpers ────────────────────────── */
function fmtDate(str)   { return str ? new Date(str).toLocaleDateString('en-GB', {day:'numeric',month:'short',year:'numeric'}) : '—'; }
function fmtMoney(val)  { return '£' + parseFloat(val || 0).toFixed(2); }
function fmtScore(n)    {
  const hue = 100 + (n / 45) * 80;
  return `<div class="score-ball" style="background:hsl(${hue},55%,35%);color:#fff;">${n}</div>`;
}
function statusBadge(s) {
  const map = { active:'green', approved:'green', paid:'green', monthly:'violet', yearly:'gold',
                pending:'gold', expired:'red', cancelled:'red', rejected:'red', published:'green',
                draft:'gray', simulated:'violet' };
  return `<span class="badge badge-${map[s]||'gray'}">${s}</span>`;
}

/* ── Pagination helper ─────────────────────── */
function renderPagination(container, current, total, onPage) {
  if (total <= 1) { container.innerHTML = ''; return; }
  let html = '<div class="flex-row" style="gap:6px;justify-content:center;margin-top:20px;">';
  if (current > 1)    html += `<button class="btn btn-ghost btn-sm" onclick="(${onPage})(${current-1})">← Prev</button>`;
  html += `<span class="text-muted text-sm" style="padding:0 8px;">Page ${current} of ${total}</span>`;
  if (current < total) html += `<button class="btn btn-ghost btn-sm" onclick="(${onPage})(${current+1})">Next →</button>`;
  html += '</div>';
  container.innerHTML = html;
}

/* ── Init on DOM ready ─────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  initSidebar();
});
