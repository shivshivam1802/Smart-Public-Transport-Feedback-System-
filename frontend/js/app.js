(function () {
  const API_BASE = window.location.origin;

  const $ = (id) => document.getElementById(id);
  const show = (el) => { el.classList.remove('hidden'); };
  const hide = (el) => { el.classList.add('hidden'); };

  function showResult(box, isError, html) {
    const resultBox = $('submit-result');
    resultBox.className = 'result-box ' + (isError ? 'error' : 'success');
    resultBox.innerHTML = html;
    show(resultBox);
  }

  function handleSubmit(e) {
    e.preventDefault();
    const form = $('feedback-form');
    const btn = $('submit-btn');
    const text = ($('feedback-text') && $('feedback-text').value) ? $('feedback-text').value.trim() : '';
    const lat = parseFloat($('lat').value);
    const lon = parseFloat($('lon').value);

    if (!text) {
      showResult($('submit-result'), true, 'Please enter your feedback.');
      return;
    }
    if (Number.isNaN(lat) || Number.isNaN(lon)) {
      showResult($('submit-result'), true, 'Please enter valid latitude and longitude (or use “Use my location”).');
      return;
    }

    btn.disabled = true;
    btn.textContent = 'Submitting…';

    fetch(`${API_BASE}/feedback`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, latitude: lat, longitude: lon }),
    })
      .then((res) => {
        if (!res.ok) throw new Error(res.statusText || 'Submit failed');
        return res.json();
      })
      .then((data) => {
        const issuesHtml = data.issues && data.issues.length
          ? '<div class="issues-list">' + data.issues.map((i) => `<span class="issue-tag">${escapeHtml(i)}</span>`).join('') + '</div>'
          : '<p class="muted">No specific issues detected.</p>';
        showResult(
          $('submit-result'),
          false,
          `<p><strong>${escapeHtml(data.message)}</strong></p>
           <p>Sentiment: <span class="sentiment ${data.sentiment}">${escapeHtml(data.sentiment)}</span></p>
           ${issuesHtml}`
        );
        form.reset();
        loadRecent();
        loadAnalytics();
      })
      .catch((err) => {
        showResult($('submit-result'), true, 'Failed to submit: ' + (err.message || 'Network error. Is the backend running on ' + API_BASE + '?'));
      })
      .finally(() => {
        btn.disabled = false;
        btn.innerHTML = '<span class="btn-icon">→</span> Submit feedback';
      });
  }

  function useLocation() {
    const latInput = $('lat');
    const lonInput = $('lon');
    if (!navigator.geolocation) {
      showResult($('submit-result'), true, 'Geolocation is not supported by your browser.');
      return;
    }
    latInput.value = '';
    lonInput.value = '';
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        latInput.value = pos.coords.latitude.toFixed(4);
        lonInput.value = pos.coords.longitude.toFixed(4);
      },
      () => {
        showResult($('submit-result'), true, 'Could not get your location. Enter coordinates manually.');
      }
    );
  }

  function escapeHtml(s) {
    const div = document.createElement('div');
    div.textContent = s;
    return div.innerHTML;
  }

  function loadAnalytics() {
    const loading = $('analytics-loading');
    const content = $('analytics-content');
    hide(content);
    show(loading);

    fetch(`${API_BASE}/analytics/summary`)
      .then((r) => r.json())
      .then((data) => {
        hide(loading);
        const total = data.total_feedback || 0;
        const bySentiment = data.by_sentiment || {};
        const byIssue = data.by_issue || {};
        const maxIssue = Math.max(0, ...Object.values(byIssue));

        let html = `
          <div class="analytics-block">
            <h3>Total feedback</h3>
            <div class="total">${total}</div>
          </div>
          <div class="analytics-block">
            <h3>By sentiment</h3>
            <div class="bars">
              ${Object.entries(bySentiment).map(([k, v]) => {
                const pct = total ? (v / total * 100).toFixed(0) : 0;
                return `<div class="analytics-bar">
                  <span class="label">${escapeHtml(k)}</span>
                  <span class="bar-wrap"><span class="bar" style="width:${pct}%"></span></span>
                  <span class="count">${v}</span>
                </div>`;
              }).join('') || '<p class="muted">No data yet.</p>'}
            </div>
          </div>
          <div class="analytics-block">
            <h3>By issue</h3>
            <div class="bars">
              ${Object.entries(byIssue).map(([k, v]) => {
                const pct = maxIssue ? (v / maxIssue * 100).toFixed(0) : 0;
                return `<div class="analytics-bar">
                  <span class="label">${escapeHtml(k)}</span>
                  <span class="bar-wrap"><span class="bar" style="width:${pct}%"></span></span>
                  <span class="count">${v}</span>
                </div>`;
              }).join('') || '<p class="muted">No issues detected yet.</p>'}
            </div>
          </div>`;
        content.innerHTML = html;
        show(content);
      })
      .catch(() => {
        hide(loading);
        content.innerHTML = '<p class="muted">Could not load analytics. Is the backend running?</p>';
        show(content);
      });
  }

  function loadHotspots() {
    const loading = $('hotspots-loading');
    const content = $('hotspots-content');
    const empty = $('hotspots-empty');
    hide(content);
    hide(empty);
    show(loading);

    fetch(`${API_BASE}/analytics/clusters`)
      .then((r) => r.json())
      .then((list) => {
        hide(loading);
        if (!list || list.length === 0) {
          show(empty);
          return;
        }
        content.innerHTML = list.map((c) => `
          <div class="hotspot-item">
            <div class="meta">
              <span class="cluster-id">Cluster ${c.cluster_id}</span>
              <span class="count">${c.count} feedback</span>
            </div>
            <div class="coords">${c.center_lat.toFixed(4)}, ${c.center_lon.toFixed(4)}</div>
            <div class="issue-tags">
              ${(c.sample_issues || []).map((i) => `<span class="issue-tag">${escapeHtml(i)}</span>`).join('')}
            </div>
          </div>
        `).join('');
        show(content);
      })
      .catch(() => {
        hide(loading);
        content.innerHTML = '<p class="muted">Could not load hotspots.</p>';
        show(content);
      });
  }

  function loadRecent() {
    const loading = $('recent-loading');
    const content = $('recent-content');
    const empty = $('recent-empty');
    hide(content);
    hide(empty);
    show(loading);

    fetch(`${API_BASE}/feedback?limit=20`)
      .then((r) => r.json())
      .then((list) => {
        hide(loading);
        if (!list || list.length === 0) {
          show(empty);
          return;
        }
        content.innerHTML = list.map((r) => `
          <div class="recent-item">
            <div class="text">${escapeHtml(r.text || '')}</div>
            <span class="sentiment ${(r.sentiment || '').toLowerCase()}">${escapeHtml(r.sentiment || '')}</span>
            <div class="issues-row">
              ${(r.issues || []).map((i) => `<span class="issue-tag">${escapeHtml(i)}</span>`).join('')}
            </div>
          </div>
        `).join('');
        show(content);
      })
      .catch(() => {
        hide(loading);
        content.innerHTML = '<p class="muted">Could not load recent feedback.</p>';
        show(content);
      });
  }

  $('feedback-form').addEventListener('submit', handleSubmit);
  $('use-location').addEventListener('click', useLocation);
  if ($('refresh-analytics')) $('refresh-analytics').addEventListener('click', loadAnalytics);
  if ($('refresh-hotspots')) $('refresh-hotspots').addEventListener('click', loadHotspots);
  if ($('refresh-recent')) $('refresh-recent').addEventListener('click', loadRecent);

  // Nav: set active on hash
  function setActiveNav() {
    const hash = window.location.hash.slice(1) || 'submit';
    document.querySelectorAll('.nav-link').forEach((a) => {
      a.classList.toggle('active', a.getAttribute('href') === '#' + hash);
    });
  }
  window.addEventListener('hashchange', setActiveNav);
  setActiveNav();

  loadAnalytics();
  loadHotspots();
  loadRecent();
})();
