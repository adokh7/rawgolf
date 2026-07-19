/* ==========================================================================
   RAWGOLF TOOLS ENGINE  v1.0
   Shared client-side layer for all 5 Raw Tools.
   100% local. No network calls, no cookies, no third parties.

   Public API (window.RawGolf):
     .save(entry)        -> push a sanitized result into rawgolf_history
     .read()             -> Array of history entries (newest first)
     .remove(id)         -> delete one entry
     .clear()            -> wipe history
     .exportPassport()   -> download rawgolf-passport-YYYY-MM-DD.json
     .importPassport(file, done) -> restore history from an uploaded file
     .downloadCard(o)    -> render verdict to <canvas>, download .png
     .shareResult(o)     -> navigator.share, clipboard fallback
     .toast(msg)         -> transient confirmation pill
   ========================================================================== */
(function (w, d) {
  'use strict';

  var KEY = 'rawgolf_history';
  var CAP = 100;                 /* hard cap so LocalStorage can never fill up */
  var SITE = 'https://www.golfraw.com';

  /* ---------- storage (every access guarded: Safari private mode throws) --- */

  function read() {
    try {
      var raw = w.localStorage.getItem(KEY);
      if (!raw) return [];
      var arr = JSON.parse(raw);
      return Object.prototype.toString.call(arr) === '[object Array]' ? arr : [];
    } catch (e) { return []; }
  }

  function write(arr) {
    try {
      w.localStorage.setItem(KEY, JSON.stringify(arr.slice(0, CAP)));
      return true;
    } catch (e) { return false; }
  }

  /* Strip anything that isn't a primitive we put there ourselves. Guarantees
     the payload stays small and that an imported file can't smuggle in junk. */
  function clean(s, max) {
    if (s === null || s === undefined) return '';
    return String(s).replace(/\s+/g, ' ').trim().slice(0, max || 160);
  }

  function save(entry) {
    if (!entry || !entry.tool) return null;
    var metrics = [];
    var src = entry.metrics || [];
    for (var i = 0; i < src.length && i < 6; i++) {
      if (!src[i]) continue;
      metrics.push({ k: clean(src[i].k, 40), v: clean(src[i].v, 40) });
    }
    var rec = {
      id: 'r' + Date.now().toString(36) + Math.random().toString(36).slice(2, 7),
      ts: Date.now(),
      tool: clean(entry.tool, 60),
      slug: clean(entry.slug, 60),
      verdict: clean(entry.verdict, 160),
      metrics: metrics
    };
    var all = read();
    all.unshift(rec);
    write(all);
    return rec;
  }

  function remove(id) {
    var all = read(), out = [];
    for (var i = 0; i < all.length; i++) if (all[i].id !== id) out.push(all[i]);
    write(out);
    return out;
  }

  function clear() { write([]); return []; }

  /* ---------- Golf Passport: export / import ------------------------------ */

  function stamp() {
    var n = new Date(), p = function (x) { return (x < 10 ? '0' : '') + x; };
    return n.getFullYear() + '-' + p(n.getMonth() + 1) + '-' + p(n.getDate());
  }

  function saveBlob(blob, filename) {
    var url = URL.createObjectURL(blob);
    var a = d.createElement('a');
    a.href = url;
    a.download = filename;
    a.style.display = 'none';
    d.body.appendChild(a);
    a.click();
    setTimeout(function () {
      d.body.removeChild(a);
      URL.revokeObjectURL(url);
    }, 1200);
  }

  function exportPassport() {
    var data = {
      format: 'golfraw-passport',
      version: 1,
      exported: new Date().toISOString(),
      count: read().length,
      history: read()
    };
    saveBlob(
      new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' }),
      'rawgolf-passport-' + stamp() + '.json'
    );
    return data.count;
  }

  /* done(err, countImported) */
  function importPassport(file, done) {
    done = done || function () {};
    if (!file) return done('No file selected.');
    if (file.size > 2 * 1024 * 1024) return done('That file is too large to be a passport.');

    var fr = new FileReader();
    fr.onerror = function () { done('Could not read that file.'); };
    fr.onload = function (ev) {
      var parsed;
      try { parsed = JSON.parse(ev.target.result); }
      catch (e) { return done('That is not a valid passport file.'); }

      /* Accept either the wrapper object or a bare array. */
      var list = null;
      if (parsed && Object.prototype.toString.call(parsed.history) === '[object Array]') list = parsed.history;
      else if (Object.prototype.toString.call(parsed) === '[object Array]') list = parsed;
      if (!list) return done('No history found inside that file.');

      /* Re-sanitize on the way in. Never trust a file. */
      var out = [];
      for (var i = 0; i < list.length && i < CAP; i++) {
        var r = list[i];
        if (!r || !r.tool) continue;
        var ms = [], src = (Object.prototype.toString.call(r.metrics) === '[object Array]') ? r.metrics : [];
        for (var j = 0; j < src.length && j < 6; j++) {
          if (!src[j]) continue;
          ms.push({ k: clean(src[j].k, 40), v: clean(src[j].v, 40) });
        }
        out.push({
          id: clean(r.id, 40) || ('r' + i + Date.now().toString(36)),
          ts: (typeof r.ts === 'number' && isFinite(r.ts)) ? r.ts : Date.now(),
          tool: clean(r.tool, 60),
          slug: clean(r.slug, 60),
          verdict: clean(r.verdict, 160),
          metrics: ms
        });
      }
      if (!out.length) return done('That passport contained no readable results.');
      out.sort(function (a, b) { return b.ts - a.ts; });
      if (!write(out)) return done('Your browser blocked local storage.');
      done(null, out.length);
    };
    fr.readAsText(file);
  }

  /* ---------- HTML5 Canvas share card ------------------------------------- */

  function wrap(ctx, text, maxW) {
    var words = String(text).split(/\s+/), lines = [], line = '';
    for (var i = 0; i < words.length; i++) {
      var test = line ? line + ' ' + words[i] : words[i];
      if (ctx.measureText(test).width > maxW && line) { lines.push(line); line = words[i]; }
      else { line = test; }
    }
    if (line) lines.push(line);
    return lines;
  }

  /* o = { eyebrow, headline, big, bigLabel, lines:[{k,v}], filename } */
  function paint(o) {
    var W = 1080, H = 1350, PAD = 78;
    var c = d.createElement('canvas');
    c.width = W; c.height = H;
    var x = c.getContext('2d');

    var INK = '#101511', PAPER = '#F3F4F0', FLAG = '#E03E2D', MUTED = '#8D9990';
    var SANS = '"Archivo", "Helvetica Neue", Helvetica, Arial, sans-serif';
    var MONO = '"IBM Plex Mono", "SFMono-Regular", Menlo, Consolas, monospace';

    /* premium dark ground + subtle vignette */
    x.fillStyle = INK; x.fillRect(0, 0, W, H);
    var g = x.createLinearGradient(0, 0, W, H);
    g.addColorStop(0, 'rgba(20,64,42,.55)');
    g.addColorStop(.55, 'rgba(16,21,17,0)');
    x.fillStyle = g; x.fillRect(0, 0, W, H);
    x.fillStyle = FLAG; x.fillRect(0, 0, W, 16);

    /* masthead */
    x.fillStyle = PAPER;
    x.font = '800 40px ' + SANS;
    x.textBaseline = 'alphabetic';
    x.fillText('GOLF', PAD, 130);
    var gw = x.measureText('GOLF').width;
    x.fillStyle = FLAG;
    x.fillText('RAW', PAD + gw + 8, 130);

    x.fillStyle = MUTED;
    x.font = '500 22px ' + MONO;
    x.fillText(clean(o.eyebrow, 48).toUpperCase(), PAD, 182);

    x.strokeStyle = 'rgba(243,244,240,.20)';
    x.lineWidth = 2;
    x.beginPath(); x.moveTo(PAD, 216); x.lineTo(W - PAD, 216); x.stroke();

    /* --- Measure first, then place, so the block sits optically centred
           between the masthead and the footer instead of hugging the top. --- */
    var rowsIn = (o.lines || []).slice(0, 6);
    x.font = '800 62px ' + SANS;
    var headLines = wrap(x, clean(o.headline, 140), W - PAD * 2).slice(0, 4);

    var blockH = 0;
    if (o.big) blockH += 170 + (o.bigLabel ? 50 : 0);
    blockH += headLines.length * 74;
    if (rowsIn.length) blockH += 34 + rowsIn.length * 66;

    var TOP = 262, BOT = H - 190;
    var y = TOP + Math.max(0, ((BOT - TOP) - blockH) / 2) + 46;

    /* hero number */
    if (o.big) {
      x.fillStyle = FLAG;
      x.font = '800 168px ' + SANS;
      x.fillText(clean(o.big, 14), PAD, y + 40);
      if (o.bigLabel) {
        x.fillStyle = MUTED;
        x.font = '500 24px ' + MONO;
        x.fillText(clean(o.bigLabel, 40).toUpperCase(), PAD, y + 90);
        y += 40;
      }
      y += 130;
    }

    /* verdict headline */
    x.fillStyle = PAPER;
    x.font = '800 62px ' + SANS;
    for (var i = 0; i < headLines.length; i++) { x.fillText(headLines[i], PAD, y); y += 74; }

    /* metric rows */
    y += 34;
    var rows = rowsIn;
    for (var r = 0; r < rows.length; r++) {
      if (!rows[r]) continue;
      x.strokeStyle = 'rgba(243,244,240,.13)';
      x.lineWidth = 1;
      x.beginPath(); x.moveTo(PAD, y - 34); x.lineTo(W - PAD, y - 34); x.stroke();

      x.fillStyle = MUTED;
      x.font = '500 26px ' + MONO;
      x.fillText(clean(rows[r].k, 34).toUpperCase(), PAD, y + 4);

      x.fillStyle = PAPER;
      x.font = '700 32px ' + SANS;
      x.textAlign = 'right';
      x.fillText(clean(rows[r].v, 30), W - PAD, y + 6);
      x.textAlign = 'left';
      y += 66;
    }

    /* footer */
    x.fillStyle = FLAG; x.fillRect(PAD, H - 132, 62, 5);
    x.fillStyle = PAPER;
    x.font = '700 28px ' + SANS;
    x.fillText('golfraw.com', PAD, H - 78);
    x.fillStyle = MUTED;
    x.font = '500 22px ' + MONO;
    x.textAlign = 'right';
    x.fillText('FREE · NO SIGN-UP', W - PAD, H - 78);
    x.textAlign = 'left';

    return c;
  }

  function downloadCard(o) {
    o = o || {};
    var name = (o.filename || 'golfraw-result') + '-' + stamp() + '.png';
    var go = function () {
      var c;
      try { c = paint(o); }
      catch (e) { toast('Could not build that card.'); return; }

      if (c.toBlob) {
        c.toBlob(function (b) {
          if (!b) { toast('Could not build that card.'); return; }
          saveBlob(b, name);
          toast('Card downloaded.');
        }, 'image/png');
      } else {                                   /* older Safari */
        var a = d.createElement('a');
        a.href = c.toDataURL('image/png');
        a.download = name;
        d.body.appendChild(a); a.click(); d.body.removeChild(a);
        toast('Card downloaded.');
      }
    };
    /* Wait for webfonts so the card never renders in a fallback face. */
    if (d.fonts && d.fonts.ready && d.fonts.ready.then) {
      d.fonts.ready.then(go)['catch'](go);
    } else { go(); }
  }

  /* ---------- Web Share API ----------------------------------------------- */

  function copyText(text) {
    if (w.navigator.clipboard && w.navigator.clipboard.writeText) {
      return w.navigator.clipboard.writeText(text);
    }
    return new Promise(function (res, rej) {           /* execCommand fallback */
      try {
        var ta = d.createElement('textarea');
        ta.value = text;
        ta.setAttribute('readonly', '');
        ta.style.position = 'fixed';
        ta.style.top = '-1000px';
        d.body.appendChild(ta);
        ta.select();
        var ok = d.execCommand('copy');
        d.body.removeChild(ta);
        ok ? res() : rej();
      } catch (e) { rej(e); }
    });
  }

  /* o = { title, text, url } */
  function shareResult(o) {
    o = o || {};
    var url = o.url || (SITE + '/' + (o.slug || '')).replace(/\/$/, '');
    var text = clean(o.text, 500);

    if (w.navigator.share) {
      w.navigator.share({ title: o.title || 'Golf Raw', text: text, url: url })
        ['catch'](function (err) {
          /* User dismissed the sheet — that is not a failure worth shouting about. */
          if (err && err.name === 'AbortError') return;
          copyText(text + '\n' + url).then(function () { toast('Copied to clipboard.'); },
            function () { toast('Could not share on this device.'); });
        });
      return;
    }
    copyText(text + '\n' + url).then(
      function () { toast('Copied — paste it in the group chat.'); },
      function () { toast('Could not copy on this device.'); }
    );
  }

  /* ---------- toast -------------------------------------------------------- */

  var toastEl = null, toastTimer = null;
  function toast(msg) {
    if (!toastEl) {
      toastEl = d.createElement('div');
      toastEl.setAttribute('role', 'status');
      toastEl.setAttribute('aria-live', 'polite');
      toastEl.style.cssText =
        'position:fixed;left:50%;bottom:26px;transform:translateX(-50%) translateY(14px);' +
        'background:#101511;color:#F3F4F0;border:2px solid #E03E2D;padding:12px 20px;' +
        'font:600 14px/1.2 "Archivo",Helvetica,Arial,sans-serif;letter-spacing:.01em;' +
        'z-index:9999;opacity:0;transition:opacity .18s ease,transform .18s ease;' +
        'pointer-events:none;max-width:88vw;text-align:center';
      d.body.appendChild(toastEl);
    }
    toastEl.textContent = msg;
    requestAnimationFrame(function () {
      toastEl.style.opacity = '1';
      toastEl.style.transform = 'translateX(-50%) translateY(0)';
    });
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () {
      toastEl.style.opacity = '0';
      toastEl.style.transform = 'translateX(-50%) translateY(14px)';
    }, 2400);
  }

  /* ---------- date helper shared with the dashboard ------------------------ */

  function when(ts) {
    var dt = new Date(ts);
    if (isNaN(dt.getTime())) return '--';
    var M = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    var h = dt.getHours(), ap = h >= 12 ? 'pm' : 'am', h12 = h % 12 || 12;
    var mm = dt.getMinutes();
    return M[dt.getMonth()] + ' ' + dt.getDate() + ', ' + h12 + ':' + (mm < 10 ? '0' : '') + mm + ap;
  }

  w.RawGolf = {
    KEY: KEY,
    save: save,
    read: read,
    remove: remove,
    clear: clear,
    exportPassport: exportPassport,
    importPassport: importPassport,
    downloadCard: downloadCard,
    shareResult: shareResult,
    copyText: copyText,
    toast: toast,
    when: when
  };
})(window, document);
