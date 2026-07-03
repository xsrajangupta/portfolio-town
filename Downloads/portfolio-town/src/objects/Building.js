const ICONS = {
  folder: '📁',
  user: '🙂',
  star: '⭐',
  trophy: '🏆',
  doc: '📄',
  mail: '✉️',
  clock: '⏰',
  ribbon: '🎗️',
  book: '🎓',
  flask: '🔬',
};

function shade(hex, amount) {
  // amount in [-1,1]; negative darkens, positive lightens
  const num = parseInt(hex.replace('#', ''), 16);
  let r = (num >> 16) & 0xff;
  let g = (num >> 8) & 0xff;
  let b = num & 0xff;
  const f = amount < 0 ? 0 : 255;
  const p = Math.abs(amount);
  r = Math.round(r + (f - r) * p);
  g = Math.round(g + (f - g) * p);
  b = Math.round(b + (f - b) * p);
  return (r << 16) + (g << 8) + b;
}

function toInt(hex) {
  return parseInt(hex.replace('#', ''), 16);
}

export class Building {
  /**
   * @param {Phaser.Scene} scene
   * @param {object} obj {x,y,width,height,name,title,color,accent,icon,blurb,
   *   wallStyle,roofStyle,doorStyle,windowStyle,windowCount,flag}
   */
  constructor(scene, obj) {
    this.scene = scene;
    this.key = obj.name;
    this.title = obj.title;
    this.color = obj.color || '#3f6fb0';
    console.log(this.title, this.color);
    this.accent = obj.accent || null; // optional secondary trim color (e.g. gold)
    this.icon = obj.icon;
    this.blurb = obj.blurb || '';
    this.wallStyle = obj.wallStyle || 'wall_brick';
    this.roofStyle = obj.roofStyle || 'roof_gable';
    this.doorStyle = obj.doorStyle || 'door';
    this.windowStyle = obj.windowStyle || 'window';
    this.windowCount = obj.windowCount || 2;
    this.hasFlag = !!obj.flag;

    const { x, y, width, height } = obj;
    this.x = x;
    this.y = y;
    this.width = width;
    this.height = height;

    this._buildVisual();
    this._buildCollision();

    this.playerInside = false;
  }

  _buildVisual() {
    const scene = this.scene;
    const { x, y, width, height } = this;
    const roofTall = this.roofStyle === 'roof_tower';
    const wallH = height * (roofTall ? 0.56 : 0.62);
    const roofH = height * (roofTall ? 0.48 : 0.42);
    const baseColor = shade(this.color, 0.35);
    const roofColor = shade(this.color, -0.25);
    const trimColor = this.accent ? toInt(this.accent) : shade(this.color, -0.55);

    const container = scene.add.container(0, 0);
    const depth = y + height;
    container.setDepth(depth);

    // ---- layered ground shadow (soft + tight) for real depth -------------
    const shadowSoft = scene.add.ellipse(x + width / 2, y + height - 2, width * 0.94, 30, 0x000000, 0.14);
    shadowSoft.setDepth(depth - 2);
    const shadowTight = scene.add.ellipse(x + width / 2, y + height - 4, width * 0.7, 18, 0x000000, 0.22);
    shadowTight.setDepth(depth - 1);

    // ---- decorative low stone footing / border ----------------------------
    const border = scene.add.image(x + width / 2, y + roofH + wallH + 3, 'building_parts', 'base_border');
    border.setDisplaySize(width * 0.96, 10);
    border.setTint(shade(this.color, -0.5));
    container.add(border);

    const wall = scene.add.image(x + width / 2, y + roofH + wallH / 2, 'building_parts', this.wallStyle);
    wall.setDisplaySize(width * 0.92, wallH);
    wall.setTint(baseColor);
    wall.setTintFill(baseColor);
    container.add(wall);

    // ---- corner posts for stronger silhouette / contrast against grass ---
    [x + width * 0.06, x + width * 0.94].forEach((cxp) => {
      const post = scene.add.image(cxp, y + roofH + wallH / 2, 'building_parts', 'corner_post');
      post.setDisplaySize(6, wallH);
      post.setTint(trimColor);
      container.add(post);
    });

    // ---- accent trim band partway down the wall ---------------------------
    const trimBand = scene.add.image(x + width / 2, y + roofH + wallH * 0.32, 'building_parts', 'trim');
    trimBand.setDisplaySize(width * 0.92, 5);
    trimBand.setTint(trimColor);
    container.add(trimBand);

    const door = scene.add.image(x + width / 2, y + roofH + wallH - 6, 'building_parts', this.doorStyle);
    door.setOrigin(0.5, 1);
    door.setDisplaySize(width * 0.16, wallH * 0.78);
    door.setTint(shade(this.color, -0.45));
    container.add(door);

    // door frame accent
    const doorTrim = scene.add.rectangle(
      x + width / 2, y + roofH + wallH - 6 - (wallH * 0.78) / 2,
      width * 0.16 + 4, wallH * 0.78 + 4
    );
    doorTrim.setStrokeStyle(2, trimColor, 0.9);
    doorTrim.setFillStyle(0x000000, 0);
    container.add(doorTrim);

    // ---- windows: count + positions vary per building for distinctness ---
    const winY = y + roofH + wallH * 0.4;
    const n = Math.max(2, Math.min(4, this.windowCount));
    const spread = width * 0.62;
    for (let i = 0; i < n; i++) {
      const t = n === 1 ? 0.5 : i / (n - 1);
      const off = (t - 0.5) * spread;
      if (Math.abs(off) < width * 0.1) continue; // keep clear of the door
      const win = scene.add.image(x + width / 2 + off, winY, 'building_parts', this.windowStyle);
      win.setDisplaySize(width * 0.13, wallH * 0.3);
      container.add(win);
      const winFrame = scene.add.rectangle(x + width / 2 + off, winY, width * 0.13 + 3, wallH * 0.3 + 3);
      winFrame.setStrokeStyle(1, trimColor, 0.8);
      winFrame.setFillStyle(0x000000, 0);
      container.add(winFrame);
    }
    const roof = scene.add.image(x + width / 2, y + roofH / 2, 'building_parts', this.roofStyle);
    roof.setDisplaySize(width * 1.04, roofH);
    roof.setTint(roofColor);
    roof.setTintFill(roofColor);
    container.add(roof);

    // roof ridge accent line
    const ridge = scene.add.rectangle(x + width / 2, y + roofH * 0.12, width * 0.5, 3, trimColor, 0.9);
    container.add(ridge);

    // chimney flourish for tower/gable buildings
    if (this.roofStyle !== 'roof_dome') {
      const chimney = scene.add.image(x + width * 0.74, y + roofH * 0.35, 'building_parts', 'chimney');
      chimney.setDisplaySize(width * 0.05, roofH * 0.6);
      chimney.setTint(shade(this.color, -0.35));
      container.add(chimney);
    }

    if (this.hasFlag) {
      const flag = scene.add.image(x + width / 2, y - roofH * 0.15, 'building_parts', 'flag');
      flag.setOrigin(0, 1);
      flag.setDisplaySize(24, 30);
      flag.setTint(trimColor);
      container.add(flag);
      scene.tweens.add({
        targets: flag,
        scaleX: { from: flag.scaleX, to: flag.scaleX * 0.85 },
        duration: 900,
        yoyo: true,
        repeat: -1,
        ease: 'Sine.inOut',
      });
    }

    const signW = Math.min(width * 0.8, 220);
    const sign = scene.add.image(x + width / 2, y - 4, 'building_parts', 'sign');
    sign.setDisplaySize(signW, 30);
    sign.setTint(shade(this.color, -0.5));
    container.add(sign);

    const signBorder = scene.add.rectangle(x + width / 2, y - 4, signW, 30);
    signBorder.setStrokeStyle(2, trimColor, 0.9);
    signBorder.setFillStyle(0x000000, 0);
    container.add(signBorder);

    const label = scene.add.text(
      x + width / 2,
      y - 4,
      `${ICONS[this.icon] || ''} ${this.title}`.trim(),
      { fontFamily: 'Inter, sans-serif', fontSize: '13px', fontStyle: '700', color: '#ffe9b0' }
    );
    label.setOrigin(0.5, 0.5);
    container.add(label);

    if (this.blurb) {
      const plaque = scene.add.text(x + width / 2, y + height + 14, this.blurb, {
        fontFamily: 'Inter, sans-serif',
        fontSize: '11px',
        color: '#eef2f6',
        backgroundColor: '#00000055',
        padding: { x: 6, y: 3 },
      });
      plaque.setOrigin(0.5, 0);
      plaque.setDepth(depth);
      this.plaque = plaque;
    }

    this.container = container;
  }

  _buildCollision() {
    const scene = this.scene;
    const { x, y, width, height } = this;
    const bodyW = width * 0.85;
    const bodyH = height * 0.5;
    const bodyX = x + (width - bodyW) / 2;
    const bodyY = y + height * 0.42;

    const zone = scene.add.zone(bodyX + bodyW / 2, bodyY + bodyH / 2, bodyW, bodyH);
    scene.physics.add.existing(zone, true);
    this.collider = zone;
  }

  setHighlighted(isHighlighted) {
    if (this.playerInside === isHighlighted) return;
    this.playerInside = isHighlighted;
  }
}
