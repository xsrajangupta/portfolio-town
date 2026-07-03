# Portfolio Town

A walkable, interactive pixel-art portfolio built with **Phaser 3**, **Vite**, and a
**Tiled**-format map. You control a character exploring a small village; an NPC
("Old Guide") greets you near the entrance, and six buildings each open a
section of the portfolio: **Projects, Resume, Skills, Experience,
Certifications, Contact**.

## Quick start

```bash
npm install
npm run dev       # http://localhost:5173
npm run build     # production build -> dist/
npm run preview   # preview the production build
```

Controls: **WASD / Arrow keys** to move, **E** to interact, **Esc** to close
any panel, click the speaker icon (top-right) to mute/unmute.

---

## Editing your content — no JavaScript required

Everything text-based lives in `src/data/*.json`:

| File | Powers |
|---|---|
| `about.json` | Your name / role, used in headers and the resume PDF |
| `projects.json` | The 10 project cards in the Projects building |
| `skills.json` | Skill categories + icons + proficiency bars |
| `experience.json` | The Experience building's timeline |
| `certifications.json` | The Certifications grid |
| `resume.json` | Resume summary + experience/education + PDF links |
| `contact.json` | Contact links (GitHub, LinkedIn, email, phone) |

Edit any of these, save, reload — **no other code changes are needed.**

### Adding an 11th project
Add another object to the array in `projects.json`:
```json
{
  "title": "New Project",
  "description": "One or two sentences.",
  "tech": ["React", "Node.js"],
  "github": "https://github.com/you/repo",
  "demo": "https://your-demo.example.com",
  "image": ""
}
```
Clicking a project card opens a detail popup in-game; the "GitHub"/"Live Demo"
buttons open those links directly — both behaviors from the same data.

### Replacing your resume
1. Put your real PDF at `public/resume.pdf` (same filename, or update
   `downloadUrl`/`viewUrl` in `resume.json`).
2. Optionally regenerate a fresh auto-built PDF from your JSON data instead:
   ```bash
   python3 tools/gen_resume_pdf.py
   ```
   (requires `pip install reportlab --break-system-packages`)

### Adding a building
Buildings are defined in `tools/gen_map.py` → `buildings_def`. Each entry has
a `key` (must match a renderer key in `src/ui/ContentPanel.js`), `title`,
`color`, `icon`, `wallStyle` (`wall_brick` / `wall_wood` / `wall_stone`),
`roofStyle` (`roof_gable` / `roof_hip` / `roof_dome` / `roof_tower`), and a
`tiles` rectangle for placement. Add an entry, then:
1. Add a matching renderer function in `src/ui/ContentPanel.js`'s `RENDERERS` map.
2. Regenerate the map: `python3 tools/gen_map.py`

---

## Architecture

```
public/
  assets/
    tilesets/town_tileset.png     ground/path/water tileset
    maps/town.json                Tiled JSON map (ground, paths, decoration,
                                   + object layers: buildings, spawn, trees,
                                   NPCs, lamps)
    characters/player.png         4-dir walk cycle (48x48 frames)
    characters/player_idle.png    4-dir idle-breathing animation
    npc/guide.png                 "Old Guide" NPC sprite
    buildings/building_parts.png  shared, tintable wall/roof/door/window/sign
                                   parts — this is the "reusable building
                                   component" system; 6 buildings, one sheet
    audio/*.wav                   click / footstep / ambient / bgm (synthesized)
  resume.pdf                      downloadable resume

src/
  main.js               Phaser bootstrap, full-viewport responsive scaling
  config.js              all tunable constants
  scenes/PreloadScene.js loads every asset, registers building-part sub-frames
  scenes/TownScene.js    builds the map, spawns buildings/NPC/trees/lamps/
                          player, drives interaction + audio + autosave
  objects/Player.js      arcade-physics player: walk/idle animation, touch input
  objects/NPC.js         stationary NPC with idle animation + dialogue payload
  objects/Building.js    reusable building component (wall/roof style + tint)
  audio/AudioManager.js  music/ambient/SFX playback + mute, backed by save state
  save/SaveManager.js    localStorage: last position, mute setting
  ui/ContentPanel.js     one panel renderer per building, fed by src/data/*.json
  ui/DialogueBox.js      NPC dialogue popup
  ui/Lightbox.js         project/certification detail popup
  data/*.json             <-- your editable content
  styles/main.css         layout, HUD, panels, dialogue, responsive rules

tools/
  gen_tileset.py          generates the ground/path/water tileset
  gen_sprites.py          generates player + NPC spritesheets
  gen_building_parts.py   generates the modular building-part sheet (3 wall
                           styles x 4 roof styles = distinct buildings)
  gen_map.py              generates public/assets/maps/town.json
  gen_audio.py            synthesizes click/footstep/ambient/bgm .wav files
  gen_resume_pdf.py       builds public/resume.pdf from the JSON data
```

**No tile is placed by hand in game code.** `tools/gen_map.py` produces a
standard Tiled JSON map; `TownScene.js` only *reads* it (`map.createLayer(...)`,
object-layer loops). Install the real **Tiled Map Editor** later and open
`public/assets/maps/town.json` directly — same layer names/property schema,
no code changes required.

---

## About the art & audio (read this before calling it "final")

Every visual and audio asset in this project is **procedurally generated by
the scripts in `tools/`** — there are no bundled third-party asset packs, so
there's nothing to license or attribute. That also means it's placeholder-
grade compared to hand-painted / commissioned RPG art or a composed
soundtrack. Two ways to upgrade it later without touching game logic:

1. **Regenerate with tweaks.** Open a `tools/gen_*.py` file, change colors/
   shapes/notes, rerun it. Frame names and sizes are documented in each
   script's docstring.
2. **Swap in real assets.** Replace the PNG/WAV files directly, keeping the
   same filenames, frame sizes (48×32 characters, 32×32 ground tiles), and
   frame names (`wall_brick`, `roof_gable`, `door`, `window`, `sign`, …) that
   `Building.js` / `Player.js` look up. Nothing else needs to change.
   `public/assets/audio/bgm.wav` and `ambient.wav` loop seamlessly if you
   replace them with your own tracks of any length.

## Responsive / mobile

The canvas fills the entire viewport (`Phaser.Scale.RESIZE`, no black bars)
on desktop, laptop, tablet, and mobile, and resizes live on window/orientation
change. On touch devices an on-screen D-pad + interact button appear
automatically (`_setupTouchControls` in `TownScene.js`).

## Save / progress

Player position and the mute setting are saved to `localStorage`
(`src/save/SaveManager.js`) every 5 seconds and on page unload, and restored
on load — closing the tab and coming back drops you where you left off.

## Deploying

`npm run build` outputs a static site in `dist/` with relative asset paths —
works from any subpath or static host (GitHub Pages, Netlify, Vercel, S3,
Cloudflare Pages, etc.). Just upload the contents of `dist/`.
