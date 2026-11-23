document.querySelectorAll('.slideshow').forEach(function (ss) {
  var track = ss.querySelector('.track'), n = track.children.length, i = 0;
  var nav = ss.nextElementSibling, count = nav.querySelector('.count');
  function go(k) { i = (k + n) % n; track.style.transform = 'translateX(' + (-100 * i) + '%)'; count.textContent = (i + 1) + ' of ' + n; }
  nav.querySelector('.prev').onclick = function () { go(i - 1); };
  nav.querySelector('.next').onclick = function () { go(i + 1); };
  document.addEventListener('keydown', function (e) { if (e.key === 'ArrowLeft') go(i - 1); if (e.key === 'ArrowRight') go(i + 1); });
  var x0 = null;
  ss.addEventListener('touchstart', function (e) { x0 = e.touches[0].clientX; });
  ss.addEventListener('touchend', function (e) { if (x0 === null) return; var d = e.changedTouches[0].clientX - x0; if (Math.abs(d) > 40) go(i + (d < 0 ? 1 : -1)); x0 = null; });
  go(0);
});
