import { ASSET_KEYS, PLAYER } from '../config.js';

const ROWS = { down: 0, left: 1, right: 2, up: 3 };
const COLS_PER_ROW = 5; // idle-a, idle-b, blink, walk-a, walk-b

export class NPC extends Phaser.GameObjects.Sprite {
  constructor(scene, obj) {
    const props = {};
    (obj.properties || []).forEach((p) => (props[p.name] = p.value));

    super(scene, obj.x, obj.y, ASSET_KEYS.guide, 0);
    scene.add.existing(this);

    this.name = props.name || 'NPC';
    this.dialogue = props.dialogue || '';
    this.direction = props.direction || 'down';
    this.homeX = obj.x;
    this.homeY = obj.y;

    this.setScale(PLAYER.displayScale);
    this.setOrigin(0.5, 0.85);
    this.setDepth(obj.y);

    this._createAnimations(scene);
    this.play(`npc-idle-${this.direction}`);
    this._startPatrolLoop(scene);
    this._startBlinkLoop(scene);
    this._startBounceLoop(scene);
  }

  _createAnimations(scene) {
    Object.entries(ROWS).forEach(([dir, row]) => {
      const start = row * COLS_PER_ROW;
      const idleKey = `npc-idle-${dir}`;
      if (!scene.anims.exists(idleKey)) {
        scene.anims.create({
          key: idleKey,
          frames: scene.anims.generateFrameNumbers(ASSET_KEYS.guide, { start, end: start + 1 }),
          frameRate: 1.6,
          repeat: -1,
        });
      }
      const blinkKey = `npc-blink-${dir}`;
      if (!scene.anims.exists(blinkKey)) {
        scene.anims.create({
          key: blinkKey,
          frames: [{ key: ASSET_KEYS.guide, frame: start + 2 }],
          frameRate: 1,
        });
      }
      const walkKey = `npc-walk-${dir}`;
      if (!scene.anims.exists(walkKey)) {
        scene.anims.create({
          key: walkKey,
          frames: scene.anims.generateFrameNumbers(ASSET_KEYS.guide, { start: start + 3, end: start + 4 }),
          frameRate: 4,
          repeat: -1,
        });
      }
    });
  }

  /** Gentle side-to-side stroll near the spawn point: walk a few steps, pause
   * and idle (with occasional blink), then walk back. Keeps the guide feeling
   * alive without wandering away from the fountain / dialogue trigger zone. */
  _startPatrolLoop(scene) {
    const range = 34;
    const walkDir = this.direction === 'up' || this.direction === 'down' ? 'right' : this.direction;

    const step = (toRight) => {
      if (!this.active) return;
      this.direction = toRight ? 'right' : 'left';
      this.play(`npc-walk-${this.direction}`, true);
      scene.tweens.add({
        targets: this,
        x: this.homeX + (toRight ? range : -range),
        duration: 1800,
        ease: 'Sine.inOut',
        onComplete: () => {
          if (!this.active) return;
          this.direction = 'down';
          this.play(`npc-idle-${this.direction}`, true);
          scene.time.delayedCall(2200, () => step(!toRight));
        },
      });
    };
    void walkDir;
    scene.time.delayedCall(1500, () => step(true));
  }

  _startBlinkLoop(scene) {
    scene.time.addEvent({
      delay: Phaser.Math.Between(2600, 4200),
      loop: true,
      callback: () => {
        if (!this.active || this.anims.currentAnim?.key.startsWith('npc-walk')) return;
        this.play(`npc-blink-${this.direction}`, true);
        scene.time.delayedCall(140, () => {
          if (this.active) this.play(`npc-idle-${this.direction}`, true);
        });
      },
    });
  }

  _startBounceLoop(scene) {
    scene.tweens.add({
      targets: this,
      scaleY: { from: PLAYER.displayScale, to: PLAYER.displayScale * 1.05 },
      scaleX: { from: PLAYER.displayScale, to: PLAYER.displayScale * 0.97 },
      duration: 1600,
      yoyo: true,
      repeat: -1,
      ease: 'Sine.inOut',
    });
  }

  preUpdate(time, delta) {
    super.preUpdate(time, delta);
    this.setDepth(this.y);
  }
}
