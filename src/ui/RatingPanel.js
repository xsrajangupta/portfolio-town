import contact from '../data/contact.json';
import { playClickSound } from './uiSound.js';

const openBtn = document.getElementById('rate-town-btn');
const overlay = document.getElementById('rating-overlay');
const closeBtn = document.getElementById('rating-close');
const starsWrap = document.getElementById('rating-stars');
const stars = Array.from(starsWrap.querySelectorAll('.rating-star'));
const commentEl = document.getElementById('rating-comment');
const errorEl = document.getElementById('rating-error');
const submitBtn = document.getElementById('rating-submit');

let selectedRating = 0;

function paintStars(value) {
  stars.forEach((star) => {
    star.classList.toggle('is-filled', Number(star.dataset.value) <= value);
  });
}

function setRating(value) {
  selectedRating = value;
  paintStars(value);
  if (value > 0) errorEl.classList.add('hidden');
}

function resetForm() {
  setRating(0);
  commentEl.value = '';
  errorEl.classList.add('hidden');
}

function openRating() {
  resetForm();
  overlay.classList.remove('hidden');
  playClickSound();
}

function closeRating() {
  overlay.classList.add('hidden');
}

function isRatingOpen() {
  return !overlay.classList.contains('hidden');
}

function submitRating() {
  if (selectedRating < 1) {
    errorEl.classList.remove('hidden');
    return;
  }
  playClickSound();

  const starLine = '★'.repeat(selectedRating) + '☆'.repeat(5 - selectedRating);
  const comment = commentEl.value.trim();

  const subject = `Portfolio Town Rating: ${selectedRating}/5`;
  const bodyLines = [
    `Rating: ${starLine} (${selectedRating}/5)`,
    '',
    comment ? `Comment: ${comment}` : 'Comment: (none)',
  ];
  const body = bodyLines.join('\n');

  const mailtoUrl =
    `mailto:${encodeURIComponent(contact.email)}` +
    `?subject=${encodeURIComponent(subject)}` +
    `&body=${encodeURIComponent(body)}`;

  // Opens in the visitor's own email client, pre-filled — nothing is sent
  // from our side, so no backend / API key is required.
  window.location.href = mailtoUrl;

  closeRating();
}

stars.forEach((star) => {
  star.addEventListener('mouseenter', () => paintStars(Number(star.dataset.value)));
  star.addEventListener('click', () => {
    playClickSound();
    setRating(Number(star.dataset.value));
  });
});
starsWrap.addEventListener('mouseleave', () => paintStars(selectedRating));

openBtn.addEventListener('click', openRating);
closeBtn.addEventListener('click', () => {
  playClickSound();
  closeRating();
});
submitBtn.addEventListener('click', submitRating);
overlay.addEventListener('click', (e) => {
  if (e.target === overlay) closeRating();
});
window.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && isRatingOpen()) closeRating();
});

export { isRatingOpen, closeRating };
