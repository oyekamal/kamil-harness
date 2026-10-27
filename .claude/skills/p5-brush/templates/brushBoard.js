// One module owns p5.brush: library state is module-global, so set it up once and draw into ONE shared WebGL canvas.
import * as brush from 'p5.brush/standalone'

let ready = false
function init() {
  if (ready) return            // StrictMode / HMR re-runs must not call scaleBrushes again (it multiplies)
  ready = true
  brush.scaleBrushes(2.5)
  brush.add('whiteboard', { type: 'marker', weight: 3, scatter: 0.12, opacity: 8, spacing: 0.025, pressure: [1.05, 0.95], markerTip: false, noise: 0.15 })
}

let surface = null
const cache = new Map()

/** Draws once with a fixed seed and returns a PNG data URL; the same key returns the cached image. */
export function renderBoard(key, w, h, { bg = '#ffffff', seed = 1, dpr = 2 } = {}, draw) {
  if (cache.has(key)) return cache.get(key)
  init()
  if (!surface) surface = document.createElement('canvas')
  surface.width = w * dpr
  surface.height = h * dpr
  brush.load(surface)
  brush.seed(seed); brush.noiseSeed(seed)
  brush.clear(bg)
  brush.push()
  brush.translate(-surface.width / 2, -surface.height / 2)
  brush.scale(dpr)
  draw(brush, w, h)
  brush.pop()
  brush.render()
  const url = surface.toDataURL('image/png')
  cache.set(key, url)
  return url
}

export function arrow(b, x1, y1, x2, y2, head = 16) {
  b.line(x1, y1, x2, y2)
  const a = Math.atan2(y2 - y1, x2 - x1)
  for (const s of [-1, 1]) b.line(x2, y2, x2 - head * Math.cos(a + s * 0.5), y2 - head * Math.sin(a + s * 0.5))
}
