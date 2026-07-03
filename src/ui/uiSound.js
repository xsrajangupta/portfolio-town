let handler = null;

export function registerUiSound(fn) {
  handler = fn;
}

export function playClickSound() {
  if (handler) handler();
}
