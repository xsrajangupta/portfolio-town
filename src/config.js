// Central, tweakable game constants — nothing else in the codebase should
// hardcode magic numbers for these values.
export const TILE_SIZE = 32;

export const GAME = {
  backgroundColor: '#5fa53d',
};

export const PLAYER = {
  speed: 210,
  bodySize: { w: 20, h: 14 },
  bodyOffset: { x: 14, y: 30 },
  frameSize: 48,
  displayScale: 1.15,
};

export const INTERACT = {
  radius: 72, // px, proximity zone size around each building's door / NPC
  key: 'E',
};

export const ASSET_KEYS = {
  tileset: 'town_tileset',
  map: 'town_map',
  player: 'player',
  playerIdle: 'player_idle',
  guide: 'guide',
  buildingParts: 'building_parts',
  buildingPartsAtlas: 'building_parts_atlas',
  interactMarker: 'interact_marker',
  sfxClick: 'sfx_click',
  sfxFootstep: 'sfx_footstep',
  sfxAmbient: 'sfx_ambient',
  sfxBgm: 'sfx_bgm',
};

export const SAVE_KEY = 'portfolio-town-save-v1';
