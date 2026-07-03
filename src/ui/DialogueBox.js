import { playClickSound } from './uiSound.js';

const overlay = document.getElementById('dialogue-overlay');
const nameEl = document.getElementById('dialogue-name');
const textEl = document.getElementById('dialogue-text');

let onCloseCallback = null;

export function openDialogue(name, text) {
  nameEl.textContent = name;
  textEl.innerHTML = text
    .split('\n')
    .map((line) => `<p>${line}</p>`)
    .join('');
  overlay.classList.remove('hidden');
  playClickSound();
}

export function closeDialogue() {
  overlay.classList.add('hidden');
  playClickSound();
  if (onCloseCallback) onCloseCallback();
}

export function isDialogueOpen() {
  return !overlay.classList.contains('hidden');
}

export function onDialogueClose(cb) {
  onCloseCallback = cb;
}

overlay.addEventListener('click', () => closeDialogue());
