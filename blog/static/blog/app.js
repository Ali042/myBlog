// Social-like front-end interactions for My Blog
(function () {
  'use strict';

  // THEME: persist light/dark using data-theme on <html>
  const root = document.documentElement;
  const THEME_KEY = 'myblog-theme';
  function applyTheme(theme) {
    if (theme === 'light') root.setAttribute('data-theme', 'light');
    else root.removeAttribute('data-theme'); // default dark
  }
  const saved = localStorage.getItem(THEME_KEY);
  if (saved) applyTheme(saved);
  else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) {
    applyTheme('light');
  }
  const themeToggle = document.getElementById('theme-toggle');
  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      const isLight = root.getAttribute('data-theme') === 'light';
      const next = isLight ? 'dark' : 'light';
      applyTheme(next);
      localStorage.setItem(THEME_KEY, next);
      themeToggle.textContent = next === 'light' ? '☀️' : '🌙';
    });
    // initialize icon
    themeToggle.textContent = root.getAttribute('data-theme') === 'light' ? '☀️' : '🌙';
  }

  // Smooth in-page anchor scrolling
  document.addEventListener('click', function (e) {
    const a = e.target.closest('a[href^="#"]');
    if (!a) return;
    const id = a.getAttribute('href').slice(1);
    const el = document.getElementById(id);
    if (el) {
      e.preventDefault();
      el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });

  // DETAIL: copy current URL helper
  const copyBtn = document.querySelector('[data-action="copy-link"]');
  if (copyBtn) {
    copyBtn.addEventListener('click', async () => {
      try {
        await navigator.clipboard.writeText(window.location.href);
        copyBtn.textContent = 'Copied!';
        setTimeout(() => (copyBtn.textContent = 'Copy link'), 1500);
      } catch (_) {
        alert('Unable to copy link');
      }
    });
  }

  // CSRF helper (Django)
  function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
  }

  // PROFILE: follow/unfollow toggle
  const followBtn = document.getElementById('follow-toggle');
  if (followBtn) {
    followBtn.addEventListener('click', async () => {
      const username = followBtn.getAttribute('data-username');
      if (!username) return;
      try {
        const res = await fetch(`/u/${username}/follow/`, {
          method: 'POST',
          headers: {
            'X-CSRFToken': getCookie('csrftoken') || '',
            'X-Requested-With': 'XMLHttpRequest',
          },
        });
        if (!res.ok) throw new Error('Failed');
        const data = await res.json();
        followBtn.textContent = data.following ? 'Unfollow' : 'Follow';
        // Update followers count if present
        const stats = document.querySelector('.stats');
        if (stats && typeof data.followers === 'number') {
          const followerChip = Array.from(stats.children).find((c) => c.textContent.includes('followers'));
          if (followerChip) {
            const num = followerChip.querySelector('.num');
            if (num) num.textContent = String(data.followers);
          }
        }
      } catch (e) {
        console.warn('Follow failed', e);
      }
    });
  }

  // PROFILE: modal for followers/following
  document.getElementById('followers-modal')?.addEventListener('click', () => openFollowModal('followers'));
  document.getElementById('following-modal')?.addEventListener('click', () => openFollowModal('following'));

  function openFollowModal(type) {
    const username = document.getElementById(`${type}-modal`)?.getAttribute('data-username');
    if (!username) return;

    const modal = document.getElementById('follow-modal');
    const title = document.getElementById('modal-title');
    const body = document.getElementById('modal-body');

    title.textContent = type === 'followers' ? 'Followers' : 'Following';
    body.innerHTML = '<p>Loading...</p>';
    modal.style.display = 'flex';

    fetch(`/u/${username}/${type}/`)
      .then(res => res.text())
      .then(html => {
        // Extract the list content from the response
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        const listContent = doc.querySelector('.modal-body ul') || doc.querySelector('ul');
        body.innerHTML = listContent ? listContent.outerHTML : '<p>No users found.</p>';
      })
      .catch(err => {
        body.innerHTML = '<p>Error loading users.</p>';
        console.error('Modal load failed:', err);
      });
  }

  // Modal close handlers
  document.getElementById('modal-close')?.addEventListener('click', closeFollowModal);
  document.getElementById('follow-modal')?.addEventListener('click', (e) => {
    if (e.target.id === 'follow-modal') closeFollowModal();
  });

  function closeFollowModal() {
    document.getElementById('follow-modal').style.display = 'none';
  }
})();
