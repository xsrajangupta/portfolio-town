import { ASSET_KEYS, INTERACT } from '../config.js';
import { Player } from '../objects/Player.js';
import { Building } from '../objects/Building.js';
import { NPC } from '../objects/NPC.js';
import { openSection, closeSection, isOpen, onClose } from '../ui/ContentPanel.js';
import { openDialogue, closeDialogue, isDialogueOpen, onDialogueClose } from '../ui/DialogueBox.js';
import { isLightboxOpen, closeLightbox } from '../ui/Lightbox.js';
import { AudioManager } from '../audio/AudioManager.js';
import { registerUiSound } from '../ui/uiSound.js';
import { loadSave, saveState } from '../save/SaveManager.js';

const hintEl = document.getElementById('interact-hint');
const hintLabelEl = document.getElementById('interact-hint-label');
const touchControlsEl = document.getElementById('touch-controls');
const settingsBtn = document.getElementById('settings-btn');

function isTouchDevice() {
  return 'ontouchstart' in window || navigator.maxTouchPoints > 0;
}

export class TownScene extends Phaser.Scene {
  constructor() {
    super('TownScene');
    this.buildings = [];
    this.nearestTarget = null; // { type: 'building'|'npc', ref }
  }

  create() {
    this._createMap();
    this._createTreeTextures();
    this._createLampTexture();
    this._createDecorTextures();
    this._createAmbientTextures();
    this._spawnTrees();
    this._spawnLamps();
    this._spawnDecor();
    this._spawnFountain();
    this._spawnBuildings();
    this._spawnNpcs();
    this._spawnPlayer();
    this._spawnAmbient();
    this._setupCamera();
    this._setupInput();
    this._setupTouchControls();
    this._setupAudio();
    this._setupSettingsButton();
    this._setupUnloadSave();

    onDialogueClose(() => {
      this.player.locked = false;
    });

    onClose(() => {
      this.player.locked = false;
    });
  }

  _createMap() {
    const map = this.make.tilemap({ key: ASSET_KEYS.map });
    const tileset = map.addTilesetImage('town_tileset', ASSET_KEYS.tileset);

    this.map = map;
    this.groundLayer = map.createLayer('Ground', tileset, 0, 0);
    this.pathLayer = map.createLayer('Paths', tileset, 0, 0);
    this.decorationLayer = map.createLayer('Decoration', tileset, 0, 0);

    this.physics.world.setBounds(0, 0, map.widthInPixels, map.heightInPixels);
    this.cameras.main.setBackgroundColor('#5fa53d');

    // Pond collision: block the water tiles flanking the bridge column so the
    // player can only cross via the bridge (decorative water feature).
    this.pondColliders = this.physics.add.staticGroup();
    const pondBlocks = [
      { x: 1 * 32, y: 1 * 32, w: 2 * 32, h: 3 * 32 }, // left of bridge
      { x: 4 * 32, y: 1 * 32, w: 3 * 32, h: 3 * 32 }, // right of bridge
    ];
    pondBlocks.forEach((b) => {
      const zone = this.add.zone(b.x + b.w / 2, b.y + b.h / 2, b.w, b.h);
      this.physics.add.existing(zone, true);
      this.pondColliders.add(zone);
    });
  }

  // ------------------------------------------------------------- TREES ----
  _createTreeTextures() {
    const make = (key, drawer, w = 40, h = 56) => {
      if (this.textures.exists(key)) return;
      const g = this.make.graphics({ x: 0, y: 0, add: false });
      drawer(g, w, h);
      g.generateTexture(key, w, h);
      g.destroy();
    };

    // classic round oak
    make('tree_oak', (g, w, h) => {
      g.fillStyle(0x6b4a2b, 1);
      g.fillRect(w / 2 - 4, h - 16, 8, 16);
      g.fillStyle(0x4a3018, 1);
      g.fillRect(w / 2 - 4, h - 16, 3, 16);
      g.fillStyle(0x2f7d3a, 1);
      g.fillCircle(w / 2, h - 20, 15);
      g.fillStyle(0x357f42, 1);
      g.fillCircle(w / 2, h - 32, 13);
      g.fillStyle(0x3a8a49, 1);
      g.fillCircle(w / 2, h - 44, 11);
      g.fillStyle(0x53a862, 1);
      g.fillCircle(w / 2 - 5, h - 46, 5);
    });

    // tall narrow pine
    make('tree_pine', (g, w, h) => {
      g.fillStyle(0x5c3d22, 1);
      g.fillRect(w / 2 - 3, h - 12, 6, 12);
      const tiers = [
        { y: h - 14, r: 15, c: 0x235c34 },
        { y: h - 26, r: 13, c: 0x2a6d3d },
        { y: h - 37, r: 11, c: 0x2f7d46 },
        { y: h - 47, r: 8, c: 0x357f42 },
      ];
      tiers.forEach((t) => {
        g.fillStyle(t.c, 1);
        g.fillTriangle(w / 2 - t.r, t.y, w / 2 + t.r, t.y, w / 2, t.y - t.r * 1.3);
      });
      g.fillStyle(0xffffff, 0.12);
      g.fillTriangle(w / 2 - 6, h - 44, w / 2, h - 44, w / 2 - 2, h - 52);
    }, 34, 58);

    // sakura (pink blossom) tree
    make('tree_sakura', (g, w, h) => {
      g.fillStyle(0x6b4a2b, 1);
      g.fillRect(w / 2 - 4, h - 16, 8, 16);
      g.fillStyle(0x8a6a49, 1);
      g.fillRect(w / 2 - 4, h - 16, 3, 16);
      const blobs = [
        [w / 2, h - 20, 15, 0xd888b0],
        [w / 2 - 9, h - 30, 10, 0xe6a0c4],
        [w / 2 + 9, h - 30, 10, 0xe6a0c4],
        [w / 2, h - 38, 12, 0xf0b8d2],
      ];
      blobs.forEach(([x, y, r, c]) => {
        g.fillStyle(c, 1);
        g.fillCircle(x, y, r);
      });
      // scattered blossom dots
      g.fillStyle(0xffe6f2, 0.9);
      for (let i = 0; i < 10; i++) {
        const bx = w / 2 - 14 + ((i * 7) % 28);
        const by = h - 42 + ((i * 5) % 26);
        g.fillCircle(bx, by, 1.2);
      }
    });

    // rounded bush-tree (low, wide)
    make('tree_bush', (g, w, h) => {
      g.fillStyle(0x2e6e38, 1);
      g.fillCircle(w / 2, h - 12, 14);
      g.fillStyle(0x367d42, 1);
      g.fillCircle(w / 2 - 7, h - 16, 10);
      g.fillCircle(w / 2 + 7, h - 16, 10);
      g.fillStyle(0x4c9457, 1);
      g.fillCircle(w / 2, h - 20, 9);
    }, 36, 34);

    // small sapling
    make('tree_sapling', (g, w, h) => {
      g.fillStyle(0x6b4a2b, 1);
      g.fillRect(w / 2 - 2, h - 8, 4, 8);
      g.fillStyle(0x3a8a49, 1);
      g.fillCircle(w / 2, h - 12, 7);
      g.fillStyle(0x53a862, 1);
      g.fillCircle(w / 2 - 2, h - 14, 3);
    }, 20, 24);
  }

  _spawnTrees() {
    const treeLayer = this.map.getObjectLayer('Trees');
    this.treeColliders = this.physics.add.staticGroup();

    treeLayer.objects.forEach((obj) => {
      const props = {};
      (obj.properties || []).forEach((p) => (props[p.name] = p.value));
      const scale = props.scale ?? 1;
      const variant = props.variant || 'oak';
      const key = `tree_${variant}`;
      const tree = this.add.image(obj.x, obj.y, this.textures.exists(key) ? key : 'tree_oak');
      tree.setOrigin(0.5, 0.92);
      tree.setScale(scale);
      tree.setDepth(obj.y);

      // soft ground shadow beneath the canopy
      const shadow = this.add.ellipse(obj.x, obj.y - 2, 22 * scale, 8 * scale, 0x000000, 0.18);
      shadow.setDepth(obj.y - 1);

      const collider = this.add.zone(obj.x, obj.y - 4, 14 * scale, 14 * scale);
      this.physics.add.existing(collider, true);
      this.treeColliders.add(collider);
    });
  }

  // -------------------------------------------------------------- LAMPS ---
  _createLampTexture() {
    if (this.textures.exists('lamp_tex')) return;
    const g = this.make.graphics({ x: 0, y: 0, add: false });
    const w = 16;
    const h = 44;
    g.fillStyle(0x2c2c2c, 1);
    g.fillRect(w / 2 - 2, 14, 4, h - 14);
    g.fillStyle(0x3a3a3a, 1);
    g.fillRect(w / 2 - 6, 8, 12, 4);
    g.fillStyle(0xffe08a, 1);
    g.fillCircle(w / 2, 8, 6);
    g.generateTexture('lamp_tex', w, h);
    g.destroy();

    const glow = this.make.graphics({ x: 0, y: 0, add: false });
    glow.fillStyle(0xffe08a, 0.35);
    glow.fillCircle(20, 20, 20);
    glow.generateTexture('lamp_glow_tex', 40, 40);
    glow.destroy();
  }

  _spawnLamps() {
    const lampLayer = this.map.getObjectLayer('Lamps');
    if (!lampLayer) return;
    lampLayer.objects.forEach((obj) => {
      const glow = this.add.image(obj.x, obj.y - 30, 'lamp_glow_tex');
      glow.setDepth(obj.y - 1);
      glow.setBlendMode(Phaser.BlendModes.ADD);
      this.tweens.add({
        targets: glow,
        alpha: { from: 0.5, to: 0.85 },
        duration: 1400 + Math.random() * 600,
        yoyo: true,
        repeat: -1,
        ease: 'Sine.inOut',
      });

      const lamp = this.add.image(obj.x, obj.y, 'lamp_tex');
      lamp.setOrigin(0.5, 1);
      lamp.setDepth(obj.y);
    });
  }

  // ------------------------------------------------------------- DECOR ----
  _createDecorTextures() {
    const make = (key, w, h, drawer) => {
      if (this.textures.exists(key)) return;
      const g = this.make.graphics({ x: 0, y: 0, add: false });
      drawer(g, w, h);
      g.generateTexture(key, w, h);
      g.destroy();
    };

    make('bench_tex', 30, 20, (g, w, h) => {
      g.fillStyle(0x5c3d22, 1);
      g.fillRect(2, 6, w - 4, 4);
      g.fillRect(2, 12, w - 4, 3);
      g.fillStyle(0x40260f, 1);
      g.fillRect(4, 9, 3, 9);
      g.fillRect(w - 7, 9, 3, 9);
      g.fillStyle(0x7a5230, 1);
      g.fillRect(2, 6, w - 4, 1);
    });

    make('barrel_tex', 20, 22, (g, w, h) => {
      g.fillStyle(0x8a5a30, 1);
      g.fillRoundedRect(2, 2, w - 4, h - 4, 4);
      g.fillStyle(0x6e4522, 1);
      g.fillRect(2, 4, w - 4, 3);
      g.fillRect(2, h - 8, w - 4, 3);
      g.fillStyle(0xa8703e, 1);
      g.fillRect(4, 7, w - 8, h - 14);
    });

    make('flowerpot_tex', 18, 22, (g, w, h) => {
      g.fillStyle(0xb5673a, 1);
      g.fillRect(3, 12, w - 6, 8);
      g.fillStyle(0x8f4f2b, 1);
      g.fillRect(2, 10, w - 4, 3);
      const petals = [0xe06868, 0xe0c850, 0xd888c8];
      for (let i = 0; i < 5; i++) {
        g.fillStyle(petals[i % petals.length], 1);
        g.fillCircle(5 + (i % 3) * 4, 6 - (i % 2) * 3, 2.4);
      }
      g.fillStyle(0x3f7d3f, 1);
      g.fillRect(w / 2 - 1, 8, 2, 6);
    });

    make('mailbox_tex', 16, 26, (g, w, h) => {
      g.fillStyle(0x4a4a4a, 1);
      g.fillRect(w / 2 - 1, 10, 2, 16);
      g.fillStyle(0xb0473f, 1);
      g.fillRoundedRect(1, 0, w - 2, 12, 4);
      g.fillStyle(0xd0655c, 1);
      g.fillRect(1, 0, w - 2, 3);
      g.fillStyle(0xe8e8e8, 1);
      g.fillRect(2, 5, 4, 2);
    });

    make('log_tex', 32, 14, (g, w, h) => {
      g.fillStyle(0x6b4a2b, 1);
      g.fillRoundedRect(0, 2, w, h - 4, 5);
      g.fillStyle(0x8a6440, 1);
      g.fillCircle(3, h / 2, 5);
      g.fillCircle(w - 3, h / 2, 5);
      g.fillStyle(0x5c3d22, 1);
      g.fillCircle(3, h / 2, 2.4);
      g.fillCircle(w - 3, h / 2, 2.4);
      for (let x = 8; x < w - 8; x += 6) {
        g.lineStyle(1, 0x54371f, 0.6);
        g.lineBetween(x, 3, x, h - 3);
      }
    });

    make('signboard_tex', 26, 30, (g, w, h) => {
      g.fillStyle(0x6b4a2b, 1);
      g.fillRect(w / 2 - 2, 14, 4, 16);
      g.fillStyle(0xd8c39a, 1);
      g.fillRoundedRect(1, 0, w - 2, 16, 3);
      g.fillStyle(0xb89c6e, 1);
      g.fillRect(1, 0, w - 2, 3);
      g.lineStyle(1, 0x8a734e, 0.8);
      g.lineBetween(4, 8, w - 4, 8);
      g.lineBetween(4, 11, w - 4, 11);
    });
  }

  _spawnDecorLayer(layerName, textureKey, originY = 1) {
    const layer = this.map.getObjectLayer(layerName);
    if (!layer) return;
    layer.objects.forEach((obj) => {
      const img = this.add.image(obj.x, obj.y, textureKey);
      img.setOrigin(0.5, originY);
      img.setDepth(obj.y);
      const shadow = this.add.ellipse(obj.x, obj.y - 1, img.width * 0.7, 6, 0x000000, 0.16);
      shadow.setDepth(obj.y - 1);
    });
  }

  _spawnDecor() {
    this._spawnDecorLayer('Benches', 'bench_tex', 0.9);
    this._spawnDecorLayer('Barrels', 'barrel_tex', 1);
    this._spawnDecorLayer('FlowerPots', 'flowerpot_tex', 1);
    this._spawnDecorLayer('Mailboxes', 'mailbox_tex', 1);
    this._spawnDecorLayer('Logs', 'log_tex', 0.85);
    this._spawnDecorLayer('Signboards', 'signboard_tex', 1);
  }

  // ----------------------------------------------------------- FOUNTAIN ---
  _spawnFountain() {
    const layer = this.map.getObjectLayer('Fountain');
    if (!layer || !layer.objects.length) return;
    const { x, y } = layer.objects[0];
    const depth = y + 40;

    // wide stone base
    const baseShadow = this.add.ellipse(x, y + 30, 120, 34, 0x000000, 0.2);
    baseShadow.setDepth(depth - 2);

    const rim = this.add.graphics();
    rim.fillStyle(0xb8b8bc, 1);
    rim.fillCircle(0, 0, 58);
    rim.fillStyle(0x9a9aa0, 1);
    rim.fillCircle(0, 0, 46);
    rim.fillStyle(0x6fa8d8, 1);
    rim.fillCircle(0, 0, 40);
    rim.setPosition(x, y);
    rim.setDepth(depth - 1);

    // inner basin water (animated ripple rings)
    const waterRings = [];
    for (let i = 0; i < 3; i++) {
      const ring = this.add.circle(x, y, 8 + i * 10, 0x9fd4ee, 0.35);
      ring.setStrokeStyle(2, 0xe4f4ff, 0.5);
      ring.setDepth(depth);
      waterRings.push(ring);
      this.tweens.add({
        targets: ring,
        radius: { from: 8 + i * 10, to: 42 },
        alpha: { from: 0.5, to: 0 },
        duration: 2200,
        delay: i * 700,
        repeat: -1,
        ease: 'Sine.out',
      });
    }

    // central spout tiers
    const spout = this.add.graphics();
    spout.fillStyle(0xc4c4c8, 1);
    spout.fillRoundedRect(-8, -34, 16, 24, 3);
    spout.fillStyle(0xa8a8ae, 1);
    spout.fillCircle(0, -34, 10);
    spout.fillStyle(0x7fbfe8, 1);
    spout.fillCircle(0, -34, 6);
    spout.setPosition(x, y);
    spout.setDepth(depth + 1);

    // little jets of water shooting up + falling (simple tweened droplets)
    for (let i = 0; i < 5; i++) {
      const angle = (i / 5) * Math.PI * 2;
      const dx = Math.cos(angle) * 3;
      const drop = this.add.circle(x + dx, y - 34, 1.6, 0xdff3fb, 0.9);
      drop.setDepth(depth + 1);
      this.tweens.add({
        targets: drop,
        y: { from: y - 34, to: y - 8 },
        x: { from: x + dx, to: x + dx + Math.cos(angle) * 14 },
        alpha: { from: 0.9, to: 0 },
        duration: 900 + i * 80,
        delay: i * 160,
        repeat: -1,
        ease: 'Sine.in',
      });
    }

    // sparkle twinkles on the water surface
    for (let i = 0; i < 4; i++) {
      const sx = x + Phaser.Math.Between(-24, 24);
      const sy = y + Phaser.Math.Between(-16, 16);
      const spark = this.add.star(sx, sy, 4, 1, 2.4, 0xffffff, 0.8);
      spark.setDepth(depth + 1);
      this.tweens.add({
        targets: spark,
        alpha: { from: 0, to: 0.9 },
        scale: { from: 0.4, to: 1 },
        duration: 1000,
        delay: Phaser.Math.Between(0, 2000),
        yoyo: true,
        repeat: -1,
      });
    }

    // collision so the player walks around the fountain, not through it
    const collider = this.add.zone(x, y, 76, 60);
    this.physics.add.existing(collider, true);
    this.fountainCollider = collider;
  }

  // ---------------------------------------------------------- AMBIENT -----
  _createAmbientTextures() {
    const make = (key, w, h, drawer) => {
      if (this.textures.exists(key)) return;
      const g = this.make.graphics({ x: 0, y: 0, add: false });
      drawer(g, w, h);
      g.generateTexture(key, w, h);
      g.destroy();
    };

    make('butterfly_tex', 12, 10, (g, w, h) => {
      g.fillStyle(0x2c2c2c, 1);
      g.fillRect(w / 2 - 1, 1, 2, h - 2);
      g.fillStyle(0xf2a63c, 1);
      g.fillEllipse(w / 2 - 3, h / 2 - 1, 5, 4);
      g.fillEllipse(w / 2 + 3, h / 2 - 1, 5, 4);
      g.fillStyle(0xffd77a, 1);
      g.fillEllipse(w / 2 - 3, h / 2 + 2, 3, 2.4);
      g.fillEllipse(w / 2 + 3, h / 2 + 2, 3, 2.4);
    });
    make('butterfly_tex_blue', 12, 10, (g, w, h) => {
      g.fillStyle(0x2c2c2c, 1);
      g.fillRect(w / 2 - 1, 1, 2, h - 2);
      g.fillStyle(0x5c8fe0, 1);
      g.fillEllipse(w / 2 - 3, h / 2 - 1, 5, 4);
      g.fillEllipse(w / 2 + 3, h / 2 - 1, 5, 4);
      g.fillStyle(0x9dc0f2, 1);
      g.fillEllipse(w / 2 - 3, h / 2 + 2, 3, 2.4);
      g.fillEllipse(w / 2 + 3, h / 2 + 2, 3, 2.4);
    });
    make('leaf_tex', 8, 8, (g, w, h) => {
      g.fillStyle(0x6fa84a, 0.9);
      g.fillEllipse(w / 2, h / 2, 6, 4);
      g.lineStyle(1, 0x4c7a34, 0.8);
      g.lineBetween(1, h / 2, w - 1, h / 2);
    });
    make('bird_tex', 14, 10, (g, w, h) => {
      g.fillStyle(0x3c3c3c, 0.85);
      g.fillTriangle(0, h / 2, w / 2, 1, w / 2, h - 1);
      g.fillTriangle(w, h / 2, w / 2, 1, w / 2, h - 1);
    });
  }

  _spawnAmbient() {
    const w = this.map.widthInPixels;
    const h = this.map.heightInPixels;

    // --- butterflies: gentle wandering loops within a small radius --------
    const butterflyKeys = ['butterfly_tex', 'butterfly_tex_blue'];
    for (let i = 0; i < 5; i++) {
      const homeX = Phaser.Math.Between(80, w - 80);
      const homeY = Phaser.Math.Between(80, h - 80);
      const key = butterflyKeys[i % butterflyKeys.length];
      const b = this.add.image(homeX, homeY, key);
      b.setDepth(homeY + 40);
      const flutter = () => {
        if (!b.active) return;
        const tx = homeX + Phaser.Math.Between(-60, 60);
        const ty = homeY + Phaser.Math.Between(-60, 60);
        this.tweens.add({
          targets: b,
          x: tx,
          y: ty,
          duration: Phaser.Math.Between(1800, 3200),
          ease: 'Sine.inOut',
          onUpdate: () => b.setDepth(b.y + 40),
          onComplete: flutter,
        });
      };
      this.tweens.add({
        targets: b,
        scaleX: { from: 1, to: -1 },
        duration: 260,
        yoyo: true,
        repeat: -1,
      });
      flutter();
    }

    // --- floating leaves: slow diagonal drift, wrap around when off-map ---
    for (let i = 0; i < 4; i++) {
      const leaf = this.add.image(Phaser.Math.Between(0, w), Phaser.Math.Between(0, h), 'leaf_tex');
      leaf.setDepth(9999);
      leaf.setAlpha(0.85);
      const speed = Phaser.Math.FloatBetween(6, 14);
      leaf.driftSpeed = speed;
      this.tweens.add({
        targets: leaf,
        angle: 360,
        duration: 4000 + i * 500,
        repeat: -1,
      });
      this._ambientLeaves = this._ambientLeaves || [];
      this._ambientLeaves.push(leaf);
    }

    // --- birds: occasional flyover across the map -------------------------
    const spawnBird = () => {
      const y0 = Phaser.Math.Between(40, 160);
      const fromLeft = Math.random() < 0.5;
      const bird = this.add.image(fromLeft ? -20 : w + 20, y0, 'bird_tex');
      bird.setDepth(9999);
      bird.setFlipX(!fromLeft);
      this.tweens.add({
        targets: bird,
        x: fromLeft ? w + 20 : -20,
        y: y0 + Phaser.Math.Between(-20, 20),
        duration: 9000,
        ease: 'Sine.inOut',
        onComplete: () => bird.destroy(),
      });
      this.time.delayedCall(Phaser.Math.Between(9000, 18000), spawnBird);
    };
    this.time.delayedCall(2000, spawnBird);
  }

  _updateAmbient(delta) {
    if (!this._ambientLeaves) return;
    const w = this.map.widthInPixels;
    const h = this.map.heightInPixels;
    this._ambientLeaves.forEach((leaf) => {
      leaf.y += leaf.driftSpeed * (delta / 1000);
      leaf.x += Math.sin(leaf.y * 0.02) * 0.3;
      if (leaf.y > h + 10) {
        leaf.y = -10;
        leaf.x = Phaser.Math.Between(0, w);
      }
    });
  }

  // ----------------------------------------------------------- BUILDINGS --
  _spawnBuildings() {
    const buildingLayer = this.map.getObjectLayer('Buildings');
    this.buildingColliders = this.physics.add.staticGroup();

    buildingLayer.objects.forEach((obj) => {
      const props = {};
      (obj.properties || []).forEach((p) => (props[p.name] = p.value));
      const building = new Building(this, {
        x: obj.x, y: obj.y, width: obj.width, height: obj.height, name: obj.name, ...props,
      });
      this.buildingColliders.add(building.collider);
      this.buildings.push(building);
    });
  }

  _spawnNpcs() {
    const npcLayer = this.map.getObjectLayer('NPCs');
    this.npcs = [];
    if (!npcLayer) return;
    npcLayer.objects.forEach((obj) => {
      const npc = new NPC(this, obj);
      this.npcs.push(npc);
    });
  }

  _spawnPlayer() {
    const spawnLayer = this.map.getObjectLayer('Spawn');
    const spawnObj = spawnLayer.objects.find((o) => o.name === 'player_start') || { x: 100, y: 100 };

    const save = loadSave();
    const startX = save.playerX ?? spawnObj.x;
    const startY = save.playerY ?? spawnObj.y;

    this.player = new Player(this, startX, startY);

    this.physics.add.collider(this.player, this.buildingColliders);
    this.physics.add.collider(this.player, this.treeColliders);
    this.physics.add.collider(this.player, this.pondColliders);
    if (this.fountainCollider) {
      this.physics.add.collider(this.player, this.fountainCollider);
    }
  }

  _setupCamera() {
    const cam = this.cameras.main;
    cam.startFollow(this.player, true, 0.12, 0.12);
    cam.setBounds(0, 0, this.map.widthInPixels, this.map.heightInPixels);
    cam.setZoom(1.4);

    this.scale.on('resize', (gameSize) => {
      cam.setSize(gameSize.width, gameSize.height);
    });
  }

  _setupInput() {
    this.interactKey = this.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.E);
    this.interactKey.on('down', () => this._tryInteract());

    this.input.keyboard.on('keydown-ESC', () => {
      if (isLightboxOpen()) closeLightbox();
      else if (isOpen()) closeSection();
      else if (isDialogueOpen()) closeDialogue();
    });
  }

  _setupTouchControls() {
    if (!isTouchDevice()) return;
    touchControlsEl.classList.remove('hidden');

    const bind = (selector, dir) => {
      const btn = touchControlsEl.querySelector(selector);
      const setState = (v) => (e) => {
        e.preventDefault();
        this.player.setTouchDirection(dir, v);
      };
      btn.addEventListener('touchstart', setState(true), { passive: false });
      btn.addEventListener('touchend', setState(false), { passive: false });
      btn.addEventListener('touchcancel', setState(false), { passive: false });
      btn.addEventListener('mousedown', setState(true));
      btn.addEventListener('mouseup', setState(false));
      btn.addEventListener('mouseleave', setState(false));
    };
    bind('.dpad-up', 'up');
    bind('.dpad-down', 'down');
    bind('.dpad-left', 'left');
    bind('.dpad-right', 'right');

    document.getElementById('touch-interact').addEventListener('click', () => this._tryInteract());
  }

  _setupAudio() {
    // Web Audio requires a user gesture before it can start on most browsers;
    // Phaser's sound manager handles the "unlock" automatically on first
    // pointerdown/keydown, we just create+play here.
    this.audio = new AudioManager(this);
    registerUiSound(() => this.audio.playClick());
    this._updateSettingsIcon();
  }

  _setupSettingsButton() {
    settingsBtn.addEventListener('click', () => {
      const muted = this.audio.toggleMute();
      this._updateSettingsIcon(muted);
    });
  }

  _updateSettingsIcon(mutedOverride) {
    const muted = mutedOverride ?? this.audio.muted;
    settingsBtn.textContent = muted ? '🔇' : '🔊';
  }

  _setupUnloadSave() {
    window.addEventListener('beforeunload', () => this._persist());
    this.time.addEvent({ delay: 5000, loop: true, callback: () => this._persist() });
  }

  _persist() {
    if (!this.player) return;
    saveState({ playerX: Math.round(this.player.x), playerY: Math.round(this.player.y) });
  }

  _tryInteract() {
    if (isLightboxOpen()) {
      closeLightbox();
      return;
    }
    if (isOpen()) {
      closeSection();
      this.player.locked = false;
      return;
    }
    if (isDialogueOpen()) {
      closeDialogue();
      return;
    }
    if (!this.nearestTarget) return;

    this.audio.playClick();
    if (this.nearestTarget.type === 'building') {
      openSection(this.nearestTarget.ref.key);
      this.player.locked = true;
    } else if (this.nearestTarget.type === 'npc') {
      openDialogue(this.nearestTarget.ref.name, this.nearestTarget.ref.dialogue);
      this.player.locked = true;
    }
    this._showHint(false);
  }

  _showHint(show, label) {
    if (!hintEl) return;
    if (label) hintLabelEl.textContent = label;
    hintEl.classList.toggle('hidden', !show);
  }

  _findNearestTarget() {
    const px = this.player.x;
    const py = this.player.y;
    let nearest = null;
    let nearestDist = Infinity;

    for (const b of this.buildings) {
      const cx = b.x + b.width / 2;
      const cy = b.y + b.height * 0.9;
      const dist = Phaser.Math.Distance.Between(px, py, cx, cy);
      if (dist < INTERACT.radius && dist < nearestDist) {
        nearest = { type: 'building', ref: b, label: `Enter ${b.title}` };
        nearestDist = dist;
      }
    }
    for (const n of this.npcs) {
      const dist = Phaser.Math.Distance.Between(px, py, n.x, n.y);
      if (dist < INTERACT.radius && dist < nearestDist) {
        nearest = { type: 'npc', ref: n, label: `Talk to ${n.name}` };
        nearestDist = dist;
      }
    }
    return nearest;
  }

  update(time, delta) {
    this.player.update();
    this.audio.updateFootsteps(this.player.isMoving && !this.player.locked, delta);
    this._updateAmbient(delta);

    const anyOverlayOpen = isOpen() || isDialogueOpen() || isLightboxOpen();
    if (!anyOverlayOpen) {
      const nearest = this._findNearestTarget();
      this.nearestTarget = nearest;
      this._showHint(!!nearest, nearest ? nearest.label : undefined);
    }
  }
}
