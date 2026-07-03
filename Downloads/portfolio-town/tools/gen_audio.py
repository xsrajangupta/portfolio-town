"""
Synthesizes short WAV sound effects + loop tracks with numpy — no external
audio libraries or copyrighted samples. These are simple procedural sounds
(a chiptune-style loop, not a composed score); swap public/assets/audio/*.wav
with licensed/composed tracks later if you want a richer soundtrack.
"""
import numpy as np
import wave
import struct
import os

SR = 44100
OUT = "/home/claude/uploaded_project/public/assets/audio"
os.makedirs(OUT, exist_ok=True)


def write_wav(path, samples, sr=SR):
    samples = np.clip(samples, -1, 1)
    data = (samples * 32767).astype(np.int16)
    with wave.open(path, "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(data.tobytes())


def envelope(n, attack=0.02, release=0.3):
    t = np.linspace(0, 1, n)
    a = np.clip(t / attack, 0, 1)
    r = np.clip((1 - t) / release, 0, 1)
    return np.minimum(a, r)


def tone(freq, dur, sr=SR, wave_type="sine"):
    t = np.linspace(0, dur, int(sr * dur), endpoint=False)
    if wave_type == "sine":
        return np.sin(2 * np.pi * freq * t)
    if wave_type == "square":
        return np.sign(np.sin(2 * np.pi * freq * t))
    if wave_type == "triangle":
        return 2 * np.abs(2 * (t * freq - np.floor(t * freq + 0.5))) - 1
    return np.sin(2 * np.pi * freq * t)


# ---- UI click ----
n = int(SR * 0.08)
click = tone(880, 0.08, wave_type="square") * envelope(n, 0.005, 0.15)
write_wav(f"{OUT}/click.wav", click * 0.35)

# ---- Footstep (short filtered noise thump) ----
n = int(SR * 0.09)
noise = np.random.uniform(-1, 1, n)
thump = tone(120, 0.09, wave_type="sine") * 0.6
foot = (noise * 0.25 + thump) * envelope(n, 0.01, 0.5)
write_wav(f"{OUT}/footstep.wav", foot * 0.4)

# ---- Ambient village loop (soft wind-like filtered noise + distant chime) ----
dur = 6.0
n = int(SR * dur)
t = np.linspace(0, dur, n, endpoint=False)
wind = np.random.uniform(-1, 1, n)
# crude low-pass via moving average
kernel = np.ones(200) / 200
wind = np.convolve(wind, kernel, mode="same")
chime = np.zeros(n)
for beat in [0.5, 2.3, 4.1]:
    idx0 = int(beat * SR)
    seg_n = int(SR * 0.6)
    if idx0 + seg_n < n:
        seg = tone(1046, 0.6, wave_type="sine") * envelope(seg_n, 0.02, 0.9) * 0.15
        chime[idx0:idx0 + seg_n] += seg
fade = np.ones(n)
fade_n = int(SR * 0.5)
fade[:fade_n] = np.linspace(0, 1, fade_n)
fade[-fade_n:] = np.linspace(1, 0, fade_n)
ambient = (wind * 0.5 + chime) * fade
write_wav(f"{OUT}/ambient.wav", ambient * 0.5)

# ---- Background chiptune loop (simple arpeggio, loops cleanly) ----
bpm = 100
beat_dur = 60 / bpm
notes = [261.63, 329.63, 392.00, 523.25, 392.00, 329.63, 293.66, 261.63]  # C major-ish arpeggio
bgm_parts = []
for f in notes:
    n = int(SR * beat_dur)
    seg = tone(f, beat_dur, wave_type="triangle") * envelope(n, 0.01, 0.85)
    bgm_parts.append(seg * 0.28)
bgm = np.concatenate(bgm_parts)
# add a soft bass note under every 2 beats
bass_notes = [130.81, 130.81, 164.81, 164.81, 130.81, 130.81, 146.83, 146.83]
bass_parts = []
for f in bass_notes:
    n = int(SR * beat_dur)
    seg = tone(f, beat_dur, wave_type="sine") * envelope(n, 0.02, 0.9)
    bass_parts.append(seg * 0.18)
bass = np.concatenate(bass_parts)
bgm = bgm[: len(bass)] + bass[: len(bgm)]
write_wav(f"{OUT}/bgm.wav", bgm)

print("audio written:", os.listdir(OUT))
