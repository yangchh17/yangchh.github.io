(function () {
  if (localStorage.getItem('dev-banner-dismissed')) return;

  var bar = document.createElement('div');
  bar.id = 'dev-banner';
  bar.innerHTML =
    '<span>\u{1F44B} Hey! I\'m still building this out. Some pages are a work in progress. Thanks for stopping by!</span>' +
    '<button aria-label="Dismiss">\u00D7</button>';

  var s = bar.style;
  s.position = 'fixed';
  s.top = '52px';
  s.left = '0';
  s.right = '0';
  s.zIndex = '199';
  s.display = 'flex';
  s.alignItems = 'center';
  s.justifyContent = 'center';
  s.gap = '12px';
  s.padding = '10px 48px';
  s.background = '#f8f4ee';
  s.borderBottom = '1px solid #e8e0d4';
  s.fontFamily = "'DM Sans', sans-serif";
  s.fontSize = '13px';
  s.fontWeight = '400';
  s.color = '#4a3828';
  s.letterSpacing = '.01em';
  s.lineHeight = '1.5';
  s.textAlign = 'center';

  var btn = bar.querySelector('button');
  var bs = btn.style;
  bs.background = 'none';
  bs.border = 'none';
  bs.cursor = 'pointer';
  bs.fontSize = '18px';
  bs.color = '#9a8878';
  bs.padding = '0 4px';
  bs.lineHeight = '1';
  bs.flexShrink = '0';
  bs.transition = 'color .16s';

  btn.onmouseover = function () { bs.color = '#d44820'; };
  btn.onmouseout = function () { bs.color = '#9a8878'; };
  btn.onclick = function () {
    bar.style.transition = 'opacity .25s';
    bar.style.opacity = '0';
    setTimeout(function () { bar.remove(); }, 260);
    localStorage.setItem('dev-banner-dismissed', '1');
  };

  document.body.appendChild(bar);
})();
