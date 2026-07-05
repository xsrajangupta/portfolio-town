import Phaser from 'phaser';
import { GAME } from './config.js';
import { PreloadScene } from './scenes/PreloadScene.js';
import { TownScene } from './scenes/TownScene.js';
import './ui/RatingPanel.js';

const config = {
  type: Phaser.AUTO,
  parent: 'game-container',
  backgroundColor: GAME.backgroundColor,
  pixelArt: true,
  roundPixels: true,
  scale: {
    mode: Phaser.Scale.RESIZE,
    autoCenter: Phaser.Scale.NO_CENTER,
    width: window.innerWidth,
    height: window.innerHeight,
  },
  physics: {
    default: 'arcade',
    arcade: {
      gravity: { y: 0 },
      debug: false,
    },
  },
  scene: [PreloadScene, TownScene],
};

const game = new Phaser.Game(config);

// RESIZE mode fills the container exactly, but the canvas itself needs to be
// told about size changes explicitly on every resize/orientation change —
// each scene additionally resizes its own camera (see TownScene._setupCamera).
window.addEventListener('resize', () => {
  game.scale.resize(window.innerWidth, window.innerHeight);
});

export default game;
