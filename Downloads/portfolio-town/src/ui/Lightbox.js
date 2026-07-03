const overlay = document.getElementById('lightbox-overlay');
const body = document.getElementById('lightbox-body');
const closeBtn = document.getElementById('lightbox-close');

export function openLightbox(html) {
  body.innerHTML = html;
  overlay.classList.remove('hidden');
}

export function closeLightbox() {
  overlay.classList.add('hidden');
}

export function isLightboxOpen() {
  return !overlay.classList.contains('hidden');
}

closeBtn.addEventListener('click', closeLightbox);
overlay.addEventListener('click', (e) => {
  if (e.target === overlay) closeLightbox();
});
