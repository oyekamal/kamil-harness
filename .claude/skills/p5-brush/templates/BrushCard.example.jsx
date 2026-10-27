import { StrictMode, useMemo } from 'react'
import { createRoot } from 'react-dom/client'
import { renderBoard, arrow } from './brushBoard'

function BrushCard({ id, w, h, draw, children, bg }) {
  const src = useMemo(() => renderBoard(id, w, h, { bg, seed: id.length * 7 }, draw), [id, w, h])
  return (
    <div className="card" style={{ position: 'relative', width: w, height: h, margin: 10 }}>
      <img src={src} width={w} height={h} alt="" style={{ display: 'block' }} />
      {children}
    </div>
  )
}
const L = (x, y, t, c = '#1f2937') => <div style={{ position: 'absolute', left: x, top: y, transform: 'translate(-50%,-50%)', font: '600 18px system-ui', color: c }}>{t}</div>

function App() {
  return (
    <div id="wrap" style={{ display: 'inline-block' }}>
      <BrushCard id="solve-1" w={640} h={220} draw={(b) => {
        b.wiggle(1)
        b.set('whiteboard', '#1f2937', 1); b.rect(30, 65, 200, 90)
        b.set('whiteboard', '#15803d', 1); b.rect(420, 65, 180, 90)
        b.noField()
        b.set('whiteboard', '#dc2626', 0.9); arrow(b, 245, 110, 405, 110)
      }}>{L(130, 110, '2x + 3 = 11')}{L(510, 110, 'x = 4')}{L(325, 80, '−3, ÷2', '#dc2626')}</BrushCard>
      <BrushCard id="cell-2" w={400} h={260} draw={(b) => {
        b.set('whiteboard', '#1d4ed8', 1); b.circle(200, 130, 100, 0.2)
        b.fill('#93c5fd', 70); b.fillBleed(0.2); b.fillTexture(0.3, 0.3); b.noStroke(); b.circle(200, 130, 40); b.noFill()
      }}>{L(200, 130, 'nucleus')}</BrushCard>
      <BrushCard id="chalk-3" w={400} h={260} bg="#2b3a33" draw={(b) => {
        b.set('charcoal', '#f1f5f9', 1); b.polygon([[40, 220], [360, 220], [360, 40]])
        b.hatchStyle('charcoal', '#fde68a', 0.8); b.hatch(12, Math.PI / 4, { rand: 0.15 }); b.noStroke(); b.polygon([[40, 220], [360, 220], [360, 40]]); b.noHatch()
      }} />
    </div>
  )
}
createRoot(document.getElementById('root')).render(<StrictMode><App /></StrictMode>)
setTimeout(() => (window.__done = true), 500)
