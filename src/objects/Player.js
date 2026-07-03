import { PLAYER, ASSET_KEYS } from '../config.js';

export class Player extends Phaser.Physics.Arcade.Sprite {
  constructor(scene, x, y) {
    super(scene, x, y, ASSET_KEYS.player, 0);
    scene.add.existing(this);
    scene.physics.add.existing(this);

    this.setScale(PLAYER.displayScale);
    this.setSize(PLAYER.bodySize.w, PLAYER.bodySize.h);
    this.setOffset(PLAYER.bodyOffset.x, PLAYER.bodyOffset.y);
    this.setCollideWorldBounds(true);

    this.direction = 'down';
    this.locked = false; // true while a content panel / dialogue is open
    this.isMoving = false;

    this._createAnimations(scene);
    this.play('idle-down');

    this.cursors = scene.input.keyboard.createCursorKeys();
    this.wasd = scene.input.keyboard.addKeys({
      up: Phaser.Input.Keyboard.KeyCodes.W,
      down: Phaser.Input.Keyboard.KeyCodes.S,
      left: Phaser.Input.Keyboard.KeyCodes.A,
      right: Phaser.Input.Keyboard.KeyCodes.D,
    });

    // External (touch) input state, merged with keyboard each frame
    this.touchState = { up: false, down: false, left: false, right: false };
  }

  _createAnimations(scene) {
    const rows = { down: 0, left: 1, right: 2, up: 3 };
    Object.entries(rows).forEach(([dir, row]) => {
      const start = row * 4;
      if (!scene.anims.exists(`walk-${dir}`)) {
        scene.anims.create({
          key: `walk-${dir}`,
          frames: scene.anims.generateFrameNumbers(ASSET_KEYS.player, { start, end: start + 3 }),
          frameRate: 9,
          repeat: -1,
        });
      }
      const idleStart = row * 2;
      if (!scene.anims.exists(`idle-${dir}`)) {
        scene.anims.create({
          key: `idle-${dir}`,
          frames: scene.anims.generateFrameNumbers(ASSET_KEYS.playerIdle, {
            start: idleStart,
            end: idleStart + 1,
          }),
          frameRate: 2,
          repeat: -1,
        });
      }
    });
  }

  setTouchDirection(dir, isDown) {
    if (dir in this.touchState) this.touchState[dir] = isDown;
  }

  update() {
    if (this.locked) {
      this.setVelocity(0, 0);
      this.isMoving = false;
      this.setTexture(ASSET_KEYS.playerIdle);
      this.play(`idle-${this.direction}`, true);
      this.setDepth(this.y);
      return;
    }

    const left = this.cursors.left.isDown || this.wasd.left.isDown || this.touchState.left;
    const right = this.cursors.right.isDown || this.wasd.right.isDown || this.touchState.right;
    const up = this.cursors.up.isDown || this.wasd.up.isDown || this.touchState.up;
    const down = this.cursors.down.isDown || this.wasd.down.isDown || this.touchState.down;

    let vx = 0;
    let vy = 0;
    if (left) vx -= 1;
    if (right) vx += 1;
    if (up) vy -= 1;
    if (down) vy += 1;

    const moving = vx !== 0 || vy !== 0;
    this.isMoving = moving;

    if (moving) {
      const len = Math.hypot(vx, vy) || 1;
      this.setVelocity((vx / len) * PLAYER.speed, (vy / len) * PLAYER.speed);

      if (Math.abs(vx) > Math.abs(vy)) {
        this.direction = vx > 0 ? 'right' : 'left';
      } else if (vy !== 0) {
        this.direction = vy > 0 ? 'down' : 'up';
      }
      this.setTexture(ASSET_KEYS.player);
      this.play(`walk-${this.direction}`, true);
    } else {
      this.setVelocity(0, 0);
      this.setTexture(ASSET_KEYS.playerIdle);
      this.play(`idle-${this.direction}`, true);
    }

    this.setDepth(this.y);
  }
}
