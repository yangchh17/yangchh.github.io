(function () {
  'use strict';

  var nav = document.querySelector('nav');
  if (!nav) return;

  var trigger = nav.querySelector('.nav-menu-trigger');
  var panel = nav.querySelector('.nav-mega-drop');
  if (!trigger || !panel) return;

  if (!panel.id) panel.id = 'site-navigation-menu';
  trigger.setAttribute('aria-controls', panel.id);
  trigger.setAttribute('aria-expanded', 'false');
  trigger.setAttribute('aria-haspopup', 'true');

  function isOpen() {
    return trigger.getAttribute('aria-expanded') === 'true';
  }

  function setOpen(open, returnFocus) {
    panel.classList.toggle('is-open', open);
    trigger.setAttribute('aria-expanded', String(open));
    if (returnFocus) trigger.focus();
  }

  trigger.addEventListener('click', function (event) {
    event.stopPropagation();
    setOpen(!isOpen(), false);
  });

  trigger.addEventListener('keydown', function (event) {
    if (event.key === 'ArrowDown') {
      event.preventDefault();
      setOpen(true, false);
      var firstLink = panel.querySelector('a, button');
      if (firstLink) firstLink.focus();
    }
  });

  nav.addEventListener('keydown', function (event) {
    if (event.key === 'Escape' && isOpen()) {
      event.preventDefault();
      event.stopPropagation();
      setOpen(false, true);
    }
  });

  panel.querySelectorAll('a, button').forEach(function (item) {
    item.addEventListener('click', function () {
      setOpen(false, false);
    });
  });

  document.addEventListener('click', function (event) {
    if (!nav.contains(event.target)) setOpen(false, false);
  });

  nav.addEventListener('focusout', function () {
    window.setTimeout(function () {
      if (!nav.contains(document.activeElement)) setOpen(false, false);
    }, 0);
  });
}());
