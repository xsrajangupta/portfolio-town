import { SAVE_KEY } from '../config.js';

const DEFAULT_STATE = {
  playerX: null,
  playerY: null,
  muted: false,
  musicVolume: 0.5,
};

export function loadSave() {
  try {
    const raw = localStorage.getItem(SAVE_KEY);
    if (!raw) return { ...DEFAULT_STATE };
    return { ...DEFAULT_STATE, ...JSON.parse(raw) };
  } catch (e) {
    return { ...DEFAULT_STATE };
  }
}

export function saveState(partial) {
  try {
    const current = loadSave();
    const next = { ...current, ...partial };
    localStorage.setItem(SAVE_KEY, JSON.stringify(next));
    return next;
  } catch (e) {
    return null;
  }
}
