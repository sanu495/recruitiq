// ── Route Guard ───────────────────────────────────────────────────────────────
function requireAuth(allowedRoles = []) {
    const user = User.get();
    const token = Token.get();
  
    if (!user || !token) {
      window.location.href = getRootPath() + 'index.html';
      return null;
    }
  
    if (allowedRoles.length && !allowedRoles.includes(user.role)) {
      if (user.role === 'recruiter') {
        window.location.href = getRootPath() + 'dashboard/recruiter.html';
      } else if (user.role === 'candidate') {
        window.location.href = getRootPath() + 'dashboard/candidate.html';
      }
      return null;
    }
    return user;
  }
  
  function requireGuest() {
    const user = User.get();
    const token = Token.get();
    if (user && token) {
      redirectByRole(user.role);
    }
  }
  
  function redirectByRole(role) {
    const root = getRootPath();
    if (role === 'recruiter' || role === 'admin') {
      window.location.href = root + 'dashboard/recruiter.html';
    } else {
      window.location.href = root + 'dashboard/candidate.html';
    }
  }
  
  function getRootPath() {
    const path = window.location.pathname;
    if (path.includes('/dashboard/') || path.includes('/pages/')) {
      return '../';
    }
    return '';
  }
  
  // ── Toast System ──────────────────────────────────────────────────────────────
  function showToast(message, type = 'info', duration = 3500) {
    let container = document.getElementById('toast-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'toast-container';
      container.className = 'toast-container';
      document.body.appendChild(container);
    }
  
    const icons = {
      success: '✓',
      error:   '✕',
      warning: '⚠',
      info:    'ℹ',
    };
  
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `<span style="font-size:15px;font-weight:700;">${icons[type] || icons.info}</span> ${message}`;
    container.appendChild(toast);
  
    setTimeout(() => {
      toast.style.animation = 'slideIn 0.3s ease reverse';
      setTimeout(() => toast.remove(), 280);
    }, duration);
  }
  
  // ── Sidebar Builder ───────────────────────────────────────────────────────────
  function buildSidebar(activeItem = '') {
    const user = User.get();
    if (!user) return;
  
    const root = getRootPath();
  
    const recruiterNav = [
      { id: 'dashboard', icon: iconDashboard(), label: 'Dashboard',  href: root + 'dashboard/recruiter.html' },
      { id: 'jobs',      icon: iconBriefcase(), label: 'My Jobs',    href: root + 'pages/jobs.html' },
      { id: 'pipeline',  icon: iconPipeline(),  label: 'Pipeline',   href: root + 'pages/pipeline.html' },
      { id: 'interviews',icon: iconCalendar(),  label: 'Interviews', href: root + 'pages/interviews.html' },
      { id: 'analytics', icon: iconChart(),     label: 'Analytics',  href: root + 'pages/analytics.html' },
    ];
  
    const candidateNav = [
      { id: 'dashboard',    icon: iconDashboard(),  label: 'Dashboard',        href: root + 'dashboard/candidate.html' },
      { id: 'jobs',         icon: iconBriefcase(),  label: 'Browse Jobs',      href: root + 'pages/jobs.html' },
      { id: 'applications', icon: iconApps(),       label: 'My Applications',  href: root + 'pages/applications.html' },
      { id: 'interviews',   icon: iconCalendar(),   label: 'Interviews',       href: root + 'pages/interviews.html' },
    ];
  
    const navItems = (user.role === 'candidate') ? candidateNav : recruiterNav;
    const initials = user.name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
  
    const notifCount = document.getElementById('notif-count');
  
    const sidebar = document.getElementById('sidebar');
    if (!sidebar) return;
  
    sidebar.innerHTML = `
      <div class="sidebar-logo">
        <div class="sidebar-logo-icon">
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <rect x="2" y="4" width="6" height="12" rx="3" fill="white" opacity="0.9"/>
            <rect x="10" y="2" width="6" height="14" rx="3" fill="white" opacity="0.6"/>
            <circle cx="17" cy="15" r="3" fill="white" opacity="0.4"/>
          </svg>
        </div>
        <div class="sidebar-logo-text">Recruit<span>IQ</span></div>
      </div>
  
      <nav class="sidebar-nav">
        <div class="nav-section-title">Main Menu</div>
        ${navItems.map(item => `
          <div class="nav-item ${activeItem === item.id ? 'active' : ''}"
               onclick="window.location.href='${item.href}'">
            ${item.icon}
            <span>${item.label}</span>
            ${item.id === 'notifications' ? `<span class="nav-badge" id="notif-badge">0</span>` : ''}
          </div>
        `).join('')}
      </nav>
  
      <div class="sidebar-footer">
        <div class="sidebar-user" onclick="AuthAPI.logout()">
          <div class="user-avatar">${initials}</div>
          <div style="flex:1;min-width:0;">
            <div class="user-name truncate">${user.name}</div>
            <div class="user-role">${capitalize(user.role)}</div>
          </div>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--text-muted)" stroke-width="2">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9"/>
          </svg>
        </div>
      </div>
    `;
  
    loadNotifBadge();
  }
  
  // ── Topbar Builder ────────────────────────────────────────────────────────────
  function buildTopbar(title, subtitle = '') {
    const topbar = document.getElementById('topbar');
    if (!topbar) return;
  
    topbar.innerHTML = `
      <div class="topbar-left">
        <button class="notif-btn" id="menu-toggle" style="display:none;" onclick="toggleSidebar()">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="18" x2="21" y2="18"/>
          </svg>
        </button>
        <div>
          <div class="topbar-title">${title}</div>
          ${subtitle ? `<div class="topbar-subtitle">${subtitle}</div>` : ''}
        </div>
      </div>
      <div class="topbar-right">
        <div class="search-box">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--text-muted)" stroke-width="2">
            <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
          </svg>
          <input type="text" placeholder="Search...">
        </div>
        <div class="notif-btn" id="notif-btn" onclick="window.location.href='${getRootPath()}pages/notifications.html'">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
            <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
          </svg>
          <div class="notif-dot hidden" id="notif-dot"></div>
        </div>
      </div>
    `;
  }
  
  // ── Notification Badge ────────────────────────────────────────────────────────
  async function loadNotifBadge() {
    try {
      const data = await NotifAPI.unreadCount();
      const badge = document.getElementById('notif-badge');
      const dot   = document.getElementById('notif-dot');
      if (data.unread_count > 0) {
        if (badge) { badge.textContent = data.unread_count; badge.style.display = 'inline'; }
        if (dot)   { dot.classList.remove('hidden'); }
      }
    } catch {}
  }
  
  // ── Helpers ───────────────────────────────────────────────────────────────────
  function capitalize(str) {
    return str ? str.charAt(0).toUpperCase() + str.slice(1) : '';
  }
  
  function formatDate(dateStr) {
    if (!dateStr) return '—';
    return new Date(dateStr).toLocaleDateString('en-IN', {
      day: '2-digit', month: 'short', year: 'numeric'
    });
  }
  
  function formatDateTime(dateStr) {
    if (!dateStr) return '—';
    return new Date(dateStr).toLocaleString('en-IN', {
      day: '2-digit', month: 'short', year: 'numeric',
      hour: '2-digit', minute: '2-digit'
    });
  }
  
  function getScoreColor(score) {
    if (!score) return 'var(--text-muted)';
    if (score >= 80) return 'var(--success)';
    if (score >= 60) return 'var(--violet-light)';
    if (score >= 40) return 'var(--warning)';
    return 'var(--danger)';
  }
  
  function getScoreLabel(score) {
    if (!score) return 'Not screened';
    if (score >= 80) return 'Strong Match';
    if (score >= 60) return 'Good Match';
    if (score >= 40) return 'Moderate Match';
    return 'Weak Match';
  }
  
  function stageBadge(stage) {
    return `<span class="badge badge-${stage}">${capitalize(stage)}</span>`;
  }
  
  function statusBadge(status) {
    return `<span class="badge badge-${status}">${capitalize(status)}</span>`;
  }
  
  function toggleSidebar() {
    document.getElementById('sidebar')?.classList.toggle('open');
  }
  
  // ── SVG Icons ─────────────────────────────────────────────────────────────────
  function iconDashboard() {
    return `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
      <rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/>
      <rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/>
    </svg>`;
  }
  function iconBriefcase() {
    return `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
      <rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 7V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v2"/>
    </svg>`;
  }
  function iconPipeline() {
    return `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
      <circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/>
      <line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/>
    </svg>`;
  }
  function iconCalendar() {
    return `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
      <rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/>
      <line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>
    </svg>`;
  }
  function iconChart() {
    return `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
      <line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/>
      <line x1="6" y1="20" x2="6" y2="14"/><line x1="2" y1="20" x2="22" y2="20"/>
    </svg>`;
  }
  function iconApps() {
    return `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
      <polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/>
    </svg>`;
  }