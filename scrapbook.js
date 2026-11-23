(function () {
  var prints = Array.prototype.slice.call(document.querySelectorAll('.print'));
  var lb = document.querySelector('.lightbox');
  if (!lb || !prints.length) return;
  var img = lb.querySelector('img'), cap = lb.querySelector('figcaption'), i = 0;
  function show(n) {
    i = (n + prints.length) % prints.length;
    img.src = prints[i].getAttribute('href');
    cap.textContent = prints[i].getAttribute('data-cap') || '';
    lb.hidden = false;
  }
  prints.forEach(function (p, n) {
    p.addEventListener('click', function (e) { e.preventDefault(); show(n); });
  });
  lb.querySelector('.lb-close').onclick = function () { lb.hidden = true; };
  lb.querySelector('.lb-prev').onclick = function () { show(i - 1); };
  lb.querySelector('.lb-next').onclick = function () { show(i + 1); };
  lb.addEventListener('click', function (e) { if (e.target === lb) lb.hidden = true; });
  document.addEventListener('keydown', function (e) {
    if (lb.hidden) return;
    if (e.key === 'Escape') lb.hidden = true;
    if (e.key === 'ArrowLeft') show(i - 1);
    if (e.key === 'ArrowRight') show(i + 1);
  });
})();
