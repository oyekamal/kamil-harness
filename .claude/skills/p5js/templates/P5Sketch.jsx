import { useEffect, useRef } from 'react';
import p5 from 'p5';

// sketch(p, getProps) sets p.setup / p.draw. Props are read through a ref, so changing them
// does NOT recreate the sketch (no flicker, state kept).
export default function P5Sketch({ sketch, ...props }) {
  const host = useRef(null);
  const propsRef = useRef(props);
  propsRef.current = props;
  useEffect(() => {
    let disposed = false;
    const inst = new p5((p) => {
      sketch(p, () => propsRef.current);
      const userSetup = p.setup;
      // p5 2.3.4: remove() called before setup has run is a no-op (start is async), so a
      // StrictMode mount->unmount->mount leaks a live canvas. Finish the removal after setup.
      p.setup = async () => { if (userSetup) await userSetup(); if (disposed) p.remove(); };
    }, host.current);
    return () => { disposed = true; inst.remove(); };
  }, [sketch]);                          // keep `sketch` a module-level function (stable identity)
  return <div ref={host} />;
}
