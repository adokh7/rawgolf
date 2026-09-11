/* GOLFRAW theme behaviour: header elevation on scroll + scroll-triggered
   reveals. Everything here is progressive enhancement — the page is complete
   and readable before this runs, and stays so if it never does. */
(function () {
  'use strict';
  var d = document, de = d.documentElement, W = window;
  var reduce = W.matchMedia && W.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---- header: one class, toggled only when the scrolled state changes ----
     Deliberately not throttled through requestAnimationFrame: rAF does not
     fire while a document is hidden, so a page opened in a background tab
     would latch the throttle flag and never elevate its header. A guarded
     classList toggle is cheaper than the throttle it replaces. */
  var scrolled = null;
  function onScroll() {
    var on = (W.scrollY || de.scrollTop) > 12;
    if (on === scrolled) return;
    scrolled = on;
    de.classList.toggle('gr-scrolled', on);
  }
  if (d.querySelector('.site-header, body > header, .board-header')) {
    onScroll();
    W.addEventListener('scroll', onScroll, { passive: true });
  }

  /* ---- reveals ---- */
  if (reduce || !('IntersectionObserver' in W)) { de.classList.add('gr-reveal-all'); return; }

  var SEL = [
    '.guide-card', '.news-grid > *', '.story', '.tool-card', '.r-card', '.rel-card',
    '.coverage-card', '.vault-item', '.evidence-item', '.hub-example', '.sec-head',
    '.aside-box', '.takeaways', '.pcard', '.myth', '.faq-item', '.verdict-box', '.raw-verdict',
    '.lead-stat', 'figure.lead-img', 'figure.inline-fig', 'blockquote.pull', '.verify',
    '.sources', '.related', '.provenance', '.article-body h2', '.cmp-scroll', '.table-wrap'
  ].join(',');

  var seen = new Set();
  var els = [];
  d.querySelectorAll(SEL).forEach(function (e) {
    if (seen.has(e)) return;
    /* index.html runs its own .reveal system; nested targets would double-fade */
    if (e.classList.contains('reveal') || e.closest('.reveal')) return;
    if (e.parentElement && e.parentElement.closest(SEL)) return;
    seen.add(e); els.push(e);
  });

  /* Stagger siblings inside the same parent (cards in a grid), capped so a
     long list never keeps the reader waiting. */
  var counters = new Map();
  var vh = W.innerHeight || de.clientHeight;
  els.forEach(function (e) {
    var p = e.parentElement, i = counters.get(p) || 0;
    counters.set(p, i + 1);
    e.style.setProperty('--gr-i', Math.min(i, 5));
    var r = e.getBoundingClientRect();
    e.classList.add('gr-reveal');
    /* Already on screen at load: mark visible in the same synchronous pass,
       so there is no frame where above-the-fold content blinks out. */
    if (r.top < vh * 0.94 && r.bottom > 0) e.classList.add('is-in');
  });

  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (en) {
      if (!en.isIntersecting) return;
      en.target.classList.add('is-in');
      io.unobserve(en.target);
    });
  }, { rootMargin: '0px 0px -6% 0px', threshold: 0.06 });
  els.forEach(function (e) { if (!e.classList.contains('is-in')) io.observe(e); });
})();
