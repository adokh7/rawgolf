/* Local stand-in for adsbygoogle.js, used only by the tool-ads browser checks
   on localhost (lib/ads/tool-ads.js reads gr_ads_test there). It never talks
   to Google. Mode comes from localStorage gr_ads_stub: fill | unfilled | silent
   | throw. */
(function () {
  var mode = 'fill';
  try { mode = localStorage.getItem('gr_ads_stub') || 'fill'; } catch (e) {}
  var q = window.adsbygoogle || [];
  var done = 0;
  function serve() {
    var units = document.querySelectorAll('ins.adsbygoogle');
    for (var i = done; i < units.length; i++) {
      (function (ins) {
        setTimeout(function () {
          if (mode === 'silent') return;
          if (mode === 'unfilled') { ins.setAttribute('data-ad-status', 'unfilled'); return; }
          ins.innerHTML = '<div style="height:280px;background:#e8ebe4;display:flex;align-items:center;justify-content:center;font:12px sans-serif">stub ad</div>';
          ins.setAttribute('data-ad-status', 'filled');
        }, 400);
      })(units[i]);
    }
    done = units.length;
  }
  var api = { loaded: true, push: function () { if (mode === 'throw') throw new Error('stub push failure'); serve(); } };
  for (var i = 0; i < q.length; i++) api.push(q[i]);
  window.adsbygoogle = api;
})();
