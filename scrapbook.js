(function () {
  var prints = Array.prototype.slice.call(document.querySelectorAll('.g-cell'));
  var lb = document.querySelector('.lightbox');
  if (!lb || !prints.length) return;
  var img = lb.querySelector('img'), i = 0;
  function show(n) {
    i = (n + prints.length) % prints.length;
    img.src = prints[i].getAttribute('href');
    lb.hidden = false;
  }
  prints.forEach(function (p, n) {
    p.addEventListener('click', function (e) { e.preventDefault(); show(n); });
  });
  lb.querySelector('.lb-close').onclick = function () { lb.hidden = true; };
  lb.querySelector('.lb-prev').onclick = function () { show(i - 1); };
  lb.querySelector('.lb-next').onclick = function () { show(i + 1); };
  lb.addEventListener('click', function (e) { if (e.target === lb) lb.hidden = true; });
  var x0 = null;
  lb.addEventListener('touchstart', function (e) { x0 = e.touches[0].clientX; }, { passive: true });
  lb.addEventListener('touchend', function (e) {
    if (x0 === null) return;
    var dx = e.changedTouches[0].clientX - x0; x0 = null;
    if (Math.abs(dx) > 40) show(dx < 0 ? i + 1 : i - 1);
  });
  document.addEventListener('keydown', function (e) {
    if (lb.hidden) return;
    if (e.key === 'Escape') lb.hidden = true;
    if (e.key === 'ArrowLeft') show(i - 1);
    if (e.key === 'ArrowRight') show(i + 1);
  });
})();
