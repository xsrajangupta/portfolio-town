import { ASSET_KEYS } from '../config.js';
import { loadSave, saveState } from '../save/SaveManager.js';

export class AudioManager {
  constructor(scene) {
    this.scene = scene;
    const save = loadSave();
    this.muted = !!save.muted;

    this.bgm = scene.sound.add(ASSET_KEYS.sfxBgm, { loop: true, volume: 0.35 });
    this.ambient = scene.sound.add(ASSET_KEYS.sfxAmbient, { loop: true, volume: 0.25 });
    this.footstepTimer = 0;

    this._applyMute();
    this.bgm.play();
    this.ambient.play();
  }

  _applyMute() {
    this.scene.sound.mute = this.muted;
  }

  toggleMute() {
    this.muted = !this.muted;
    this._applyMute();
    saveState({ muted: this.muted });
    return this.muted;
  }

  playClick() {
    this.scene.sound.play(ASSET_KEYS.sfxClick, { volume: 0.4 });
  }

  /** Call every frame with whether the player is currently moving. */
  updateFootsteps(isMoving, delta) {
    if (!isMoving) {
      this.footstepTimer = 0;
      return;
    }
    this.footstepTimer -= delta;
    if (this.footstepTimer <= 0) {
      this.scene.sound.play(ASSET_KEYS.sfxFootstep, { volume: 0.22 });
      this.footstepTimer = 260; // ms between footstep sounds
    }
  }
}
