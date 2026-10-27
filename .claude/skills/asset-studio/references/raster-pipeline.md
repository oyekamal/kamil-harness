# Raster & Sprite Sheet Pipeline Reference

For engines and cases where PNG is the right target (Unity, Godot, Phaser, perf-critical Flame entities, icon exports).

## Rendering SVG sources to PNG

```python
import cairosvg
cairosvg.svg2png(bytestring=svg_string.encode(), write_to=path,
                 output_width=320, output_height=320)  # 2x the 160 viewBox
```

Always render at **2× the design viewBox minimum** for high-DPI screens; engines downscale cleanly, never the reverse. Transparent backgrounds by default (no background rect in sprite SVGs).

## Sprite sheet construction

Horizontal strip, single row, equal square frames — the layout every engine's sheet loader handles without config:

```python
from PIL import Image
sheet = Image.new("RGBA", (fw * n, fh), (0, 0, 0, 0))
for i, im in enumerate(frames):
    sheet.paste(im, (i * fw, 0))
```

Order frames: loop cycle first (0..n), then distinct poses (jump, duck, hit) — and document the index map in the README. Keep the subject's ground-contact point at a consistent y across frames or the character will jitter.

## Engine integration snippets for READMEs

**Flame:**
```dart
final sheet = SpriteSheet(image: await images.load('hero.png'), srcSize: Vector2.all(320));
final run = sheet.createAnimation(row: 0, stepTime: 0.09, from: 0, to: 3);
final jumpSprite = sheet.getSprite(0, 3); // single-pose frame
```
Typical stepTimes: fast cycles (wheels, rolls) 0.08–0.12s, walks 0.25–0.3s, idle pulses 0.35–0.45s.

**Unity**: import as Sprite (2D and UI), Sprite Mode = Multiple, slice by cell size in the Sprite Editor; drive with an Animation clip or a frame-index script.

**Godot**: `AnimatedSprite2D` + `SpriteFrames`, "Add frames from sprite sheet", set h_frames = frame count, v_frames = 1.

**Phaser**: `this.load.spritesheet('hero', 'hero.png', { frameWidth: 320, frameHeight: 320 })`.

## Hitboxes (document in every game delivery)

Collision boxes ~70–80% of the visible body, positioned to exclude decorative effects (mist, glow, speed lines, shadows). Fair-feeling near-misses matter more than pixel accuracy. Publish per-asset suggested display size and hitbox rect in the README, scaled relative to the player's display size.

## Review artifacts

After generating a pack, always build a labeled contact sheet (`scripts/contact_sheet.py <dir> sheet.png`), VIEW it, and critique before delivering. For sprite deliveries, include a preview HTML animating the sheet with CSS `background-position` stepping (embed the PNG as base64 when under ~300KB) so the user sees motion without installing anything:

```javascript
setInterval(() => { frame = (frame + 1) % 3;
  el.style.backgroundPosition = (-frame * FRAME_W) + 'px 0'; }, 90);
```

## Deciding raster vs Lottie mid-project

If the user asks for easy resize/recolor, wants to edit assets later, or targets Flutter — switch to (or add) Lottie and say why. If they need hundreds of simultaneous entities or a raster-only engine — sprite sheets, with generator scripts shipped so re-exports at any resolution stay trivial. Offering both from the same SVG source costs little and has repeatedly been the answer users actually wanted.
