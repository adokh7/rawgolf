/* ============================================================================
   GOLFRAW LOCKER — DRAWER
   ----------------------------------------------------------------------------
   The persistent "My Bag / Locker" slide-out. Thumb-first: the launcher sits
   bottom-right above the safe area, the panel comes in from the right and the
   primary actions sit low where a thumb reaches.

   The site is deliberately light-only and brutalist (hard 2-3px ink borders,
   no radii, flag red for destructive/primary), so the drawer commits to that
   one look rather than inventing a second design language. Every colour is
   stated explicitly so nothing is inherited from a host page.

   Accessibility: role=dialog + aria-modal, focus trap, ESC to close, focus
   returns to the launcher, background gets aria-hidden, 44px minimum targets,
   and all motion collapses under prefers-reduced-motion.

   Exposed as window.GolfrawDrawer.
   ========================================================================== */
(function (root, doc) {
  'use strict';

  var L = root.GolfrawLocker;
  if (!L) { return; }

  var INK = '#101511', PAPER = '#F3F4F0', WHITE = '#fff';
  var FLAG = '#E03E2D', GREY = '#5B665E', LINE = '#DADDD4', FAIRWAY = '#14402A';

  var el = null, panel = null, scrim = null, launcher = null, bodyEl = null;
  var open = false, lastFocus = null, unsubscribe = null, built = false;

  /* -------------------------------------------------------------- icons -- */
  /* Inline SVG, 1.75 stroke throughout — never emoji, which render
     differently per platform and cannot be themed. */
  function icon(path, size) {
    return '<svg viewBox="0 0 24 24" width="' + (size || 22) + '" height="' + (size || 22) +
      '" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" ' +
      'stroke-linejoin="round" aria-hidden="true" focusable="false">' + path + '</svg>';
  }
  var ICON_BAG = icon('<path d="M6 8h12l-1 12H7L6 8Z"/><path d="M9 8V5a3 3 0 0 1 6 0v3"/><path d="M12 12v5"/>');
  var ICON_CLOSE = icon('<path d="M18 6 6 18"/><path d="m6 6 12 12"/>');
  var ICON_DOWN = icon('<path d="M12 3v12"/><path d="m7 12 5 5 5-5"/><path d="M4 21h16"/>', 18);
  var ICON_UP = icon('<path d="M12 21V9"/><path d="m7 12 5-5 5 5"/><path d="M4 3h16"/>', 18);
  var ICON_TRASH = icon('<path d="M4 7h16"/><path d="M10 11v6"/><path d="M14 11v6"/>' +
    '<path d="M5 7l1 13h12l1-13"/><path d="M9 7V4h6v3"/>', 18);

  /* --------------------------------------------------------------- utils -- */
  function esc(s) {
    return String(s === null || s === undefined ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;')
      .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }
  function $(id) { return doc.getElementById(id); }

  /* ---------------------------------------------------------------- css --- */
  function injectCss() {
    if ($('gr-locker-css')) return;
    var css = [
      '.gr-lk-launch{position:fixed;right:16px;bottom:calc(16px + env(safe-area-inset-bottom,0px));z-index:8999;',
      'display:flex;align-items:center;gap:8px;min-height:48px;padding:0 16px;background:' + INK + ';color:' + WHITE + ';',
      'border:3px solid ' + INK + ';font:800 12.5px/1 Archivo,system-ui,sans-serif;text-transform:uppercase;',
      'letter-spacing:.06em;cursor:pointer;box-shadow:4px 4px 0 rgba(16,21,17,.25);transition:background .15s,color .15s}',
      '.gr-lk-launch:hover{background:' + FLAG + ';border-color:' + FLAG + '}',
      '.gr-lk-launch:focus-visible{outline:3px solid ' + FLAG + ';outline-offset:3px}',
      '.gr-lk-launch .gr-lk-count{background:' + FLAG + ';color:' + WHITE + ';font-size:11px;padding:2px 6px;min-width:20px}',

      '.gr-lk-scrim{position:fixed;inset:0;z-index:9000;background:rgba(16,21,17,.55);opacity:0;',
      'pointer-events:none;transition:opacity .22s ease}',
      '.gr-lk-scrim.on{opacity:1;pointer-events:auto}',

      '.gr-lk-panel{position:fixed;top:0;right:0;bottom:0;z-index:9001;width:min(420px,100%);background:' + PAPER + ';',
      'color:' + INK + ';border-left:3px solid ' + INK + ';display:flex;flex-direction:column;',
      'transform:translateX(100%);transition:transform .26s cubic-bezier(.32,.72,0,1);',
      'font-family:Archivo,system-ui,sans-serif}',
      '.gr-lk-panel.on{transform:translateX(0)}',

      '.gr-lk-head{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:14px 16px;',
      'padding-top:calc(14px + env(safe-area-inset-top,0px));border-bottom:3px solid ' + INK + ';background:' + PAPER + '}',
      '.gr-lk-title{display:flex;align-items:center;gap:9px;font-weight:900;font-size:17px;text-transform:uppercase;letter-spacing:-.01em}',
      '.gr-lk-x{display:flex;align-items:center;justify-content:center;width:44px;height:44px;margin:-4px -6px -4px 0;',
      'background:none;border:2px solid transparent;color:' + INK + ';cursor:pointer}',
      '.gr-lk-x:hover{background:' + INK + ';color:' + WHITE + '}',
      '.gr-lk-x:focus-visible{outline:3px solid ' + FLAG + ';outline-offset:-3px}',

      '.gr-lk-body{flex:1;overflow-y:auto;-webkit-overflow-scrolling:touch;padding:16px;',
      'padding-bottom:calc(24px + env(safe-area-inset-bottom,0px))}',
      '.gr-lk-sec{margin-bottom:22px}',
      '.gr-lk-h{font-size:11px;font-weight:800;text-transform:uppercase;letter-spacing:.1em;color:' + GREY + ';',
      'margin-bottom:8px;display:flex;justify-content:space-between;align-items:baseline}',

      '.gr-lk-card{background:' + WHITE + ';border:2px solid ' + INK + ';padding:12px}',
      '.gr-lk-row{display:flex;justify-content:space-between;align-items:center;gap:10px;padding:7px 0;',
      'border-bottom:1px solid ' + LINE + ';font-size:14px}',
      '.gr-lk-row:last-child{border-bottom:0}',
      '.gr-lk-row b{font-weight:700}',
      '.gr-lk-num{font-family:"IBM Plex Mono",ui-monospace,monospace;font-weight:600}',
      '.gr-lk-empty{font-size:13.5px;color:' + GREY + ';line-height:1.5}',

      '.gr-lk-f{display:block;margin-bottom:12px}',
      '.gr-lk-f label{display:block;font-size:11px;font-weight:800;text-transform:uppercase;',
      'letter-spacing:.08em;color:' + GREY + ';margin-bottom:5px}',
      '.gr-lk-f input,.gr-lk-f select{width:100%;min-height:46px;padding:10px 12px;background:' + WHITE + ';',
      'color:' + INK + ';border:2px solid ' + INK + ';font:600 15px/1.2 Archivo,system-ui,sans-serif}',
      '.gr-lk-f input:focus,.gr-lk-f select:focus{outline:3px solid ' + FLAG + ';outline-offset:-1px}',

      '.gr-lk-btn{display:inline-flex;align-items:center;justify-content:center;gap:7px;min-height:46px;',
      'padding:0 14px;background:' + INK + ';color:' + WHITE + ';border:2px solid ' + INK + ';cursor:pointer;',
      'font:800 12px/1 Archivo,system-ui,sans-serif;text-transform:uppercase;letter-spacing:.06em;',
      'transition:background .15s,color .15s}',
      '.gr-lk-btn:hover{background:' + FAIRWAY + ';border-color:' + FAIRWAY + '}',
      '.gr-lk-btn:focus-visible{outline:3px solid ' + FLAG + ';outline-offset:2px}',
      '.gr-lk-btn.ghost{background:' + WHITE + ';color:' + INK + '}',
      '.gr-lk-btn.ghost:hover{background:' + INK + ';color:' + WHITE + '}',
      '.gr-lk-btn.danger{background:' + WHITE + ';color:' + FLAG + ';border-color:' + FLAG + '}',
      '.gr-lk-btn.danger:hover{background:' + FLAG + ';color:' + WHITE + '}',
      '.gr-lk-btn[disabled]{opacity:.45;cursor:not-allowed}',
      '.gr-lk-btn[disabled]:hover{background:' + INK + ';border-color:' + INK + '}',
      '.gr-lk-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px}',

      '.gr-lk-note{margin-top:9px;font-size:12.5px;line-height:1.5;color:' + GREY + '}',
      '.gr-lk-msg{margin-top:10px;padding:9px 11px;border:2px solid ' + INK + ';background:' + WHITE + ';',
      'font-size:13px;font-weight:600;line-height:1.45;display:none}',
      '.gr-lk-msg.on{display:block}',
      '.gr-lk-msg.bad{border-color:' + FLAG + ';color:' + FLAG + '}',
      '.gr-lk-msg.good{border-color:' + FAIRWAY + ';color:' + FAIRWAY + '}',
      '.gr-lk-sr{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;',
      'clip:rect(0 0 0 0);white-space:nowrap;border:0}',

      '@media (max-width:420px){.gr-lk-panel{border-left:0;border-top:3px solid ' + INK + '}',
      '.gr-lk-launch{right:12px;bottom:calc(12px + env(safe-area-inset-bottom,0px))}}',
      '@media (prefers-reduced-motion:reduce){.gr-lk-panel,.gr-lk-scrim{transition:none}}'
    ].join('');
    var st = doc.createElement('style');
    st.id = 'gr-locker-css';
    st.textContent = css;
    doc.head.appendChild(st);
  }

  /* --------------------------------------------------------------- build -- */
  function build() {
    if (built) return;
    built = true;
    injectCss();
    bodyEl = doc.body;

    launcher = doc.createElement('button');
    launcher.type = 'button';
    launcher.className = 'gr-lk-launch';
    launcher.setAttribute('aria-haspopup', 'dialog');
    launcher.setAttribute('aria-expanded', 'false');
    launcher.setAttribute('aria-controls', 'gr-lk-panel');
    launcher.innerHTML = ICON_BAG + '<span>My Bag</span><span class="gr-lk-count" id="gr-lk-count" aria-hidden="true">0</span>';
    launcher.addEventListener('click', toggle);

    scrim = doc.createElement('div');
    scrim.className = 'gr-lk-scrim';
    scrim.addEventListener('click', close);

    panel = doc.createElement('div');
    panel.className = 'gr-lk-panel';
    panel.id = 'gr-lk-panel';
    panel.setAttribute('role', 'dialog');
    panel.setAttribute('aria-modal', 'true');
    panel.setAttribute('aria-labelledby', 'gr-lk-title');
    panel.setAttribute('hidden', '');
    panel.innerHTML =
      '<div class="gr-lk-head">' +
        '<span class="gr-lk-title" id="gr-lk-title">' + ICON_BAG + 'The Locker</span>' +
        '<button type="button" class="gr-lk-x" id="gr-lk-close" aria-label="Close the locker">' + ICON_CLOSE + '</button>' +
      '</div>' +
      '<div class="gr-lk-body" id="gr-lk-content"></div>' +
      '<p class="gr-lk-sr" role="status" aria-live="polite" id="gr-lk-live"></p>';

    doc.body.appendChild(launcher);
    doc.body.appendChild(scrim);
    doc.body.appendChild(panel);

    $('gr-lk-close').addEventListener('click', close);
    doc.addEventListener('keydown', onKey);

    unsubscribe = L.subscribe(function () { refresh(); });
    refresh();
  }

  /* ------------------------------------------------------------- refresh -- */
  function refresh() {
    if (!built) return;
    return Promise.all([L.getProfile(), L.getActiveBag(), L.listRounds(), L.listBags()])
      .then(function (r) { render(r[0], r[1], r[2], r[3]); })
      .catch(function () { /* a read fault must not blank the panel */ });
  }

  function clubCount(bag) {
    if (!bag || !bag.clubs) return 0;
    var n = 0;
    for (var i = 0; i < bag.clubs.length; i++) {
      if (bag.clubs[i].name && bag.clubs[i].carry) n++;
    }
    return n;
  }

  function render(profile, bag, rounds, bags) {
    var n = clubCount(bag);
    var cnt = $('gr-lk-count');
    if (cnt) cnt.textContent = String(n);
    launcher.setAttribute('aria-label', 'Open the locker. ' + n + ' clubs saved.');

    var scored = 0;
    for (var i = 0; i < rounds.length; i++) {
      if (rounds[i].score !== null && rounds[i].cr !== null && rounds[i].slope !== null) scored++;
    }

    var clubsHtml;
    if (!n) {
      clubsHtml = '<p class="gr-lk-empty">No clubs saved yet. Open the ' +
        '<a href="/tools-bag-audit" style="color:' + FLAG + ';font-weight:700;text-decoration:underline">Bag Audit</a> ' +
        'and your carry numbers will land here automatically.</p>';
    } else {
      var rows = [];
      for (var j = 0; j < bag.clubs.length; j++) {
        var c = bag.clubs[j];
        if (!c.name || !c.carry) continue;
        rows.push('<div class="gr-lk-row"><b>' + esc(c.name) + '</b>' +
          '<span class="gr-lk-num">' + esc(c.carry) + ' yd</span></div>');
      }
      clubsHtml = '<div class="gr-lk-card">' + rows.join('') + '</div>';
    }

    $('gr-lk-content').innerHTML =
      '<div class="gr-lk-sec">' +
        '<div class="gr-lk-h"><span>Your profile</span></div>' +
        '<div class="gr-lk-f"><label for="gr-lk-name">Name (optional)</label>' +
          '<input id="gr-lk-name" type="text" maxlength="60" autocomplete="name" value="' + esc(profile.displayName) + '"></div>' +
        '<div class="gr-lk-f"><label for="gr-lk-hcp">Claimed handicap</label>' +
          '<input id="gr-lk-hcp" type="number" inputmode="decimal" step="0.1" min="-10" max="54" ' +
          'value="' + (profile.claimedHandicap === null ? '' : esc(profile.claimedHandicap)) + '"></div>' +
        '<div class="gr-lk-f"><label for="gr-lk-course">Home course (optional)</label>' +
          '<input id="gr-lk-course" type="text" maxlength="80" value="' + esc(profile.homeCourse) + '"></div>' +
        '<div class="gr-lk-f"><label for="gr-lk-units">Distance units</label>' +
          '<select id="gr-lk-units">' +
            '<option value="yards"' + (profile.units === 'yards' ? ' selected' : '') + '>Yards</option>' +
            '<option value="meters"' + (profile.units === 'meters' ? ' selected' : '') + '>Meters</option>' +
          '</select></div>' +
        '<button type="button" class="gr-lk-btn" id="gr-lk-save">Save profile</button>' +
        '<div class="gr-lk-msg" id="gr-lk-pmsg" role="status"></div>' +
      '</div>' +

      '<div class="gr-lk-sec">' +
        '<div class="gr-lk-h"><span>Your bag</span><span class="gr-lk-num">' + n + ' / 14</span></div>' +
        clubsHtml +
      '</div>' +

      '<div class="gr-lk-sec">' +
        '<div class="gr-lk-h"><span>Scoring record</span></div>' +
        '<div class="gr-lk-card">' +
          '<div class="gr-lk-row"><b>Rounds saved</b><span class="gr-lk-num">' + rounds.length + '</span></div>' +
          '<div class="gr-lk-row"><b>Complete enough to score</b><span class="gr-lk-num">' + scored + '</span></div>' +
          '<div class="gr-lk-row"><b>Bags stored</b><span class="gr-lk-num">' + bags.length + '</span></div>' +
        '</div>' +
        (rounds.length ? '' : '<p class="gr-lk-note">Add rounds in the ' +
          '<a href="/tools-handicap-detector" style="color:' + FLAG + ';font-weight:700;text-decoration:underline">Handicap Lie Detector</a>.</p>') +
      '</div>' +

      '<div class="gr-lk-sec">' +
        '<div class="gr-lk-h"><span>Your data</span></div>' +
        '<div class="gr-lk-grid">' +
          '<button type="button" class="gr-lk-btn ghost" id="gr-lk-export">' + ICON_DOWN + 'Export</button>' +
          '<button type="button" class="gr-lk-btn ghost" id="gr-lk-import">' + ICON_UP + 'Import</button>' +
        '</div>' +
        '<input type="file" id="gr-lk-file" accept="application/json,.json" class="gr-lk-sr" tabindex="-1" aria-hidden="true">' +
        '<p class="gr-lk-note">Everything here is stored on this device only &mdash; it is never uploaded. ' +
          'Export writes a JSON backup you can keep or move to another browser.</p>' +
        '<div class="gr-lk-msg" id="gr-lk-dmsg" role="status"></div>' +
        '<div style="margin-top:14px"><button type="button" class="gr-lk-btn danger" id="gr-lk-clear">' +
          ICON_TRASH + 'Erase everything</button></div>' +
      '</div>';

    wire();
  }

  function msg(id, text, kind) {
    var m = $(id);
    if (!m) return;
    m.className = 'gr-lk-msg on ' + (kind || '');
    m.textContent = text;
    var live = $('gr-lk-live');
    if (live) live.textContent = text;
  }

  function wire() {
    $('gr-lk-save').addEventListener('click', function () {
      var hcpRaw = $('gr-lk-hcp').value.replace(/^\s+|\s+$/g, '');
      var hcp = hcpRaw === '' ? null : parseFloat(hcpRaw);
      if (hcp !== null && (!isFinite(hcp) || hcp < -10 || hcp > 54)) {
        msg('gr-lk-pmsg', 'Handicap must be between -10 and 54.', 'bad');
        $('gr-lk-hcp').focus();
        return;
      }
      L.saveProfile({
        displayName: $('gr-lk-name').value,
        claimedHandicap: hcp,
        homeCourse: $('gr-lk-course').value,
        units: $('gr-lk-units').value
      }).then(function () {
        msg('gr-lk-pmsg', 'Profile saved on this device.', 'good');
      })['catch'](function (e) {
        msg('gr-lk-pmsg', e && e.message ? e.message : 'Could not save.', 'bad');
      });
    });

    $('gr-lk-export').addEventListener('click', function () {
      L.exportJSON().then(function (json) {
        var d = new Date(), pad = function (x) { return (x < 10 ? '0' : '') + x; };
        var name = 'golfraw-locker-' + d.getFullYear() + pad(d.getMonth() + 1) + pad(d.getDate()) + '.json';
        var blob = new Blob([json], { type: 'application/json' });
        var url = URL.createObjectURL(blob);
        var a = doc.createElement('a');
        a.href = url; a.download = name;
        doc.body.appendChild(a); a.click(); doc.body.removeChild(a);
        setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
        msg('gr-lk-dmsg', 'Backup downloaded as ' + name, 'good');
      })['catch'](function (e) {
        msg('gr-lk-dmsg', e && e.message ? e.message : 'Export failed.', 'bad');
      });
    });

    var file = $('gr-lk-file');
    $('gr-lk-import').addEventListener('click', function () { file.click(); });
    file.addEventListener('change', function () {
      var f = file.files && file.files[0];
      if (!f) return;
      if (f.size > 4 * 1024 * 1024) {
        msg('gr-lk-dmsg', 'That file is too large to be a locker backup.', 'bad');
        file.value = '';
        return;
      }
      var reader = new FileReader();
      reader.onload = function () {
        var replace = root.confirm(
          'Import this backup?\n\nOK  — replace everything currently in your locker.\n' +
          'Cancel — merge it in, keeping what you already have.');
        L.importJSON(String(reader.result), replace ? 'replace' : 'merge').then(function (r) {
          msg('gr-lk-dmsg', 'Imported ' + r.bags + ' bag(s) and ' + r.rounds + ' round(s) (' + r.mode + ').', 'good');
        })['catch'](function (e) {
          msg('gr-lk-dmsg', e && e.message ? e.message : 'Import failed.', 'bad');
        });
        file.value = '';
      };
      reader.onerror = function () { msg('gr-lk-dmsg', 'Could not read that file.', 'bad'); file.value = ''; };
      reader.readAsText(f);
    });

    $('gr-lk-clear').addEventListener('click', function () {
      if (!root.confirm('Erase your profile, bag and every saved round from this device? This cannot be undone.')) return;
      L.clearAll().then(function () { msg('gr-lk-dmsg', 'Locker erased.', 'good'); });
    });
  }

  /* ------------------------------------------------------ open / close --- */
  function focusables() {
    var sel = 'a[href],button:not([disabled]),input:not([disabled]),select:not([disabled]),textarea,[tabindex]:not([tabindex="-1"])';
    var all = panel.querySelectorAll(sel), out = [];
    for (var i = 0; i < all.length; i++) {
      /* The file input is visually hidden and driven by its own button. */
      if (all[i].getAttribute('aria-hidden') === 'true') continue;
      out.push(all[i]);
    }
    return out;
  }

  function onKey(e) {
    if (!open) return;
    if (e.key === 'Escape' || e.keyCode === 27) { e.preventDefault(); close(); return; }
    if (e.key !== 'Tab' && e.keyCode !== 9) return;
    var f = focusables();
    if (!f.length) return;
    var first = f[0], last = f[f.length - 1];
    if (e.shiftKey && doc.activeElement === first) { e.preventDefault(); last.focus(); }
    else if (!e.shiftKey && doc.activeElement === last) { e.preventDefault(); first.focus(); }
  }

  function openDrawer() {
    if (open) return;
    build();
    open = true;
    lastFocus = doc.activeElement;
    panel.removeAttribute('hidden');
    /* Force a reflow so the transform transition actually runs. */
    void panel.offsetWidth;
    scrim.classList.add('on');
    panel.classList.add('on');
    launcher.setAttribute('aria-expanded', 'true');
    bodyEl.style.overflow = 'hidden';
    refresh().then(function () {
      var f = focusables();
      if (f.length) f[0].focus();
    });
  }

  function close() {
    if (!open) return;
    open = false;
    scrim.classList.remove('on');
    panel.classList.remove('on');
    launcher.setAttribute('aria-expanded', 'false');
    bodyEl.style.overflow = '';
    /* Keep it out of the tab order once it is off-screen. */
    setTimeout(function () { if (!open) panel.setAttribute('hidden', ''); }, 280);
    if (lastFocus && lastFocus.focus) { try { lastFocus.focus(); } catch (e) { } }
  }

  function toggle() { if (open) close(); else openDrawer(); }

  function init() {
    if (doc.body) build(); else doc.addEventListener('DOMContentLoaded', build);
  }

  if (doc.readyState === 'loading') doc.addEventListener('DOMContentLoaded', init);
  else init();

  root.GolfrawDrawer = {
    open: openDrawer,
    close: close,
    toggle: toggle,
    refresh: refresh,
    destroy: function () {
      if (unsubscribe) unsubscribe();
      if (panel) panel.parentNode.removeChild(panel);
      if (scrim) scrim.parentNode.removeChild(scrim);
      if (launcher) launcher.parentNode.removeChild(launcher);
      built = false; open = false;
    }
  };
})(window, document);
