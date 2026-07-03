import { ASSET_KEYS, PLAYER } from '../config.js';

const loadingFill = document.getElementById('loading-bar-fill');
const loadingScreen = document.getElementById('loading-screen');

export class PreloadScene extends Phaser.Scene {
  constructor() {
    super('PreloadScene');
  }

  preload() {
    this.load.on('progress', (value) => {
      if (loadingFill) loadingFill.style.width = `${Math.round(value * 100)}%`;
    });

    this.load.image(ASSET_KEYS.tileset, 'assets/tilesets/town_tileset.png');
    this.load.tilemapTiledJSON(ASSET_KEYS.map, 'assets/maps/town.json');

    this.load.spritesheet(ASSET_KEYS.player, 'assets/characters/player.png', {
      frameWidth: PLAYER.frameSize,
      frameHeight: PLAYER.frameSize,
    });
    this.load.spritesheet(ASSET_KEYS.playerIdle, 'assets/characters/player_idle.png', {
      frameWidth: PLAYER.frameSize,
      frameHeight: PLAYER.frameSize,
    });
    this.load.image(ASSET_KEYS.interactMarker, 'assets/characters/interact_marker.png');

    this.load.spritesheet(ASSET_KEYS.guide, 'assets/npc/guide.png', {
      frameWidth: PLAYER.frameSize,
      frameHeight: PLAYER.frameSize,
    });

    this.load.image(ASSET_KEYS.buildingParts, 'assets/buildings/building_parts.png');
    this.load.json(ASSET_KEYS.buildingPartsAtlas, 'assets/buildings/building_parts.json');

    this.load.audio(ASSET_KEYS.sfxClick, 'assets/audio/click.wav');
    this.load.audio(ASSET_KEYS.sfxFootstep, 'assets/audio/footstep.wav');
    this.load.audio(ASSET_KEYS.sfxAmbient, 'assets/audio/ambient.wav');
    this.load.audio(ASSET_KEYS.sfxBgm, 'assets/audio/bgm.wav');
  }

  create() {
    // Register named sub-frames on the building parts sheet (variable-size parts,
    // so a uniform spritesheet grid doesn't work — frames come from the JSON
    // that tools/gen_building_parts.py wrote out alongside the image).
    const atlas = this.cache.json.get(ASSET_KEYS.buildingPartsAtlas);
    const texture = this.textures.get(ASSET_KEYS.buildingParts);
    Object.entries(atlas).forEach(([name, f]) => {
      texture.add(name, 0, f.x, f.y, f.w, f.h);
    });

    if (loadingScreen) {
      loadingScreen.classList.add('hidden');
      setTimeout(() => loadingScreen.remove(), 400);
    }

    this.scene.start('TownScene');
  }
}
