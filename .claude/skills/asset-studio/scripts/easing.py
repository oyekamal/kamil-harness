"""easing.py — standard easing curves for animation frame interpolation.

No dependency: pure math, Robert Penner's formulas (industry standard,
see https://easings.net). Use to turn a handful of key poses into a smooth
frame sequence instead of showing raw keyframes as linear steps.

Usage:
    from easing import ease_in_out_sine, ease_out_back, lerp, sample

    # interpolate N in-between frames across keyframe values [0, -22, 0]
    values = sample([0, -22, 0], n=12, ease=ease_in_out_sine)
"""
import math


def lerp(a, b, t):
    return a + (b - a) * t


def ease_in_out_sine(t):
    return -(math.cos(math.pi * t) - 1) / 2


def ease_out_back(t, overshoot=1.70158):
    """Landing/impact easing — slight overshoot then settle. Good for squash."""
    c1 = overshoot
    c3 = c1 + 1
    t -= 1
    return 1 + c3 * t ** 3 + c1 * t ** 2


def ease_out_bounce(t):
    n1, d1 = 7.5625, 2.75
    if t < 1 / d1:
        return n1 * t * t
    if t < 2 / d1:
        t -= 1.5 / d1
        return n1 * t * t + 0.75
    if t < 2.5 / d1:
        t -= 2.25 / d1
        return n1 * t * t + 0.9375
    t -= 2.625 / d1
    return n1 * t * t + 0.984375


def sample(keyframes, n, ease=ease_in_out_sine):
    """Interpolate `n` evenly-spaced samples across a list of keyframe values,
    applying `ease` within each segment. Returns a list of length n."""
    segments = len(keyframes) - 1
    out = []
    for i in range(n):
        pos = i / (n - 1) * segments
        seg = min(int(pos), segments - 1)
        t = ease(pos - seg)
        out.append(lerp(keyframes[seg], keyframes[seg + 1], t))
    return out


def demo():
    vals = sample([0, -22, 0], n=8, ease=ease_in_out_sine)
    assert len(vals) == 8
    assert vals[0] == 0 and abs(vals[-1]) < 1e-9
    assert min(vals) < -15  # actually reaches near the peak
    print("easing.py self-check OK:", [round(v, 1) for v in vals])


if __name__ == "__main__":
    demo()
